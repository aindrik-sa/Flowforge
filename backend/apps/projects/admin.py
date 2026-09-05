from django.contrib import admin

from apps.projects.models import Board, BoardColumn


class BoardColumnInline(admin.TabularInline):
    model = BoardColumn
    extra = 0
    ordering = ["position"]
    fields = ("name", "slug", "position", "color", "wip_limit")
    readonly_fields = ("slug",)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "is_default", "created_at")
    list_filter = ("is_default",)
    search_fields = ("name", "project__name")
    readonly_fields = ("slug", "created_at", "updated_at")
    inlines = [BoardColumnInline]


@admin.register(BoardColumn)
class BoardColumnAdmin(admin.ModelAdmin):
    list_display = ("name", "board", "position", "color", "wip_limit")
    list_filter = ("board",)
    search_fields = ("name", "board__name")
    readonly_fields = ("slug", "created_at", "updated_at")
