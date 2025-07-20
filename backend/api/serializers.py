from rest_framework import serializers
from .models import UploadedDoc

class UploadedDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedDoc
        fields = ['id', 'file', 'uploaded_at']
