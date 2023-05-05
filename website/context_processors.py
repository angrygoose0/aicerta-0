from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from .forms import ContactForm

def contact_forms(response):
    if response.method == "POST":
        form = ContactForm(response.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            from_email = form.cleaned_data["from_email"]
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, from_email, ["admin@example.com"])
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            return {'form': form, 'success': True}
    else:
        form = ContactForm()
    return {'contact_form': form}
