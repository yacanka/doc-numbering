from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


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
