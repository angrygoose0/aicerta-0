from django.urls import path

from . import views

urlpatterns = [
    path("<int:id>/", views.index, name="index"),
    path("", views.home, name="home"),
    path("create/", views.create, name="create"),
    path("<int:id>/mark/", views.marked, name="mark"),
    path("<int:id>/delete/", views.delete_ncea_document, name="delete_ncea_document"),
    path("settings/", views.settings, name="settings"),
    path("standard/", views.standard, name="standard"),
    path("standard1/<int:id>", views.standard1, name="standard1"),
    path("tempmark/", views.tempmark, name="tempmark")
]