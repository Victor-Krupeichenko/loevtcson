from django import template
from loevtcson.models import Chapter, About, News, FooterInfo

register = template.Library()


@register.inclusion_tag("_inc/all_chapters.html")
def show_all_chapters():
    chapters = Chapter.objects.filter(show=True)
    about_chapter = True if len(About.objects.filter(show=True)) else False
    return {
        "chapters": chapters,
        'about_chapter': about_chapter
    }


@register.inclusion_tag("_inc/news.html")
def show_news():
    news = News.objects.filter(show=True).order_by('-created_at')[:3]
    news_count = True if len(news) > 1 else False
    return {
        "news": news,
        "news_count": news_count
    }


@register.inclusion_tag("_inc/footer.html")
def show_footer_url():
    urls = FooterInfo.objects.filter(show=True)
    return {
        "urls": urls
    }
