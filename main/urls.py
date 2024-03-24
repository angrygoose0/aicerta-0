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
    path("createclass/", views.createclass, name="createclass"),
    path("createassignment/", views.createassignment, name="createassignment"),
    path("classroom-join/", views.classroom_join, name="classroom_join"),
    path("<int:id>/delete/assignment", views.delete_assignment, name="delete_assignment"),
    path("account/", views.settings_page, name="settings"),
    path("standards/", views.standards, name="create_standard"),
    path("<int:id>/edit-standard/", views.edit_standard, name="edit_standard"),
    path("tempmark/", views.tempmark, name="tempmark"),
    path("support/", views.support, name="support"),
    path('<int:id>/trigger-mark', views.trigger_mark, name='trigger_mark'),
    path('<int:id>/prepare/', views.prepare_mark, name='prepare_mark'),
    path('check-task/<str:task_id>', views.check_task, name='check_task'),
    path('<int:id>/save_image', views.save_image, name='save_image'),
    path('protected_files/<int:file_id>/', views.serve_protected_file, name='serve_protected_file'),
    path('classroom/<int:id>', views.classroom, name="classroom"),
    path('assignment/<int:id>', views.new_assignment_doc, name="new_assignment_doc"),
    path("edit-assignment/<int:id>", views.edit_assignment, name="edit_assignment"),
    path("add-image/", views.add_image_to_question, name="add-image-to-question"),
    path("remove-image-from-question/<int:id>", views.remove_image_from_question, name="remove-image-from-question")
    
]