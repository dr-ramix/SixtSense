from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import BookingContext, ChatSession, ChatMessage
from .serializers import StartChatSerializer, ChatMessageSerializer


class StartChatAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = StartChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking_id = serializer.validated_data["booking_id"]

        # --- Step 1: Fetch booking from Sixt (stub for now) ---
        # Later replace this with real request to Sixt API
        fake_booking_data = {
            "booking_id": booking_id,
            "pickup_station": "MUC",
            "dropoff_station": "MUC",
            "start_date": "2025-02-14",
            "end_date": "2025-02-17",
            "original_car_group": "CXXX",
        }

        # --- Step 2: Store booking context ---
        booking_context, _ = BookingContext.objects.get_or_create(
            booking_id=booking_id,
            defaults={"data": fake_booking_data}
        )

        # --- Step 3: Create new chat session ---
        chat_session = ChatSession.objects.create(
            booking=booking_context,
            state={},       # empty state initially
            user=None       # no authentication yet
        )

        return Response({
            "chat_session_id": str(chat_session.id),
            "booking": booking_context.data
        })


class ChatAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        chat_session_id = serializer.validated_data["chat_session_id"]
        message_text = serializer.validated_data["message"]

        # --- Load chat session ---
        try:
            chat_session = ChatSession.objects.get(id=chat_session_id)
        except ChatSession.DoesNotExist:
            return Response({"detail": "ChatSession not found."}, status=404)

        # --- Save user's message ---
        ChatMessage.objects.create(
            chat_session=chat_session,
            role=ChatMessage.ROLE_USER,
            content=message_text
        )

        # --- Dummy assistant logic (replace later with real AI) ---
        assistant_reply = f"I received your message: '{message_text}'."

        ChatMessage.objects.create(
            chat_session=chat_session,
            role=ChatMessage.ROLE_ASSISTANT,
            content=assistant_reply
        )

        # --- Build message list for frontend ---
        messages = [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in chat_session.messages.all()
        ]

        # --- No car recs yet ---
        cars = []

        return Response({
            "chat_session_id": str(chat_session.id),
            "messages": messages,
            "cars": cars
        })
