from django.urls import path

from . views import home_view, search_view


urlpatterns = [
    path('', home_view, name="home_page"),
    path('search/', search_view, name="search")
]