from django.urls import path

from . import views
from.views import trigger_mark

urlpatterns = [
    path("<int:id>/edit", views.index, name="index"),
    path("<int:id>/view", views.viewmarked, name="viewmarked"),
    path("", views.home, name="home"),
    path("create/", views.create, name="create"),
    path("<int:id>/delete/", views.delete_ncea_document, name="delete_ncea_document"),
    path("account/", views.settings, name="settings"),
    #path("standard/", views.standard, name="standard"),
    path("tempmark/", views.tempmark, name="tempmark"),
    path("support/", views.support, name="support"),
    path('<int:id>/mark', trigger_mark, name='trigger_mark'),
]