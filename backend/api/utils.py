from docxtpl import DocxTemplate
import docx, re, os
from django.utils.crypto import get_random_string
from .models import UploadedDoc
from django.conf import settings

def extract_placeholders(doc_id: int):
    """
    Получаем все переменные шаблона (простые и таблицы) по id документа.
    Возвращает список вида:
    ["name", "date", {"type": "table", "name": "items", "columns": [{"name": "product", "label": "Product"}]}]
    """
    try:
        template = UploadedDoc.objects.get(id=doc_id)
    except UploadedDoc.DoesNotExist:
        return []

    docx_path = template.file.path
    doc = DocxTemplate(docx_path)

    # Простые переменные
    simple_fields = list(doc.get_undeclared_template_variables())

    # Убираем дубликаты и сортируем по порядку появления
    seen = set()
    unique_fields = []
    for f in simple_fields:
        if f not in seen:
            seen.add(f)
            unique_fields.append(f)

    # Таблицы
    docx_doc = docx.Document(docx_path)
    tables = []
    for table in docx_doc.tables:
        text = "\n".join(cell.text for row in table.rows for cell in row.cells)
        match = re.search(r"{%\s*for\s+row\s+in\s+(\w+)\s*%}", text)
        if match:
            table_name = match.group(1)
            cols = []
            for row in table.rows:
                for cell in row.cells:
                    cols += re.findall(r"{{\s*row\.([\w_]+)\s*}}", cell.text)
            columns = list(dict.fromkeys(cols))
            if columns:
                tables.append({
                    "type": "table",
                    "name": table_name,
                    "columns": [{"name": c, "label": c.replace('_', ' ').capitalize()} for c in columns]
                })

    # Убираем имена таблиц из простых переменных
    unique_fields = [f for f in unique_fields if f not in [t["name"] for t in tables]]

    return unique_fields + tables



def replace_placeholders(doc_id: int, values: dict, output_dir: str = None):
    """
    Заполняет шаблон по id документа значениями values и сохраняет в выбранную папку.
    Возвращает путь к заполненному файлу.

    :param doc_id: id документа в базе
    :param values: словарь {placeholder: value}
    :param output_dir: путь к папке для сохранения (по умолчанию media/output)
    """
    template = UploadedDoc.objects.get(id=doc_id)
    docx_path = template.file.path

    doc = DocxTemplate(docx_path)
    doc.render(values)

    # если путь не передан — сохраняем в media/output
    if output_dir is None:
        output_dir = os.path.join(settings.MEDIA_ROOT, "output")

    os.makedirs(output_dir, exist_ok=True)

    # Генерация уникального имени
    output_filename = f"filled_{get_random_string(10)}.docx"
    output_path = os.path.join(output_dir, output_filename)

    doc.save(output_path)
    return output_path

