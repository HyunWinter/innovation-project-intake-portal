from django.contrib import admin

from .models import AuditEvent, Comment, DraftRequest, Request


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "status",
        "funding_status",
        "presentation_status",
        "submitter",
        "created_at",
        "deleted_at",
    )
    list_filter = ("category", "status", "funding_status", "presentation_status")
    search_fields = ("title", "contact_name", "contact_email")
    date_hierarchy = "created_at"

    # Include soft-deleted rows so the admin is a full view.
    def get_queryset(self, request):
        return self.model.all_objects.all()


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "request",
        "event_type",
        "from_status",
        "to_status",
        "actor",
    )
    list_filter = ("event_type", "from_status", "to_status")
    search_fields = ("request__title", "event_type")
    date_hierarchy = "created_at"

    # Append-only: view only.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("created_at", "request", "author", "deleted_at")
    search_fields = ("body", "request__title")

    def get_queryset(self, request):
        return self.model.all_objects.all()


@admin.register(DraftRequest)
class DraftRequestAdmin(admin.ModelAdmin):
    list_display = ("author", "created_at", "updated_at")
    date_hierarchy = "created_at"
