from django.urls import path

from . import views


urlpatterns = [
    path('create-checkout-session/<int:price>', views.checkoutsession, name="create-checkout-session"),
    path('checkout/', views.landing, name='landing'),
]