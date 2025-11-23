# ai_engine/ai/car_scoring.py
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI


def score_deal(deal: Dict[str, Any],
               profile: Dict[str, Any],
               original_total_price: float) -> float:
    """
    Rule-based scoring: matches vehicle features to customer needs.
    Higher score = better match for upselling.
    """
    score = 0.0
    vehicle = deal["vehicle"]
    pricing = deal["pricing"]

    # Core needs
    passengers = profile.get("passengers")
    if passengers and vehicle.get("passengersCount", 0) >= passengers:
        score += 3

    luggage = profile.get("luggage")
    if luggage == "many" and vehicle.get("bagsCount", 0) >= 4:
        score += 2

    # Comfort & trip type
    comfort = profile.get("comfort_priority")
    if comfort == "high":
        if vehicle.get("isMoreLuxury") or "PREMIUM" in vehicle.get("groupType", "").upper():
            score += 3

    trip_type = profile.get("trip_type")
    if trip_type == "family":
        if vehicle.get("groupType") in ["SUV", "MINIVAN"] or vehicle.get("passengersCount", 0) >= 7:
            score += 2
    if trip_type == "business":
        if "SEDAN" in vehicle.get("groupType", "") or vehicle.get("isMoreLuxury"):
            score += 2
    if trip_type == "party":
        # prefer fun / SUV / ‘moreLuxury’
        if vehicle.get("groupType") in ["SUV", "COUPE"] or vehicle.get("isMoreLuxury"):
            score += 2

    # Quality indicators
    if vehicle.get("isRecommended"):
        score += 1
    if vehicle.get("isNewCar"):
        score += 1

    # Price-based scoring: upsell but stay reasonable
    total_price = pricing["totalPrice"]["amount"]
    uplift = total_price - original_total_price
    if uplift > 0:
        # reward upsell, but cap it
        score += min(uplift / 40.0, 4.0)
    elif uplift == 0:
        score += 1.0  # same price is safe
    else:
        score += max(uplift / 100.0, -2.0)  # penalty if much cheaper

    # Extra bump for “higher tier”
    if total_price > original_total_price * 1.5:
        score += 3
    elif total_price > original_total_price * 1.2:
        score += 2
    elif total_price > original_total_price:
        score += 1

    return score


def rank_deals(deals: List[Dict[str, Any]],
               profile: Dict[str, Any],
               original_total_price: float,
               k: int = 3) -> List[Dict[str, Any]]:
    scored = []
    for d in deals:
        s = score_deal(d, profile, original_total_price)
        scored.append((s, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for s, d in scored[:k]]


def llm_rank_all_deals_batch(
    deals: List[Dict[str, Any]],
    profile: Dict[str, Any],
    original_total_price: float,
    k: int = 3,
    llm: Optional[ChatOpenAI] = None,
) -> List[Dict[str, Any]]:
    """
    Optional: use LLM to re-rank a small candidate set.
    """
    if not deals:
        return []

    if llm is None:
        # fallback to rule-based
        return rank_deals(deals, profile, original_total_price, k)

    # Build concise vehicle descriptions
    vehicles_summary = []
    for i, deal in enumerate(deals):
        v = deal["vehicle"]
        p = deal["pricing"]
        tags = []
        if v.get("isNewCar"):
            tags.append("New")
        if v.get("isRecommended"):
            tags.append("Recommended")
        if v.get("isMoreLuxury"):
            tags.append("Luxury")
        tags_str = f" [{', '.join(tags)}]" if tags else ""

        vehicles_summary.append(
            f"{i+1}. {v['brand']} {v['model']} - "
            f"{v['groupType']}, {v['passengersCount']} seats, "
            f"{v['bagsCount']} bags, {v['transmissionType']}, "
            f"{v['fuelType']}, {p['displayPrice']['amount']} {p['displayPrice']['currency']}/day "
            f"({p['totalPrice']['amount']} total){tags_str}"
        )

    profile_parts = []
    if profile.get("passengers"):
        profile_parts.append(f"{profile['passengers']} passengers")
    if profile.get("trip_type"):
        profile_parts.append(f"{profile['trip_type']} trip")
    if profile.get("comfort_priority"):
        profile_parts.append(f"{profile['comfort_priority']} comfort")
    if profile.get("luggage"):
        profile_parts.append(f"{profile['luggage']} luggage")
    if profile.get("budget_total"):
        profile_parts.append(f"budget: {profile['budget_total']}")

    customer_desc = ", ".join(profile_parts) if profile_parts else "general needs"

    prompt = f"""You are a car rental expert. Rank these {len(deals)} vehicles for this customer from BEST to WORST match.

Customer needs: {customer_desc}
Original booking price: {original_total_price}

Available vehicles:
{chr(10).join(vehicles_summary)}

Instructions:
- Balance customer fit with upsell opportunity.
- Do not pick something much more expensive if it’s not clearly better.
- Prefer vehicles that match passengers, luggage, trip type and comfort.
- Value for money is important.

Respond with ONLY the top {k} vehicle numbers in order, comma-separated (e.g., "3,1,2")."""

    try:
        resp = llm.invoke([{"role": "user", "content": prompt}])
        indices = [int(x.strip()) - 1 for x in resp.content.strip().split(",")]
        result = []
        for i in indices[:k]:
            if 0 <= i < len(deals):
                result.append(deals[i])
        return result or deals[:k]
    except Exception:
        return rank_deals(deals, profile, original_total_price, k)


def hybrid_rank_deals(
    deals: List[Dict[str, Any]],
    profile: Dict[str, Any],
    original_total_price: float,
    k: int = 3,
    use_llm: bool = False,
) -> List[Dict[str, Any]]:
    """
    Hybrid strategy: filter → rule-based scoring → optional LLM reranking.
    """
    filtered = []

    for d in deals:
        v = d["vehicle"]
        p = d["pricing"]

        # Hard filters
        if profile.get("passengers") and v["passengersCount"] < profile["passengers"]:
            continue

        if profile.get("luggage") == "many" and v.get("bagsCount", 0) < 3:
            continue

        budget = profile.get("budget_total")
        if budget and p["totalPrice"]["amount"] > budget * 1.5:
            # too expensive even for upsell
            continue

        filtered.append(d)

    if not filtered:
        filtered = deals

    if not use_llm:
        return rank_deals(filtered, profile, original_total_price, k)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    if len(filtered) <= 5:
        return llm_rank_all_deals_batch(filtered, profile, original_total_price, k, llm)
    elif len(filtered) <= 15:
        top_rule = rank_deals(filtered, profile, original_total_price, k=10)
        return llm_rank_all_deals_batch(top_rule, profile, original_total_price, k, llm)
    else:
        return rank_deals(filtered, profile, original_total_price, k)
