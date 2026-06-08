from django.urls import path
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class CurrentUserView(APIView):
    """Return the authenticated user's public profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return identity fields needed by the frontend."""
        user = request.user
        return Response({
            'success': True,
            'data': {
                'id': user.id,
                'username': user.get_username(),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
        })


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
]
