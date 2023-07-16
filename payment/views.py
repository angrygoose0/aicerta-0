from django.shortcuts import render, redirect
from django.views import View
from .models import Product, ProductPrice
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import stripe
from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
YOUR_DOMAIN = 'http://127.0.0.1:8000'

# Create your views here.


@login_required(login_url="login/")
def landing(response):
    context = ""
    
    
    return render(response, "payment/checkout.html", )

def checkoutsession(response, price):
    if response.method == "POST":
        try:
            checkout_price = ProductPrice.objects.get(id=price)
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price': checkout_price.price_key,
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=YOUR_DOMAIN + '/success/',
                cancel_url=YOUR_DOMAIN + '/cancel/',
                automatic_tax={'enabled': True},
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
        return HttpResponseRedirect(checkout_session.url)




