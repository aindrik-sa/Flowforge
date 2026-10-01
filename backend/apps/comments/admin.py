from django.contrib import admin

from apps.comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("task", "author", "is_edited", "parent", "created_at")
    list_filter = ("is_edited",)
    search_fields = ("body", "author__email", "task__title")
    readonly_fields = ("is_edited", "created_at", "updated_at")
    raw_id_fields = ("task", "author", "parent")
