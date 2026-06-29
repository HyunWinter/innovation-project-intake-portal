"""DRF serializers for requests, comments, and audit trail
Used in views.py rest api endpoints
"""

from rest_framework import serializers
from django.utils import timezone

from workflow.engine import available_actions, workflow_status

from .enums import Category, FundingStatus, Status
from .models import AuditEvent, Comment, Request

NON_TERMINAL = (
    Status.PENDING,
    Status.UNDER_REVIEW,
    Status.APPROVED,
    Status.IN_PROGRESS,
    Status.ON_HOLD,
)


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True, default=None)

    class Meta:
        model = Comment
        fields = ["id", "author_name", "body", "created_at"]


class AuditEventSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.name", read_only=True, default=None)

    class Meta:
        model = AuditEvent
        fields = [
            "id",
            "actor_name",
            "event_type",
            "from_status",
            "to_status",
            "payload",
            "created_at",
        ]


class RequestListSerializer(serializers.ModelSerializer):
    submitter_name = serializers.CharField(source="submitter.name", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    category_label = serializers.CharField(source="get_category_display", read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Request
        fields = [
            "id",
            "title",
            "category",
            "category_label",
            "status",
            "status_label",
            "funding_required",
            "funding_status",
            "presentation_status",
            "submitter_name",
            "contact_name",
            "tech_category",
            "start_date",
            "end_date",
            "is_overdue",
            "created_at",
            "updated_at",
        ]

    def get_is_overdue(self, obj):
        return bool(
            obj.end_date and obj.end_date < timezone.localdate() and obj.status in NON_TERMINAL
        )


class RequestDetailSerializer(serializers.ModelSerializer):
    """All fields and audit trail, comments,
    available actions, and workflow progress."""

    submitter_name = serializers.CharField(source="submitter.name", read_only=True)
    decision_made_by_name = serializers.CharField(
        source="decision_made_by.name", read_only=True, default=None
    )
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    category_label = serializers.CharField(source="get_category_display", read_only=True)

    # Custom
    audit_events = AuditEventSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    available_actions = serializers.SerializerMethodField()
    workflow = serializers.SerializerMethodField()

    class Meta:
        model = Request
        exclude = ["deleted_at"]

    def get_available_actions(self, obj):
        user = self.context["request"].user
        return available_actions(obj, getattr(user, "role", None))

    def get_workflow(self, obj):
        return workflow_status(obj)


class RequestCreateSerializer(serializers.ModelSerializer):
    """Create (POST) and resubmit (PATCH) accept only the four sections stuff"""

    class Meta:
        model = Request
        fields = [
            # Section 1: Prior-Art
            "keywords",
            "similar_projects_found",
            "differentiation",
            "collaboration_opportunities",
            # Section 2: Basic info
            "contact_name",
            "contact_email",
            "site_or_team",
            "tech_category",
            "collaboration_interest",
            # Section 3: Scope
            "title",
            "description",
            "objectives",
            "outcomes",
            "start_date",
            "end_date",
            "phases",
            # Section 4: Resources
            "funding_required",
            "personnel",
            "equipment",
            "budget",
            "estimated_roi",
        ]

    def validate(self, data):
        start = data.get("start_date")
        end = data.get("end_date")
        if start and end and end < start:
            raise serializers.ValidationError(
                {"end_date": "End date must be on or after the start date."}
            )

        # 4 · Resources
        # Funding required? (→ Cat A/B); personnel; equipment.
        # If funded: budget > 0; estimated ROI
        funding = data.get("funding_required", getattr(self.instance, "funding_required", False))
        if funding:
            budget = data.get("budget", getattr(self.instance, "budget", None))
            if budget is None or budget <= 0:
                raise serializers.ValidationError(
                    {"budget": "Funded proposals need a budget greater than 0."}
                )
            roi = data.get("estimated_roi", getattr(self.instance, "estimated_roi", ""))
            if not roi:
                raise serializers.ValidationError(
                    {"estimated_roi": "Funded proposals need an estimated ROI."}
                )
        return data

    def _derive(self, validated, instance=None):
        # Category and funding_status follow from the funding checkbox
        funding = validated.get("funding_required", getattr(instance, "funding_required", False))
        validated["category"] = Category.B if funding else Category.A
        validated["funding_status"] = (
            FundingStatus.PENDING if funding else FundingStatus.NOT_REQUIRED
        )
        return validated

    def create(self, validated):
        validated = self._derive(validated)
        validated["status"] = Status.PENDING
        validated["submitter"] = self.context["request"].user
        return Request.objects.create(**validated)

    def update(self, instance, validated):
        # Resubmit only edits the sections
        # The state machine keeps it pending
        validated = self._derive(validated, instance)
        return super().update(instance, validated)
