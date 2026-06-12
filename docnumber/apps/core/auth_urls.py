from django.contrib.auth import get_user_model
from django.urls import path
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.throttles import TokenObtainRateThrottle, TokenRefreshRateThrottle


class CurrentUserSerializer(serializers.ModelSerializer):
    """Serialize authenticated user profile fields exposed to the frontend."""

    username = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username']
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def get_username(self, user):
        """Return the configured username identifier for the user model."""
        return user.get_username()

    def validate_email(self, value):
        """Normalize the email address before saving it."""
        normalized_email = value.strip().lower()
        if not normalized_email:
            raise serializers.ValidationError('Email address is required.')
        return normalized_email


class ScopedTokenObtainPairView(TokenObtainPairView):
    """Issue JWT pairs with a throttle scope isolated from refresh attempts."""

    throttle_classes = [TokenObtainRateThrottle]


class ScopedTokenRefreshView(TokenRefreshView):
    """Refresh access tokens without consuming the login throttle quota."""

    throttle_classes = [TokenRefreshRateThrottle]


class CurrentUserView(APIView):
    """Return and update the authenticated user's public profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return identity fields needed by the frontend."""
        return Response({
            'success': True,
            'data': CurrentUserSerializer(request.user).data,
        })

    def patch(self, request):
        """Update editable profile fields without allowing username changes."""
        serializer = CurrentUserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'data': serializer.data})


urlpatterns = [
    path('token/', ScopedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', ScopedTokenRefreshView.as_view(), name='token_refresh'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
]
