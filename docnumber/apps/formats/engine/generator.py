# apps/formats/engine/generator.py
import logging
from typing import Dict, Any, List, Optional
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone

from .segments import BaseSegment, SegmentConfig, get_segment_class, ChecksumSegment

logger = logging.getLogger(__name__)


class DocumentNumberGenerator:
    """
    Main engine for generating unique document numbers.
    Thread-safe with distributed locking via Redis.
    """

    LOCK_TIMEOUT = 30  # seconds
    LOCK_PREFIX = 'docnum:lock:'

    def __init__(self, format_instance):
        self.format = format_instance
        self.segments = self._build_segments()

    def _build_segments(self) -> List[BaseSegment]:
        segments = []
        for seg_config in self.format.segments_config:
            seg_type = seg_config.get('type')
            options = seg_config.get('config', {})
            cls = get_segment_class(seg_type)
            segments.append(cls(SegmentConfig(**options)))
        return segments

    def generate(
        self,
        context_data: Optional[Dict[str, Any]] = None,
        user=None,
        metadata: Optional[Dict] = None,
    ) -> 'GeneratedDocument':
        """
        Generate a unique document number with distributed locking.
        """
        lock_key = f"{self.LOCK_PREFIX}{self.format.id}"

        # Acquire distributed lock
        lock = cache.lock(lock_key, timeout=self.LOCK_TIMEOUT)

        try:
            acquired = lock.acquire(blocking=True, blocking_timeout=10)
            if not acquired:
                raise RuntimeError("Could not acquire lock for document generation")

            return self._generate_internal(context_data, user, metadata)

        finally:
            try:
                lock.release()
            except Exception:
                pass

    @transaction.atomic
    def _generate_internal(
        self,
        context_data: Optional[Dict[str, Any]],
        user,
        metadata: Optional[Dict],
    ) -> 'GeneratedDocument':
        from apps.documents.models import GeneratedDocument

        now = timezone.now()

        # Get or create sequence
        sequence_value = self._get_next_sequence(now)

        context = {
            'timestamp': now,
            'sequence_value': sequence_value,
            'context_data': context_data or {},
            'format': self.format,
            'user': user,
        }

        # Build number segment by segment
        parts = []
        for segment in self.segments:
            if isinstance(segment, ChecksumSegment):
                context['partial_number'] = ''.join(parts)
            parts.append(segment.generate(context))

        document_number = ''.join(parts)

        # Validate uniqueness
        if GeneratedDocument.objects.filter(
            document_number=document_number
        ).exists():
            logger.warning(
                f"Duplicate number detected: {document_number}, "
                f"retrying with incremented sequence"
            )
            # Force increment and retry
            sequence_value = self._force_increment_sequence(now)
            context['sequence_value'] = sequence_value
            parts = []
            for segment in self.segments:
                if isinstance(segment, ChecksumSegment):
                    context['partial_number'] = ''.join(parts)
                parts.append(segment.generate(context))
            document_number = ''.join(parts)

        # Validate against format pattern
        if self.format.validation_regex:
            import re
            if not re.match(self.format.validation_regex, document_number):
                raise ValueError(
                    f"Generated number '{document_number}' does not match "
                    f"validation pattern '{self.format.validation_regex}'"
                )

        # Save to database
        doc = GeneratedDocument.objects.create(
            format=self.format,
            document_number=document_number,
            sequence_value=sequence_value,
            context_data=context_data or {},
            generated_by=user,
            generated_at=now,
            metadata=metadata or {},
        )

        logger.info(
            f"Generated document number: {document_number} "
            f"(format={self.format.code}, sequence={sequence_value})"
        )

        return doc

    def _get_next_sequence(self, now) -> int:
        from apps.formats.models import FormatSequence

        reset_period = self.format.sequence_reset_period
        period_key = self._get_period_key(now, reset_period)

        seq, created = FormatSequence.objects.select_for_update().get_or_create(
            format=self.format,
            period_key=period_key,
            defaults={
                'current_value': self.format.sequence_start,
                'step': self.format.sequence_step,
            }
        )

        if not created:
            seq.current_value += seq.step
            seq.save(update_fields=['current_value', 'updated_at'])

        return seq.current_value

    def _force_increment_sequence(self, now) -> int:
        from apps.formats.models import FormatSequence

        reset_period = self.format.sequence_reset_period
        period_key = self._get_period_key(now, reset_period)

        seq = FormatSequence.objects.select_for_update().get(
            format=self.format,
            period_key=period_key,
        )
        seq.current_value += seq.step
        seq.save(update_fields=['current_value', 'updated_at'])
        return seq.current_value

    def _get_period_key(self, now, reset_period: str) -> str:
        from django.utils.timezone import localtime
        local_now = localtime(now)

        period_map = {
            'never': 'ALL',
            'daily': local_now.strftime('%Y%m%d'),
            'weekly': local_now.strftime('%Y-W%W'),
            'monthly': local_now.strftime('%Y%m'),
            'quarterly': f"{local_now.year}-Q{(local_now.month-1)//3+1}",
            'yearly': local_now.strftime('%Y'),
        }
        return period_map.get(reset_period, 'ALL')

    def preview(self, context_data: Optional[Dict] = None) -> str:
        """Generate a preview without saving"""
        context = {
            'timestamp': timezone.now(),
            'sequence_value': self.format.sequence_start,
            'context_data': context_data or {},
        }

        parts = []
        for segment in self.segments:
            if isinstance(segment, ChecksumSegment):
                context['partial_number'] = ''.join(parts)
            parts.append(segment.generate(context))

        return ''.join(parts)

    def bulk_generate(
        self,
        count: int,
        context_data: Optional[Dict] = None,
        user=None,
    ) -> List['GeneratedDocument']:
        """Generate multiple document numbers efficiently"""
        if count > 1000:
            raise ValueError("Bulk generate limit is 1000")

        results = []
        for _ in range(count):
            doc = self.generate(context_data=context_data, user=user)
            results.append(doc)

        return results