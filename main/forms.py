from django.forms import ModelForm
from django import forms
from .models import NceaExam, Classroom, NceaQUESTION, NceaSecondaryQuestion, HelpMessage, NceaUserDocument, NceaUserQuestions, File, OCRImage
import roman
from django.db.models import Q

def int_to_alpha(value):
    return chr(ord("a") + int(value) - 1)


class CreateNewDocument(forms.Form):
    name = forms.CharField(label="Name", max_length=200)
    exam = forms.ModelChoiceField(queryset=NceaExam.objects.none())  # start with an empty queryset

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Query for exams the user can see
            self.fields['exam'].queryset = NceaExam.objects.filter(Q(is_public=True) | Q(users=user))

class CreateClass(ModelForm):
    class Meta:
        model = Classroom
        fields = ['name']
        

    
    
class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ['name', 'file']
        
        
class OCRImageForm(ModelForm):
    class Meta:
        model = OCRImage
        fields = ['image']

    
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