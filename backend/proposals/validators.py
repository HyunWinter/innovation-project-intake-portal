"""Typed checks on transition payloads for TransitionView
Check payload contents before apply_transition
"""

from rest_framework import serializers
from django.utils import timezone


def validate_transition_payload(action, payload):
    # For scheduled payload = requested -> scheduled = presentation requirements
    if action == "schedule":
        raw = payload.get("presentation_date")
        if raw in (None, ""):
            return
        dt = serializers.DateTimeField().to_internal_value(raw)
        if dt <= timezone.now():
            raise serializers.ValidationError(
                {"presentation_date": "Presentation date must be in the future."}
            )
    # For hold payload = Reasoning + expected resume date
    elif action == "hold":
        raw = payload.get("expected_resume_date")
        if raw not in (None, ""):
            serializers.DateField().to_internal_value(raw)  # raises 400 if malformed
    # For combine_existing the merge target must be a real request
    elif action == "combine_existing":
        target_id = payload.get("merged_into")
        if target_id not in (None, ""):
            target_id = serializers.UUIDField().to_internal_value(target_id)  # 400 if malformed
            from proposals.models import Request

            if not Request.objects.filter(pk=target_id).exists():
                raise serializers.ValidationError(
                    {"merged_into": "Selected project does not exist."}
                )
