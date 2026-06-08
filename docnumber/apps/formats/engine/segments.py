# apps/formats/engine/segments.py
import re
import random
import string
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from django.utils import timezone


class SegmentConfig:
    """Segment configuration container"""
    def __init__(self, **kwargs):
        self.options = kwargs

    def get(self, key, default=None):
        return self.options.get(key, default)


class BaseSegment(ABC):
    """Abstract base for all segment types"""
    segment_type: str = ''
    label: str = ''
    description: str = ''
    icon: str = ''

    def __init__(self, config: SegmentConfig):
        self.config = config
        self.validate_config()

    @abstractmethod
    def generate(self, context: Dict[str, Any]) -> str:
        """Generate segment value"""
        pass

    @abstractmethod
    def preview(self) -> str:
        """Preview segment value"""
        pass

    @abstractmethod
    def validate_config(self) -> None:
        """Validate configuration"""
        pass

    def to_dict(self) -> Dict:
        return {
            'type': self.segment_type,
            'config': self.config.options,
            'preview': self.preview(),
        }


class StaticSegment(BaseSegment):
    """Fixed text segment"""
    segment_type = 'static'
    label = 'Sabit Metin'
    description = 'Değişmeyen sabit bir metin'
    icon = 'text'

    def validate_config(self):
        value = self.config.get('value', '')
        if not value:
            raise ValueError("Static segment requires 'value'")
        if len(value) > 50:
            raise ValueError("Static value cannot exceed 50 characters")

    def generate(self, context: Dict[str, Any]) -> str:
        return self.config.get('value', '')

    def preview(self) -> str:
        return self.config.get('value', 'TEXT')


class DateSegment(BaseSegment):
    """Date-based segment"""
    segment_type = 'date'
    label = 'Tarih'
    description = 'Tarih bazlı segment'
    icon = 'calendar'

    ALLOWED_FORMATS = {
        'YYYY': '%Y',
        'YY': '%y',
        'MM': '%m',
        'DD': '%d',
        'YYYYMMDD': '%Y%m%d',
        'YYYYMM': '%Y%m',
        'DDMMYYYY': '%d%m%Y',
        'MMYYYY': '%m%Y',
        'Q': 'quarter',
        'WW': '%W',
    }

    def validate_config(self):
        fmt = self.config.get('format', 'YYYY')
        if fmt not in self.ALLOWED_FORMATS:
            raise ValueError(
                f"Invalid date format '{fmt}'. "
                f"Allowed: {', '.join(self.ALLOWED_FORMATS.keys())}"
            )

    def generate(self, context: Dict[str, Any]) -> str:
        now = context.get('timestamp', timezone.now())
        if timezone.is_aware(now):
            from django.utils.timezone import localtime
            now = localtime(now)

        fmt = self.config.get('format', 'YYYY')

        if fmt == 'Q':
            quarter = (now.month - 1) // 3 + 1
            return str(quarter)

        strftime_fmt = self.ALLOWED_FORMATS[fmt]
        return now.strftime(strftime_fmt)

    def preview(self) -> str:
        return self.generate({'timestamp': timezone.now()})


class SequenceSegment(BaseSegment):
    """Auto-incrementing sequence segment"""
    segment_type = 'sequence'
    label = 'Sıra Numarası'
    description = 'Otomatik artan sıra numarası'
    icon = 'number'

    def validate_config(self):
        padding = self.config.get('padding', 4)
        if not isinstance(padding, int) or padding < 1 or padding > 20:
            raise ValueError("Padding must be integer between 1-20")

        start = self.config.get('start', 1)
        if not isinstance(start, int) or start < 0:
            raise ValueError("Start must be non-negative integer")

        step = self.config.get('step', 1)
        if not isinstance(step, int) or step < 1:
            raise ValueError("Step must be positive integer")

    def generate(self, context: Dict[str, Any]) -> str:
        sequence_value = context.get('sequence_value', 1)
        padding = self.config.get('padding', 4)
        return str(sequence_value).zfill(padding)

    def preview(self) -> str:
        padding = self.config.get('padding', 4)
        start = self.config.get('start', 1)
        return str(start).zfill(padding)


class RandomSegment(BaseSegment):
    """Random character segment"""
    segment_type = 'random'
    label = 'Rastgele'
    description = 'Rastgele karakter dizisi'
    icon = 'shuffle'

    CHAR_SETS = {
        'numeric': string.digits,
        'alpha': string.ascii_uppercase,
        'alphanumeric': string.ascii_uppercase + string.digits,
        'hex': string.hexdigits.upper()[:16],
    }

    def validate_config(self):
        length = self.config.get('length', 6)
        if not isinstance(length, int) or length < 1 or length > 20:
            raise ValueError("Length must be integer between 1-20")

        char_type = self.config.get('char_type', 'alphanumeric')
        if char_type not in self.CHAR_SETS:
            raise ValueError(f"Invalid char_type. Allowed: {', '.join(self.CHAR_SETS.keys())}")

    def generate(self, context: Dict[str, Any]) -> str:
        length = self.config.get('length', 6)
        char_type = self.config.get('char_type', 'alphanumeric')
        chars = self.CHAR_SETS[char_type]
        return ''.join(random.choices(chars, k=length))

    def preview(self) -> str:
        length = self.config.get('length', 6)
        char_type = self.config.get('char_type', 'alphanumeric')
        chars = self.CHAR_SETS[char_type]
        return ''.join(random.choices(chars, k=length))


class ChecksumSegment(BaseSegment):
    """Checksum/validation digit segment"""
    segment_type = 'checksum'
    label = 'Kontrol Hanesi'
    description = 'Otomatik hesaplanan kontrol hanesi'
    icon = 'check'

    ALGORITHMS = ['luhn', 'mod10', 'mod11', 'simple']

    def validate_config(self):
        algorithm = self.config.get('algorithm', 'mod10')
        if algorithm not in self.ALGORITHMS:
            raise ValueError(f"Invalid algorithm. Allowed: {', '.join(self.ALGORITHMS)}")

    def generate(self, context: Dict[str, Any]) -> str:
        partial = context.get('partial_number', '')
        algorithm = self.config.get('algorithm', 'mod10')
        return self._calculate(partial, algorithm)

    def _calculate(self, number: str, algorithm: str) -> str:
        digits = re.sub(r'\D', '', number)

        if algorithm == 'luhn':
            return self._luhn(digits)
        elif algorithm == 'mod10':
            return self._mod10(digits)
        elif algorithm == 'mod11':
            return self._mod11(digits)
        else:
            return self._simple(digits)

    def _luhn(self, digits: str) -> str:
        total = 0
        for i, d in enumerate(reversed(digits)):
            n = int(d)
            if i % 2 == 0:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        return str((10 - total % 10) % 10)

    def _mod10(self, digits: str) -> str:
        total = sum(int(d) for d in digits)
        return str((10 - total % 10) % 10)

    def _mod11(self, digits: str) -> str:
        weights = [2, 3, 4, 5, 6, 7]
        total = sum(int(d) * weights[i % len(weights)] for i, d in enumerate(reversed(digits)))
        remainder = total % 11
        if remainder == 0:
            return '0'
        elif remainder == 1:
            return 'X'
        return str(11 - remainder)

    def _simple(self, digits: str) -> str:
        return str(sum(int(d) for d in digits) % 10)

    def preview(self) -> str:
        return 'C'


class ContextSegment(BaseSegment):
    """Dynamic context-based segment (department, category, etc.)"""
    segment_type = 'context'
    label = 'Bağlam Değeri'
    description = 'Dinamik bağlam değeri (departman, kategori vb.)'
    icon = 'tag'

    def validate_config(self):
        key = self.config.get('key', '')
        if not key:
            raise ValueError("Context segment requires 'key'")

    def generate(self, context: Dict[str, Any]) -> str:
        key = self.config.get('key', '')
        default = self.config.get('default', 'UNKNOWN')
        value = context.get('context_data', {}).get(key, default)
        max_length = self.config.get('max_length', 10)

        value = str(value).upper()[:max_length]

        if self.config.get('pad_to_length'):
            value = value.ljust(self.config.get('pad_to_length', len(value)))

        return value

    def preview(self) -> str:
        key = self.config.get('key', 'CONTEXT')
        return f'[{key.upper()}]'


class SeparatorSegment(BaseSegment):
    """Separator/delimiter segment"""
    segment_type = 'separator'
    label = 'Ayraç'
    description = 'Bölüm ayracı (-,/,.,_ vs)'
    icon = 'minus'

    ALLOWED_SEPARATORS = ['-', '/', '.', '_', '|', ':', '\\']

    def validate_config(self):
        sep = self.config.get('value', '-')
        if sep not in self.ALLOWED_SEPARATORS:
            raise ValueError(
                f"Invalid separator. Allowed: {', '.join(self.ALLOWED_SEPARATORS)}"
            )

    def generate(self, context: Dict[str, Any]) -> str:
        return self.config.get('value', '-')

    def preview(self) -> str:
        return self.config.get('value', '-')


class YearlyResetSequenceSegment(BaseSegment):
    """Sequence that resets yearly"""
    segment_type = 'yearly_sequence'
    label = 'Yıllık Sıfırlanan Numara'
    description = 'Her yıl başında sıfırlanan sıra numarası'
    icon = 'refresh'

    def validate_config(self):
        padding = self.config.get('padding', 4)
        if not isinstance(padding, int) or padding < 1 or padding > 20:
            raise ValueError("Padding must be integer between 1-20")

    def generate(self, context: Dict[str, Any]) -> str:
        sequence_value = context.get('sequence_value', 1)
        padding = self.config.get('padding', 4)
        return str(sequence_value).zfill(padding)

    def preview(self) -> str:
        return '0001'


# Segment Registry
SEGMENT_REGISTRY: Dict[str, type] = {
    'static': StaticSegment,
    'date': DateSegment,
    'sequence': SequenceSegment,
    'yearly_sequence': YearlyResetSequenceSegment,
    'random': RandomSegment,
    'checksum': ChecksumSegment,
    'context': ContextSegment,
    'separator': SeparatorSegment,
}


def get_segment_class(segment_type: str) -> type:
    cls = SEGMENT_REGISTRY.get(segment_type)
    if not cls:
        raise ValueError(f"Unknown segment type: '{segment_type}'")
    return cls


def get_available_segments() -> list:
    return [
        {
            'type': cls.segment_type,
            'label': cls.label,
            'description': cls.description,
            'icon': cls.icon,
        }
        for cls in SEGMENT_REGISTRY.values()
    ]