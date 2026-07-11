from django.views.generic import ListView, DetailView
from .models import About, Chapter, News, ContentChapter, Event
from django.utils.html import strip_tags
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings


class AboutView(ListView):
    model = About
    template_name = "index.html"
    context_object_name = "about"

    def get_queryset(self):
        return About.objects.filter(show=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ChapterDetailView(DetailView):
    model = Chapter
    template_name = "content_chapter.html"
    context_object_name = "chapter"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contents'] = self.object.contents.filter(show=True)
        return context


class NewsDetailView(DetailView):
    model = News
    template_name = "news_detail.html"
    context_object_name = "news"


class NewsListView(ListView):
    model = News
    template_name = "all_news.html"
    context_object_name = "news"
    paginate_by = 10

    def get_queryset(self):
        return News.objects.filter(show=True).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_pagination'] = context['page_obj'].paginator.num_pages > 1
        return context


def get_snippet(text, query, window=30):
    """
    Возвращает фрагмент текста с контекстом вокруг первого вхождения query.
    :param text: исходный текст (может содержать HTML)
    :param query: искомая подстрока (оригинальный запрос)
    :param window: количество символов до и после найденного слова
     :return: строка с ... и выделенным (жирным) найденным словом
    """
    if not text or not query:
        return ""

    clean_text = strip_tags(text)
    lower_text = clean_text.lower()
    lower_query = query.lower()
    pos = lower_text.find(lower_query)

    if pos == -1:
        return clean_text[:window * 2] + "..." if len(clean_text) > window * 2 else clean_text

    start = max(0, pos - window)
    end = min(len(clean_text), pos + len(query) + window)

    snippet = clean_text[start:end]

    if start > 0:
        snippet = "..." + snippet
    if end < len(clean_text):
        snippet = snippet + "..."

    lower_snippet = snippet.lower()
    pos_in_snippet = lower_snippet.find(lower_query)
    if pos_in_snippet != -1:
        word = snippet[pos_in_snippet:pos_in_snippet + len(query)]
        snippet = (snippet[:pos_in_snippet] +
                   f"<strong>{word}</strong>" +
                   snippet[pos_in_snippet + len(query):])

    return snippet


def loading_models_conf():
    """
    Загружает данные из полей модели по которым будет проходить поиск
    :return: список словарей с полученными данными
    """
    conf_search = [
        {
            'queryset': News.objects.filter(show=True),
            'search_fields': ['title', 'content'],
            'snippet_text_func': lambda obj: obj.content or obj.title,
        },
        {
            'queryset': ContentChapter.objects.filter(show=True),
            'search_fields': ['title', 'content'],
            'snippet_text_func': lambda obj: obj.content or obj.title,
        },
        {
            'queryset': About.objects.filter(show=True),
            'search_fields': ['title', 'director', 'address', 'telephone', 'info', 'email', 'content'],
            'snippet_text_func': lambda obj: (obj.info or '') + ' ' + (obj.content or ''),
        },
    ]
    return conf_search


def pagination(request, results, pages):
    """
    Постраничная навигация (пагинация)
    :param request: запрос
    :param results: список с результатами поиска
    :param pages: количество записей на странице № из settings.py - PAGINATE_BY
    :return: Объект пагинации
    """
    paginator = Paginator(results, pages)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


if not settings.DATABASEPOSTGRESQL:
    # sqlite3
    def search(request):
        query = request.GET.get('q', '').strip()
        results = []
        message = None

        if query:
            lower_query = query.lower()

            models_config = loading_models_conf()

            for config in models_config:
                qs = config['queryset']
                fields = config['search_fields']
                snippet_func = config['snippet_text_func']

                for obj in qs:
                    found = False
                    for field_name in fields:
                        value = getattr(obj, field_name, '')
                        if value and lower_query in value.lower():
                            found = True
                            break
                    if found:
                        text_for_snippet = snippet_func(obj)
                        obj.snippet = get_snippet(text_for_snippet, query)
                        results.append(obj)

            # Пагинация
            page_obj = pagination(request, results, settings.PAGINATE_BY)

        else:
            if 'q' in request.GET:
                message = 'Пожалуйста, введите запрос для поиска.'
            page_obj = None  # чтобы не было ошибки в шаблоне

        context = {
            "query": query,
            "page_obj": page_obj,  # вместо results
            "message": message,
        }
        return render(request, "view_search_result.html", context)
else:
    # postgresql
    def search(request):
        query = request.GET.get('q', '').strip()
        message = None
        results = []

        if query:
            models_config = loading_models_conf()

            for model_config in models_config:
                qs = model_config['queryset']
                fields = model_config['search_fields']
                snippet_func = model_config['snippet_text_func']

                # Строим Q-условие: OR по всем полям с icontains
                q_filter = Q()
                for field in fields:
                    q_filter |= Q(**{f"{field}__icontains": query})

                # Применяем фильтр к queryset
                filtered_qs = qs.filter(q_filter)

                # Для каждого найденного объекта генерируем сниппет
                for obj in filtered_qs:
                    text_for_snippet = snippet_func(obj)
                    obj.snippet = get_snippet(text_for_snippet, query)
                    # Для сохранения порядка добавим объект
                    results.append(obj)

            # Пагинация
            page_obj = pagination(request, results, settings.PAGINATE_BY)

        else:
            if 'q' in request.GET:
                message = 'Пожалуйста, введите запрос для поиска.'
            page_obj = None

        context = {
            "query": query,
            "page_obj": page_obj,
            "message": message,
        }
        return render(request, "view_search_result.html", context)


def event_list(request):
    events = Event.objects.all().values('title', 'start_time', 'end_time', 'description', 'color')
    event_data = [
        {
            'title': e['title'],
            'start': e['start_time'].isoformat(),
            'end': e['end_time'].isoformat(),
            'description': e['description'] or '',
            'color': e['color'],
        }
        for e in events
    ]
    return JsonResponse(event_data, safe=False)


def calendar_view(request):
    return render(request, 'calendar.html')
