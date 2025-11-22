from django.conf import settings
from django.db import models


class BookingLink(models.Model):
    booking_id = models.CharField(max_length=64, unique=True, db_index=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bookings",
    )

    extra_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.booking_id} -> {self.user or 'guest'}"