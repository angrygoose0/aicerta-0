from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import NceaExam, NceaQUESTION, NceaSecondaryQuestion, NceaUserDocument, NceaUserQuestions, NceaScores, AssesmentSchedule
from .forms import CreateNewDocument, AnswerForm
from django.forms import modelformset_factory
from django.forms.widgets import TextInput
from django.contrib.auth.decorators import login_required
from payment.models import Plan
from django.shortcuts import render, redirect
from django.contrib import messages
import openai
import os
import re
from django.utils.safestring import mark_safe
import json
from .helpers import number_to_alphabet, alphabet_to_number, number_to_roman, roman_to_number


openai.api_key = os.getenv('AI_API')

# Create your views here.


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
        You are tasked with marking NCEA Questions based on a provided assessment schedule and model answers. Each question's response should be evaluated on the following criteria:

        1. Every bullet point in the answer corresponds to a point in the assessment schedule. If an answer correctly addresses a bullet point from the schedule, it receives a point.
        2. If an answer does not answer the question or provides a random response, it should be marked as incorrect.
        3. An answer containing a diagram or a table represented as {img} should be automatically marked as incorrect since these types of content are not supported in the current context.

        Your goal is to determine the number of Achievement, Merit, and Excellence marks for each question. If no marks of a certain type are awarded for a question, assign "0" to that mark type. 

        For each question, provide feedback. The feedback should include the type of mark (Achievement, Merit, or Excellence), the relevant bullet point from the assessment schedule that the answer addressed correctly, and a quote from the user's answer that correctly addressed the bullet point.

        The output should be in JSON format and structured as follows:

        {"questions":[{"question":"(a)(i)","feedback":[{"type":"(Achievement/Merit/Excellence)","bullet_point":"•(1,2,5)(the number of the bullet point that the user's answer addresses.)","mention":"(quote from user's answer that addressed the bullet point)"}],"achievement":"(number of Achievement marks)","merit":"(number of Merit marks)","excellence":"(number of Excellence marks)"}]}

        Note: The number of questions in the 'questions' array will vary based on the number of questions being assessed. Similarly, the number of feedback items for each question will depend on the number of bullet points in the assessment schedule for that question.

        Assesment Schedule:
        
        """
        
        
        counter = 1
        document_mark = 0
        for QUESTION in QUESTIONS:
            ass = ""
            ass_html = '<li class="list-group-item">'
            schedules = AssesmentSchedule.objects.filter(QUESTION=QUESTION)

            for schedule in schedules:
                if schedule.type == "n":
                    parts = schedule.text.split(':', 1)
                    bold_part = parts[0].strip()
                    rest = parts[1].strip() if len(parts) > 1 else ''
                    ass += "%s \n \n" % (schedule.text.strip())
                    # Use <p> and <br> to keep line breaks in HTML
                    rest_html = '<br>'.join(rest.split('\n'))
                    ass_html += mark_safe(f"<b>{bold_part}:</b><p>{rest_html}</p>")
                else:
                    if schedule.type in ["a", "m", "e"]:
                        type_dict = {"a": "Achievement", "m": "Merit", "e": "Excellence"}
                        ass += f"{type_dict[schedule.type]}: \n"
                        ass_html += mark_safe(f"<b>{type_dict[schedule.type]}:</b>")

                    bullet_points = schedule.text.split('•')[1:]
                            
                    for point in bullet_points:
                        formatted_point = f"•{counter} {point.strip()}"
                        ass += "%s \n" % formatted_point.strip()

                            # Add a unique id for each bullet point in ass_html
                        bullet_points_html = f'<li class="bullet_point_{counter}">{point.strip()}</li>'
                        ass_html += mark_safe(f"<ul>{bullet_points_html}</ul>")
                                
                        counter += 1

                    ass_html += mark_safe("<br>")
                            
            ass_html += '</li>'
            QUESTION.system = ass
            QUESTION.system_html = ass_html
            QUESTION.save()


                    
            messages = []
            system_message = {"role":"system", "content": 
                """ 
                %s
                
                %s
                """ % (start_system, ass)}
            messages.append(system_message)
            
            secondary_questions = NceaSecondaryQuestion.objects.filter(QUESTION=QUESTION)
            
            
            useranswer = ""
            for secondary_question in secondary_questions:
                userquestion = userquestions.get(question=secondary_question)
                primary = number_to_alphabet(secondary_question.primary)
                secondary = number_to_roman(secondary_question.secondary)
                useranswer += "(%s)(%s):\n" % (primary, secondary)
                useranswer += "%s\n" % (userquestion.answer)
                useranswer += "\n"
                
                
            user_message = {"role":"user", "content":useranswer}
            messages.append(user_message)

            
            res = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages
            )
            
            
            marks = res["choices"][0]["message"]["content"]
            print(marks)
            
            data = json.loads(marks)
            
            total_a = 0
            total_m = 0
            total_e = 0
            for i, question in enumerate(data['questions']):
                sec = question['question']
                match = re.search(r"\((.*?)\)\((.*?)\)", sec)
                if match is not None:
                    primary = match.group(1)
                    secondary=match.group(2)
                    primary= alphabet_to_number(primary)
                    secondary = roman_to_number(secondary)
                else:
                    primary = 0
                    secondary = 0
                
                sec_question = secondary_questions.get(primary=primary, secondary=secondary)
                userquestion = userquestions.get(question=sec_question)

                # Increment counters
                total_a += int(question['achievement'])
                total_m += int(question['merit'])
                total_e += int(question['excellence'])

                userquestion.achievement = int(question['achievement'])
                userquestion.merit = int(question['merit'])
                userquestion.excellence = int(question['excellence'])
                userquestion.save()
            
            if total_e >= QUESTION.e8:
                score = 8
            elif total_e >= QUESTION.e7:
                score = 7
            elif total_m >= QUESTION.m6:
                score = 6
            elif total_m >= QUESTION.m5:
                score = 5
            elif total_a >= QUESTION.a4:
                score = 4
            elif total_a >= QUESTION.a3:
                score = 3
            elif total_a >= QUESTION.n2:
                score = 2
            elif total_a >= QUESTION.n1:
                score = 1
            elif total_a >= QUESTION.n0:
                score = 0
            else:
                score = 0
            
            ncea_score = NceaScores.objects.get(document=doc, QUESTION=QUESTION)
            
            ncea_score.score = score
            ncea_score.save()

            document_mark += score
                        
        doc.mark = document_mark
        doc.save()
        
        
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
                
                scores = NceaScores(document=user_exam, QUESTION=QUESTION, score=0)
                scores.save()
                    
            return HttpResponseRedirect("/app/%s" % user_exam.id)
            #return HttpResponse("hooray")

    else:
        form = CreateNewDocument(initial = initial_data)
        return render(response, "main/create.html", {"form":form})
    
@login_required(login_url="login/")
def settings(response):
    plans = Plan.objects.all()
    return render(response, "main/settings.html", {"plans": plans})