from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
# Create your views here.

def index(response):
    return render(response, "website/index.html")

def pricing(response):
    return render(response, "website/pricing.html")


def successView(response):
    return HttpResponse("Success! Thank you for your message.")

def contact(response):

    return render(response, "website/contact.html",)

#sendgrid password: G4`P)3[qk[PGsd6$