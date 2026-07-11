from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import About, Chapter, ContentChapter, ContentFile, News, FooterInfo, NewsImage, Event

admin.site.site_header = "Лоевский территориальный центр социального обслуживания населения"
admin.site.site_title = "Лоевский территориальный центр социального обслуживания населения"
admin.site.index_title = "Добро пожаловать в систему управления"


class NewsAdminForm(forms.ModelForm):
    clear_photo = forms.BooleanField(
        required=False,
        label="Удалить текущее фото",
        help_text="Отметьте, чтобы удалить загруженное изображение."
    )

    class Meta:
        model = News
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('clear_photo'):
            if instance.photo:
                instance.photo.delete(save=False)
            instance.photo = None
        if commit:
            instance.save()
        return instance


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1
    fields = ('image', 'preview')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "-"

    preview.short_description = "Превью"


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    inlines = [NewsImageInline]
    list_display = ('title', 'show', 'created_at')
    search_fields = ['title']
    list_editable = ('show',)
    readonly_fields = ('photo_preview',)

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.photo.url)
        return "-"

    photo_preview.short_description = "Фото"


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('title', 'show', 'photo_preview')
    list_editable = ('show',)
    readonly_fields = ('photo_preview',)

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.photo.url)
        return "-"

    photo_preview.short_description = "Фото"


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'show')
    list_editable = ('show',)
    search_fields = ('title',)


class ContentFileInline(admin.TabularInline):
    model = ContentFile
    extra = 1


@admin.register(ContentChapter)
class ContentChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'chapter', 'show')
    list_editable = ('show',)
    inlines = [ContentFileInline]


@admin.register(FooterInfo)
class FooterInfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'show', 'photo_preview')
    list_editable = ('show',)
    search_fields = ('title',)
    readonly_fields = ('photo_preview',)

    def photo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.logo.url)
        return "-"

    photo_preview.short_description = "Логотип"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time')
    search_fields = ('title',)
    list_filter = ('start_time',)
