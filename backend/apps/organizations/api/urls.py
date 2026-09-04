from django.urls import path

from .views import (
    OrganizationListCreateView,
    OrganizationDetailView,
    OrganizationMemberListView,
    OrganizationMemberDetailView,
)

app_name = "organizations"

urlpatterns = [
    path(
        "",
        OrganizationListCreateView.as_view(),
        name="list-create",
    ),
    path(
        "<uuid:pk>/",
        OrganizationDetailView.as_view(),
        name="detail",
    ),
    path(
        "<uuid:pk>/members/",
        OrganizationMemberListView.as_view(),
        name="member-list",
    ),
    path(
        "<uuid:org_pk>/members/<uuid:member_pk>/",
        OrganizationMemberDetailView.as_view(),
        name="member-detail",
    ),
]
