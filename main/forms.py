from django.forms import ModelForm
from django import forms
from .models import NceaExam, NceaQUESTION, Specifics, NceaSecondaryQuestion, NceaUserDocument, NceaUserQuestions
import roman

def int_to_alpha(value):
    return chr(ord("a") + int(value) - 1)

class CreateNewDocument(forms.Form):
    name = forms.CharField(label="Name", max_length=200)
    standard = forms.IntegerField()
    year = forms.IntegerField()
    
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
            
            
