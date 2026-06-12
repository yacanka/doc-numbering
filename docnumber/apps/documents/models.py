# apps/documents/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class GeneratedDocument(models.Model):
    """Record of every generated document number"""

    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('cancelled', 'İptal Edildi'),
        ('used', 'Kullanıldı'),
        ('expired', 'Süresi Doldu'),
    ]

    format = models.ForeignKey(
        'formats.DocumentFormat',
        on_delete=models.PROTECT,
        related_name='generated_documents'
    )
    document_number = models.CharField(max_length=200, unique=True, db_index=True)
    sequence_value = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Context and metadata
    context_data = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict)

    # Generation info
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_documents'
    )
    generated_at = models.DateTimeField()

    # Usage tracking
    used_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'Generated Document'
        verbose_name_plural = 'Generated Documents'
        indexes = [
            models.Index(fields=['format', 'generated_at']),
            models.Index(fields=['status', 'generated_at']),
            models.Index(fields=['document_number']),
        ]

    def __str__(self):
        return self.document_number

    def cancel(self, reason='', user=None):
        """Cancel this document number and store an optional reason."""
        self.change_status('cancelled', reason=reason)

    def mark_used(self):
        """Mark this document number as used."""
        self.change_status('used')

    def change_status(self, new_status, reason=''):
        """Change lifecycle status while keeping audit timestamps consistent."""
        if new_status not in dict(self.STATUS_CHOICES):
            raise ValueError(f'Unsupported document status: {new_status}')
        from django.utils import timezone
        now = timezone.now()
        self.status = new_status
        self.used_at = now if new_status == 'used' else None
        self.cancelled_at = now if new_status == 'cancelled' else None
        self.cancellation_reason = reason if new_status == 'cancelled' else ''
        self.save(update_fields=[
            'status', 'used_at', 'cancelled_at', 'cancellation_reason'
        ])

    @property
    def is_valid(self):
        return self.status == 'active'
