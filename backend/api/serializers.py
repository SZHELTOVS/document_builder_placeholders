from rest_framework import serializers
from .models import UploadedDoc
from .models import PlaceholderSet, PlaceholderValue
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from docxtpl import DocxTemplate
from django.utils.crypto import get_random_string
from .models import UploadedDoc, PlaceholderSet

class UploadedDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedDoc
        fields = ["id", "name", "file", "uploaded_at"]

class PlaceholderValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceholderValue
        fields = ["id", "name", "value"]

class PlaceholderSetSerializer(serializers.ModelSerializer):
    placeholders = PlaceholderValueSerializer(many=True)

    class Meta:
        model = PlaceholderSet
        fields = ["id", "title", "placeholders"]

    def create(self, validated_data):
        placeholders_data = validated_data.pop("placeholders", [])
        set_obj = PlaceholderSet.objects.create(**validated_data)
        for ph in placeholders_data:
            PlaceholderValue.objects.create(set=set_obj, **ph)
        return set_obj

    def update(self, instance, validated_data):
        placeholders_data = validated_data.pop("placeholders", [])
        instance.title = validated_data.get("title", instance.title)
        instance.save()

        instance.placeholders.all().delete()
        for ph in placeholders_data:
            PlaceholderValue.objects.create(set=instance, **ph)
        return instance

class UploadedDocViewSet(viewsets.ModelViewSet):
    queryset = UploadedDoc.objects.all()
    serializer_class = UploadedDocSerializer

    @action(detail=True, methods=['post'], url_path='render')
    def render_doc(self, request, pk=None):
        """
        Генерация DOCX с данными из выбранного PlaceholderSet
        POST body: { "set_id": <id набора> }
        """
        doc = self.get_object()
        set_id = request.data.get("set_id")
        if not set_id:
            return Response({"error": "set_id is required"}, status=400)

        try:
            placeholder_set = PlaceholderSet.objects.get(id=set_id)
        except PlaceholderSet.DoesNotExist:
            return Response({"error": "Placeholder set not found"}, status=404)

        tpl = DocxTemplate(doc.file.path)
        context = {p.name: p.value for p in placeholder_set.placeholders.all()}
        tpl.render(context)

        # Сохраняем в память
        file_stream = BytesIO()
        tpl.save(file_stream)
        file_stream.seek(0)

        filename = f"filled_{get_random_string(8)}.docx"
        return FileResponse(file_stream, as_attachment=True, filename=filename)