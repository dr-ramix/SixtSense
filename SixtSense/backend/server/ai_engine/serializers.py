from rest_framework import serializers


class StartChatSerializer(serializers.Serializer):
    booking_id = serializers.CharField()


class ChatMessageSerializer(serializers.Serializer):
    chat_session_id = serializers.UUIDField()
    message = serializers.CharField()

