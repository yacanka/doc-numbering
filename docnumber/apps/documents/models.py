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
        from django.utils import timezone
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.save(update_fields=['status', 'cancelled_at', 'cancellation_reason'])

    def mark_used(self):
        from django.utils import timezone
        self.status = 'used'
        self.used_at = timezone.now()
        self.save(update_fields=['status', 'used_at'])

    @property
    def is_valid(self):
        return self.status == 'active'