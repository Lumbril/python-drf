from rest_framework import serializers

from apps.core.models import Currency


class CurrencySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Currency
        fields = '__all__'
