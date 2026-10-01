from django.contrib import admin
from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "actor", "verb", "target", "is_read", "created_at")
    list_filter = ("is_read",)
    search_fields = ("recipient__email", "actor__email", "verb")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("recipient", "actor", "target_content_type")
