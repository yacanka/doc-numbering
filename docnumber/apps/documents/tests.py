from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.documents.models import GeneratedDocument
from apps.formats.models import DocumentFormat


class GeneratedDocumentModelTests(TestCase):
    """Tests for generated document lifecycle helpers."""

    def setUp(self):
        """Create a persisted generated document."""
        user = get_user_model().objects.create_user('operator')
        document_format = DocumentFormat.objects.create(
            code='PO',
            name='Purchase Order',
            status='active',
            segments_config=[{'type': 'static', 'config': {'value': 'PO'}}],
            created_by=user,
        )
        self.document = GeneratedDocument.objects.create(
            format=document_format,
            document_number='PO-1',
            sequence_value=1,
            generated_by=user,
            generated_at=timezone.now(),
        )

    def test_cancel_marks_document_invalid(self):
        """Cancelling records the reason and invalidates the document."""
        self.document.cancel(reason='Wrong customer')

        self.document.refresh_from_db()
        self.assertEqual(self.document.status, 'cancelled')
        self.assertFalse(self.document.is_valid)
        self.assertEqual(self.document.cancellation_reason, 'Wrong customer')

    def test_mark_used_updates_usage_timestamp(self):
        """Marking a document as used sets status and usage timestamp."""
        self.document.mark_used()

        self.document.refresh_from_db()
        self.assertEqual(self.document.status, 'used')
        self.assertIsNotNone(self.document.used_at)


class GeneratedDocumentApiTests(TestCase):
    """Tests for generated document API status management."""

    def setUp(self):
        """Create an authenticated API client and a document."""
        from rest_framework.test import APIClient

        self.user = get_user_model().objects.create_user('apiuser', password='secret')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        document_format = DocumentFormat.objects.create(
            code='API_DOC',
            name='API Document',
            status='active',
            segments_config=[{'type': 'static', 'config': {'value': 'API'}}],
            created_by=self.user,
        )
        self.document = GeneratedDocument.objects.create(
            format=document_format,
            document_number='API-1',
            sequence_value=1,
            generated_by=self.user,
            generated_at=timezone.now(),
        )

    def test_update_status_marks_document_used(self):
        """Status endpoint updates status and usage timestamp."""
        response = self.client.patch(
            f'/api/v1/documents/{self.document.id}/status/',
            {'status': 'used'},
            format='json',
        )

        self.document.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['status'], 'used')
        self.assertIsNotNone(self.document.used_at)

    def test_update_status_rejects_unknown_status(self):
        """Status endpoint validates the requested lifecycle status."""
        response = self.client.patch(
            f'/api/v1/documents/{self.document.id}/status/',
            {'status': 'unknown'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
