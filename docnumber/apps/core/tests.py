from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.core.auth_urls import ScopedTokenObtainPairView, ScopedTokenRefreshView


class CurrentUserApiTests(TestCase):
    """Tests for authenticated profile retrieval and self-service updates."""

    def setUp(self):
        """Create an authenticated client for profile endpoint tests."""
        self.user = get_user_model().objects.create_user(
            username='operator',
            email='old@example.com',
            password='secret',
            first_name='Old',
            last_name='Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_patch_updates_profile_without_username(self):
        """Editable profile fields update while username remains immutable."""
        response = self.client.patch('/api/v1/auth/me/', {
            'username': 'changed',
            'email': ' NEW@Example.COM ',
            'first_name': 'New',
            'last_name': 'Person',
        }, format='json')

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.username, 'operator')
        self.assertEqual(self.user.email, 'new@example.com')
        self.assertEqual(response.data['data']['username'], 'operator')

    def test_patch_rejects_blank_email(self):
        """Blank email values are rejected before they reach the database."""
        response = self.client.patch('/api/v1/auth/me/', {'email': ' '}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data['error']['details'])


class AuthenticationThrottleScopeTests(TestCase):
    """Tests for independent authentication endpoint throttling scopes."""

    def test_token_views_use_isolated_throttle_scopes(self):
        """Login and refresh attempts do not consume the same throttle bucket."""
        self.assertEqual(ScopedTokenObtainPairView.throttle_classes[0].scope, 'token_obtain')
        self.assertEqual(ScopedTokenRefreshView.throttle_classes[0].scope, 'token_refresh')
