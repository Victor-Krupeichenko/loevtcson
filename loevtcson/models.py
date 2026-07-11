import re
from django.db import models
from django.urls import reverse_lazy
from django_ckeditor_5.fields import CKEditor5Field
from autoslug import AutoSlugField
from uuslug import uuslug


def instance_title(instance):
    """
    Возвращает заголовок для slug
    """
    return instance.title


def slugify_value(value):
    """
    Возвращает slug с замененными пробелами на тире
    """
    return value.replace(" ", "-")


def clean_value(value):
    return re.sub(r"[^a-zA-Z0-9а-яА-ЯЁё]", '-', value)


def content_file_upload_path(instance, filename):
    title = clean_value(instance.content.title)
    return f'files_chapter/{title}/{filename}'


def news_photo_upload_path(instance, filename):
    title = clean_value(instance.title)
    return f'news/{title}/title/{filename}'


def news_image_upload_path(instance, filename):
    title = clean_value(instance.news.title)
    return f'news/{title}/rest_images/{filename}'


class About(models.Model):
    """
    О нас
    """
    title = models.CharField(max_length=255, verbose_name="Название", db_index=True)
    slug = AutoSlugField(populate_from=instance_title, slugify=slugify_value, unique=True, max_length=255)
    director = models.CharField(max_length=255, verbose_name="Руководитель", db_index=True)
    cabinet = models.IntegerField(verbose_name="Номер кабинета")
    address = models.CharField(max_length=255, verbose_name="Юридический адрес", db_index=True)
    telephone = models.CharField(max_length=255, verbose_name="Телефон", db_index=True)
    info = CKEditor5Field(verbose_name="Информация", config_name="extends")
    email = models.EmailField(verbose_name="Адрес электронной почты")
    content = CKEditor5Field(verbose_name="Содержание", config_name="extends")
    photo = models.ImageField(upload_to="about", verbose_name="Фото")
    show = models.BooleanField(default=True, verbose_name="Показывать")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        context = {
            "slug": self.slug
        }
        return reverse_lazy("about", kwargs=context)

    class Meta:
        verbose_name = "О нас"
        verbose_name_plural = "О нас"


class Chapter(models.Model):
    """
    Добавление раздела
    """
    title = models.CharField(max_length=255, verbose_name="Раздел", db_index=True)
    slug = AutoSlugField(populate_from=instance_title, slugify=slugify_value, unique=True, max_length=255)
    show = models.BooleanField(default=True, verbose_name="Показывать")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy('chapter', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Раздел"
        verbose_name_plural = "Разделы"


class ContentChapter(models.Model):
    """
    Добавление содержания к разделу
    """
    title = models.CharField(max_length=255, verbose_name="Название", db_index=True)
    slug = AutoSlugField(populate_from=instance_title, slugify=slugify_value, unique=True, max_length=255)
    content = CKEditor5Field(verbose_name="Содержание", config_name="extends")
    show = models.BooleanField(default=True, verbose_name="Показывать")
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='contents',
        verbose_name="Раздел",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        context = {
            "slug": self.slug
        }
        return reverse_lazy("chapter", kwargs=context)

    class Meta:
        verbose_name = "Содержание раздела"
        verbose_name_plural = "Содержания разделов"


class ContentFile(models.Model):
    content = models.ForeignKey(
        ContentChapter,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name="Содержание раздела"
    )
    file = models.FileField(upload_to=content_file_upload_path, verbose_name="Файл", blank=True)
    filename = models.CharField(max_length=255, blank=True, null=True, verbose_name="Имя файла, которое будет показано на сайте")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Прикреплённый файл"
        verbose_name_plural = "Прикреплённые файлы"

    def __str__(self):
        return self.file.name


class News(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок", db_index=True)
    slug = AutoSlugField(populate_from='title', unique=True, max_length=255)
    content = CKEditor5Field(verbose_name="Содержание", config_name="extends")
    photo = models.ImageField(upload_to=news_photo_upload_path, blank=True, null=True, verbose_name="Фото")
    show = models.BooleanField(default=True, verbose_name="Показывать")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuslug(self.title, instance=self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy('news', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"


class NewsImage(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='images', verbose_name="Новость")
    image = models.ImageField(upload_to=news_image_upload_path, verbose_name="Изображение")

    def __str__(self):
        return self.news.title

    class Meta:
        verbose_name = "Фото новости"
        verbose_name_plural = "Фото для новости"


class FooterInfo(models.Model):
    """
    Добавление ссылки в footer
    """
    title = models.CharField(max_length=255, verbose_name="Название")
    url = models.URLField(verbose_name="Url-адрес")
    logo = models.ImageField(upload_to="footer_logo_url", verbose_name="Логотип для ссылки")
    show = models.BooleanField(default=True, verbose_name="Показать")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Ссылка для подвала"
        verbose_name_plural = "Ссылки для подвала"


class Event(models.Model):
    title = models.CharField(max_length=255, verbose_name="Названия события")
    start_time = models.DateTimeField(verbose_name="Дата и время начала")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания")
    description = models.TextField(blank=True, null=True, verbose_name="Описания события")  # Почему не показывается содержимое этого поля???
    color = models.CharField(max_length=7, default='#3788d8', verbose_name="цвет события в календаре")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Мероприятия"
        verbose_name_plural = "Мероприятия"
