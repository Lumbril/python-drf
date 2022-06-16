from rest_framework import serializers

from .models import *


class SystemInfoSerializer(serializers.ModelSerializer):

    value = serializers.SerializerMethodField('get_value')

    def get_value(self, obj):
        return obj.get_value()

    def to_representation(self, instance):
        res = super().to_representation(instance)

        res['type'] = res['type']['name']

        return res

    class Meta:
        depth = 1
        model = SystemInfo
        fields = ('key', 'value', 'type')
