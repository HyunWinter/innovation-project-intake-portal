from django.urls import path

from .views import (
    stream_view,
    NotificationListView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
    NotificationClearAllView,
)

urlpatterns = [
    path("stream/", stream_view, name="sse-stream"),
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path(
        "notifications/<uuid:pk>/read/",
        NotificationMarkReadView.as_view(),
        name="notification-read",
    ),
    path(
        "notifications/read-all/",
        NotificationMarkAllReadView.as_view(),
        name="notification-read-all",
    ),
    path(
        "notifications/clear-all/",
        NotificationClearAllView.as_view(),
        name="notification-clear-all",
    ),
]
