from langchain_openai import ChatOpenAI
import json

# Initialize OpenAI LLM for conversation and ranking
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.4,  # Balanced creativity for sales conversations
)

# Load available car deals from SIXT API data
with open("cars_dataset_example.json", encoding="utf-8") as f:
    data = json.load(f)

deals = data["deals"]

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
    220  # Fallback if no booked category found
)

def score_deal(deal, profile, original_total_price):
    """
    Rule-based scoring: matches vehicle features to customer needs.
    Higher score = better match for upselling.
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
    
    # Price-based scoring: favor more expensive cars for upselling
    uplift = pricing["totalPrice"]["amount"] - original_total_price
    if uplift > 0:
        score += min(uplift / 40, 4)  # Cap at +4 points
    elif uplift == 0:
        score += 1  # Same price is safe
    else:
        score += max(uplift / 100, -2)  # Penalty for cheaper options
    
    # Additional upsell incentives
    if vehicle.get("isMoreLuxury"):
        score += 2
    
    # Tiered pricing bonuses encourage higher-value bookings
    total_price = pricing["totalPrice"]["amount"]
    if total_price > original_total_price * 1.5:
        score += 3  # Premium tier
    elif total_price > original_total_price * 1.2:
        score += 2  # Mid-tier
    elif total_price > original_total_price:
        score += 1  # Light upsell
    
    return score

def rank_deals(deals, profile, original_total_price, k=3):
    """Rule-based ranking: score all deals and return top k."""
    scored = []
    for d in deals:
        s = score_deal(d, profile, original_total_price)
        scored.append((s, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for s, d in scored[:k]]

def llm_rank_all_deals_batch(deals, profile, original_total_price, k=3):
    """
    LLM-based ranking: uses AI to intelligently rank vehicles in one API call.
    More contextual than rule-based, understands nuanced customer needs.
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
    
    customer_desc = ", ".join(profile_parts) if profile_parts else "general needs"
    
    # LLM prompt: balance customer fit with upsell opportunity
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
        
        # Parse LLM response: "3,7,1" -> [deals[2], deals[6], deals[0]]
        indices = [int(x.strip())-1 for x in response.content.strip().split(',')]
        
        result = []
        for i in indices[:k]:
            if 0 <= i < len(deals):
                result.append(deals[i])
        
        return result if result else deals[:k]
            
    except Exception as e:
        print(f"[Warning] LLM ranking failed: {e}. Using rule-based fallback.")
        return rank_deals(deals, profile, original_total_price, k)

def hybrid_rank_deals(deals, profile, original_total_price, k=3):
    """
    Hybrid strategy: Fast rule-based filtering, then intelligent LLM ranking.
    Optimizes cost (fewer LLM calls) and quality (smart final ranking).
    """
    # Phase 1: Hard filters eliminate clearly unsuitable vehicles
    filtered = []
    for deal in deals:
        vehicle = deal["vehicle"]
        pricing = deal["pricing"]
        
        # Must-have criteria
        if profile.get("passengers") and vehicle["passengersCount"] < profile["passengers"]:
            continue  # Not enough seats
        
        if profile.get("budget_total"):
            if pricing["totalPrice"]["amount"] > profile["budget_total"] * 1.5:
                continue  # Too expensive (allow 50% buffer for upsell)
        
        if profile.get("luggage") == "many" and vehicle["bagsCount"] < 3:
            continue  # Insufficient luggage space
        
        filtered.append(deal)
    
    # Fallback: if filters too strict, use all deals
    if not filtered:
        print("[Info] No deals passed filters, using all deals")
        filtered = deals
    
    # Phase 2: Adaptive ranking based on candidate count
    if len(filtered) <= 5:
        # Few candidates: use LLM directly (best quality)
        print(f"[Info] Using LLM batch ranking for {len(filtered)} candidates")
        return llm_rank_all_deals_batch(filtered, profile, original_total_price, k)
    
    elif len(filtered) <= 15:
        # Medium candidates: rule-based narrowing + LLM final ranking (balanced)
        print(f"[Info] Using hybrid: rule-based pre-ranking -> LLM final ranking")
        rule_based_top = rank_deals(filtered, profile, original_total_price, k=10)
        return llm_rank_all_deals_batch(rule_based_top, profile, original_total_price, k)
    
    else:
        # Too many candidates: pure rule-based (cost-effective)
        print(f"[Info] Too many candidates ({len(filtered)}), using rule-based ranking only")
        return rank_deals(filtered, profile, original_total_price, k)

from langchain.tools import tool
import re

def update_profile_from_text(profile, text):
    """Extract customer preferences from natural language using keyword matching and regex."""
    t = text.lower()
    
    # Trip type detection
    if "kids" in t or "family" in t or "children" in t:
        profile["trip_type"] = "family"
    if "business" in t or "work" in t:
        profile["trip_type"] = "business"
    
    # Comfort level
    if "comfortable" in t or "luxury" in t or "premium" in t:
        profile["comfort_priority"] = "high"
    
    # Passenger count (regex: "5 people", "3 passengers")
    if m := re.search(r"(\d+)\s*(people|persons|passengers|adults)", t):
        profile["passengers"] = int(m.group(1))
    
    # Luggage needs
    if "many bags" in t or "a lot of luggage" in t or "lots of luggage" in t:
        profile["luggage"] = "many"
    
    # Budget constraints
    if "tight budget" in t or "not too expensive" in t or "cheap" in t:
        profile["budget_total"] = original_total_price
    
    return profile

@tool("get_top_upsell_deals")
def get_top_upsell_deals(user_message: str) -> str:
    """
    LangChain tool: LLM calls this to fetch personalized car recommendations.
    Returns JSON with top 3 deals based on customer profile.
    """
    global user_profile
    user_profile = update_profile_from_text(user_profile, user_message)
    
    print(f"\n[Profile] {user_profile}")
    top = hybrid_rank_deals(deals, user_profile, original_total_price, k=3)
    
    # Format deals into clean JSON for LLM to present
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

# Conversation memory: tracks chat history per user session
store = {}

def get_session_history(session_id: str):
    """Get or create chat history for a user session."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# System prompt: defines AI's role, behavior, and constraints
with open("long_prompt.txt", "r", encoding="utf-8") as file:
    content = file.read()
system_message_content = (content)

# Bind tool to LLM: allows AI to call get_top_upsell_deals during conversation
llm_with_tools = llm.bind_tools([get_top_upsell_deals])

# Chat loop
session_id = "user-session-1"

print("SIXT Car Rental Assistant (type 'quit' or 'exit' to end)")
print("=" * 60)

while True:
    msg = input("\nYou: ")
    if msg.lower() in ["quit", "exit"]:
        print("Thank you for using SIXT! Goodbye!")
        break
    
    try:
        history = get_session_history(session_id)
        
        # Build message list: system prompt + chat history + current message
        messages = [{"role": "system", "content": system_message_content}]
        
        # Add all previous conversation turns
        for hist_msg in history.messages:
            if isinstance(hist_msg, HumanMessage):
                messages.append({"role": "user", "content": hist_msg.content})
            elif isinstance(hist_msg, AIMessage):
                msg_dict = {"role": "assistant", "content": hist_msg.content}
                if hasattr(hist_msg, 'tool_calls') and hist_msg.tool_calls:
                    msg_dict["tool_calls"] = hist_msg.tool_calls  # Include tool call metadata
                messages.append(msg_dict)
            elif isinstance(hist_msg, ToolMessage):
                messages.append({
                    "role": "tool",
                    "content": hist_msg.content,
                    "tool_call_id": hist_msg.tool_call_id  # Must match original tool call
                })
        
        messages.append({"role": "user", "content": msg})
        
        # Get LLM response (may include tool calls)
        result = llm_with_tools.invoke(messages)
        history.add_user_message(msg)
        
        # Two-step process if LLM calls tools
        if hasattr(result, 'tool_calls') and result.tool_calls:
            print("\n[Checking available deals...]")
            
            history.add_ai_message(result)
            
            # Execute tool and save result
            for tool_call in result.tool_calls:
                tool_result = get_top_upsell_deals.invoke(tool_call['args']['user_message'])
                
                history.add_message(ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call['id']
                ))
            
            # Second LLM call: format tool results for user
            final_messages = [{"role": "system", "content": system_message_content}]
            
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
            # Direct response (no tools needed)
            history.add_ai_message(result.content)
            print(f"\nBot: {result.content}")
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
