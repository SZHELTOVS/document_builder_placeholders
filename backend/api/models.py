from django.db import models

class UploadedDoc(models.Model):
    name = models.CharField(max_length=255, blank=True)  # Название шаблона
    file = models.FileField(upload_to="uploads/")        # .docx файл
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.file.name


class PlaceholderSet(models.Model):
    """Набор данных (например, для конкретного человека)"""
    title = models.CharField(max_length=200)  # Название набора (например "Иванов Иван")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PlaceholderValue(models.Model):
    """Конкретные плейсхолдеры внутри набора"""
    set = models.ForeignKey(PlaceholderSet, on_delete=models.CASCADE, related_name="placeholders")
    name = models.CharField(max_length=100)   # имя плейсхолдера (fio, passport, address)
    value = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.set.title}: {self.name} = {self.value}"
    
class Doc(models.Model):
    name = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
