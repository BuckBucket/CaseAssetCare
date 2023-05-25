from .views import RedirectView, ShortenView, StatsView
from django.urls import path

urlpatterns = [
    path("shorten", ShortenView.as_view(), name='shorten-view'),
    path("<str:shortcode>", RedirectView.as_view(), name='redirect-view'),
    path("<str:shortcode>/stats", StatsView.as_view(), name='stats-view'),
]