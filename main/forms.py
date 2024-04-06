from django.forms import ModelForm, inlineformset_factory
from django import forms
from .models import NceaExam, NceaUserImages, Classroom, NceaQUESTION, NceaSecondaryQuestion, HelpMessage, NceaUserDocument, NceaUserQuestions, File, OCRImage, Assignment
import roman
from django.db.models import Q
import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone

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
        
class CreateAssignment(ModelForm):
    class Meta:
        model = Assignment
        fields = ['name', 'exam', 'description', 'classroom', 'starts_at', 'ends_at', 'strict']
        widgets = {
            'ends_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'starts_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),  # Added widget for starts_at
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Query for exams the user can see
            self.fields['exam'].queryset = NceaExam.objects.filter(Q(is_public=True) | Q(users=user))
            self.fields['classroom'].queryset = Classroom.objects.filter(Q(teacher=user))

        # Set default value for ends_at field to now
        self.fields['ends_at'].initial = timezone.now()
        self.fields['starts_at'].initial = timezone.now()

    def clean_starts_at(self):
        starts_at = self.cleaned_data.get('starts_at')
        now = timezone.now()  # Use the same timezone as your 'starts_at' field

        # Check if 'starts_at' is in the past
        if starts_at and starts_at <= now:
            raise ValidationError("The start date and time must be in the future.")

        return starts_at

    def clean_ends_at(self):
        ends_at = self.cleaned_data.get('ends_at')
        now = timezone.now()  # Use the same timezone as your 'ends_at' field

        # Check if 'ends_at' is in the past
        if ends_at and ends_at < now:
            raise ValidationError("The end date and time cannot be in the past.")

        return ends_at
class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ['name', 'file']
        
        
class OCRImageForm(ModelForm):
    class Meta:
        model = OCRImage
        fields = ['image']
        
class UserImageForm(ModelForm):
    user_question_id = forms.IntegerField(
        widget=forms.HiddenInput(),
    )
    
    class Meta:
        model = NceaUserImages
        fields = ['image',]

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
        thequestion = self.instance.question.thequestion
        primary_alpha = int_to_alpha(primary)
        secondary_roman = roman.toRoman(secondary).lower()
        self.fields['answer'].label = (
            f"""
            ({primary_alpha})({secondary_roman}):
            {thequestion}
            """
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

class ClassroomJoin(forms.Form):
    code = forms.CharField(label="Join Code", max_length=10)
    
    

