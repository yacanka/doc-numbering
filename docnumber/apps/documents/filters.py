# apps/documents/filters.py
import django_filters
from apps.formats.models import DocumentFormat
from .models import GeneratedDocument


class GeneratedDocumentFilter(django_filters.FilterSet):
    """Filter generated documents by lifecycle and related format."""

    format = django_filters.ModelChoiceFilter(
        field_name='format',
        queryset=DocumentFormat.objects.all(),
    )
    status = django_filters.CharFilter(lookup_expr='exact')
    search = django_filters.CharFilter(field_name='document_number', lookup_expr='icontains')
    date_from = django_filters.DateFilter(field_name='generated_at', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='generated_at', lookup_expr='date__lte')
    generated_by = django_filters.NumberFilter(field_name='generated_by__id')

    class Meta:
        model = GeneratedDocument
        fields = ['format', 'status', 'generated_by']