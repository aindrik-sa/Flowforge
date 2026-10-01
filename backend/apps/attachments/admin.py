from django.contrib import admin

from apps.attachments.models import Attachment


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "original_filename",
        "task",
        "content_type",
        "file_size",
        "uploaded_by",
        "created_at",
    )
    list_filter = ("content_type",)
    search_fields = ("original_filename", "task__title", "uploaded_by__email")
    readonly_fields = ("file_size", "content_type", "created_at", "updated_at")
    raw_id_fields = ("task", "uploaded_by")
