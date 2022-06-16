from rest_framework.validators import UniqueValidator

from rest_framework import serializers

from apps.core.models import Storage


class StorageSerializer(serializers.ModelSerializer):

    media_id = serializers.IntegerField(
        min_value=1,
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=Storage.objects.all()
            )
        ]
    )
    name = serializers.CharField(
        max_length=255,
        validators=[
            UniqueValidator(
                queryset=Storage.objects.all()
            )
        ]
    )
    url = serializers.CharField(
        max_length=255
    )

    class Meta:
        model = Storage
        fields = ('media_id', 'name', 'url')
