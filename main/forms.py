from django.forms import ModelForm
from django import forms
from .models import NceaQuestions
import roman

def int_to_alpha(value):
    return chr(ord("a") + value - 1) + ")"

class CreateNewDocument(forms.Form):
    name = forms.CharField(label="Name", max_length=200)
    standard = forms.IntegerField()
    year = forms.IntegerField()
    
class AnswerForm(ModelForm):

    class Meta:
        model = NceaQuestions
        fields = ['text','mark']
        
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
            'mark': forms.TextInput(attrs={'disabled':True})
            }
        labels = {
            'text': 'Answer:',
            'mark': "Mark:"
        }
        required = {
            'text': False,
            'mark': False,
        }
        

    
    def __init__(self, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)
        
        QUESTION = self.instance.QUESTION
        primary = self.instance.primary
        secondary = self.instance.secondary
        
        primary_alpha = int_to_alpha(primary)
        secondary_roman = roman.toRoman(secondary)

        
        self.fields['text'].label = (
            f" {QUESTION}, {primary_alpha}, {secondary_roman}"
        )
        self.fields['text'].required = False  # Set required to False for the field
        self.fields['mark'].required = False
        
        if self.instance.mark == 0 :
            self.fields['mark'].widget = forms.HiddenInput()
            
            
