from django.contrib import admin
from .models import BookingContext, ChatSession, ChatMessage

# Register your models here.
admin.site.register(BookingContext)
admin.site.register(ChatSession)
admin.site.register(ChatMessage)