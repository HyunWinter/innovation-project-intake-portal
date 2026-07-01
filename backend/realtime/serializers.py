from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.name", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "event_type",
            "request_ref",
            "action",
            "actor",
            "actor_name",
            "title",
            "from_status",
            "to_status",
            "read",
            "created_at",
        ]
        read_only_fields = fields
