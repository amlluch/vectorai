from rest_framework import serializers
from .models import Document

import re

class UploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ('image',)
        write_only_fields = ('image',)

    def validate_image(self, obj):
        pattern = re.compile('^([a-zA-Z0-9\s_\\.\-\(\):])+(.jpg|.png)+$')
        if pattern.match(obj.name):
            return super(UploadSerializer, self).validate(obj)
        else:
            raise serializers.ValidationError('Only jpg and png files admitted')

    def create(self, validated_data):
        return Document.objects.create(**validated_data)

