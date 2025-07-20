from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import UploadedDoc
from .serializers import UploadedDocSerializer
from .utils import extract_placeholders, replace_placeholders  

@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'Hello from Django!'})

class UploadDocView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = UploadedDocSerializer(data=request.data)
        if serializer.is_valid():
            doc = serializer.save()
            fields = extract_placeholders(doc.file.path)
            return Response({"file_id": doc.id, "placeholders": fields})
        return Response(serializer.errors, status=400)

class FillDocView(APIView):
    def post(self, request):
        file_id = request.data.get("file_id")
        values = request.data.get("values", {})

        try:
            doc = UploadedDoc.objects.get(id=file_id)
            output_path = replace_placeholders(doc.file.path, values)
            # Возвращаем ссылку для скачивания
            download_url = f"/media/{output_path.split('/')[-1]}"
            return Response({"download_url": download_url})
        except UploadedDoc.DoesNotExist:
            return Response({"error": "File not found"}, status=404)