from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.formats.models import DocumentFormat, FormatSequence


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class DocumentNumberGeneratorTests(TestCase):
    """Integration tests for unique document number generation."""

    def setUp(self):
        """Create an active invoice format used by every test."""
        self.user = get_user_model().objects.create_user('operator', password='secret')
        self.format = DocumentFormat.objects.create(
            code='INV',
            name='Invoice',
            status='active',
            sequence_start=7,
            sequence_step=2,
            segments_config=[
                {'type': 'static', 'order': 1, 'config': {'value': 'INV-'}},
                {'type': 'date', 'order': 2, 'config': {'format': 'YYYY'}},
                {'type': 'separator', 'order': 3, 'config': {'value': '-'}},
                {'type': 'sequence', 'order': 4, 'config': {'padding': 4}},
            ],
            created_by=self.user,
        )

    def test_generate_persists_unique_number_and_sequence(self):
        """Generated numbers are saved and sequence values increase atomically."""
        first = self.format.get_generator().generate(user=self.user)
        second = self.format.get_generator().generate(user=self.user)

        self.assertNotEqual(first.document_number, second.document_number)
        self.assertEqual(first.sequence_value, 7)
        self.assertEqual(second.sequence_value, 9)
        self.assertTrue(first.document_number.endswith('0007'))

    def test_preview_does_not_advance_sequence(self):
        """Preview renders a sample number without creating sequence state."""
        preview = self.format.generate_preview()

        self.assertIn('INV-', preview)
        self.assertFalse(FormatSequence.objects.exists())

    def test_monthly_reset_uses_period_specific_sequences(self):
        """Reset periods are isolated by period key in sequence storage."""
        self.format.sequence_reset_period = 'monthly'
        self.format.save(update_fields=['sequence_reset_period'])

        document = self.format.get_generator().generate(user=self.user)

        self.assertEqual(document.sequence_value, 7)
        self.assertEqual(FormatSequence.objects.count(), 1)
