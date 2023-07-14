from django.forms import ModelForm
from django import forms
from .models import NceaExam, NceaQUESTION, NceaSecondaryQuestion, HelpMessage, NceaUserDocument, NceaUserQuestions, AssesmentSchedule
import roman

def int_to_alpha(value):
    return chr(ord("a") + int(value) - 1)

class CreateNewDocument(forms.Form):
    name = forms.CharField(label="Name", max_length=200)
    exam = forms.ModelChoiceField(queryset=NceaExam.objects.all())
    
class AnswerForm(ModelForm):
    class Meta:
        model = NceaUserQuestions
        fields = ['answer']
        widgets = {
            'answer': forms.Textarea(attrs={'rows': 4}),
            }
        labels = {
            'Answer': 'Answer:',
        }
        required = {
            'Answer': False,
        }
    def __init__(self, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)
        primary =self.instance.question.primary
        secondary =self.instance.question.secondary
        primary_alpha = int_to_alpha(primary)
        secondary_roman = roman.toRoman(secondary).lower()
        self.fields['answer'].label = (
            f"({primary_alpha})({secondary_roman}):"
        )
        self.fields['answer'].required = False  # Set required to False for the field

class StandardForm(ModelForm):
    class Meta:
        model = AssesmentSchedule
        fields = ['text', 'type']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
            'type': forms.Select(),
            }
        labels = {
            'text': 'Text:',
            'type': 'Type:',
        }
        
class SupportForm(forms.ModelForm):
    class Meta:
        model = HelpMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'message': 'Message:'
        }

class CreateNewStandard(forms.Form):
    name = forms.CharField(label="Name", max_length=200)
    standard = forms.IntegerField()
    year = forms.IntegerField()