"""
Tests for notification API endpoints.
"""
import pytest

from apps.organizations.models import Organization, OrganizationMember
from apps.projects.models import Workspace, Project, ProjectMember
from apps.notifications.services import create_notification


@pytest.fixture
def setup_api(user, authenticated_client):
    org = Organization.objects.create(name="Test Org", owner=user)
    OrganizationMember.objects.create(
        organization=org,
        user=user,
        role=OrganizationMember.Role.OWNER,
    )
    workspace = Workspace.objects.create(organization=org, name="Engineering")
    project = Project.objects.create(
        workspace=workspace,
        name="Backend API",
        key="API",
        created_by=user,
    )
    ProjectMember.objects.create(
        project=project,
        user=user,
        role=ProjectMember.Role.MANAGER,
    )
    return {
        "client": authenticated_client,
        "user": user,
    }


@pytest.mark.django_db
class TestNotificationAPI:
    def test_list_notifications(self, setup_api):
        user = setup_api["user"]
        create_notification(recipient=user, verb="action 1")
        create_notification(recipient=user, verb="action 2")
        
        response = setup_api["client"].get("/api/v1/notifications/")
        assert response.status_code == 200
        
        data = response.json()["results"]
        assert len(data) == 2
        assert data[0]["is_read"] is False

    def test_mark_notification_as_read(self, setup_api):
        user = setup_api["user"]
        notification = create_notification(recipient=user, verb="action")
        
        url = f"/api/v1/notifications/{notification.id}/read/"
        response = setup_api["client"].post(url)
        
        assert response.status_code == 200
        assert response.json()["is_read"] is True

    def test_mark_all_as_read(self, setup_api):
        user = setup_api["user"]
        create_notification(recipient=user, verb="action 1")
        create_notification(recipient=user, verb="action 2")
        
        response = setup_api["client"].post("/api/v1/notifications/read-all/")
        assert response.status_code == 200
        
        list_response = setup_api["client"].get("/api/v1/notifications/")
        for n in list_response.json()["results"]:
            assert n["is_read"] is True
