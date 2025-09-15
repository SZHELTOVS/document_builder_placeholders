from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import viewsets
from django.http import FileResponse, HttpResponse
from django.utils.crypto import get_random_string
import os, io
from docxtpl import DocxTemplate
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import UploadedDoc, PlaceholderSet
from .serializers import UploadedDocSerializer, PlaceholderSetSerializer
from .utils import extract_placeholders
from django.http import FileResponse
from io import BytesIO

@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'Hello from Django!'})


@api_view(['GET'])
def list_docs(request):
    docs = UploadedDoc.objects.all().order_by('-uploaded_at')
    data = []
    for doc in docs:
        data.append({
            "id": doc.id,
            "name": doc.file.name.split('/')[-1],
            "uploaded_at": doc.uploaded_at,
            "placeholders": []
        })
    return Response(data)


@api_view(['GET'])
def get_placeholders(request, doc_id):
    try:
        doc = UploadedDoc.objects.get(id=doc_id)
    except UploadedDoc.DoesNotExist:
        return Response({"placeholders": []}, status=404)

    placeholders = extract_placeholders(doc.id)
    return Response({"placeholders": placeholders})


@api_view(['DELETE'])
def delete_doc(request, doc_id):
    try:
        doc = UploadedDoc.objects.get(id=doc_id)
        file_path = doc.file.path
        doc.delete()
        if os.path.exists(file_path):
            os.remove(file_path)
        return Response({"success": True})
    except UploadedDoc.DoesNotExist:
        return Response({"error": "Документ не найден"}, status=404)


class UploadDocView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = UploadedDocSerializer(data=request.data)
        if serializer.is_valid():
            doc = serializer.save()
            fields = extract_placeholders(doc.id)
            return Response({"file_id": doc.id, "placeholders": fields})
        return Response(serializer.errors, status=400)


class FillDocView(APIView):
    def post(self, request):
        file_id = request.data.get("file_id")
        values = request.data.get("values", {})

        try:
            template = UploadedDoc.objects.get(id=file_id)
            docx_path = template.file.path

            doc = DocxTemplate(docx_path)
            doc.render(values)

            file_stream = io.BytesIO()
            doc.save(file_stream)
            file_stream.seek(0)

            filename = f"filled_{get_random_string(8)}.docx"
            return FileResponse(file_stream, as_attachment=True, filename=filename)
        except UploadedDoc.DoesNotExist:
            return Response({"error": "File not found"}, status=404)


class PlaceholderSetViewSet(viewsets.ModelViewSet):
    queryset = PlaceholderSet.objects.all()
    serializer_class = PlaceholderSetSerializer

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

