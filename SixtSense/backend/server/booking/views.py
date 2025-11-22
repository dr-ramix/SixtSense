from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import BookingLink
from .serializers import (
    BookingLinkSerializer,
    BookingLinkWithProfileSerializer,
)


class BookingLinkCreateAPIView(APIView):
    """
    POST /api/bookings/
    Body: { "booking_id": "...", "extra_data": {...} }

    Creates a BookingLink.
    No authentication required.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = BookingLinkSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            booking = serializer.save()
            return Response(BookingLinkSerializer(booking).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingLinkDetailAPIView(APIView):
    """
    GET /api/bookingLink/<booking_id>/

    Returns booking + user (no profile).
    """
    permission_classes = [permissions.AllowAny]

    def get_object(self, booking_id):
        return get_object_or_404(
            BookingLink.objects.select_related("user"),
            booking_id=booking_id,
        )

    def get(self, request, booking_id, *args, **kwargs):
        booking = self.get_object(booking_id)
        serializer = BookingLinkSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookingLinkDetailWithProfileAPIView(APIView):
    """
    GET /api/bookingLink/<booking_id>/detail/

    Returns booking + user + full profile info.
    """
    permission_classes = [permissions.AllowAny]

    def get_object(self, booking_id):
        return get_object_or_404(
            BookingLink.objects.select_related("user", "user__profile"),
            booking_id=booking_id,
        )

    def get(self, request, booking_id, *args, **kwargs):
        booking = self.get_object(booking_id)
        serializer = BookingLinkWithProfileSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)



class BookingLinkFullDetailAPIView(APIView):
    """
    GET /booking/bookingLink/<booking_id>/full/

    Returns:
    - BookingLink fields (id, booking_id, extra_data)
    - user
    - profile
    - booking (live data from SIXT API)
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, booking_id, *args, **kwargs):
        booking_link = get_object_or_404(
            BookingLink.objects.select_related("user", "user__profile"),
            booking_id=booking_id,
        )

        try:
            sixt_booking = get_booking(booking_id)
        except Exception as e:
            sixt_booking = None

        serializer = BookingLinkWithProfileSerializer(
            booking_link,
            context={"booking": sixt_booking},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)