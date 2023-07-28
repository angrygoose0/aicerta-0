from django.shortcuts import render, redirect
from django.views import View
from .models import Product, ProductPrice
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import stripe
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
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
    
def success(response):
    return render(response, "payment/success.html", )

def cancel(response):
    return render(response, "payment/cancel.html", )

@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
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
        # Retrieve the session. If you require line items in the response, you may include them by expanding line_items.
        session = stripe.checkout.Session.retrieve(
            event['data']['object']['id'],
            expand=['line_items'],
        )
        print(session)
        
        product_id =""

        line_items = session.line_items
        # Fulfill the purchase...
        fulfill_order(line_items)

    # Passed signature verification
    return HttpResponse(status=200)

def fulfill_order(line_items):
    # TODO: fill me in
    print("Fulfilling order")




