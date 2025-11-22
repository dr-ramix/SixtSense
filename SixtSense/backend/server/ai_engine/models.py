import uuid
from django.conf import settings
from django.db import models


class BookingContext(models.Model):
    """
    Stores the raw booking data we get from the Sixt API for a given booking_id.
    This lets us avoid calling the Sixt API on every chat turn.
    """
    booking_id = models.CharField(
        max_length=64,
        unique=True,
        help_text="Sixt booking reference provided by the user."
    )

    # Full JSON payload from the Sixt booking API (dates, station, car group, price, etc.)
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Raw booking data as returned by the Sixt API."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BookingContext(booking_id={self.booking_id})"


class ChatSession(models.Model):
    """
    One conversation between the user and the AI sales assistant,
    tied to a single booking via BookingContext.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Optional: link to authenticated user (you can leave this empty for now)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chat_sessions",
    )

    # Every chat session is for exactly one booking
    booking = models.ForeignKey(
        BookingContext,
        on_delete=models.CASCADE,
        related_name="sessions",
        help_text="Booking this chat session is based on."
    )

    # This is where we store derived info/preferences from the conversation.
    # Example:
    # {
    #   "passengers": 4,
    #   "luggage": "3 large",
    #   "preferences": { "automatic": true, "suv": false },
    #   "dislikes": { "colors": ["red"], "fuel": ["diesel"] }
    # }
    state = models.JSONField(
        default=dict,
        blank=True,
        help_text="Evolving conversation state: preferences, dislikes, etc."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ChatSession(id={self.id}, booking_id={self.booking.booking_id})"


class ChatMessage(models.Model):
    """
    A single message bubble in the chat (either from the user or the assistant).
    """
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_SYSTEM = "system"

    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_ASSISTANT, "Assistant"),
        (ROLE_SYSTEM, "System"),
    ]

    chat_session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        help_text="Who sent the message."
    )

    content = models.TextField(help_text="The text content of the message.")

    # Optional: extra metadata (tool calls, scores, which cars were shown, etc.)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Optional extra info about this message."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.role}] {self.content[:40]}..."
