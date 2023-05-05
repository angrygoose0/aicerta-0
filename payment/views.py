from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
import stripe
from django.http import JsonResponse
from django.conf import settings
import djstripe
from djstripe.models import Customer, Subscription

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

# Create your views here.





def student_payment(response):
    return render(response, "payment/student.html")


#def checkout(response):