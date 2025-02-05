from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from .models import NceaExam, NceaUserImages, HelpMessage, NceaQUESTION, NceaSecondaryQuestion, NceaUserDocument, NceaUserQuestions, NceaScores, File, OCRImage, Criteria, BulletPoint, Quoted, Assignment
from accounts.models import CustomUser
from .forms import CreateAssignment, UserImageForm, CreateNewDocument, AnswerForm, CreateNewStandard, SupportForm, FileForm, OCRImageForm, CreateClass, Classroom, ClassroomJoin
from django.forms import modelformset_factory
from django.forms.widgets import TextInput
from django.forms.models import inlineformset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from payment.models import ProductPrice
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
import re
import boto3
from storages.backends.s3boto3 import S3Boto3Storage
from .helpers import number_to_alphabet, alphabet_to_number, number_to_roman, roman_to_number
import math
from datetime import datetime
import json
import base64
from django.conf import settings
from google.cloud import vision
from collections import defaultdict
from mathpix.mathpix import MathPix






mathpix = MathPix(app_id=settings.MATHPIX_APP_ID, app_key=settings.MATHPIX_APP_KEY)




from .tasks import mark_document, prepare_document, ocr_task
from celery.result import AsyncResult

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
channel_layer = get_channel_layer()






# Create your views here.



@login_required(login_url="/login/")
def home(response):
    user = response.user
    
    return render(response, "main/home.html")
        
@login_required(login_url="/login/")
def prepare_mark(response, id):
    doc = NceaUserDocument.objects.get(id=id)
    if doc.assignment:
        if doc.assignment.teacher == response.user:
            task = prepare_document.delay(id)
            
            context ={
                "doc":doc,
                "task_id": task.id,
            }
            return render(response, "main/prepare_mark.html", context, status=202)
        
    return HttpResponseForbidden()

@login_required(login_url="login/")        
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
        if doc.assignment.teacher == user:
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
def delete_assignment(response, id):
    try:
        assignment = Assignment.objects.get(id=id)
        if assignment.teacher == response.user:
            assignment.delete()
            data = {'success': True}
    except assignment.DoesNotExist:
        data = {'success': False}
    return JsonResponse(data)


@login_required(login_url="/login/")
def classroom_join(response):
    if response.method == 'POST':
        form = ClassroomJoin(response.POST)
        if form.is_valid():
            classroom = Classroom.objects.get(secret_code=form.cleaned_data["code"])
            classroom.students.add(response.user)

            classroom.save()
            return HttpResponseRedirect("/app/classroom/%s" % classroom.id)
    return



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
    if response.user.student:
        return HttpResponseForbidden
    
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
                secondaryquestions = NceaSecondaryQuestion.objects.filter(QUESTION=QUESTION)
                
                criterias = Criteria.objects.filter(
                    secondary_questions__in=secondaryquestions
                ).prefetch_related('secondary_questions')
                
                for criteria in criterias:
                    bulletpoint = BulletPoint(criteria=criteria, document=user_exam)
                    bulletpoint.save()                   

                for secondaryquestion in secondaryquestions:
                    nceauserexamquestion = NceaUserQuestions(document=user_exam, question=secondaryquestion, answer="")
                    nceauserexamquestion.save()

                scores = NceaScores(document=user_exam, QUESTION=QUESTION, score=0)
                scores.save()
                    
            return HttpResponseRedirect("/app/%s/edit" % user_exam.id)
        else:
            print(form.errors)
            form = CreateNewDocument(user=response.user)
            print("lala")
            return render(response, "main/create.html", {"form":form})

    return render(response, "main/create.html", {"form":form})


@login_required(login_url="/login/")
def createclass(response):
    
    if response.user.student:
        return HttpResponseForbidden

    if response.method == "POST":
        form = CreateClass(response.POST)
        if form.is_valid():
            # Automatically set the user from the request
            class_instance = form.save(commit=False)
            class_instance.teacher = response.user
            class_instance.save()
            return HttpResponseRedirect("/app/")
    else:
        form = CreateClass()
    
    context = {
        'form': form
    }
    return render(response, "main/createclass.html", context)

@login_required(login_url="/login/")
def createassignment(response):
    
    if response.user.student:
        return HttpResponseForbidden
    
    if response.method == "POST":
        form = CreateAssignment(response.POST)
        if form.is_valid():
            # Automatically set the user from the request
            assignment_instance = form.save(commit=False)
            assignment_instance.teacher = response.user
            assignment_instance.status = 0
            assignment_instance.save()
            return HttpResponseRedirect("/app/")
    else:
        form = CreateAssignment(user=response.user)
    
    context = {
        'form': form
    }
    return render(response, "main/createassignment.html", context)

@login_required(login_url="/login/")
def standards(response):
    user = response.user
    if user.student:
        return HttpResponseForbidden
    
    standards = NceaExam.objects.filter(users=user)
    
    context = {
        'standards' : standards,
        
    }
        
    return render(response, "main/standards.html", context)

@login_required(login_url="/login/")
def edit_standard(request, id):
    exam = get_object_or_404(NceaExam, pk=id)
    

    return HttpResponseBadRequest()




@login_required(login_url="/login/")
def preview(response, id):
    doc = NceaUserDocument.objects.get(id=id)
    if doc.user == response.user or doc.assignment.teacher == response.user:
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
    
    return HttpResponseForbidden()




def generate_signed_url(file_path):
    # Initialize S3 client
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )

        # Generate the presigned URL
        url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': file_path,
            },
            ExpiresIn=3600
        )
        return url
    except:
        return HttpResponseBadRequest()




@login_required(login_url="/login/")
def index(response, id):   
    doc = NceaUserDocument.objects.get(id=id)
    if doc.user == response.user:

        qs = NceaUserQuestions.objects.filter(document = doc)
        AnswerFormset = modelformset_factory(NceaUserQuestions, form=AnswerForm , extra = 0,)
        formset = AnswerFormset(queryset=qs,)
        
        OCRform = OCRImageForm()
        user_image_form = UserImageForm() 

        form_groups = {}
        for form in formset:
            question = form.instance.question.QUESTION.QUESTION
            if question not in form_groups:
                form_groups[question] = []
            form_groups[question].append(form)
            
        files = File.objects.filter(user=response.user)
        development_mode = settings.DEVELOPMENT_MODE
        signed_url = ""
        if doc.file:
            if development_mode == False:
                signed_url = generate_signed_url(doc.file.file.name)
                
        
        context = {
            "development_mode" : development_mode,
            "doc": doc,
            'formset' : formset,
            'form_groups': form_groups,
            'files': files,
            "ocrform": OCRform,
            "signed_url" : signed_url,
            'user_image_form' : user_image_form,
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
            else:
                print(form.errors)  
        if response.htmx:
            return render(response, "main/partials/forms.html", context)    
        doc.save()
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


    

def detect_document(image_model):
    """Detects document features in an image."""
    from google.cloud import vision

    client = vision.ImageAnnotatorClient.from_service_account_info(settings.GOOGLE_CREDENTIALS)
        
    with image_model.image.open("rb") as image_file:
            content = image_file.read()
            

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    
    if response.text_annotations:
        return response.text_annotations[0].description


    elif response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )

@login_required(login_url="login/")
def serve_protected_file(request, file_id):
    file_instance = File.objects.get(pk=file_id)
    
    # Ensure the user requesting the file is the owner
    if request.user != file_instance.user:
        return HttpResponseForbidden

    # Generate a signed URL
    s3_storage = S3Boto3Storage()
    url = s3_storage.url(file_instance.file.name, expire=300)  # URL will be valid for 5 minutes
    print(url)

    return HttpResponseRedirect(url)

@login_required(login_url="login/")
def save_image(request, id):
    if request.method == "POST":
        form = OCRImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            image_instance.document_id = id
            image_instance.save()

            crop_method = request.POST.get('crop_method')
            
            if crop_method == 'text':
                text = detect_document(image_instance)
                image_instance.text = text.replace('\n', ' ')  # Add this line to remove line breaks

            elif crop_method == 'math':
                ocr = mathpix.process_image(image=image_instance)
                text = ocr.latex
                image_instance.text = text.replace('\n', ' ')  # Add this line to remove line breaks

            image_instance.save()


            # Return a JSON response with the OCRed result and the cropped image URL
            return JsonResponse({
                'status': 'success',
                'ocr_result': image_instance.text,
                'cropped_image_url': image_instance.image.url,
            })
        else:
            print(form.errors)
            return JsonResponse({'status': 'error', 'message': 'There was an error saving the image.'})



@login_required(login_url="/login/")
def preview(response, id):
    doc = NceaUserDocument.objects.get(id=id)
    if doc.user == response.user or doc.assignment.teacher == response.user:
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

    if doc.marked_before == 1:
        if (doc.assignment is not None and doc.assignment.teacher == response.user) or doc.user == response.user:
            userquestions = NceaUserQuestions.objects.filter(document = doc)
            
            secondary_questions = NceaSecondaryQuestion.objects.filter(nceauserquestions__in=userquestions)
            
            criteria_qs = Criteria.objects.filter(
                secondary_questions__in=secondary_questions
            ).prefetch_related('secondary_questions')

            QUESTIONS = NceaQUESTION.objects.filter(exam=doc.exam)
            userquestion_groups = {}
            
            bullet_points = BulletPoint.objects.filter(document=doc, criteria__in=criteria_qs)
            
            data = []
            for bullet_point in bullet_points:
                quotes = Quoted.objects.filter(bullet_point=bullet_point)
                for quote in quotes:
                    userquestion = userquestions.get(question=quote.secondary_question)
                    quote_data = {
                        "bulletpoint_id": bullet_point.id,
                        "quote_id": quote.id,
                        "quote_question_id": userquestion.id,
                        "quote": quote.quote
                    }
                    data.append(quote_data)
                
            

            for userquestion in userquestions:
                score = NceaScores.objects.get(document=doc, QUESTION=userquestion.question.QUESTION)
                criteria_list = [criteria for criteria in criteria_qs if criteria.secondary_questions.last() == userquestion.question]
                bullet_points = BulletPoint.objects.filter(criteria__in=criteria_list, document=doc)
                
                bullet_point_groups = {}
                for bullet_point in bullet_points:
                    bullet_point_type=""
                    if bullet_point.criteria:
                        if bullet_point.criteria.type == "a":
                            bullet_point_type="Achieved:"
                        elif bullet_point.criteria.type == "m":
                            bullet_point_type="Merit:"
                        elif bullet_point.criteria.type == "e":
                            bullet_point_type="Excellence:"
                        
                    if bullet_point_type not in bullet_point_groups:
                        bullet_point_groups[bullet_point_type] = []
                    bullet_point_groups[bullet_point_type].append(bullet_point)
                    
                    
                userquestion_with_bullet = (userquestion, bullet_point_groups)


                question = (userquestion.question.QUESTION.QUESTION, score.score)
                if question not in userquestion_groups:
                    userquestion_groups[question] = []
                userquestion_groups[question].append(userquestion_with_bullet)
                


            context ={
                "doc": doc,
                "userquestion_groups" : userquestion_groups,
                "QUESTIONS" : QUESTIONS,
                "quotes_data" : data,
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
        
        if doc.assignment.teacher != user:
            return HttpResponseForbidden()
                    
        if credits < required_credits:
            return HttpResponseForbidden()
        
        if doc.status != 'submitted':
            return HttpResponseForbidden()

        user_id = response.user.id
        mark_document.delay(id, user_id)

        user.credits -= required_credits
        user.save()

        return HttpResponseRedirect("/app/")
        




    
@login_required(login_url="login/")
def settings_page(response):
    
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

@login_required(login_url="login/")
def classroom(response, id):
    classroom = Classroom.objects.get(id=id)
    
    assignments = Assignment.objects.filter(classroom=classroom)
    people = classroom.students.all()
    
    context = {
        'classroom' : classroom,
        'assignments' : assignments,
        'people' : people,
        }
    return render(response, "main/classroom.html", context)

def send_socket_message(room_name, message):
    async_to_sync(channel_layer.group_send)(
        room_name,  # Group name
        {   
            'type': 'send.message',
            'message' : message
        }
    )
    
def teacher_student_group(teacher_id, student_id, document_id):
    return f"doc_{document_id}_teacher_{teacher_id}_student_{student_id}"



@login_required(login_url="/login")
def new_assignment_doc(response, id):
    if response.method == "POST":
        assignment = Assignment.objects.get(id=id)
        if response.user in assignment.classroom.students.all():
            #one more if to check if the student has already made an assignment doc.
            if response.user.tester == False:
                
                assessment = NceaUserDocument.objects.filter(user=response.user, assignment=assignment).first()         
                if assessment:
                    return HttpResponseRedirect("/app/%s/edit" % assessment.id)
                
            
            exam = assignment.exam
            QUESTIONS = NceaQUESTION.objects.filter(exam=exam)
        
            user = str(response.user)
            name = "%s %s" % (assignment.name, user.split('@')[0])
            
            user_exam = NceaUserDocument(user=response.user, exam=exam, name=name, mark=0, assignment=assignment, status='pending')
            user_exam.save()

            for QUESTION in QUESTIONS:
                secondaryquestions = NceaSecondaryQuestion.objects.filter(QUESTION=QUESTION)
                
                criterias = Criteria.objects.filter(
                    secondary_questions__in=secondaryquestions
                ).prefetch_related('secondary_questions')
                
                for criteria in criterias:
                    bulletpoint = BulletPoint(criteria=criteria, document=user_exam)
                    bulletpoint.save()                   

                for secondaryquestion in secondaryquestions:
                    nceauserexamquestion = NceaUserQuestions(document=user_exam, question=secondaryquestion, answer="")
                    nceauserexamquestion.save()

                scores = NceaScores(document=user_exam, QUESTION=QUESTION, score=0)
                scores.save()
                
        

            return HttpResponseRedirect("/app/%s/edit" % user_exam.pk)

@login_required(login_url="/login")
def edit_assignment(response, id):
    user = response.user
    assignment = Assignment.objects.get(id=id)
    
    if user == assignment.teacher:
        
        userdocuments = NceaUserDocument.objects.filter(assignment=assignment)
        
        context = {
            'userdocuments' : userdocuments,
            'assignment' : assignment,
        }
        
        return render(response, "main/edit_assignment.html", context)
    return HttpResponseRedirect("/app/")

@login_required(login_url="/login")
def add_image_to_question(response):
    print("added_image")
    if response.method == "POST":
        print(1)
        form = UserImageForm(response.POST, response.FILES)
        if form.is_valid():
            print(2)
            user_question_id = form.cleaned_data['user_question_id']
            user_question = NceaUserQuestions.objects.get(id=user_question_id)
            if response.user == user_question.document.user:
                image = form.cleaned_data['image']
                new_image = NceaUserImages(image=image, user_question=user_question)
                new_image.save()
                return HttpResponseRedirect("/app/%s/edit" % user_question.document.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"- {field}: {error}")
        return HttpResponseForbidden()


@login_required(login_url="/login")
def remove_image_from_question(response, id):
    if response.method == "POST":
        user_image = NceaUserImages.objects.get(id=id)
        if user_image.user_question.document.user == response.user:
            user_image.delete()
            return HttpResponseRedirect("/app/%s/edit" % user_image.user_question.document.pk)
        return HttpResponseForbidden()
    
    
    