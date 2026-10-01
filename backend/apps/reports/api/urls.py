from django.urls import path

from .views import ProjectDashboardAPI, UserProductivityAPI

app_name = "reports"

urlpatterns = [
    path("projects/<uuid:project_id>/dashboard/", ProjectDashboardAPI.as_view(), name="project-dashboard"),
    path("users/<uuid:user_id>/productivity/", UserProductivityAPI.as_view(), name="user-productivity"),
]
