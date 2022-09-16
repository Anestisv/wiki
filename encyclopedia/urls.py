from unicodedata import name
from django.urls import path

from . import views

urlpatterns = [
    path("wiki/", views.index, name="index"),
    path("wiki/<str:entry>", views.entrypage, name="entrypage"),
    path("wiki/newentry/", views.newentry, name="newentry"),
    path("wiki/random/", views.randompage, name="randompage"),
    path("wiki/edit/", views.edit, name="editpage"),
    path("wiki/edit/save/", views.save, name="save"),
    path("wiki/search/", views.search, name="search")
]
