from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    # Read-only, filled from request.user
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    # Computed / helper fields (read-only)
    age = serializers.SerializerMethodField()
    risk_category = serializers.SerializerMethodField()
    upsell_likelihood = serializers.SerializerMethodField()
    preferred_vehicle_type = serializers.SerializerMethodField()
    is_family_user = serializers.SerializerMethodField()
    has_today_birthday = serializers.ReadOnlyField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "phone_number",
            "city",
            "country",
            "preferred_language",
            "preferred_transmission",
            "fuel_preference",
            "comfort_priority",
            "power_priority",
            "gender",
            "birth_date",
            "profile_picture",
            "license_id",
            "family_situation",
            "has_kids",
            # computed fields
            "age",
            "risk_category",
            "upsell_likelihood",
            "preferred_vehicle_type",
            "is_family_user",
            "has_today_birthday",
        ]
        read_only_fields = (
            "user",
            "age",
            "risk_category",
            "upsell_likelihood",
            "preferred_vehicle_type",
            "is_family_user",
            "has_today_birthday",
        )

    # ---- Computed field getters ----

    def get_age(self, obj):
        return obj.age()

    def get_risk_category(self, obj):
        return obj.risk_category()

    def get_upsell_likelihood(self, obj):
        return obj.upsell_likelihood()

    def get_preferred_vehicle_type(self, obj):
        return obj.preferred_vehicle_type()

    def get_is_family_user(self, obj):
        return obj.is_family_user()

    # ---- Create / update ----

    def create(self, validated_data):
        """
        Normally profile is auto-created via signals, but this makes the serializer
        robust if you ever call .save() without one.
        """
        user = self.context["request"].user
        return Profile.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        # Standard update (you can customize if needed)
        return super().update(instance, validated_data)
