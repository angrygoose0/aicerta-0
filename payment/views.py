from django.shortcuts import render, redirect
from django.views import View
from .models import Product, ProductPrice
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import stripe
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.conf import settings
import json
from accounts.models import CustomUser


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

if settings.DEVELOPMENT_MODE == True:
    
    YOUR_DOMAIN = "http://127.0.0.1:8000"
else:
    YOUR_DOMAIN = "aicerta.com"



# Create your views here.


@login_required(login_url="login/")
def landing(response):
    context = ""
    
    
    return render(response, "payment/checkout.html", )

@login_required
def checkoutsession(response, price):
    if response.method == "POST":
        try:
            product_price = ProductPrice.objects.get(price_key=price)
            user = response.user

            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price':price,
                        'quantity':1,
                    },
                ],
                mode=product_price.type,
                success_url=YOUR_DOMAIN + '/app/account/',
                cancel_url=YOUR_DOMAIN + '/cancel/',
                automatic_tax={'enabled': True},
                client_reference_id=user.id,
                customer=user.stripe_customer_id
                
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
        return HttpResponseRedirect(checkout_session.url)
    
    
    
def success(response):
    return render(response, "payment/success.html", )

def cancel(response):
    return render(response, "payment/cancel.html", )

@csrf_exempt
def my_webhook_view(response):
    payload = response.body
    sig_header = response.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
    # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
    # Invalid signature
        return HttpResponse(status=400)
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("aaaaa")
        # Retrieve the session. If you require line items in the response, you may include them by expanding line_items.
        session = stripe.checkout.Session.retrieve(
            event['data']['object']['id'],
            expand=['line_items'],
        )
        print(session)
        
        price_key = session['line_items']['data'][0]['price']['id']
        user_id = session['client_reference_id']
        customer_id = session['customer']
        
        user = CustomUser.objects.get(id=user_id)
        product = ProductPrice.objects.get(price_key=price_key)
        
        user.stripe_customer_id = customer_id

        if product.type == "subscription":
            user.plan = product
            
        elif product.type == "payment":
            user.credits += product.credit #credit packages
        
        
        user.save()

    # Passed signature verification
    return HttpResponse(status=200)


def portalsession(response):
    if response.method == "POST":
        user = response.user
        try:
            portalSession = stripe.billing_portal.Session.create(
                customer=user.stripe_customer_id, #id
                return_url=YOUR_DOMAIN + '/app/',
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
        return redirect(portalSession.url, code=303)
    




