from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q

from apps.projects.models import Project
from apps.tasks.models import Task


def get_project_dashboard_stats(project_id: str) -> dict:
    """
    Retrieve aggregated dashboard statistics for a project.
    
    WHAT: Calculates total, pending, and completed tasks, caching the result
          to prevent heavy DB aggregations on every page load.
    WHY:  Dashboard queries can be expensive; caching is essential for perf.
    """
    cache_key = f"project_stats_{project_id}"
    stats = cache.get(cache_key)

    if not stats:
        # Check if project exists to avoid returning 0s for missing projects
        if not Project.objects.filter(id=project_id).exists():
            raise ValueError(f"Project {project_id} does not exist.")

        # Aggregate task statistics
        aggs = Task.objects.filter(project_id=project_id).aggregate(
            total_tasks=Count("id"),
            completed_tasks=Count("id", filter=Q(column__slug="done")),
            pending_tasks=Count("id", filter=~Q(column__slug="done")),
        )

        stats = {
            "total_tasks": aggs["total_tasks"] or 0,
            "completed_tasks": aggs["completed_tasks"] or 0,
            "pending_tasks": aggs["pending_tasks"] or 0,
        }
        
        if stats["total_tasks"] > 0:
            stats["completion_percentage"] = round((stats["completed_tasks"] / stats["total_tasks"]) * 100)
        else:
            stats["completion_percentage"] = 0

        # Cache for 5 minutes
        cache.set(cache_key, stats, timeout=300)

    return stats


def get_user_productivity_stats(user_id: str) -> dict:
    """
    Retrieve productivity statistics for a user over the last 30 days.
    """
    cache_key = f"user_productivity_{user_id}"
    stats = cache.get(cache_key)

    if not stats:
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Count tasks completed by user in last 30 days
        completed_last_30_days = Task.objects.filter(
            assignments__user_id=user_id,
            column__slug="done",
            updated_at__gte=thirty_days_ago
        ).count()

        pending_tasks = Task.objects.filter(
            assignments__user_id=user_id,
        ).exclude(
            column__slug="done"
        ).count()

        stats = {
            "completed_last_30_days": completed_last_30_days,
            "current_pending_tasks": pending_tasks,
        }

        # Cache for 1 hour
        cache.set(cache_key, stats, timeout=3600)

    return stats
