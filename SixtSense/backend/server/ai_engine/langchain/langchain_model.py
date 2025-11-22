from langchain_openai import ChatOpenAI
import json

# Initialize OpenAI LLM for conversation and ranking
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.4,
)

# Load available car deals from SIXT API data
with open("cars_dataset_example.json", encoding="utf-8") as f:
    data = json.load(f)

deals = data["deals"]

# Load registered user profiles
with open("user_profiles.json", encoding="utf-8") as f:
    user_data = json.load(f)
    registered_users = {user["id"]: user for user in user_data["registered_users"]}

# User profile tracks customer preferences learned from conversation
user_profile = {
    "passengers": None,
    "luggage": None,
    "budget_total": None,
    "trip_type": None,
    "comfort_priority": None,
    "risk_aversion": None,
    "upgrade_openness": None,
}

# Find original booking price to calculate upsell margins
original_total_price = next(
    (deal["pricing"]["totalPrice"]["amount"] for deal in deals if deal["dealInfo"] == "BOOKED_CATEGORY"),
    220
)

# Current user session data
current_user_id = None  # Set this to user ID if logged in, None for guests
current_registered_profile = None

def load_registered_user(user_id):
    """Load registered user profile and merge with user_profile."""
    global current_registered_profile, user_profile
    
    if user_id in registered_users:
        current_registered_profile = registered_users[user_id]
        
        # Pre-populate user_profile with stored preferences
        if current_registered_profile.get("has_kids") or current_registered_profile.get("is_family_user"):
            user_profile["trip_type"] = "family"
        
        user_profile["comfort_priority"] = current_registered_profile.get("comfort_priority", "medium")
        
        # Estimate passengers from family situation
        if current_registered_profile.get("has_kids"):
            user_profile["passengers"] = 4  # Assume family of 4
        
        return True
    return False

def score_deal(deal, profile, original_total_price, registered_profile=None):
    """
    Rule-based scoring: matches vehicle features to customer needs.
    Enhanced with registered user preferences.
    """
    score = 0
    vehicle = deal["vehicle"]
    pricing = deal["pricing"]
    
    # Core needs matching (capacity, luggage)
    if profile["passengers"] and vehicle["passengersCount"] >= profile["passengers"]:
        score += 3
    
    if profile["luggage"] == "many" and vehicle["bagsCount"] >= 4:
        score += 2
    
    # Trip-type specific preferences
    if profile["comfort_priority"] == "high":
        if vehicle.get("isMoreLuxury") or "premium" in vehicle["groupType"].lower():
            score += 3
    
    if profile["trip_type"] == "family":
        if vehicle["groupType"] in ["SUV", "MINIVAN"] or vehicle["passengersCount"] >= 7:
            score += 2
    
    if profile["trip_type"] == "business":
        if "SEDAN" in vehicle["groupType"] or vehicle.get("isMoreLuxury"):
            score += 2
    
    # Quality indicators
    if vehicle.get("isRecommended"):
        score += 1
    
    if vehicle.get("isNewCar"):
        score += 1
    
    # REGISTERED USER BONUSES
    if registered_profile:
        # Transmission preference match
        if registered_profile.get("preferred_transmission"):
            pref_trans = registered_profile["preferred_transmission"].lower()
            vehicle_trans = vehicle["transmissionType"].lower()
            if pref_trans in vehicle_trans:
                score += 2
        
        # Fuel preference match
        if registered_profile.get("fuel_preference"):
            pref_fuel = registered_profile["fuel_preference"].lower()
            vehicle_fuel = vehicle["fuelType"].lower()
            if pref_fuel in vehicle_fuel:
                score += 2
        
        # Preferred vehicle type match
        if registered_profile.get("preferred_vehicle_type"):
            pref_type = registered_profile["preferred_vehicle_type"].lower()
            vehicle_type = vehicle["groupType"].lower()
            if pref_type in vehicle_type or vehicle_type in pref_type:
                score += 3
        
        # Power priority
        if registered_profile.get("power_priority") == "high":
            if vehicle.get("isMoreLuxury") or "sport" in vehicle["groupType"].lower():
                score += 2
        
        # Upsell likelihood adjustment
        upsell_level = registered_profile.get("upsell_likelihood", "medium")
        if upsell_level in ["high", "very_high"]:
            score += 2  # More likely to accept premium options
        elif upsell_level == "low":
            score -= 1  # Prefer budget options
    
    # Price-based scoring: favor more expensive cars for upselling
    uplift = pricing["totalPrice"]["amount"] - original_total_price
    if uplift > 0:
        score += min(uplift / 40, 4)
    elif uplift == 0:
        score += 1
    else:
        score += max(uplift / 100, -2)
    
    # Additional upsell incentives
    if vehicle.get("isMoreLuxury"):
        score += 2
    
    # Tiered pricing bonuses
    total_price = pricing["totalPrice"]["amount"]
    if total_price > original_total_price * 1.5:
        score += 3
    elif total_price > original_total_price * 1.2:
        score += 2
    elif total_price > original_total_price:
        score += 1
    
    return score

def rank_deals(deals, profile, original_total_price, k=3, registered_profile=None):
    """Rule-based ranking: score all deals and return top k."""
    scored = []
    for d in deals:
        s = score_deal(d, profile, original_total_price, registered_profile)
        scored.append((s, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for s, d in scored[:k]]

def llm_rank_all_deals_batch(deals, profile, original_total_price, k=3, registered_profile=None):
    """
    LLM-based ranking: uses AI to intelligently rank vehicles in one API call.
    Enhanced with registered user preferences.
    """
    if not deals:
        return []
    
    # Build concise vehicle descriptions for LLM
    vehicles_summary = []
    for i, deal in enumerate(deals):
        vehicle = deal["vehicle"]
        pricing = deal["pricing"]
        
        tags = []
        if vehicle.get("isNewCar"):
            tags.append("New")
        if vehicle.get("isRecommended"):
            tags.append("Recommended")
        if vehicle.get("isMoreLuxury"):
            tags.append("Luxury")
        
        tags_str = f" [{', '.join(tags)}]" if tags else ""
        
        vehicles_summary.append(
            f"{i+1}. {vehicle['brand']} {vehicle['model']} - "
            f"{vehicle['groupType']}, {vehicle['passengersCount']} seats, "
            f"{vehicle['bagsCount']} bags, {vehicle['transmissionType']}, "
            f"{vehicle['fuelType']}, €{pricing['displayPrice']['amount']}/day "
            f"(€{pricing['totalPrice']['amount']} total){tags_str}"
        )
    
    # Build customer profile summary
    profile_parts = []
    if profile.get('passengers'):
        profile_parts.append(f"{profile['passengers']} passengers")
    if profile.get('trip_type'):
        profile_parts.append(f"{profile['trip_type']} trip")
    if profile.get('comfort_priority'):
        profile_parts.append(f"{profile['comfort_priority']} comfort priority")
    if profile.get('luggage'):
        profile_parts.append(f"{profile['luggage']} luggage")
    if profile.get('budget_total'):
        profile_parts.append(f"budget: €{profile['budget_total']}")
    
    # Add registered user preferences
    if registered_profile:
        if registered_profile.get("preferred_transmission"):
            profile_parts.append(f"prefers {registered_profile['preferred_transmission']} transmission")
        if registered_profile.get("fuel_preference"):
            profile_parts.append(f"prefers {registered_profile['fuel_preference']} fuel")
        if registered_profile.get("preferred_vehicle_type"):
            profile_parts.append(f"usually books {registered_profile['preferred_vehicle_type']}")
        if registered_profile.get("power_priority"):
            profile_parts.append(f"{registered_profile['power_priority']} power priority")
    
    customer_desc = ", ".join(profile_parts) if profile_parts else "general needs"
    
    # LLM prompt with registered user context
    extra_context = ""
    if registered_profile:
        extra_context = f"\nRegistered User Profile: {registered_profile.get('upsell_likelihood', 'medium')} upsell likelihood"
    
    prompt = f"""You are a car rental expert. Rank these {len(deals)} vehicles for this customer from BEST to WORST match.

Customer needs: {customer_desc}
Original booking price: €{original_total_price}{extra_context}

Available vehicles:
{chr(10).join(vehicles_summary)}

Instructions:
- Consider how well each vehicle fits the customer's specific needs
- PRIORITIZE matching their stated preferences (transmission, fuel, vehicle type)
- Value for money is important (price vs features)
- Prefer vehicles with practical features matching their trip type
- New and recommended vehicles are good but not if they don't fit needs
- Balance upsell opportunity with genuine customer benefit

Respond with ONLY the top {k} vehicle numbers in order, comma-separated (e.g., "3,7,1").
Best match first, worst of the top {k} last."""
    
    try:
        response = llm.invoke([{"role": "user", "content": prompt}])
        
        indices = [int(x.strip())-1 for x in response.content.strip().split(',')]
        
        result = []
        for i in indices[:k]:
            if 0 <= i < len(deals):
                result.append(deals[i])
        
        return result if result else deals[:k]
            
    except Exception as e:
        print(f"[Warning] LLM ranking failed: {e}. Using rule-based fallback.")
        return rank_deals(deals, profile, original_total_price, k, registered_profile)

def hybrid_rank_deals(deals, profile, original_total_price, k=3, registered_profile=None):
    """
    Hybrid strategy: Fast rule-based filtering, then intelligent LLM ranking.
    Enhanced with registered user preferences.
    """
    # Phase 1: Hard filters
    filtered = []
    for deal in deals:
        vehicle = deal["vehicle"]
        pricing = deal["pricing"]
        
        # Basic filters
        if profile.get("passengers") and vehicle["passengersCount"] < profile["passengers"]:
            continue
        
        if profile.get("budget_total"):
            if pricing["totalPrice"]["amount"] > profile["budget_total"] * 1.5:
                continue
        
        if profile.get("luggage") == "many" and vehicle["bagsCount"] < 3:
            continue
        
        # Registered user preference filters (soft filters - don't eliminate, just deprioritize)
        # These are handled in scoring instead
        
        filtered.append(deal)
    
    if not filtered:
        print("[Info] No deals passed filters, using all deals")
        filtered = deals
    
    # Phase 2: Adaptive ranking
    if len(filtered) <= 5:
        print(f"[Info] Using LLM batch ranking for {len(filtered)} candidates")
        return llm_rank_all_deals_batch(filtered, profile, original_total_price, k, registered_profile)
    
    elif len(filtered) <= 15:
        print(f"[Info] Using hybrid: rule-based pre-ranking -> LLM final ranking")
        rule_based_top = rank_deals(filtered, profile, original_total_price, k=10, registered_profile=registered_profile)
        return llm_rank_all_deals_batch(rule_based_top, profile, original_total_price, k, registered_profile)
    
    else:
        print(f"[Info] Too many candidates ({len(filtered)}), using rule-based ranking only")
        return rank_deals(filtered, profile, original_total_price, k, registered_profile)

from langchain.tools import tool
import re

def update_profile_from_text(profile, text):
    """Extract customer preferences from natural language."""
    t = text.lower()
    
    if "kids" in t or "family" in t or "children" in t:
        profile["trip_type"] = "family"
    if "business" in t or "work" in t:
        profile["trip_type"] = "business"
    
    if "comfortable" in t or "luxury" in t or "premium" in t:
        profile["comfort_priority"] = "high"
    
    if m := re.search(r"(\d+)\s*(people|persons|passengers|adults)", t):
        profile["passengers"] = int(m.group(1))
    
    if "many bags" in t or "a lot of luggage" in t or "lots of luggage" in t:
        profile["luggage"] = "many"
    
    if "tight budget" in t or "not too expensive" in t or "cheap" in t:
        profile["budget_total"] = original_total_price
    
    return profile

@tool("get_top_upsell_deals")
def get_top_upsell_deals(user_message: str) -> str:
    """
    LangChain tool: LLM calls this to fetch personalized car recommendations.
    Uses registered user profile if available.
    """
    global user_profile, current_registered_profile
    user_profile = update_profile_from_text(user_profile, user_message)
    
    print(f"\n[Profile] {user_profile}")
    if current_registered_profile:
        print(f"[Registered User] {current_registered_profile['user']} - {current_registered_profile.get('preferred_vehicle_type', 'No preference')}")
    
    top = hybrid_rank_deals(deals, user_profile, original_total_price, k=3, registered_profile=current_registered_profile)
    
    # Format deals into clean JSON
    compact = []
    for d in top:
        vehicle = d["vehicle"]
        pricing = d["pricing"]
        
        transmission = "automatic" if "automatic" in vehicle["transmissionType"].lower() else "manual"
        
        features = []
        if vehicle.get("isNewCar"):
            features.append("New car")
        if vehicle.get("isRecommended"):
            features.append("Recommended")
        if vehicle.get("isMoreLuxury"):
            features.append("Luxury")
        features.append(vehicle["transmissionType"])
        features.append(vehicle["fuelType"])
        features.append(vehicle["tyreType"])
        
        # Add preference match indicators for registered users
        preference_matches = []
        if current_registered_profile:
            if current_registered_profile.get("preferred_transmission", "").lower() in vehicle["transmissionType"].lower():
                preference_matches.append("Matches your transmission preference")
            if current_registered_profile.get("fuel_preference", "").lower() in vehicle["fuelType"].lower():
                preference_matches.append("Matches your fuel preference")
            if current_registered_profile.get("preferred_vehicle_type", "").lower() in vehicle["groupType"].lower():
                preference_matches.append("Your preferred vehicle type")
        
        compact.append({
            "id": vehicle["id"],
            "name": f"{vehicle['brand']} {vehicle['model']}",
            "category": vehicle["groupType"],
            "seats": vehicle["passengersCount"],
            "luggage": vehicle["bagsCount"],
            "transmission": transmission,
            "daily_price": pricing["displayPrice"]["amount"],
            "total_price": pricing["totalPrice"]["amount"],
            "currency": pricing["displayPrice"]["currency"],
            "discount_percentage": pricing.get("discountPercentage", 0),
            "features": ", ".join(features),
            "preference_matches": preference_matches,  # New field
            "extras": d.get("extras", []),
            "deal_info": d["dealInfo"],
            "is_new": vehicle.get("isNewCar", False),
            "is_recommended": vehicle.get("isRecommended", False),
            "image": vehicle["images"][0] if vehicle.get("images") else None,
        })
    
    return json.dumps(compact, indent=2)

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

store = {}

def get_session_history(session_id: str):
    """Get or create chat history for a user session."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# System prompt
with open("long_prompt.txt", "r", encoding="utf-8") as file:
    content = file.read()
system_message_content = content

llm_with_tools = llm.bind_tools([get_top_upsell_deals])

session_id = "user-session-1"

print("SIXT Car Rental Assistant (type 'quit' or 'exit' to end)")
print("=" * 60)

# Ask if user is logged in
user_login = input("\nAre you a registered SIXT customer? (Enter user ID or 'guest'): ").strip()

if user_login.lower() != "guest" and user_login:
    if load_registered_user(user_login):
        current_user_id = user_login
        print(f"✅ Welcome back, {current_registered_profile['user']}!")
    else:
        print(f"❌ User ID not found. Continuing as guest.")
        current_user_id = None
else:
    print("👤 Continuing as guest user.")
    current_user_id = None

# Build initial context with user info
history = get_session_history(session_id)

user_context = ""
if current_registered_profile:
    user_context = f"""
REGISTERED USER CONTEXT:
- Name: {current_registered_profile['user']}
- Age: {current_registered_profile['age']}
- Family: {current_registered_profile['family_situation']}, {'Has kids' if current_registered_profile['has_kids'] else 'No kids'}
- Preferred transmission: {current_registered_profile.get('preferred_transmission', 'Not specified')}
- Fuel preference: {current_registered_profile.get('fuel_preference', 'Not specified')}
- Comfort priority: {current_registered_profile.get('comfort_priority', 'medium')}
- Power priority: {current_registered_profile.get('power_priority', 'medium')}
- Preferred vehicle type: {current_registered_profile.get('preferred_vehicle_type', 'Not specified')}
- Upsell likelihood: {current_registered_profile.get('upsell_likelihood', 'medium')}
- Risk category: {current_registered_profile.get('risk_category', 'medium')}

Use this information to personalize your recommendations!
"""
else:
    user_context = "GUEST USER: No stored preferences. Ask discovery questions to understand needs."

# Generate initial greeting
initial_greeting = llm.invoke([
    {"role": "system", "content": system_message_content + "\n\n" + user_context},
    {"role": "user", "content": "Greet the customer and start the conversation according to your instructions."}
])

print(f"\nBot: {initial_greeting.content}")
history.add_ai_message(initial_greeting.content)

while True:
    msg = input("\nYou: ")
    if msg.lower() in ["quit", "exit"]:
        print("Thank you for using SIXT! Enjoy your trip!")
        break
    
    try:
        history = get_session_history(session_id)
        
        # Build message list with user context
        messages = [{"role": "system", "content": system_message_content + "\n\n" + user_context}]
        
        for hist_msg in history.messages:
            if isinstance(hist_msg, HumanMessage):
                messages.append({"role": "user", "content": hist_msg.content})
            elif isinstance(hist_msg, AIMessage):
                msg_dict = {"role": "assistant", "content": hist_msg.content}
                if hasattr(hist_msg, 'tool_calls') and hist_msg.tool_calls:
                    msg_dict["tool_calls"] = hist_msg.tool_calls
                messages.append(msg_dict)
            elif isinstance(hist_msg, ToolMessage):
                messages.append({
                    "role": "tool",
                    "content": hist_msg.content,
                    "tool_call_id": hist_msg.tool_call_id
                })
        
        messages.append({"role": "user", "content": msg})
        
        result = llm_with_tools.invoke(messages)
        history.add_user_message(msg)
        
        if hasattr(result, 'tool_calls') and result.tool_calls:
            print("\n[Checking available deals...]")
            
            history.add_ai_message(result)
            
            for tool_call in result.tool_calls:
                tool_result = get_top_upsell_deals.invoke(tool_call['args']['user_message'])
                
                history.add_message(ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call['id']
                ))
            
            final_messages = [{"role": "system", "content": system_message_content + "\n\n" + user_context}]
            
            for hist_msg in history.messages:
                if isinstance(hist_msg, HumanMessage):
                    final_messages.append({"role": "user", "content": hist_msg.content})
                elif isinstance(hist_msg, AIMessage):
                    msg_dict = {"role": "assistant", "content": hist_msg.content or ""}
                    if hasattr(hist_msg, 'tool_calls') and hist_msg.tool_calls:
                        msg_dict["tool_calls"] = hist_msg.tool_calls
                    final_messages.append(msg_dict)
                elif isinstance(hist_msg, ToolMessage):
                    final_messages.append({
                        "role": "tool",
                        "content": hist_msg.content,
                        "tool_call_id": hist_msg.tool_call_id
                    })
            
            final_result = llm_with_tools.invoke(final_messages)
            history.add_ai_message(final_result.content)
            
            print(f"\nBot: {final_result.content}")
        else:
            history.add_ai_message(result.content)
            print(f"\nBot: {result.content}")
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
