from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Columns in the list page
    list_display = (
        "user",
        "phone_number",
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
        "license_id",
        "has_today_birthday",
    )

    # Fields you can search by
    search_fields = (
        "user__username",
        "user__email",
        "phone_number",
        "city",
        "country",
        "license_id",
    )

    # Filters on the right side
    list_filter = (
        "gender",
        "preferred_language",
        "preferred_transmission",
        "fuel_preference",
        "country",
    )

    # Show these as read-only in the form
    readonly_fields = ("has_today_birthday",)