from django.urls import path
from .views import UploadDocView, FillDocView

urlpatterns = [
    path('upload/', UploadDocView.as_view(), name='upload_file'),
    path('fill/', FillDocView.as_view(), name='fill_file'),
]