"""Request endpoints: list, create, detail, resubmit, transitions

Writes -> workflow service or create serializer
role/state errors -> 4xx exception
"""

from django.db import transaction
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response

from accounts.models import Role
from workflow.exceptions import IllegalTransition, RoleNotAllowed

from .enums import Status
from .models import AuditEvent, Request
from .serializers import (
    RequestCreateSerializer,
    RequestDetailSerializer,
    RequestListSerializer,
)


class RequestListCreateView(generics.ListCreateAPIView):
    """GET /requests (filterable, paginated)
    POST /requests (submitters).
    """

    def get_queryset(self):
        qs = Request.objects.select_related("submitter")
        p = self.request.query_params

        if p.get("status"):
            qs = qs.filter(status=p["status"])
        if p.get("category"):
            qs = qs.filter(category=p["category"])
        if p.get("funding") in ("true", "false"):
            qs = qs.filter(funding_required=(p["funding"] == "true"))
        if p.get("mine") == "true":
            qs = qs.filter(submitter=self.request.user)

        q = p.get("q")
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(keywords__icontains=q)
                | Q(contact_name__icontains=q)
            )
        return qs

    def get_serializer_class(self):
        return RequestCreateSerializer if self.request.method == "POST" else RequestListSerializer

    def create(self, request, *args, **kwargs):
        if request.user.role != Role.SUBMITTER:
            raise RoleNotAllowed("create")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            obj = serializer.save()
            # First audit row: the submission itself
            AuditEvent.objects.create(
                request=obj,
                actor=request.user,
                event_type="create",
                from_status=None,
                to_status=obj.status,
            )

        out = RequestDetailSerializer(obj, context=self.get_serializer_context())
        return Response(out.data, status=status.HTTP_201_CREATED)


class RequestDetailView(generics.RetrieveUpdateAPIView):
    """GET /requests/:id (detail + timeline)
    PATCH /requests/:id (resubmit)
    """

    queryset = Request.objects.select_related("submitter", "decision_made_by").prefetch_related(
        "audit_events__actor", "comments__author"
    )
    http_method_names = ["get", "patch", "head", "options"]

    def get_serializer_class(self):
        return (
            RequestCreateSerializer if self.request.method == "PATCH" else RequestDetailSerializer
        )

    def update(self, request, *args, **kwargs):
        obj = self.get_object()

        # Only the owner
        # Only while pending
        # For search_insufficient
        if obj.submitter_id != request.user.id or request.user.role != Role.SUBMITTER:
            raise RoleNotAllowed("resubmit")
        if obj.status != Status.PENDING:
            raise IllegalTransition(f"'resubmit' not allowed from '{obj.status}'")

        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            obj = serializer.save()
            AuditEvent.objects.create(
                request=obj,
                actor=request.user,
                event_type="resubmit",
                from_status=obj.status,
                to_status=obj.status,
            )

        out = RequestDetailSerializer(obj, context=self.get_serializer_context())
        return Response(out.data)
