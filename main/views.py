from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import NceaExam, NceaQUESTION, Specifics, NceaSecondaryQuestion, NceaUserDocument, NceaUserQuestions
from .forms import CreateNewDocument, AnswerForm
from django.forms import modelformset_factory
from django.forms.widgets import TextInput
from.mark import Marking
from django.contrib.auth.decorators import login_required
from payment.models import Plan
from django.shortcuts import render, redirect
from django.contrib import messages

# Create your views here.

@login_required(login_url="login/")
def home(response):
    return render(response, "main/home.html")


@login_required(login_url="login/")
def delete_ncea_document(response, id):
    try:
        ncea_document = NceaUserDocument.objects.get(id=id, user=response.user)
        ncea_document.delete()
        data = {'success': True}
    except NceaUserDocument.DoesNotExist:
        data = {'success': False}
    return JsonResponse(data)




@login_required(login_url="login/")
def index(response, id):
    doc = NceaUserDocument.objects.get(id=id)
    
    if doc in response.user.nceauserdocument.all():
        
        UserQuestions = NceaUserQuestions.objects.filter(document = doc)

        AnswerFormset = modelformset_factory(NceaUserQuestions, form=AnswerForm , extra = 0,)

        form = AnswerFormset(queryset=UserQuestions,)
        context = {
            'id': doc.id, 
            'form': form
        }
        if response.method == "POST":

            form = AnswerFormset(response.POST or None, queryset=UserQuestions)
            if form.is_valid():
                
                form.save()
                print("saved")
                context['message'] = "Data Saved."
            else:
                print(form.errors)
            
        
        if response.htmx:
            print("htmx")
            return render(response, "main/partials/forms.html", context)    
            
        return render(response, "main/index.html", context)
    
        
    return HttpResponseRedirect("/")




@login_required(login_url="login/")    
def marked(response, id):
    doc = NceaUserDocument.objects.get(id=id)
    if doc in response.user.nceauserdocument.all():
        qs = NceaUserQuestions.objects.filter(document = doc)
        context ={
            "id" : doc.id,
            "qs" : qs
        }
        
    
    
        
        #Marking.mark(id)
        return render(response, "main/marked.html", context)

        
    
        
@login_required(login_url="login")
def create(response):
    initial_data = {
    'name': '',
    'standard': "",
    'year': "",
    }
    if response.method == "POST":

        form = CreateNewDocument(response.POST, initial=initial_data, )
        
        if form.is_valid():
            
            
            n = form.cleaned_data["name"]
            s = form.cleaned_data["standard"]  
            y = form.cleaned_data["year"]
            
            exam = NceaExam.objects.get(standard=s, year=y)
            QUESTIONS = NceaQUESTION.objects.filter(exam=exam)
            
            if exam:
                user_exam = NceaUserDocument(exam=exam, name=n, mark=0)
                user_exam.save()
                response.user.nceauserdocument.add(user_exam)
                
                for QUESTION in QUESTIONS:
                    SecondaryQuestions = NceaSecondaryQuestion.objects.filter(QUESTION=QUESTION, )

                    for SecondaryQuestion in SecondaryQuestions:
                        nceauserexamquestion = NceaUserQuestions(document=user_exam, question=SecondaryQuestion, answer="")
                        nceauserexamquestion.save()
                    
                    return HttpResponseRedirect("/app/%s" % user_exam.id)

    else:
        form = CreateNewDocument(initial = initial_data)
        return render(response, "main/create.html", {"form":form})
    
@login_required(login_url="login/")
def settings(response):
    plans = Plan.objects.all()
    return render(response, "main/settings.html", {"plans": plans})