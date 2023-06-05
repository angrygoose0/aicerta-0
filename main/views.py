from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import NceaExam, NceaQUESTION, Specifics, NceaSecondaryQuestion, NceaUserDocument, NceaUserQuestions
from .forms import CreateNewDocument, AnswerForm
from django.forms import modelformset_factory
from django.forms.widgets import TextInput
from django.contrib.auth.decorators import login_required
from payment.models import Plan
from django.shortcuts import render, redirect
from django.contrib import messages
import openai
import os

openai.api_key = os.getenv('AI_API')

# Create your views here.
def number_to_alphabet(number):
    if 1 <= number <= 26:
        return chr(number + 96)  # Convert number to lowercase alphabet
    else:
        return None  # Return None for numbers outside the range 1-26
def number_to_roman(number):
    roman_numerals = {
        1: "i",
        4: "iv",
        5: "v",
        9: "ix",
        10: "x",
        40: "xl",
        50: "l",
        90: "xc",
        100: "c",
        400: "cd",
        500: "d",
        900: "cm",
        1000: "m"
    }

    result = ""
    for value, numeral in sorted(roman_numerals.items(), reverse=True):
        while number >= value:
            result += numeral
            number -= value

    return result

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
            'form_groups': form_groups}
            
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
            print("htmx")
            return render(response, "main/partials/forms.html", context)    
                
        return render(response, "main/index.html", context)
    
        
    return HttpResponseRedirect("/")



@login_required(login_url="/login/")    
def marked(response, id):
    doc = NceaUserDocument.objects.get(id=id)
    if doc.user == response.user:
        userquestions = NceaUserQuestions.objects.filter(document = doc)
        #get how many QUESTIONS there are
        QUESTIONS = NceaQUESTION.objects.filter(exam=doc.exam)
        # for each QUESTION, the system message will be the system in the NceaQUESTION
        start_system = """
        You are an AI NCEA exam marking tool.
        Assesment Schedule:
        """
        end_system = """
        Use this assesment schedule to mark NCEA Questions.
        Use the model answers as a guideline.
        A model answer of {img} means that the question is in the form of a diagram or a table which is not supported.
        Every bullet point correct is a point, if an answer answers the bullet point correctly, then it is a point.
        If an answer doesnt answer the question, or is random, mark it as incorrect.

        Give your mark in this format:
        Achieved: _, Merit: _, Excellence: _
        """
        for QUESTION in QUESTIONS:
            secondary_questions = NceaSecondaryQuestion.objects.filter(QUESTION=QUESTION)
            messages = []
            system_message = {"role":"system", "content": 
                """ %s
                %s
                %s
                        """ % (start_system, QUESTION.system, end_system)}
            messages.append(system_message)
            specifics = Specifics.objects.filter(nceaQUESTION=QUESTION).order_by('order')
            if specifics.exists():
                for specific in specifics:
                    specific_message = {"role":specific.type, "content":specific.text}
                    messages.append(specific_message)
            useranswer = ""
            for secondary_question in secondary_questions:
                userquestion = userquestions.get(question=secondary_question)
                primary = number_to_alphabet(secondary_question.primary)
                secondary = number_to_roman(secondary_question.secondary)
                useranswer += "(%s)(%s)\n" % (primary, secondary)
                useranswer += "%s\n" % (userquestion.answer)
                useranswer += "\n"
                
                
            user_message = {"role":"user", "content":useranswer}
            messages.append(user_message)
            
            #res = openai.ChatCompletion.create(
            #model="gpt-3.5-turbo",
            #messages=messages
            #)
            #print(res["choices"][0]["message"]["content"])
            
                    
                        
        #and then to ensure the answer is spitted out by openai properly, we need a template, so it will have a template as well.
            
        # and then for specifics, the order is after the first two have been done and adds extra templates to ensure the answer given is accurate
        # now for each user question, "(primary)(secondary):{nextline} the answer"
        # and then the assistant should give out the points
        #which we will extract and then calculate the overall score.
        
    #this is done for each QUESTION.
        

        context ={
            "id" : doc.id,
            "name" : doc.name,
            "userquestions" : userquestions,
            "QUESTIONS" : QUESTIONS,
        }
    
        return render(response, "main/marked.html", context)

def tempmark(response, id):
        doc = NceaUserDocument.objects.get(id=id)
        if doc.user == response.user:
            userquestions = NceaUserQuestions.objects.filter(document = doc)
    
            context ={
                    "id" : doc.id,
                    "name" : doc.name
                }
            return render(response, "main/tempmark.html", context)
            
            
        
@login_required(login_url="/login")
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
            
        
            user_exam = NceaUserDocument(user=response.user, exam=exam, name=n, mark=0)
            user_exam.save()
                
            for QUESTION in QUESTIONS:
                secondaryquestions = NceaSecondaryQuestion.objects.filter(QUESTION=QUESTION,)

                for secondaryquestion in secondaryquestions:
                    nceauserexamquestion = NceaUserQuestions(document=user_exam, question=secondaryquestion, answer="")
                    nceauserexamquestion.save()
                    
            return HttpResponseRedirect("/app/%s" % user_exam.id)
            #return HttpResponse("hooray")

    else:
        form = CreateNewDocument(initial = initial_data)
        return render(response, "main/create.html", {"form":form})
    
@login_required(login_url="login/")
def settings(response):
    plans = Plan.objects.all()
    return render(response, "main/settings.html", {"plans": plans})