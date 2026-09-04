from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.organizations.models import Organization, OrganizationMember
from apps.organizations.permissions import (
    IsOrganizationMember,
    IsOrganizationAdmin,
    IsOrganizationOwner,
)
from apps.organizations.selectors import (
    get_user_organizations,
    get_organization_members,
)
from apps.organizations.services import (
    create_organization,
    add_member,
    remove_member,
    change_member_role,
)
from .serializers import (
    OrganizationSerializer,
    CreateOrganizationSerializer,
    UpdateOrganizationSerializer,
    OrganizationMemberSerializer,
    AddMemberSerializer,
    ChangeMemberRoleSerializer,
)

User = get_user_model()


class OrganizationListCreateView(APIView):
    """
    GET  /api/v1/organizations/          — List user's organizations
    POST /api/v1/organizations/          — Create a new organization

    WHAT: Entry point for organization CRUD.
    WHY:  GET returns only organizations the user belongs to (tenant isolation).
          POST creates an org and automatically adds the creator as owner.
    IMPORTANT: get_user_organizations() is the ONLY way to list orgs.
               Never query Organization.objects.all() directly.
    """

    @extend_schema(responses={200: OrganizationSerializer(many=True)})
    def get(self, request):
        organizations = get_user_organizations(user=request.user)
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CreateOrganizationSerializer,
        responses={201: OrganizationSerializer},
    )
    def post(self, request):
        serializer = CreateOrganizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization = create_organization(
            owner=request.user,
            **serializer.validated_data,
        )

        return Response(
            OrganizationSerializer(organization).data,
            status=status.HTTP_201_CREATED,
        )


class OrganizationDetailView(APIView):
    """
    GET    /api/v1/organizations/<pk>/   — Retrieve organization
    PATCH  /api/v1/organizations/<pk>/   — Update organization
    DELETE /api/v1/organizations/<pk>/   — Delete organization

    Permissions:
    - GET: any organization member
    - PATCH: admin or owner
    - DELETE: owner only
    """

    def get_object(self, pk):
        try:
            return Organization.objects.select_related("owner").get(pk=pk)
        except Organization.DoesNotExist:
            return None

    @extend_schema(responses={200: OrganizationSerializer})
    def get(self, request, pk):
        organization = self.get_object(pk)
        if organization is None:
            return Response(
                {"detail": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check membership
        permission = IsOrganizationMember()
        if not permission.has_object_permission(request, self, organization):
            return Response(
                {"detail": "You are not a member of this organization."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = OrganizationSerializer(organization)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UpdateOrganizationSerializer,
        responses={200: OrganizationSerializer},
    )
    def patch(self, request, pk):
        organization = self.get_object(pk)
        if organization is None:
            return Response(
                {"detail": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only admin or owner can update
        permission = IsOrganizationAdmin()
        if not permission.has_object_permission(request, self, organization):
            return Response(
                {"detail": "Only admins can update organization settings."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UpdateOrganizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr(organization, field, value)
        organization.save()

        return Response(
            OrganizationSerializer(organization).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        organization = self.get_object(pk)
        if organization is None:
            return Response(
                {"detail": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only owner can delete
        permission = IsOrganizationOwner()
        if not permission.has_object_permission(request, self, organization):
            return Response(
                {"detail": "Only the organization owner can delete it."},
                status=status.HTTP_403_FORBIDDEN,
            )

        organization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrganizationMemberListView(APIView):
    """
    GET  /api/v1/organizations/<pk>/members/     — List members
    POST /api/v1/organizations/<pk>/members/     — Add a member
    """

    def get_organization(self, pk):
        try:
            return Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return None

    @extend_schema(responses={200: OrganizationMemberSerializer(many=True)})
    def get(self, request, pk):
        organization = self.get_organization(pk)
        if organization is None:
            return Response(
                {"detail": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        permission = IsOrganizationMember()
        if not permission.has_object_permission(request, self, organization):
            return Response(
                {"detail": "You are not a member of this organization."},
                status=status.HTTP_403_FORBIDDEN,
            )

        members = get_organization_members(organization=organization)
        serializer = OrganizationMemberSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=AddMemberSerializer,
        responses={201: OrganizationMemberSerializer},
    )
    def post(self, request, pk):
        organization = self.get_organization(pk)
        if organization is None:
            return Response(
                {"detail": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only admin or owner can add members
        permission = IsOrganizationAdmin()
        if not permission.has_object_permission(request, self, organization):
            return Response(
                {"detail": "Only admins can add members."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])

        try:
            member = add_member(
                organization=organization,
                user=user,
                role=serializer.validated_data["role"],
            )
        except IntegrityError:
            return Response(
                {"detail": "User is already a member of this organization."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            OrganizationMemberSerializer(member).data,
            status=status.HTTP_201_CREATED,
        )


class OrganizationMemberDetailView(APIView):
    """
    PATCH  /api/v1/organizations/<org_pk>/members/<member_pk>/  — Change role
    DELETE /api/v1/organizations/<org_pk>/members/<member_pk>/  — Remove member
    """

    def get_organization(self, org_pk):
        try:
            return Organization.objects.get(pk=org_pk)
        except Organization.DoesNotExist:
            return None

    def get_member(self, member_pk):
        try:
            return OrganizationMember.objects.select_related("user").get(
                pk=member_pk
            )
        except OrganizationMember.DoesNotExist:
            return None

    @extend_schema(
        request=ChangeMemberRoleSerializer,
        responses={200: OrganizationMemberSerializer},
    )
    def patch(self, request, org_pk, member_pk):
        organization = self.get_organization(org_pk)
        if organization is None:
            return Response(
                {"detail": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only admin or owner can change roles
        permission = IsOrganizationAdmin()
        if not permission.has_object_permission(request, self, organization):
            return Response(
                {"detail": "Only admins can change member roles."},
                status=status.HTTP_403_FORBIDDEN,
            )

        member = self.get_member(member_pk)
        if member is None or member.organization_id != organization.pk:
            return Response(
                {"detail": "Member not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ChangeMemberRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_member = change_member_role(
                organization=organization,
                user=member.user,
                new_role=serializer.validated_data["role"],
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            OrganizationMemberSerializer(updated_member).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, org_pk, member_pk):
        organization = self.get_organization(org_pk)
        if organization is None:
            return Response(
                {"detail": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only admin or owner can remove members
        permission = IsOrganizationAdmin()
        if not permission.has_object_permission(request, self, organization):
            return Response(
                {"detail": "Only admins can remove members."},
                status=status.HTTP_403_FORBIDDEN,
            )

        member = self.get_member(member_pk)
        if member is None or member.organization_id != organization.pk:
            return Response(
                {"detail": "Member not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            remove_member(
                organization=organization,
                user=member.user,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
