from apps.core.models import Notification

from rest_framework import serializers


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'
        
        
class NotificationReadSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Notification
        fields = ('id',)
