from django.urls import path

from . import views

urlpatterns = [
    path("<int:id>/edit", views.index, name="index"),
    path("<int:id>/view", views.viewmarked, name="viewmarked"),
    path("<int:id>/preview", views.preview, name="preview"),
    path("<int:id>/upload", views.upload, name="upload"),
    path("<int:id>/ocr/<int:ocr>", views.file_to_doc, name="file_to_doc"),
    path("", views.home, name="home"),
    path("create/", views.create, name="create"),
    path("<int:id>/delete/", views.delete_ncea_document, name="delete_ncea_document"),
    path("account/", views.settings_page, name="settings"),
    #path("standard/", views.standard, name="standard"),
    path("tempmark/", views.tempmark, name="tempmark"),
    path("support/", views.support, name="support"),
    path('<int:id>/trigger-mark', views.trigger_mark, name='trigger_mark'),
    path('<int:id>/prepare/', views.prepare_mark, name='prepare_mark'),
    path('check-task/<str:task_id>', views.check_task, name='check_task'),
    path('<int:id>/save_image', views.save_image, name='save_image'),
]