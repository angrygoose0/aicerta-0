from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from .models import NceaExam, HelpMessage, NceaQUESTION, NceaSecondaryQuestion, NceaUserDocument, NceaUserQuestions, NceaScores, AssesmentSchedule, File, OCRImage
from .forms import CreateNewDocument, AnswerForm, CreateNewStandard, StandardForm, SupportForm, FileForm, OCRImageForm
from django.forms import modelformset_factory
from django.forms.widgets import TextInput
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from payment.models import ProductPrice
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
import math
import json
import base64

from .tasks import mark_document, prepare_document, test
from celery.result import AsyncResult



# Create your views here.



@login_required(login_url="/login/")
def home(response):

    return render(response, "main/home.html")
        
@login_required(login_url="/login/")
def prepare_mark(response, id):
    doc = NceaUserDocument.objects.get(id=id)
    if doc.user == response.user:
        task = prepare_document.delay(id)
        
        context ={
            "doc":doc,
            "task_id": task.id,
        }
        return render(response, "main/prepare_mark.html", context, status=202)
    else:
        return HttpResponseForbidden()
    
def check_task(response, task_id,):
    task = AsyncResult(task_id)
    user = response.user
    credits = user.credits
    credits_required = task.result
    if task.ready():
        
        doc_id = response.GET.get('doc_id')
        
        doc = NceaUserDocument.objects.get(id=doc_id)

        result = credits_required/100
        required = math.ceil(result)
        doc.credit_price = required
        doc.save()
        if doc.user == user:
            context ={
                'result': doc.credit_price,
                'credits': credits,
                'doc_id': doc_id
                }

            
            return render(response, "main/partials/task_completed.html", context)
        #return JsonResponse({'status': 'READY', 'result': task.result})
    else:
        return JsonResponse({'status': 'PENDING'})
    



@login_required(login_url="/login/")
def delete_ncea_document(response, id):
    try:
        ncea_document = NceaUserDocument.objects.get(id=id, user=response.user)
        ncea_document.delete()
        data = {'success': True}
    except NceaUserDocument.DoesNotExist:
        data = {'success': False}
    return JsonResponse(data)




@login_required(login_url="/login/")
def upload(response, id):
    
    if response.method == "POST":
        form = FileForm(response.POST, response.FILES)
        if form.is_valid():
            # Automatically set the user from the request
            file_instance = form.save(commit=False)
            file_instance.user = response.user
            file_instance.save()
            return HttpResponseRedirect("/app/%s/edit" % id)
    else:
        form = FileForm()
    
    context = {
        'form': form
    }
    return render(response, "main/upload.html", context)

@login_required(login_url="/login")
def create(response):
    
    form = CreateNewDocument(user=response.user)
        

    if response.method == "POST":

        form = CreateNewDocument(response.POST, user=response.user)

        if form.is_valid():
            n = form.cleaned_data["name"]
            exam = form.cleaned_data["exam"]

            
            QUESTIONS = NceaQUESTION.objects.filter(exam=exam)

        
            user_exam = NceaUserDocument(user=response.user, exam=exam, name=n, mark=0)
            user_exam.save()

            for QUESTION in QUESTIONS:
                secondaryquestions = NceaSecondaryQuestion.objects.filter(QUESTION=QUESTION,)

                for secondaryquestion in secondaryquestions:
                    nceauserexamquestion = NceaUserQuestions(document=user_exam, question=secondaryquestion, answer="")
                    nceauserexamquestion.save()

                scores = NceaScores(document=user_exam, QUESTION=QUESTION, score=0)
                scores.save()
                    
            return HttpResponseRedirect("/app/%s/edit" % user_exam.id)
            #return HttpResponse("hooray")
        else:
            print(form.errors)
            form = CreateNewDocument(user=response.user)
            print("lala")
            return render(response, "main/create.html", {"form":form})

    return render(response, "main/create.html", {"form":form})
        


@login_required(login_url="/login/")
def index(response, id):   
    doc = NceaUserDocument.objects.get(id=id)
    if doc.user == response.user:
        
        qs = NceaUserQuestions.objects.filter(document = doc)
        AnswerFormset = modelformset_factory(NceaUserQuestions, form=AnswerForm , extra = 0,)
        formset = AnswerFormset(queryset=qs,)
        
        OCRform = OCRImageForm()

        form_groups = {}
        for form in formset:
            question = form.instance.question.QUESTION.QUESTION
            if question not in form_groups:
                form_groups[question] = []
            form_groups[question].append(form)
            
        files = File.objects.filter(user=response.user)
        
        context = {
            "doc": doc,
            'formset' : formset,
            'form_groups': form_groups,
            'files': files,
            "ocrform": OCRform,
            }

        if response.method == "POST":
            print(response.POST)
            form = AnswerFormset(response.POST)
            if form.is_valid():
                form.save()

                # Rebuild formset with the latest queryset
                qs = NceaUserQuestions.objects.filter(document = doc)
                formset = AnswerFormset(queryset=qs)
                form_groups = {}
                for form in formset:
                    question = form.instance.question.QUESTION.QUESTION
                    if question not in form_groups:
                        form_groups[question] = []
                    form_groups[question].append(form)

                context['formset'] = formset
                context['form_groups'] = form_groups
                context['message'] = "Data Saved."
            else:
                print(form.errors)  
        if response.htmx:
            return render(response, "main/partials/forms.html", context)    
                
        return render(response, "main/index.html", context)
    return HttpResponseRedirect("/app/")


@login_required(login_url="/login/")
def ocrpdf(response, id, ocr):
    doc = NceaUserDocument.objects.get(id=id)
    ocrpdf = File.objects.get(id=ocr)
    
    context ={
            "doc": doc,
            "ocrpdf" : ocrpdf,
        }
    
    return render(response, "main/ocrpdf.html", context)

@login_required(login_url="/login/")
def file_to_doc(response, id, ocr):
    if response.method == "POST":
        doc = NceaUserDocument.objects.get(id=id)
        ocrpdf = File.objects.get(id=ocr)
        doc.file = ocrpdf
        doc.save()
        return HttpResponseRedirect("/app/%s/edit" % (id))

 



def save_image(request, id):
    if request.method == "POST":
        form = OCRImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            # Assuming that NceaUserDocument is imported and you want to link the image to a specific document.
            # Here, I assume 'id' is the ID of the NceaUserDocument.
            image_instance.document_id = id
            image_instance.save()
            # Return a JSON response if you want an AJAX-style response.
            # You can modify this to return whatever you wish.
            return HttpResponseRedirect("/app/%s/edit" % (id))
        else:
            print(form.errors)
            return JsonResponse({'status': 'error', 'message': 'There was an error saving the image.'})








@login_required(login_url="/login/")
def preview(response, id):
    doc = NceaUserDocument.objects.get(id=id)
    if doc.user == response.user:
        userquestions = NceaUserQuestions.objects.filter(document = doc)
        #get how many QUESTIONS there are
        QUESTIONS = NceaQUESTION.objects.filter(exam=doc.exam)
        # for each QUESTION, the system message will be the system in the NceaQUESTION
    
        userquestion_groups = {}
        for userquestion in userquestions:

            question = userquestion.question.QUESTION.QUESTION
            if question not in userquestion_groups:
                userquestion_groups[question] = []
            userquestion_groups[question].append(userquestion)

        context ={
            "doc": doc,
            "userquestion_groups" : userquestion_groups,
            "QUESTIONS" : QUESTIONS,
        }

        return render(response, "main/preview.html", context)

@login_required(login_url="login/")
def viewmarked(response, id):
    doc = NceaUserDocument.objects.get(id=id)
    if doc.user == response.user:
        userquestions = NceaUserQuestions.objects.filter(document = doc)
        #get how many QUESTIONS there are
        QUESTIONS = NceaQUESTION.objects.filter(exam=doc.exam)
        # for each QUESTION, the system message will be the system in the NceaQUESTION
    
        userquestion_groups = {}
        for userquestion in userquestions:
            score = NceaScores.objects.get(document=doc, QUESTION=userquestion.question.QUESTION)

            question = (userquestion.question.QUESTION.QUESTION, score.score, userquestion.question.QUESTION.system_html)
            if question not in userquestion_groups:
                userquestion_groups[question] = []
            userquestion_groups[question].append(userquestion)

        context ={
            "doc": doc,
            "userquestion_groups" : userquestion_groups,
            "QUESTIONS" : QUESTIONS,
        }
    
    
        return render(response, "main/marked.html", context)




@require_POST
@login_required(login_url="login/")
def trigger_mark(response, id):
    if response.method == "POST":

        doc = NceaUserDocument.objects.get(id=id)
        required_credits = doc.credit_price
        user = response.user
        credits = user.credits
        
        if doc.user != user:
            return HttpResponseForbidden()
                    
        if credits < required_credits:
            return HttpResponseForbidden()

        user_id = response.user.id
        mark_document.delay(id, user_id)
        #test.delay(id,user_id)

        
        user.credits -= required_credits
        user.save()
        
        
        return HttpResponseRedirect("/app/")
        







    
@login_required(login_url="login/")
def settings(response):
    
    productprice = ProductPrice.objects.all()    
    subscriptions = productprice.filter(type="subscription")
    
    monthly = subscriptions.filter(m_or_y="m")
    yearly = subscriptions.filter(m_or_y="y")

    products = productprice.filter(type="payment")
    credits = response.user.credits
    user = response.user
    context ={
        "products":products,
        "credits":credits,
        "user":user,
        "yearly":yearly,
        "monthly":monthly,
        }
    
    
    return render(response, "main/settings.html", context)

@login_required(login_url="login/")
def tempmark(response):
    return render(response, "main/tempmark.html")

@login_required(login_url="login/")
def support(response):
    
    if response.method == "POST":
        form = SupportForm(response.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = response.user
            message.date = timezone.now()
            message.save()
            
            return HttpResponseRedirect("/app/")
    else:
        form = SupportForm()
        
    context = {
        'form': form,
        }
    return render(response, "main/support.html", context)
    
