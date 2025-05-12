from rest_framework import serializers

from .models import ConversationHistory


class ConversationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationHistory
        fields = ["id", "timestamp", "user_message", "assistant_response", "thread_id", "user"]
        read_only_fields = ["timestamp", "user"]


class CreateAssistantSerializer(serializers.Serializer):
    message = serializers.CharField()


class UpdateAssistantResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    thread_id = serializers.CharField()
