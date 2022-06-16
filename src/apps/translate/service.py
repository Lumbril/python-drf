from django_filters import rest_framework as drf_filters


class TranslateLanguageFilter(drf_filters.FilterSet):

    language = drf_filters.BaseInFilter(field_name='language__abbreviation')

    class Meta:
        fields = ('language',)
