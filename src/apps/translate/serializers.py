from rest_framework import serializers

from .models import *


class LanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Language
        fields = '__all__'


class TranslatePackSerializer(serializers.ModelSerializer):

    class Meta:
        model = Translate
        exclude = ('id', 'language')


class TranslateSerializer(serializers.ModelSerializer):

    language = serializers.SlugRelatedField(
        slug_field='abbreviation',
        read_only=True
    )

    class Meta:
        model = Translate
        exclude = ('id', )
