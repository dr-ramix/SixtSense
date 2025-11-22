import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.messages import ToolMessage

from sixt_client import SixtApiClient
profile_store: Dict[str, Dict] = {}

# ------------------- LLM setup -------------------
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.4,
)

# Prompt lungo preso dal file
PROMPT_PATH = Path(__file__).parent / "long_prompt.txt"
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# ------------------- Profilo utente -------------------

"""
def init_user_profile() -> Dict:
    return {
        "passengers": None,
        "luggage": None,
        "budget_total": None,
        "trip_type": None,
        "comfort_priority": None,
        "risk_aversion": None,
        "upgrade_openness": None,
    }
"""
def get_profile_for_booking(booking_id: str, original_total_price: float) -> Dict:
    """
    Restituisce il profilo cumulativo per questo booking.
    Se non esiste, lo crea con tutti i campi None + original_total_price.
    """
    if booking_id not in profile_store:
        profile_store[booking_id] = {
            "passengers": None,
            "luggage": None,
            "budget_total": None,
            "trip_type": None,
            "comfort_priority": None,
            "risk_aversion": None,
            "upgrade_openness": None,
            # salviamo anche il prezzo originale per eventuali usi futuri
            "original_total_price": original_total_price,
        }
    else:
        # se per qualche motivo non c'è ancora, lo aggiungiamo
        if "original_total_price" not in profile_store[booking_id]:
            profile_store[booking_id]["original_total_price"] = original_total_price

    return profile_store[booking_id]


def update_profile_from_text(profile: Dict, text: str) -> Dict:
    """
    Estrai preferenze base dal testo utente e aggiorna il profilo ESISTENTE
    senza azzerare le info precedenti.
    """
    t = text.lower()

    # Trip type – imposta solo se non c'è già, così non lo sovrascriviamo a caso
    if profile.get("trip_type") is None:
        if any(w in t for w in ["kids", "family", "children", "child"]):
            profile["trip_type"] = "family"
        if any(w in t for w in ["business", "work", "meeting"]):
            profile["trip_type"] = "business"

    # Comfort – se compaiono parole chiave, portiamo la comfort_priority a "high"
    if any(w in t for w in ["comfortable", "comfort", "luxury", "premium"]):
        profile["comfort_priority"] = "high"

    # Passeggeri – se trova un numero, aggiorniamo sempre (magari corregge)
    m = re.search(r"(\d+)\s*(people|persons|passengers|adults|kids|children)", t)
    if m:
        profile["passengers"] = int(m.group(1))

    # Bagagli
    if any(w in t for w in ["many bags", "a lot of luggage", "lots of luggage", "many suitcases", "big suitcases"]):
        profile["luggage"] = "many"

    # Budget – solo se menziona il budget e non abbiamo già un budget_total
    if any(w in t for w in ["tight budget", "not too expensive", "cheap", "low budget", "don't want to spend too much"]):
        if profile.get("budget_total") is None:
            otp = profile.get("original_total_price")
            if otp is not None:
                profile["budget_total"] = otp

    return profile


# ------------------- Scoring e ranking (su deals reali) -------------------

def score_deal(deal: Dict, profile: Dict, original_total_price: float) -> float:
    """
    Stessa logica del teammate, ma applicata ai deals reali dal Sixt API.
    """
    score = 0.0
    vehicle = deal["vehicle"]
    pricing = deal["pricing"]

    # Core needs: passengers
    if profile.get("passengers") and vehicle["passengersCount"] >= profile["passengers"]:
        score += 3

    # Luggage
    if profile.get("luggage") == "many" and vehicle["bagsCount"] >= 4:
        score += 2

    # Trip-type
    if profile.get("comfort_priority") == "high":
        if vehicle.get("isMoreLuxury") or "premium" in (vehicle.get("groupType") or "").lower():
            score += 3

    if profile.get("trip_type") == "family":
        if vehicle["groupType"] in ["SUV", "MINIVAN"] or vehicle["passengersCount"] >= 7:
            score += 2

    if profile.get("trip_type") == "business":
        if "SEDAN" in (vehicle["groupType"] or "") or vehicle.get("isMoreLuxury"):
            score += 2

    # Quality indicators
    if vehicle.get("isRecommended"):
        score += 1
    if vehicle.get("isNewCar"):
        score += 1

    # Prezzo
    uplift = pricing["totalPrice"]["amount"] - original_total_price
    if uplift > 0:
        score += min(uplift / 40, 4)
    elif uplift == 0:
        score += 1
    else:
        score += max(uplift / 100, -2)

    # Luxury
    if vehicle.get("isMoreLuxury"):
        score += 2

    total_price = pricing["totalPrice"]["amount"]
    if total_price > original_total_price * 1.5:
        score += 3
    elif total_price > original_total_price * 1.2:
        score += 2
    elif total_price > original_total_price:
        score += 1

    return score


def rank_deals(deals: List[Dict], profile: Dict, original_total_price: float, k: int = 3) -> List[Dict]:
    scored = []
    for d in deals:
        s = score_deal(d, profile, original_total_price)
        scored.append((s, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for s, d in scored[:k]]


def llm_rank_all_deals_batch(
    deals: List[Dict], profile: Dict, original_total_price: float, k: int = 3
) -> List[Dict]:
    """
    Opzionale: ranking via LLM; per ora lo teniamo, ma se vuoi puoi toglierlo.
    """
    if not deals:
        return []

    # Summary veicoli (testuale)
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
            f"{v.get('groupType','')}, {v['passengersCount']} seats, "
            f"{v['bagsCount']} bags, {v['transmissionType']}, "
            f"{v['fuelType']}, €{p['displayPrice']['amount']}/day "
            f"(€{p['totalPrice']['amount']} total){tags_str}"
        )

    profile_parts = []
    if profile.get("passengers"):
        profile_parts.append(f"{profile['passengers']} passengers")
    if profile.get("trip_type"):
        profile_parts.append(f"{profile['trip_type']} trip")
    if profile.get("comfort_priority"):
        profile_parts.append(f"{profile['comfort_priority']} comfort priority")
    if profile.get("luggage"):
        profile_parts.append(f"{profile['luggage']} luggage")
    if profile.get("budget_total"):
        profile_parts.append(f"budget: €{profile['budget_total']}")

    customer_desc = ", ".join(profile_parts) if profile_parts else "general needs"

    prompt = f"""You are a car rental expert. Rank these {len(deals)} vehicles for this customer from BEST to WORST match.

Customer needs: {customer_desc}
Original booking price: €{original_total_price}

Available vehicles:
{chr(10).join(vehicles_summary)}

Instructions:
- Consider how well each vehicle fits the customer's specific needs
- Value for money is important (price vs features)
- Prefer vehicles with practical features matching their trip type
- New and recommended vehicles are good but not if they don't fit needs
- Balance upsell opportunity with genuine customer benefit

Respond with ONLY the top {k} vehicle numbers in order, comma-separated (e.g., "3,7,1").
Best match first, worst of the top {k} last."""

    try:
        response = llm.invoke([{"role": "user", "content": prompt}])
        indices = [int(x.strip()) - 1 for x in response.content.strip().split(",")]
        result = []
        for i in indices[:k]:
            if 0 <= i < len(deals):
                result.append(deals[i])
        return result or deals[:k]
    except Exception:
        return rank_deals(deals, profile, original_total_price, k)


def hybrid_rank_deals(deals: List[Dict], profile: Dict, original_total_price: float, k: int = 3) -> List[Dict]:
    """
    Filtra + ranking (come nello script del teammate).
    """
    filtered = []
    for deal in deals:
        v = deal["vehicle"]
        p = deal["pricing"]

        if profile.get("passengers") and v["passengersCount"] < profile["passengers"]:
            continue
        if profile.get("budget_total"):
            if p["totalPrice"]["amount"] > profile["budget_total"] * 1.5:
                continue
        if profile.get("luggage") == "many" and v["bagsCount"] < 3:
            continue

        filtered.append(deal)

    if not filtered:
        filtered = deals

    if len(filtered) <= 5:
        return llm_rank_all_deals_batch(filtered, profile, original_total_price, k)
    elif len(filtered) <= 15:
        rule_top = rank_deals(filtered, profile, original_total_price, k=10)
        return llm_rank_all_deals_batch(rule_top, profile, original_total_price, k)
    else:
        return rank_deals(filtered, profile, original_total_price, k)

# ------------------- TOOL: get_top_upsell_deals -------------------

@tool("get_top_upsell_deals")
def get_top_upsell_deals(booking_id: str, user_message: str) -> str:
    """
    Tool chiamato dall'LLM per ottenere le top 3 offerte reali (deals) da SIXT
    per quella prenotazione e quel messaggio utente.

    Ritorna una lista JSON di oggetti:
    [
      {
        "vehicle_id": "...",
        "score": 6.5,
        "reason": "SKODA ENYAQ (SUV) · 5 seats · automatic ...",
      },
      ...
    ]
    """
    client = SixtApiClient()

    # Prendiamo i deals GREZZI dalla Sixt API (non pydantic)
    url = client._url(f"/api/booking/{booking_id}/vehicles")
    import requests
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    deals = data.get("deals", [])

    if not deals:
        return json.dumps([])

    original_total_price = next(
        (
            d["pricing"]["totalPrice"]["amount"]
            for d in deals
            if d.get("dealInfo") == "BOOKED_CATEGORY"
        ),
        deals[0]["pricing"]["totalPrice"]["amount"],
    )

    # Profilo CUMULATIVO per questo booking
    profile = get_profile_for_booking(booking_id, original_total_price)
    profile = update_profile_from_text(profile, user_message)
    print(f"[Profile for {booking_id}] {profile}") # Just for debugging

    top_deals = hybrid_rank_deals(deals, profile, original_total_price, k=3)

    results = []
    for d in top_deals:
        v = d["vehicle"]
        p = d["pricing"]
        score = score_deal(d, profile, original_total_price)

        parts = [f"{v['brand']} {v['model']} ({v.get('groupType','')})"]
        parts.append(f"{v['passengersCount']} seats")
        if v["bagsCount"]:
            parts.append(f"{v['bagsCount']} bags")
        parts.append(v["transmissionType"])
        parts.append(v["fuelType"])
        if v.get("isNewCar"):
            parts.append("new car")
        if v.get("isRecommended"):
            parts.append("recommended")
        if v.get("isMoreLuxury"):
            parts.append("more luxury")

        daily = p["displayPrice"]["amount"]
        total = p["totalPrice"]["amount"]
        parts.append(f"+{daily} {p['displayPrice']['currency']}/day (≈ {total} total)")

        reason = " · ".join(parts)

        results.append(
            {
                "vehicle_id": v["id"],
                "score": score,
                "reason": reason,
            }
        )

    return json.dumps(results, indent=2)


# LLM con tool associato
llm_with_tools = llm.bind_tools([get_top_upsell_deals])

# ------------------- Funzione principale da usare nel backend -------------------

# ------------------- VEHICLE STEP -------------------


def run_vehicle_chat(booking_id: str, user_message: str) -> dict:
    """
    Step auto (vehicle):
    - Calcola SEMPRE le top offerte (via get_top_upsell_deals)
    - Passa il risultato al modello come contesto
    - Ritorna un dict:
        {
          "step": "vehicle",
          "answer": str,
          "vehicle_recommendations": [ { "vehicle_id", "score", "reason" }, ... ]
        }
    """

    # 1) Calcola SEMPRE le top deals usando il tool (ma lo chiamiamo noi)
    try:
        tool_output_str = get_top_upsell_deals.invoke({
            "booking_id": booking_id,
            "user_message": user_message,
        })
    except Exception as e:
        print(f"[Warning] get_top_upsell_deals failed: {e}")
        tool_output_str = "[]"

    try:
        recs_data = json.loads(tool_output_str)
    except Exception as e:
        print(f"[Warning] failed to parse tool output as JSON: {e}")
        recs_data = []

    # 2) Riassunto testuale delle raccomandazioni per il modello
    if recs_data:
        lines = ["Here are the top upgrade options for this customer:"]
        for i, r in enumerate(recs_data, start=1):
            lines.append(f"{i}. {r.get('reason', '')}")
        recs_text = "\n".join(lines)
    else:
        recs_text = "No clear upgrade options could be determined for this booking."

    # 3) Prompt per il modello: prompt lungo + contesto + messaggio utente
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": (
                "You are currently in the VEHICLE SELECTION / UPGRADE step.\n"
                "The system has pre-computed the best matching upgrade options for this customer.\n"
                "Use them to give concrete, honest recommendations.\n\n"
                + recs_text
            ),
        },
        {"role": "user", "content": user_message},
    ]

    resp = llm.invoke(messages)
    answer = resp.content

    return {
        "step": "vehicle",
        "answer": answer,
        "vehicle_recommendations": recs_data,
    }

# ------------------- HELPERS: protections & addons -------------------


def summarize_protection_packages(packages) -> str:
    """
    packages è una lista di ProtectionPackage (pydantic) ritornati da SixtApiClient.
    """
    lines = []
    for i, pkg in enumerate(packages, start=1):
        name = pkg.name
        display = pkg.price.displayPrice
        amount = display.amount
        currency = display.currency
        suffix = display.suffix or ""

        includes_titles = [inc.title for inc in pkg.includes]
        if includes_titles:
            includes_str = ", ".join(includes_titles[:3])
            if len(includes_titles) > 3:
                includes_str += ", ..."
        else:
            includes_str = "Basic coverages only"

        lines.append(
            f"{i}. {name} – {currency} {amount}{suffix}. Includes: {includes_str}"
        )

    return "\n".join(lines) if lines else "No protection packages available."


def summarize_addons(addon_groups) -> str:
    """
    addon_groups è una lista di AddonGroup (pydantic) da SixtApiClient.
    """
    lines = []
    for group in addon_groups:
        lines.append(f"Group: {group.name}")
        for opt in group.options:
            title = opt.chargeDetail.title
            desc = opt.chargeDetail.description

            price = opt.additionalInfo.price.displayPrice
            amount = price.amount
            currency = price.currency
            suffix = price.suffix or ""

            multi = opt.additionalInfo.selectionStrategy.isMultiSelectionAllowed
            multi_str = "multiple allowed" if multi else "single selection"

            lines.append(
                f"  - {title} – {currency} {amount}{suffix}, {multi_str}. {desc}"
            )
        lines.append("")  # riga vuota tra gruppi

    return "\n".join(lines) if lines else "No addons available."

# ------------------- PROTECTION STEP -------------------

def run_protection_chat(booking_id: str, user_message: str) -> dict:
    """
    Step protections:
    - Aggiorna il profilo cumulativo con il messaggio
    - Carica i protection packages disponibili
    - Li passa al modello per spiegare / consigliare
    - Ritorna:
        {
          "step": "protection",
          "answer": str,
          "protection_packages": [ProtectionPackage, ...]
        }
    """
    client = SixtApiClient()

    # Aggiorna profilo (può parlare di rischio, budget, ecc.)
    profile = get_profile_for_booking(booking_id, original_total_price=0.0)
    update_profile_from_text(profile, user_message)
    print(f"[Profile (protections) for {booking_id}] {profile}")

    packages = client.get_available_protection_packages(booking_id)
    protections_text = summarize_protection_packages(packages)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": (
                "You are currently in the PROTECTION PACKAGES step.\n"
                "The customer has already chosen a vehicle and now you should help them "
                "decide which level of protection (insurance/coverage) makes sense.\n\n"
                "Here are the available protection packages for this booking:\n\n"
                f"{protections_text}\n\n"
                "Based on the customer's trip, risk appetite, and budget, explain the options, "
                "highlight at most 2–3 packages that make the most sense, and clearly mention "
                "the daily and total cost differences. Be honest if basic protection is enough."
            ),
        },
        {"role": "user", "content": user_message},
    ]

    resp = llm.invoke(messages)
    answer = resp.content

    return {
        "step": "protection",
        "answer": answer,
        "protection_packages": packages,
    }

# ------------------- ADDONS STEP -------------------


def run_addons_chat(booking_id: str, user_message: str) -> dict:
    """
    Step addons:
    - Aggiorna il profilo
    - Carica gli addons disponibili
    - Li passa al modello per spiegare / consigliare
    - Ritorna:
        {
          "step": "addons",
          "answer": str,
          "addons": [AddonGroup, ...]
        }
    """
    client = SixtApiClient()

    profile = get_profile_for_booking(booking_id, original_total_price=0.0)
    update_profile_from_text(profile, user_message)
    print(f"[Profile (addons) for {booking_id}] {profile}")

    addon_groups = client.get_available_addons(booking_id)
    addons_text = summarize_addons(addon_groups)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": (
                "You are currently in the ADD-ONS & EXTRAS step.\n"
                "The customer has already chosen a vehicle and protection package. "
                "Now you help them decide which extras (like child seats, additional driver, toll service, etc.) "
                "are worth adding.\n\n"
                "Here are the available addons:\n\n"
                f"{addons_text}\n\n"
                "Based on the customer's trip, party composition (e.g. children), driving distance and habits, "
                "recommend only the extras that add clear value. Avoid pushing unnecessary extras. "
                "Always mention the extra daily cost and whether the addon is per rental, per day, or per driver."
            ),
        },
        {"role": "user", "content": user_message},
    ]

    resp = llm.invoke(messages)
    answer = resp.content

    return {
        "step": "addons",
        "answer": answer,
        "addons": addon_groups,
    }

# ------------------- ROUTER GENERALE -------------------


def run_sales_chat(booking_id: str, user_message: str, step: str = "vehicle") -> dict:
    """
    Router generale:
    - step == "vehicle"    -> run_vehicle_chat
    - step == "protection" -> run_protection_chat
    - step == "addons"     -> run_addons_chat
    """
    if step == "vehicle":
        return run_vehicle_chat(booking_id, user_message)
    elif step == "protection":
        return run_protection_chat(booking_id, user_message)
    elif step == "addons":
        return run_addons_chat(booking_id, user_message)
    else:
        # fallback: torna allo step veicolo
        return run_vehicle_chat(booking_id, user_message)
