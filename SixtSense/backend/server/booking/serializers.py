from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import BookingLink
from accounts.serializers import ProfileSerializer  # your existing profile serializer

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    """
    Minimal user info to embed in booking responses.
    """

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class BookingLinkSerializer(serializers.ModelSerializer):
    """
    BookingLink + user (no profile) + live booking data from SIXT.
    """

    user = SimpleUserSerializer(read_only=True)
    # This will hold the booking details from SIXT
    booking = serializers.SerializerMethodField()

    class Meta:
        model = BookingLink
        fields = (
            "id",
            "booking_id",
            "user",
            "extra_data",  # optional, can be null or legacy
            "booking",     # <-- live data from SIXT
        )
        read_only_fields = ("id", "user", "booking")

    def create(self, validated_data):
        """
        If request.user is authenticated, attach the booking to that user.
        Otherwise keep it as a guest booking (user stays None).
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("user", request.user)
        return super().create(validated_data)

    def get_booking(self, obj):
        """
        Expect the view to pass 'booking' in context.
        We do NOT call SIXT from inside the serializer.
        """
        return self.context.get("booking")
    

class BookingLinkWithProfileSerializer(serializers.ModelSerializer):
    """
    BookingLink + user + full profile + live booking data from SIXT.
    """

    user = SimpleUserSerializer(read_only=True)
    profile = ProfileSerializer(source="user.profile", read_only=True)
    booking = serializers.SerializerMethodField()

    class Meta:
        model = BookingLink
        fields = (
            "id",
            "booking_id",
            "user",      # basic user info
            "profile",   # full profile info
            "extra_data",
            "booking",   # <-- live data from SIXT
        )
        read_only_fields = ("id", "user", "profile", "booking")

    def get_booking(self, obj):
        return self.context.get("booking")
