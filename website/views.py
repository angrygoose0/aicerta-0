from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import ContactForm

# Create your views here.

def index(response):
    return render(response, "website/index.html")

def pricing(response):
    return render(response, "website/pricing.html")


def successView(response):
    return HttpResponse("Success! Thank you for your message.")

def contact(response):
    if response.method == "POST":
        form = ContactForm(response.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            from_email = form.cleaned_data["from_email"]
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, from_email, ["admin@aicerta.com"])
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            return redirect("success")
    else:
        form = ContactForm()
    return render(response, "website/contact.html",  {"form": form})

#sendgrid password: G4`P)3[qk[PGsd6$