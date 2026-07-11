import os
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class CustomStorage(FileSystemStorage):
    """Пользовательское хранилище для изображений django_ckeditor_5."""

    location = os.path.join(settings.MEDIA_ROOT, "ckeditor_5")
    base_url = urljoin(settings.MEDIA_URL, "ckeditor_5/")