from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


class RegisterView(APIView):
    """
    POST /api/v1/auth/register/

    Create a new user account.
    Returns the created user data with 201 status.

    WHAT: Registration endpoint.
    WHY:  APIView (not generic) because registration is a one-off action,
          not a standard model CRUD operation.
    IMPORTANT: permission_classes = [AllowAny] — unauthenticated users
               must be able to register. Without this, DRF's default
               IsAuthenticated would block registration entirely.
    """

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/v1/auth/login/

    Authenticate with email and password.
    Returns user data + JWT access/refresh tokens.

    WHAT: Custom login endpoint.
    WHY:  We control the response shape (user + tokens together),
          which is friendlier for frontend developers than simplejwt's
          default TokenObtainPairView that only returns tokens.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        request=LoginSerializer,
        responses={200: dict},
    )
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """
    GET /api/v1/auth/me/

    Return the authenticated user's profile.

    WHAT: Profile endpoint for the current user.
    WHY:  After login, the frontend stores the JWT token but may need
          to re-fetch the user profile (page reload, token still valid).
          This avoids storing user data in localStorage.
    IMPORTANT: Uses default IsAuthenticated — no explicit permission_classes
               needed since it's the DRF default in our settings.
    """

    serializer_class = UserSerializer

    @extend_schema(
        responses={200: UserSerializer},
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
