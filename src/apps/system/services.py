from django_filters import rest_framework as drf_filters


class SystemTypeFilter(drf_filters.FilterSet):

    type = drf_filters.BaseInFilter(field_name='type__name')

    class Meta:
        fields = ('type', )
