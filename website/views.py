from django.shortcuts import render

# Create your views here.

def index(response):
    return render(response, "website/index.html")

def pricing(response):
    return render(response, "website/pricing.html")

