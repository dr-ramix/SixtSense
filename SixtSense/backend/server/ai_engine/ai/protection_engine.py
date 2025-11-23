# ai_engine/ai/protection_engine.py
from typing import List, Dict, Any


def recommend_protections(
    packages: List[Dict[str, Any]],
    state: Dict[str, Any],
    abstract_needs: List[str],
) -> List[Dict[str, Any]]:
    """
    Map abstract needs like ["full_cover", "liability", "roadside"]
    + state (trip_type, risk_aversion, kids, winter_driving)
    to concrete protectionPackages from API.
    """
    results = []

    risk = state.get("risk_aversion", "medium")
    trip_type = state.get("trip_type")
    winter = state.get("winter_driving", False)
    kids = state.get("kids", False)

    for pkg in packages:
        name = pkg["name"].lower()

        score = 0
        why_parts = []

        if "full_cover" in abstract_needs or risk == "high":
            if "peace of mind" in name or "cover the car & liability" in name:
                score += 3
                why_parts.append("You prefer strong protection.")

        if "liability" in abstract_needs or trip_type == "business":
            if "liability" in name:
                score += 2
                why_parts.append("Liability is important for your trip.")

        if "roadside" in abstract_needs or winter:
            if any(i.get("id") == "BC" for i in pkg.get("includes", [])):
                score += 2
                why_parts.append("Roadside help is useful for your conditions.")

        if kids:
            score += 1
            why_parts.append("Travelling with family usually benefits from better coverage.")

        if "no_protection" in abstract_needs and pkg["name"].lower().startswith("i don’t need protection"):
            score += 100  # force this one

        if score > 0:
            results.append(
                {
                    "id": pkg["id"],
                    "name": pkg["name"],
                    "total_price": pkg["price"]["totalPrice"]["amount"],
                    "currency": pkg["price"]["totalPrice"]["currency"],
                    "is_recommended": True,
                    "why": " ".join(why_parts) or "Matches your stated preferences.",
                }
            )

    # Fallback: if nothing matched, suggest the middle option as a safe choice
    if not results and packages:
        mid = sorted(
            packages, key=lambda p: p["price"]["totalPrice"]["amount"]
        )[len(packages) // 2]
        results.append(
            {
                "id": mid["id"],
                "name": mid["name"],
                "total_price": mid["price"]["totalPrice"]["amount"],
                "currency": mid["price"]["totalPrice"]["currency"],
                "is_recommended": True,
                "why": "Balanced protection for most customers.",
            }
        )

    return results[:3]


def recommend_addons(
    addons: List[Dict[str, Any]],
    state: Dict[str, Any],
    abstract_needs: List[str],
) -> List[Dict[str, Any]]:
    """
    Map abstract addon needs (child_seat, toll, additional_driver) + state
    to concrete addon options.
    """
    results = []
    has_kids = state.get("kids", False)

    for group in addons:
        for option in group.get("options", []):
            cd = option["chargeDetail"]
            info = option["additionalInfo"]
            cid = cd["id"]

            score = 0
            why_parts = []

            if "toll" in abstract_needs and cid == "T4":
                score += 2
                why_parts.append("You mentioned highways / long drives.")

            if "additional_driver" in abstract_needs and cid == "AD":
                score += 2
                why_parts.append("You want to share the driving.")

            if has_kids and cid in ["BS", "CS", "BO"]:
                score += 3
                why_parts.append("You travel with kids, a child seat is recommended.")

            if score > 0:
                price = info["price"]["displayPrice"]
                results.append(
                    {
                        "id": cd["id"],
                        "name": cd["title"],
                        "price_per_day": price["amount"],
                        "currency": price["currency"],
                        "why": " ".join(why_parts),
                        "is_recommended": True,
                    }
                )

    return results[:5]
