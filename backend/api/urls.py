from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import hello_world, UploadDocView, FillDocView, list_docs, get_placeholders, delete_doc, PlaceholderSetViewSet, UploadedDocViewSet

router = DefaultRouter()
router.register(r'placeholder-sets', PlaceholderSetViewSet)
router.register(r'docs', UploadedDocViewSet) 

urlpatterns = [
    path("hello/", hello_world),
    path("upload/", UploadDocView.as_view()),
    path("fill/", FillDocView.as_view()),
    path("docs/", list_docs),
    path("docs/<int:doc_id>/placeholders/", get_placeholders),
    path("docs/<int:doc_id>/delete/", delete_doc),
    path('', include(router.urls)),
]
