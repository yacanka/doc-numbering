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
