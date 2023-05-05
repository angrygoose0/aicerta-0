from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import NceaDocument, NceaQuestions, NceaOne, NceaTwo
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
        ncea_document = NceaDocument.objects.get(id=id, user=response.user)
        ncea_document.delete()
        data = {'success': True}
    except NceaDocument.DoesNotExist:
        data = {'success': False}
    return JsonResponse(data)




@login_required(login_url="login/")
def index(response, id):
    doc = NceaDocument.objects.get(id=id)
    
    if doc in response.user.nceadocument.all():
        
        qs = NceaQuestions.objects.filter(document = doc)

        AnswerFormset = modelformset_factory(NceaQuestions, form=AnswerForm , extra = 0,)

        form = AnswerFormset(queryset=qs,)
        context = {
            'id': doc.id, 
            'form': form
        }
        if response.method == "POST":

            form = AnswerFormset(response.POST or None, queryset=qs)
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
    doc = NceaDocument.objects.get(id=id)
    if doc in response.user.nceadocument.all():
        qs = NceaQuestions.objects.filter(document = doc)
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
            
            one = NceaOne.objects.get(standard=s, year=y)
            two = NceaTwo.objects.filter(exam=one)
            
            if one:
                t = NceaDocument(exam=one, name=n, mark=0)
                t.save()
                response.user.nceadocument.add(t)
                
                for x in range(1,4):
                    bss = two.filter(QUESTION=x)
                    
                    for bs in bss:
                        
                        a = bss.filter(primary = bs.primary)
                        for b in a:
                            t.nceaquestions_set.create(QUESTION=x, primary=bs.primary, secondary=b.secondary, text="", mark=0)
        
        return HttpResponseRedirect("/app/%s" % t.id)

    else:
        form = CreateNewDocument(initial = initial_data)
        return render(response, "main/create.html", {"form":form})
    
@login_required(login_url="login/")
def settings(response):
    plans = Plan.objects.all()
    return render(response, "main/settings.html", {"plans": plans})