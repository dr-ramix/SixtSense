from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date


class Profile(models.Model):
    TRANSMISSION_CHOICES = [
        ("automatic", "Automatic"),
        ("manual", "Manual"),
    ]

    FUEL_CHOICES = [
        ("petrol", "Petrol"),
        ("diesel", "Diesel"),
        ("electric", "Electric"),
        ("hybrid", "Hybrid"),
    ]

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    FAMILY_SITUATION_CHOICES = [
        ("single", "Single"),
        ("married", "Married"),
        ("divorced", "Divorced"),
        ("other", "Other"),
    ]

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("de", "German"),
        ("it", "Italian"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    # Basic info
    phone_number = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=250, blank=True, null=True)
    preferred_language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default="en"
    )

    # Driving preferences
    preferred_transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES,
        blank=True,
    )
    fuel_preference = models.CharField(
        max_length=20,
        choices=FUEL_CHOICES,
        blank=True,
    )

    # Priority fields (1–5)
    comfort_priority = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    power_priority = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    # Personal details
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
    )
    birth_date = models.DateField(blank=True, null=True)

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
    )

    # Driver information
    license_id = models.IntegerField(blank=True, null=True)

    # Family & lifestyle
    family_situation = models.CharField(
        max_length=20,
        choices=FAMILY_SITUATION_CHOICES,
        blank=True,
        null=True,
    )
    has_kids = models.BooleanField(default=False)

    # --------------------
    # Helper / logic methods
    # --------------------

    @property
    def has_today_birthday(self) -> bool:
        if not self.birth_date:
            return False
        today = date.today()
        return (
            self.birth_date.month == today.month
            and self.birth_date.day == today.day
        )

    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def is_family_user(self):
        return self.has_kids or self.family_situation == "married"

    def preferred_vehicle_type(self):
        if self.is_family_user():
            return "family_car"
        if self.power_priority >= 4:
            return "sports"
        if self.comfort_priority >= 4:
            return "premium"
        return "standard"

    def is_power_user(self):
        return self.power_priority > self.comfort_priority

    def is_comfort_user(self):
        return self.comfort_priority > self.power_priority

    def risk_category(self):
        age = self.age()
        if age is None:
            return "unknown"
        if age < 25:
            return "high"
        if 25 <= age <= 65:
            return "normal"
        return "low"

    def upsell_likelihood(self):
        score = (self.comfort_priority + self.power_priority) / 2
        if score >= 4:
            return "high"
        if score >= 2.5:
            return "medium"
        return "low"

    def travel_profile(self):
        return {
            "age": self.age(),
            "family_user": self.is_family_user(),
            "vehicle_type": self.preferred_vehicle_type(),
            "risk_category": self.risk_category(),
            "upsell_likelihood": self.upsell_likelihood(),
            "comfort_priority": self.comfort_priority,
            "power_priority": self.power_priority,
            "has_kids": self.has_kids,
            "family_situation": self.family_situation,
            "preferred_language": self.preferred_language,
        }

    def __str__(self):
        return f"{self.user.username}'s Profile"
