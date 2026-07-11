from django.urls import path
from .views import AboutView, ChapterDetailView, NewsDetailView, NewsListView, search, event_list, calendar_view

urlpatterns = [
    path("", AboutView.as_view(), name="about"),
    path("about/<str:slug>", AboutView.as_view(), name="about"),
    path("chapter/<slug:slug>/", ChapterDetailView.as_view(), name="chapter"),
    path("news/<slug:slug>/", NewsDetailView.as_view(), name="news"),
    path("all-news/", NewsListView.as_view(), name="all-news"),
    path("search/", search, name="search", ),
    path('api/events/', event_list, name='event_list'),
    path('api/events/', event_list, name='event_list'),
    path('calendar/', calendar_view, name='calendar_view'),
]
