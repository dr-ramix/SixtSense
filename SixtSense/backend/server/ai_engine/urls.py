from django.urls import path
from .views import StartChatAPIView, ChatAPIView


urlpatterns = [
    path("start/", StartChatAPIView.as_view(), name="assistant-start"),
    path("chat/", ChatAPIView.as_view(), name="assistant-chat"),
]