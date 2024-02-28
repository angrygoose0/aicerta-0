from celery import shared_task, current_task
from main.models import Assignment, NceaUserDocument, NceaQUESTION, NceaUserQuestions, NceaSecondaryQuestion, NceaScores, Criteria, Quoted, BulletPoint
from accounts.models import CustomUser
from .helpers import number_to_alphabet, alphabet_to_number, number_to_roman, roman_to_number
from django.utils.safestring import mark_safe
import json
from django.db.models import Max, OuterRef, Subquery
import openai
import os
import re
import tiktoken
from django.conf import settings
import logging
import time

from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from mathpix.mathpix import MathPix
mathpix = MathPix(app_id="aicerta_dba064_cf8251", app_key="1edb871fea6133e08b718918bdfa84093d4bdeade502e3e0eb461d600ad9def7")

from openai import OpenAI

client = OpenAI(
    organization='org-oYF2mFI0qL1ksfDhutt5vPEi',
    api_key=settings.AI_API
    
)

system = """
    You are tasked with marking exam answers.

    You will be given one or multiple criteria, and one or multiple user answers.

    For each criteria, your job is to figure out if the one or multiple answers fulfil the specific criteria.

    You are also given a model answer for each question, this is a guideline that human markers use to ensure accurate marking. Keep in mind, one answer might be trying to fulfil multiple criteria, ones you may or may not be given, and so the evidence may be more detailed than needed.
    Just focus on if the specific criteria you are on is fulfilled by the user answers you are given.

    When processing the input text, please pay special attention to patterns that match the LaTeX notation for inline and display equations, to ensure accurate processing of mathematical content.

    Pay attention to AND/OR in the criteria.
    AND means both conditions must be met. For example, if the criteria say "A AND B," then both A and B must be true for the condition to be satisfied.

    OR means only one condition needs to be met. If the criteria say "A OR B," then either A or B (or both) can be true for the condition to be satisfied.

    An implied answer doesn't count. Criteria must be explicitly met—suggestions or implications are considered incorrect. Clarity and directness are key.

    Responses should be in JSON like this:
    {"criteria":[{"no":<criteria number>,"confidence":<confidence number from 0 to 100>,"explanation":"<explanation for the confidence number>","quotes":{"<question identifier>":"<direct quote from the USER answer>"}}]}
    
    - Criteria Number (no): The number of the criteria being evaluated.
    - Confidence Number (confidence): A number from 0 to 100 representing how confident you are that the answer fulfills the criteria. A score of 0 means you are completely confident the answer is wrong, and a score of 100 means you are 100% confident the answer is correct.
    - Explanation (explanation): A detailed explanation of why you gave the confidence number you did.
    - Quotes (quotes): A dictionary where each key is a question identifier and each value is a direct quote from the USER answer that fulfills the criteria. This direct quote must be accurate(punctuation and spaces)

    Here is an example of a possible user input:
    Model Answer:
    (a)(i):
    The capital of New Zealand is Auckland.
    (b)(i):
    Water freezes at 0 degrees Celsius at standard atmospheric pressure.
    (b)(ii):
    Water boils at 100 degrees Celsius at standard atmospheric pressure.
    (c)(i):
    \begin{aligned} &\frac{5}{5}\times\frac{2}{5}=\frac{10}{25} \\ &\frac{2}{5} \\ \end{aligned}

    User Answer:
    (a)(i):
    The capital of New Zealand is Tauranga.
    (b)(i):
    At standard atmospheric pressure, water freezes at 0°C.
    (b)(ii): 
    At standard atmosphericpressure, water boils at 90°C.
    (c)(i): \(\frac{5}{5}\cdot\frac{2}{5}=\frac{10}{25}\)

    Criteria:
    1: States that the capital of New Zealand is Auckland.
    2: States that water boils at 100 degrees celsius, AND freezes at 0 degrees celsius at standard atmospheric pressure.
    3: Gets the answer to \begin{aligned} &\frac{5}{5}\times\frac{2}{5}=\frac{10}{25} \\ &\frac{2}{5} \\ \end{aligned} , AND simplifies


    Here is an example of the JSON output:
    {"criteria":[{"no":1,"confidence":0,"explanation":"The response was completely incorrect, as the capital of New Zealand is NOT Tauranga.","quotes":{"(a)(i)":"The capital of New Zealand is Tauranga."}},{"no":2,"confidence":40,"explanation":" The response is partially correct because it mentions water freezes at 0°C but omits that water boils at 100°C at standard atmospheric pressure..","quotes":{"(b)(i)":"At standard pressure, water freezes at 0°C.","(b)(ii)":"At standard pressure, water boils at 90°C"}},{"no":3,"confidence":40,"explanation":"The response gets the answer to \\begin{aligned} &\\frac{5}{5}\\times\\frac{2}{5}=\\frac{10}{25} \\ &\\frac{2}{5} \\ \\end{aligned}, but doesnt simplify","quotes":{"(c)(i)":"\\(\\frac{5}{5}\\cdot\\frac{2}{5}=\\frac{10}{25}\\)."}}]}
"""









logger = logging.getLogger(__name__)


def backslash(text):
    processed_text = text.replace("\\", "\\\\")
    return processed_text



from collections import defaultdict

openai.api_key = settings.AI_API

encoding = tiktoken.encoding_for_model("gpt-4-0125-preview")



def interpolate_color(color1, color2, factor):
    """ Interpolates between two colors based on the factor. """
    r = color1[0] + (color2[0] - color1[0]) * factor
    g = color1[1] + (color2[1] - color1[1]) * factor
    b = color1[2] + (color2[2] - color1[2]) * factor
    return int(r), int(g), int(b)

def get_pastel_color(value):
    """ Returns the pastel color for the given value. """
    pastel_red = (255, 128, 128)
    pastel_yellow = (255, 255, 128)
    pastel_green = (128, 255, 128)

    if value <= 50:
        # Interpolate between pastel red and pastel yellow
        return interpolate_color(pastel_red, pastel_yellow, value / 50.0)
    else:
        # Interpolate between pastel yellow and pastel green
        return interpolate_color(pastel_yellow, pastel_green, (value - 50) / 50.0)

# Test the function with different values
def pastel_color(bullet_point): 
    r, g, b = get_pastel_color(bullet_point.confidence)
    bullet_point.r = r
    bullet_point.g = g
    bullet_point.b = b
    bullet_point.save()

@shared_task
def prepare_document(id):
    try:
        text= ""
        text += system
        
        document = NceaUserDocument.objects.get(id=id)
        user_questions = NceaUserQuestions.objects.filter(document=document)
        secondary_questions = NceaSecondaryQuestion.objects.filter(nceauserquestions__in=user_questions)
        criteria_qs = Criteria.objects.filter(
            secondary_questions__in=secondary_questions
        ).prefetch_related('secondary_questions')
        
        for user_question in user_questions:
            text += "%s \n" % (user_question.answer)
        
        for secondary_question in secondary_questions:
            text += "%s \n" % (secondary_question.evidence)
            
        for criteria in criteria_qs:
            text += "%s \n" % (criteria.text)
            
        tokens = len(encoding.encode(text))   
        tokens = tokens * 2
            
        return tokens
    except Exception as e:
        print(e)
        return e
    
    
    
@shared_task(bind=True)
def ocr_task(self, image_instance):
    channel_layer = get_channel_layer()
    try:
        # OCR Process (e.g., using pytesseract or any OCR tool)
        async_to_sync(channel_layer.send)(
            websocket_channel_name,
            {
                "type": "task_message",
                "message": "OCR started",
                "status": "started",
            }
        )
        
        # Simulating OCR task
        time.sleep(5)  # Assume OCR takes 5 seconds, replace this with actual OCR process
        
        ocr = mathpix.process_image(image=image_instance)
            
        print(ocr.latex)

        
    except Exception as e:
        async_to_sync(channel_layer.send)(
            websocket_channel_name,
            {
                "type": "task_message",
                "message": str(e),
                "status": "failed",
            }
        )


def websocket(room_name, task_id, doc, progress, error):
    async_to_sync(channel_layer.group_send)(
        room_name,  # Group name
        {   
            'type': 'notification.message',
            'task_id': task_id,
            'user_document_name':doc.name,
            'exam_name':doc.exam.exam_name,
            'progress': progress, #0-100%
            'doc_id':doc.id,
            'error':error
        }
    )
    
def alert(room_name, message, alert, icon):
    async_to_sync(channel_layer.group_send)(
        room_name,  # Group name
        {   
            'type': 'alert.message',
            'message': message,
            'alert': alert,
            'icon': icon,
        }
    )
    




@shared_task
def mark_document(id, user_id): 
    
    try:   
        document = NceaUserDocument.objects.get(id=id)
        
        user = CustomUser.objects.get(id=user_id)

        required_credits = document.credit_price
        credits = user.credits
        
        room_name = f"user_{user_id}"
        task_id = current_task.request.id
        
        if document.assignment and document.assignment.teacher != user:
            error_message="Unauthorized attempt"
            websocket(room_name, task_id, document, 0, error_message)
            return error_message

        if credits < required_credits:
            error_message="Not enough credits"
            websocket(room_name, task_id, document, 0, error_message)
            return error_message
        
    except Exception as error_message:
        print(error_message)
        return str(error_message)

    try:
        websocket(room_name, task_id, document, 0, None)
        
        counter=0
        tokens = 0 

        user_questions = NceaUserQuestions.objects.filter(document=document)
        secondary_questions = NceaSecondaryQuestion.objects.filter(nceauserquestions__in=user_questions)

        # Step 1: Annotate and Order Criteria Queryset
        last_secondary_question_subquery = NceaSecondaryQuestion.objects.filter(
            nceacriteria=OuterRef('pk')
        ).order_by('-QUESTION', '-primary', '-secondary').values('id')[:1]

        criteria_qs = Criteria.objects.filter(
            secondary_questions__in=secondary_questions
        ).annotate(
            last_secondary_question_id=Subquery(last_secondary_question_subquery)
        ).order_by('last_secondary_question_id').prefetch_related('secondary_questions')

        bullet_points = BulletPoint.objects.filter(document=document, criteria__in=criteria_qs)
        
        if document.marked_before  == 1 :
            quoted_qs = Quoted.objects.filter(bullet_point__in=bullet_points)
            quoted_qs.delete()

        x = 0
        for bullet_point in bullet_points:
            x += 1
            bullet_point.no = x
            bullet_point.save()  

        # 2. Create a dictionary to hold the groups.
        groups = defaultdict(list)

        # 3. For each Criteria object, add it to the appropriate group in the dictionary.
        for criteria in criteria_qs:
            # Get the set of NceaSecondaryQuestion IDs for this Criteria object.
            question_ids = {question.id for question in criteria.secondary_questions.all()}
            # Add the Criteria object to the group.
            groups[frozenset(question_ids)].append(criteria)
            
        for question_ids, criteria_list in groups.items():

            messages = []
            
            # 1. Create a set of all NceaSecondaryQuestion IDs related to the first Criteria object in the list.
            common_question_ids = {question.id for question in criteria_list[0].secondary_questions.all()}
            
            # 2. For each of the other Criteria objects in the list, intersect the set of common IDs with the set of IDs related to that Criteria object.
            for criteria in criteria_list[1:]:
                question_ids = {question.id for question in criteria.secondary_questions.all()}
                common_question_ids &= question_ids
            
            # 3. Now common_question_ids contains the IDs of NceaSecondaryQuestion objects that are related to all Criteria objects in the list.
            # Retrieve those NceaSecondaryQuestion objects.
            common_questions = NceaSecondaryQuestion.objects.filter(id__in=common_question_ids)

            if any(criteria.image == 1 for criteria in criteria_list):
                y=0
                for criteria in criteria_list:
                    bullet_point = bullet_points.filter(criteria=criteria)
                    
                    for bullet in bullet_point:
                    
                        bullet.confidence = 100
                        bullet.explanation = "images as answers aren't supported, so the response has been marked correct as a placeholder."
                        pastel_color(bullet)
                        bullet.save()
                    
                        for question in common_questions:
                            user_question = user_questions.get(question=question)
                            
                            quote = Quoted(bullet_point=bullet, secondary_question=question, quote=user_question.answer)
                            quote.save()
            else:
                system_message = {"role":"system", "content": 
                    r"%s" % (system)}
                
                messages.append(system_message)   
                message = "Model Answer: \n"
            
                # 4. Now you can loop through common_questions and do whatever you want with each one.
                for question in common_questions:
                    primary = number_to_alphabet(question.primary)
                    secondary = number_to_roman(question.secondary)
                    message += "(%s)(%s): \n" % (primary, secondary)
                    message += "%s \n \n" % (question.evidence)
                    
                message += "User Answer: \n"
                for question in common_questions:
                    userquestion = user_questions.get(question=question, document=document)
                    primary = number_to_alphabet(question.primary)
                    secondary = number_to_roman(question.secondary)
                    message += "(%s)(%s): \n" % (primary, secondary)
                    message += "%s \n \n" % (userquestion.answer)
                
                index=0
                message += "Criteria: \n"
                for index, criteria in enumerate(criteria_list):
                    index += 1
                    message += "%s: %s \n" % (index, criteria.text)
                    criteria.order = index
                    criteria.save()
                    
                user_message = {"role":"user", "content":message}
                messages.append(user_message)
                print(messages)
                

                temperature=0
                res = client.chat.completions.create(
                    model="gpt-4-0125-preview",
                    response_format={"type":"json_object"},
                    messages=messages,
                    temperature=temperature
                )


                marks = res.choices[0].message.content
                tokens += res.usage.total_tokens
                processed_marks = backslash(marks)
                data = json.loads(processed_marks)
                

                for criterion_data in data['criteria']:
                    order = criterion_data['no']
                    confidence = criterion_data['confidence']
                    explanation = criterion_data['explanation']
                    quotes = criterion_data['quotes']

                    criteria = next((c for c in criteria_list if c.order == order), None)
                    if criteria is not None:
                        bullet_point = bullet_points.filter(criteria=criteria)
                        for bullet in bullet_point:  
                            bullet.confidence = confidence
                            bullet.explanation = explanation
                            pastel_color(bullet)
                            bullet.save()
                            
                            for key, value in quotes.items():
                                match = re.match(r"\((.*?)\)\((.*?)\)", key)
                                if match:
                                    alphabet, roman = match.groups()
                                    primary = alphabet_to_number(alphabet)
                                    secondary = roman_to_number(roman)
                                    
                                    secondary_question = common_questions.get(primary=primary, secondary=secondary)  
                                    Quoted.objects.create(secondary_question=secondary_question, bullet_point=bullet, quote=value)
                                    
        QUESTIONS = NceaQUESTION.objects.filter(exam=document.exam)
        
        
        document_mark = 0
        for QUESTION in QUESTIONS:
            total_a=0
            total_m=0
            total_e=0
            minimum_confidence=80
            second = secondary_questions.filter(QUESTION=QUESTION)
            
            criterias = Criteria.objects.filter(
                secondary_questions__in=second
            )
            
            for criteria in criterias:
                bulletpoints = BulletPoint.objects.filter(document=document, criteria=criteria)
                for bulletpoint in bulletpoints:
    
                    if bulletpoint.confidence >= minimum_confidence:
                        if criteria.type == "a":
                            total_a += 1
                        elif criteria.type == "m":
                            total_m += 1
                        elif criteria.type == "e":
                            total_e += 1
                            
            conditions = [
                (8, 'e', QUESTION.e8),
                (7, 'e', QUESTION.e7),
                (6, 'm', QUESTION.m6),
                (5, 'm', QUESTION.m5),
                (4, 'a', QUESTION.a4),
                (3, 'a', QUESTION.a3),
                (2, 'a', QUESTION.n2),
                (1, 'a', QUESTION.n1),
                (0, 'a', QUESTION.n0),
            ]
            
            score = 0
            total_values = {'e': total_e, 'm': total_m, 'a': total_a}
            for s, var, condition in conditions:
                if total_values[var] >= condition:
                    score = s
                    break
                
            ncea_score = NceaScores.objects.get(document=document, QUESTION=QUESTION)
            ncea_score.score = score
            ncea_score.save()
            
            document_mark += ncea_score.score
            
        document.mark = document_mark
        document.marked_before = 1
        document.save()
        
        websocket(room_name, task_id, document, 100, None)
    except Exception as error_message:
        print(error_message)
        websocket(room_name, task_id, document, 0, error_message)

        return str(error_message)
   
channel_layer = get_channel_layer()

def send_socket_message(room_name, message):
    async_to_sync(channel_layer.group_send)(
        room_name,  # Group name
        {   
            'type': 'send.message',
            'message': json.dumps(message)  # Convert the dictionary to a JSON string
        }
    )
    
@shared_task
def set_assignment_ended(assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    assignment.status = 2
    assignment.save()

    #NceaUserDocument.objects.filter(assignment=assignment).update()
    
    users = CustomUser.objects.filter(nceadocument__assignment=assignment).distinct()
    
    for user in users:
        doc = NceaUserDocument.objects.get(user=user, assignment=assignment)
        doc.status = 'submitted'
        message = f"<p><strong>Time's Up for Assignment: {assignment.name}</strong> - Please note that your document <strong>\"{doc.name}\"</strong> for the assignment <strong>\"{assignment.name}\"</strong> has reached the deadline. <hr>Access to editing this document is now disabled.</p>"
        
        alert(f"user_{user.pk}", message, "danger", "exclamation-triangle-fill")
        
        doc.save()
        
        message = {
            'message_type': 'update_status',
            'status': 'submitted',
            'document_id': f'{doc.pk}',
            'assignment_id': f'{doc.assignment.id}'
        }

        send_socket_message(f"doc_{doc.pk}_teacher_{doc.assignment.teacher.id}_student_{user.pk}", message)
        

@receiver(post_save, sender=Assignment)
def schedule_assignment_update(sender, instance, **kwargs):
    if instance.ends_at and instance.status == 1:
        delay = (instance.ends_at - timezone.now()).total_seconds()
        if delay > 0:
            set_assignment_ended.apply_async((instance.id,), countdown=delay)
            


    
    
    


