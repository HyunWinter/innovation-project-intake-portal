"""Request API routes (mounted under /api/)."""

from django.urls import path

from .views import RequestDetailView, RequestListCreateView

urlpatterns = [
    path("requests/", RequestListCreateView.as_view(), name="request-list"),
    path("requests/<uuid:pk>/", RequestDetailView.as_view(), name="request-detail"),
]
