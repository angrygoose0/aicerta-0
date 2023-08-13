from django.urls import path

from . import views


urlpatterns = [
    path('create-checkout-session/<str:price>', views.checkoutsession, name="create-checkout-session"),
    path('checkout/', views.landing, name='landing'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path("webhook/stripe", views.my_webhook_view, name="stripe-webhook"),
    path('create-portal-session/', views.portalsession, name="create-portal-session"),
]