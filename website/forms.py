from django import forms

class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    
class ExamForm(forms.Form):
    exams_per_month = forms.IntegerField(label='How many exams do you mark per month?')