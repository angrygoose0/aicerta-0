from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import NceaExam, HelpMessage, NceaQUESTION, NceaSecondaryQuestion, NceaUserDocument, NceaUserQuestions, NceaScores, AssesmentSchedule
from .forms import CreateNewDocument, AnswerForm, CreateNewStandard, StandardForm, SupportForm
from django.forms import modelformset_factory
from django.forms.widgets import TextInput
from django.contrib.auth.decorators import login_required
from payment.models import Plan
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
import openai
import os
import re
from django.utils.safestring import mark_safe
import json
from .helpers import number_to_alphabet, alphabet_to_number, number_to_roman, roman_to_number
import datetime
import tiktoken
from .tasks import mark_document



# Create your views here.


def mark_text(txt, json_feedback):
    # Create a dictionary that maps each character in the text to its CSS classes
    classes_for_each_char = [set() for _ in range(len(txt))]

    # For each feedback item, mark the corresponding characters with the CSS class
    for feedback in json_feedback:
        # Check if feedback type is not "Achievement", "Merit", or "Excellence" and skip if so
        if feedback['type'] not in ["Achievement", "Merit", "Excellence"]:
            continue

        css_class = "bullet_point" + feedback['bullet_point'].replace("•","_")
        start_index = txt.index(feedback['answer'])
        end_index = start_index + len(feedback['answer'])
        for i in range(start_index, end_index):
            classes_for_each_char[i].add(css_class)

    # Construct the marked-up text
    marked_up_text = ""
    current_classes = set()
    for i, char in enumerate(txt):
        if classes_for_each_char[i] != current_classes:
            # Close the current span(s), if any
            if current_classes:
                marked_up_text += "</span>" * len(current_classes)
            # Open a new span(s) for the new classes
            for css_class in classes_for_each_char[i]:
                marked_up_text += f'<span class="{css_class}">'
            current_classes = classes_for_each_char[i]
        marked_up_text += char
    # Close the final span(s), if any
    if current_classes:
        marked_up_text += "</span>" * len(current_classes)

    return marked_up_text



@login_required(login_url="/login/")
def home(response):
    return render(response, "main/home.html")


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
def index(response, id):   
    doc = NceaUserDocument.objects.get(id=id)
    if doc.user == response.user:
        
        qs = NceaUserQuestions.objects.filter(document = doc)
        AnswerFormset = modelformset_factory(NceaUserQuestions, form=AnswerForm , extra = 0,)
        formset = AnswerFormset(queryset=qs,)

        form_groups = {}
        for form in formset:
            question = form.instance.question.QUESTION.QUESTION
            if question not in form_groups:
                form_groups[question] = []
            form_groups[question].append(form)
        context = {
            'name': doc.name,
            'id': doc.id, 
            'formset' : formset,
            'form_groups': form_groups,
            'standard' : doc.exam.standard,
            'year' : doc.exam.year
            }
            
            
        if response.method == "POST":
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


@login_required(login_url="login/")
def trigger_mark(response, id):
    credits = response.user.credits
    if credits < 5.00:
        pass
    doc = NceaUserDocument.objects.get(id=id)
    if doc.user == response.user:
        mark_document.delay(id)
        
        return HttpResponseRedirect("/app/")




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
            "id" : doc.id,
            "standard" : doc.exam.standard,
            "year" : doc.exam.year,
            "name" : doc.name,
            "userquestion_groups" : userquestion_groups,
            "QUESTIONS" : QUESTIONS,
        }
    
    
        return render(response, "main/marked.html", context)


@login_required(login_url="/login")
def create(response):
    initial_data = {
    'name': '',
    }
    if response.method == "POST":

        form = CreateNewDocument(response.POST, initial=initial_data, )

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
        form = CreateNewDocument(initial = initial_data)
        return render(response, "main/create.html", {"form":form})
    
@login_required(login_url="login/")
def settings(response):
    plans = Plan.objects.all()
    credits = response.user.credits
    context ={
        "plans":plans,
        "credits":credits,
        }
    
    
    return render(response, "main/settings.html", context)
"""
@login_required(login_url="login/")
def standard(response):
    initial_data = {
    'name': '',
    'standard': "",
    'year': "",
    }
    if response.method == "POST":

        form = CreateNewStandard(response.POST, initial=initial_data, )

        if form.is_valid():
            n = form.cleaned_data["name"]
            s = form.cleaned_data["standard"]
            y = form.cleaned_data["year"]
            
            exam = NceaExam(standard=s, year=y, exam_name=n, user=response.user)
            exam.save()
            
            QUESTION = NceaQUESTION(exam=exam, QUESTION=1)
            QUESTION.save()
            
            secondary = NceaSecondaryQuestion(QUESTION=QUESTION, primary=1, secondary=1)
            secondary.save()
            
            #return HttpResponseRedirect("/standard1")
            return HttpResponseRedirect("/app/standard1/%s" % exam.id)

    else:
        form = CreateNewStandard(initial = initial_data)
        return render(response, "main/standard.html", {"form":form})
"""
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
        
    context = {'form': form}
    return render(response, "main/support.html", context)
    
