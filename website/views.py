from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from .forms import ExamForm
from django.template.loader import render_to_string
# Create your views here.

def index(request):
    form = ExamForm()
    return render(request, "website/index.html", {"form":form})

def calculate(request):
    form = ExamForm(request.POST)
    if form.is_valid():
        result = form.cleaned_data['exams_per_month'] * 75
        return render(request, "partials/results.html", {"result":result})
    else:
        return HttpResponseBadRequest("Invalid form")

def pricing(response):
    return render(response, "website/pricing.html")


def successView(response):
    return HttpResponse("Success! Thank you for your message.")

def contact(response):

    return render(response, "website/contact.html",)

