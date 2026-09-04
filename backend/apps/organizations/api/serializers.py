from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.api.serializers import UserSerializer
from apps.organizations.models import Organization, OrganizationMember

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Read serializer for Organization — includes owner info.
    """

    owner = UserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "owner",
            "member_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_member_count(self, obj) -> int:
        # If annotated, use it; otherwise count from DB
        if hasattr(obj, "member_count_annotation"):
            return obj.member_count_annotation
        return obj.members.count()


class CreateOrganizationSerializer(serializers.Serializer):
    """
    Input serializer for creating an organization.

    WHAT: Validates name and optional description/slug.
    WHY:  Using Serializer (not ModelSerializer) keeps creation logic in the
          service layer. The serializer only handles input shape.
    """

    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=False, default="", allow_blank=True)


class UpdateOrganizationSerializer(serializers.Serializer):
    """Input serializer for updating an organization."""

    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Read serializer for organization membership."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = OrganizationMember
        fields = (
            "id",
            "user",
            "role",
            "joined_at",
        )
        read_only_fields = fields


class AddMemberSerializer(serializers.Serializer):
    """
    Input serializer for adding a member to an organization.

    WHAT: Takes a user email and optional role.
    WHY:  Email is friendlier than UUID for inviting users.
          The service layer handles the actual membership creation.
    """

    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=OrganizationMember.Role.choices,
        default=OrganizationMember.Role.MEMBER,
    )

    def validate_email(self, value: str) -> str:
        email = value.lower().strip()
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "No user found with this email address."
            )
        return email

    def validate_role(self, value: str) -> str:
        if value == OrganizationMember.Role.OWNER:
            raise serializers.ValidationError(
                "Cannot assign owner role. Use ownership transfer instead."
            )
        return value


class ChangeMemberRoleSerializer(serializers.Serializer):
    """Input serializer for changing a member's role."""

    role = serializers.ChoiceField(choices=OrganizationMember.Role.choices)

    def validate_role(self, value: str) -> str:
        if value == OrganizationMember.Role.OWNER:
            raise serializers.ValidationError(
                "Cannot assign owner role. Use ownership transfer instead."
            )
        return value
