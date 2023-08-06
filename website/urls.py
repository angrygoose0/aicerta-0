from django.urls import path
from .views import successView
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("pricing/", views.pricing, name="pricing"),
    path("success/", successView, name="success"),
    path("calculate/", views.calculate, name="calculate"),

]