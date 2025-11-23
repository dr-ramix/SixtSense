# ai_engine/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import BookingContext, ChatSession, ChatMessage
from .serializers import StartChatSerializer, ChatMessageSerializer

# LangChain AI + recommendation engines
from .ai.agent import SalesAgent
from .ai.car_scoring import hybrid_rank_deals
from .ai.protection_engine import recommend_protections, recommend_addons

# Real integration with SIXT HackaTUM API
from sixtbridge.sixt_api import (
    get_booking,
    get_vehicles,
    get_protections,
    get_addons,
)


# -------------------------------------------------------------------------
#  START CHAT  (creates BookingContext + ChatSession)
# -------------------------------------------------------------------------
class StartChatAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = StartChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking_id = serializer.validated_data["booking_id"]

        # --- Fetch real booking from SIXT ---
        try:
            booking_data = get_booking(booking_id)
        except Exception:
            return Response(
                {"error": "Invalid booking_id or SIXT API unavailable"},
                status=400,
            )

        # --- Store booking context ---
        booking_context, created = BookingContext.objects.get_or_create(
            booking_id=booking_id,
            defaults={"data": booking_data}
        )

        # If booking exists: refresh data
        if not created:
            booking_context.data = booking_data
            booking_context.save()

        # --- Create chat session ---
        chat_session = ChatSession.objects.create(
            booking=booking_context,
            state={},
            user=None,  # no auth for now
        )

        return Response({
            "chat_session_id": str(chat_session.id),
            "booking": booking_context.data
        })
        

# -------------------------------------------------------------------------
#  MAIN CHAT BOT ENDPOINT (AI + recommendations)
# -------------------------------------------------------------------------
class ChatAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        chat_session = ChatSession.objects.get(
            id=serializer.validated_data["chat_session_id"]
        )
        user_message = serializer.validated_data["message"]

        # 1) Save user message
        ChatMessage.objects.create(
            chat_session=chat_session,
            role="user",
            content=user_message,
        )

        booking_data = chat_session.booking.data
        profile_data = {}            # future: link user profile
        current_state = chat_session.state or {}

        # 2) Run AI Agent (LangChain)
        agent = SalesAgent()
        result = agent.run(
            booking=booking_data,
            profile=profile_data,
            state=current_state,
            message=user_message,
        )

        assistant_message = result["assistant_message"]
        state_update = result.get("state_update", {}) or {}
        needs = result.get("needs", {}) or {}
        protection_needs = needs.get("protections", [])
        addon_needs = needs.get("addons", [])

        # 3) Save updated state
        new_state = {**current_state, **state_update}
        chat_session.state = new_state
        chat_session.save()

        # 4) Fetch live SIXT data (vehicles, protections, addons)
        deals = self.fetch_deals(booking_data)
        protections_raw = self.fetch_protections(booking_data)
        addons_raw = self.fetch_addons(booking_data)

        original_price = self.get_original_price(deals)

        # 5) Rank vehicles
        top_deals = hybrid_rank_deals(
            deals=deals,
            profile=new_state,
            original_total_price=original_price,
            k=3,
            use_llm=True,  # set False if you want cheaper LLM usage
        )

        cars = [self.compact_car(d, original_price) for d in top_deals]

        # 6) Recommend protections & addons
        protections = recommend_protections(
            protections_raw.get("protectionPackages", []),
            new_state,
            protection_needs,
        )

        addons = recommend_addons(
            addons_raw.get("addons", []),
            new_state,
            addon_needs,
        )

        # 7) Save assistant message
        ChatMessage.objects.create(
            chat_session=chat_session,
            role="assistant",
            content=assistant_message,
        )

        # 8) Return full conversation + recs
        messages = [
            {
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat()
            }
            for m in chat_session.messages.all()
        ]

        return Response({
            "chat_session_id": str(chat_session.id),
            "messages": messages,
            "cars": cars,
            "protections": protections,
            "addons": addons,
            "state": new_state,
        })

    # ---------------------------------------------------------------------
    # Helper Methods
    # ---------------------------------------------------------------------

    def fetch_deals(self, booking_id: str):
        try:
            response = get_vehicles(booking_id)
            return response.get("deals", [])
        except Exception as e:
            print("Error fetching vehicles:", e)
            return []

    def fetch_protections(self, booking_id: str):
        try:
            return get_protections(booking_id)
        except Exception as e:
            print("Error fetching protections:", e)
            return {"protectionPackages": []}

    def fetch_addons(self, booking_id: str):
        try:
            return get_addons(booking_id)
        except Exception as e:
            print("Error fetching addons:", e)
            return {"addons": []}

    # --- Pricing helpers ---

    def get_original_price(self, deals):
        for d in deals:
            if d.get("dealInfo") == "BOOKED_CATEGORY":
                return d["pricing"]["totalPrice"]["amount"]
        if deals:
            return deals[0]["pricing"]["totalPrice"]["amount"]
        return 0.0

    # --- Format compact car card ---

    def compact_car(self, deal, original_price):
        v = deal["vehicle"]
        p = deal["pricing"]

        tags = []
        if v.get("isRecommended"):
            tags.append("Recommended")
        if v.get("isNewCar"):
            tags.append("New")
        if v.get("isMoreLuxury"):
            tags.append("Luxury")
        if p.get("discountPercentage", 0) > 0:
            tags.append(f"{p['discountPercentage']}% off")

        return {
            "id": v["id"],
            "name": f"{v['brand']} {v['model']}",
            "brand": v["brand"],
            "model": v["model"],
            "image": v["images"][0] if v.get("images") else None,
            "groupType": v["groupType"],
            "passengers": v["passengersCount"],
            "bags": v["bagsCount"],
            "transmission": v["transmissionType"],
            "fuelType": v["fuelType"],
            "daily_price": p["displayPrice"]["amount"],
            "total_price": p["totalPrice"]["amount"],
            "currency": p["displayPrice"]["currency"],
            "tags": tags,
        }