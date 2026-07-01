"""SSE streaming endpoint + notification REST API

Accepts a JWT query parameter and streams events from the in-process
bus as Server-Sent Events.

Also provides REST endpoints for persisted notifications so that
offline users can retrieve missed notifications on login.
"""

import json
import queue
import time

from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from accounts.models import User

from . import bus
from .models import Notification
from .serializers import NotificationSerializer

# Heartbeat interval in seconds (keeps the connection alive)
HEARTBEAT_INTERVAL = 25


def _authenticate_from_token(token_str):
    """Validate JWT from query param and return the user"""
    if not token_str:
        return None
    try:
        validated = AccessToken(token_str)
        user_id = validated["user_id"]
        return User.objects.get(id=user_id)
    except (TokenError, User.DoesNotExist, KeyError):
        return None


def _format_sse(event_type, data):
    """Format a dict as an SSE message"""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


def _event_stream(q):
    """Generator that yields SSE events from the queue + heartbeats"""

    # Yield an initial comment to flush headers and trigger frontend immediately
    yield ": connected\n\n"

    last_heartbeat = time.monotonic()

    try:
        while True:
            try:
                event = q.get(timeout=1.0)
                yield _format_sse(event["type"], event["data"])
            except queue.Empty:
                pass

            # Periodic heartbeat
            now = time.monotonic()
            if now - last_heartbeat >= HEARTBEAT_INTERVAL:
                yield ": heartbeat\n\n"
                last_heartbeat = now
    finally:
        bus.unsubscribe(q)


def stream_view(request):
    """GET /api/events/stream/?token=<jwt>

    Returns a StreamingHttpResponse with SSE content type
    Authentication is via JWT query parameter
    """
    token = request.GET.get("token")
    user = _authenticate_from_token(token)

    if user is None:
        return StreamingHttpResponse(
            _format_sse("error", {"detail": "Authentication required"}),
            content_type="text/event-stream",
            status=401,
        )

    q = bus.subscribe(user.id)

    response = StreamingHttpResponse(
        _event_stream(q),
        content_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
    return response


# Persisted notifications
class NotificationListView(APIView):
    """GET /api/notifications/

    Returns the current user's notifications (most recent first).
    Query params:
        unread=true  — only unread notifications
    """

    def get(self, request):
        qs = Notification.objects.filter(
            recipient=request.user,
        ).select_related("actor")

        if request.query_params.get("unread") == "true":
            qs = qs.filter(read=False)

        # Cap at 50 most recent
        qs = qs[:50]
        serializer = NotificationSerializer(qs, many=True)
        return Response(serializer.data)


class NotificationMarkReadView(APIView):
    """PATCH /api/notifications/<uuid:pk>/read/

    Mark a single notification as read.
    """

    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        notification.read = True
        notification.save(update_fields=["read"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationMarkAllReadView(APIView):
    """POST /api/notifications/read-all/

    Mark all of the current user's notifications as read.
    """

    def post(self, request):
        Notification.objects.filter(
            recipient=request.user,
            read=False,
        ).update(read=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationClearAllView(APIView):
    """POST /api/notifications/clear-all/

    Deletes all notifications for the current user.
    """

    def post(self, request):
        Notification.objects.filter(recipient=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
