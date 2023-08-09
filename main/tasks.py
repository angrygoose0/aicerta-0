from celery import shared_task
from .models import NceaUserDocument, NceaQUESTION, NceaUserQuestions, NceaSecondaryQuestion, AssesmentSchedule, NceaScores
from .helpers import number_to_alphabet, alphabet_to_number, number_to_roman, roman_to_number
from django.utils.safestring import mark_safe
import json
import openai
import os
import re
import tiktoken
from django.conf import settings

start_system = """
You are tasked with marking NCEA Questions based on a provided assessment schedule and model answers. Each question's response should be evaluated on the following criteria:

1. Every bullet point in the answer corresponds to a point in the assessment schedule. If an answer correctly addresses a bullet point from the schedule, it receives a point.
2. If an answer does not answer the question or provides a random response, it should be marked as incorrect.
3. An answer containing a diagram or a table represented as {img} should be automatically marked as correct since these types of content are not supported in the current context.

Your goal is to determine the number of Achievement, Merit, and Excellence marks for each question. If no marks of a certain type are awarded for a question, assign "0" to that mark type. 

For each question, provide feedback. The feedback should include the type of mark (Achievement, Merit, or Excellence), the relevant bullet point from the assessment schedule that the answer addressed correctly, and a quote from the user's answer that correctly addressed the bullet point.

The output should be in JSON format and structured as follows:

{"questions":[{"question":"(a)(i)","feedback":[{"type":"(Achievement/Merit/Excellence)","bullet_point":"•(1,2,5) (the number of the bullet point that the user's answer addresses.)","answer":"(quoted from the snippet of the user's answer that addresses the bullet point.( whitespace, punctuation, and capital letters has to be accurate))"}],"achievement":"(number of Achievement marks)","merit":"(number of Merit marks)","excellence":"(number of Excellence marks)"}]}

Note: The number of questions in the 'questions' array will vary based on the number of questions being assessed. Similarly, the number of feedback items for each question will depend on the number of bullet points in the assessment schedule for that question.

Assesment Schedule:      

"""


openai.api_key = settings.AI_API

encoding = tiktoken.encoding_for_model("gpt-4")



@shared_task
def prepare_document(id):
    try:
        doc = NceaUserDocument.objects.get(id=id)
        userquestions = NceaUserQuestions.objects.filter(document = doc)
        QUESTIONS = NceaQUESTION.objects.filter(exam=doc.exam)
        counter = 1
        tokens = 0
        
        for QUESTION in QUESTIONS:
            secondary_questions = NceaSecondaryQuestion.objects.filter(QUESTION=QUESTION)
            
            
            ass = ""
            ass_html = '<li class="list-group-item">'
            schedules = AssesmentSchedule.objects.filter(QUESTION=QUESTION)

            for schedule in schedules:
                if schedule.type == "n":
                    primary = number_to_alphabet(schedule.secondary_question.primary)
                    secondary = number_to_roman(schedule.secondary_question.secondary)
                    ass += "(%s)(%s):\n" % (primary, secondary)
                    ass += "Model Answer:\n"
                    ass += "%s\n\n" % (schedule.text.strip())
                    
                    ass_html += mark_safe("<b>(%s)(%s):</b>\n" % (primary, secondary))
                    ass_html += mark_safe("<p>Model Answer:</p>\n")
                    ass_html += mark_safe("<p>%s</p>\n\n" % (schedule.text.strip()))
                    
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
            
        
            useranswer = ""
            for secondary_question in secondary_questions:
                userquestion = userquestions.get(question=secondary_question)
                primary = number_to_alphabet(secondary_question.primary)
                secondary = number_to_roman(secondary_question.secondary)
                useranswer += "(%s)(%s):\n" % (primary, secondary)
                useranswer += "%s\n" % (userquestion.answer)
                useranswer += "\n"
                
            
            text = start_system + "\n" + ass + "\n" + useranswer
            tokens += len(encoding.encode(text))
            
        return tokens

    except Exception as e:
        print(e)
        return e

@shared_task
def mark_document(id): 
    try:
        doc = NceaUserDocument.objects.get(id=id)
        userquestions = NceaUserQuestions.objects.filter(document = doc)
        QUESTIONS = NceaQUESTION.objects.filter(exam=doc.exam)
        counter = 1
        document_mark = 0
        tokens = 0
        
        for QUESTION in QUESTIONS:
            secondary_questions = NceaSecondaryQuestion.objects.filter(QUESTION=QUESTION)
            
            messages = []
            system_message = {"role":"system", "content": 
                """ 
                %s
                
                %s
                """ % (start_system, QUESTION.system)}
            messages.append(system_message)
                    
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
                messages=messages,
                temperature=0
            )
            
            marks = res["choices"][0]["message"]["content"]
            tokens += res["usage"]["total_tokens"]
            data = json.loads(marks)
            
            total_a = 0
            total_m = 0
            total_e = 0
            for i, question in enumerate(data['questions']):
                sec = question['question']
                feedbacks = question['feedback']
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
                txt = userquestion.answer
                classes_for_each_char = [set() for _ in range(len(txt))]

                # For each feedback item, mark the corresponding characters with the CSS class
                for feedback in feedbacks:
                    # Check if feedback type is not "Achievement", "Merit", or "Excellence" and skip if so
                    if feedback['type'] in ["Achievement", "Merit", "Excellence"]:
                        css_class = "bullet_point" + feedback['bullet_point'].replace("•","_")
                        try:
                            start_index = txt.index(feedback['answer'])
                            end_index = start_index + len(feedback['answer'])
                            for i in range(start_index, end_index):
                                classes_for_each_char[i].add(css_class)

                            marked_up_text = ""
                            current_classes = set()
                            for i, char in enumerate(txt):
                                if classes_for_each_char[i] != current_classes:
                                    # Close the current span(s), if any
                                    if current_classes:
                                        marked_up_text += "</div>" * len(current_classes)
                                    # Open a new span(s) for the new classes
                                    for css_class in classes_for_each_char[i]:
                                        marked_up_text += f'<div class="{css_class}">'
                                    current_classes = classes_for_each_char[i]
                                marked_up_text += char
                            # Close the final span(s), if any
                            if current_classes:
                                marked_up_text += "</div>" * len(current_classes)

                            userquestion.answer_html = mark_safe(marked_up_text)
                        except:
                            continue
                    else:
                        continue
                    
                # Increment counters
                total_a += int(question['achievement'])
                total_m += int(question['merit'])
                total_e += int(question['excellence'])

                userquestion.achievement = int(question['achievement'])
                userquestion.merit = int(question['merit'])
                userquestion.excellence = int(question['excellence'])
                userquestion.save()

            conditions = [
                (8, 'e', QUESTION.e8),
                (7, 'e', QUESTION.e7),
                (6, 'm', QUESTION.m6),
                (5, 'm', QUESTION.m5),
                (4, 'a', QUESTION.a4),
                (3, 'a', QUESTION.a3),
                (2, 'a', QUESTION.n2),
                (1, 'a', QUESTION.n1),
                (0, 'a', QUESTION.n0)
            ]

            score = 0
            total_values = {'e': total_e, 'm': total_m, 'a': total_a}
            for s, var, condition in conditions:
                if total_values[var] >= condition:
                    score = s
                    break

            ncea_score = NceaScores.objects.get(document=doc, QUESTION=QUESTION)
            ncea_score.score = score
            ncea_score.save()
            document_mark += score
            
        doc.mark = document_mark
        doc.marked_before = 1
        doc.save()
    except Exception as e:
        print(e)
        return str(e)