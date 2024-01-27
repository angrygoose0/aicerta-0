from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import string
import random

#from account.models import CustomUser

# Create your models here.

class NceaExam(models.Model):
    standard = models.IntegerField()
    year = models.IntegerField()
    exam_name = models.TextField(null=True, blank=True)

    # Many-to-Many relationship with users
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="nceaexams", blank=True)

    # Boolean field to determine if the exam is visible to everyone
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return "%s - %s - %s" % (self.exam_name, self.standard, self.year)

def generate_choices(letter):
        return [(i, f"{i}{letter}") for i in range(1, 11)]  
class NceaQUESTION(models.Model):
    ACHOICES = generate_choices('a')
    MCHOICES = generate_choices('m')
    ECHOICES = generate_choices('e')

    exam = models.ForeignKey(NceaExam, on_delete=models.CASCADE)
    QUESTION = models.IntegerField()
    
    n0 = models.IntegerField(default=0, choices=ACHOICES)
    n1 = models.IntegerField(default=1, choices=ACHOICES)
    n2 = models.IntegerField(default=2, choices=ACHOICES)
    a3 = models.IntegerField(default=3, choices=ACHOICES)
    a4 = models.IntegerField(default=4, choices=ACHOICES)
    m5 = models.IntegerField(default=2, choices=MCHOICES)
    m6 = models.IntegerField(default=3, choices=MCHOICES)
    e7 = models.IntegerField(default=1, choices=ECHOICES)
    e8 = models.IntegerField(default=2, choices=ECHOICES)
    
    
    def __str__(self):
        return "%s, %s" % (self.exam, self.QUESTION)

    class Meta:
            ordering = ['exam', 'QUESTION']
    
class NceaSecondaryQuestion(models.Model):
    QUESTION = models.ForeignKey(NceaQUESTION, on_delete=models.CASCADE)

    primary = models.IntegerField()
    secondary = models.IntegerField()
    
    evidence = models.TextField(null=True, blank=True)

    
    def __str__(self):
        return "%s, %s, %s" % (self.QUESTION, self.primary, self.secondary)
    
    class Meta:
        ordering = ['QUESTION', 'primary', 'secondary']
        
    
    
class Criteria(models.Model):
    secondary_questions = models.ManyToManyField(NceaSecondaryQuestion, related_name="nceacriteria", blank=True)
    text = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=10) # a, m, e
    image = models.IntegerField(default=0) #1 for image, 0 for not image
    
    order = models.IntegerField(default=0)


    def __str__(self):
        return "%s, %s, %s" % (self.secondary_questions, self.type, self.order)

    
    

class File(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    file = models.FileField()
    
    def __str__(self):
        return "%s - %s" % (self.name, self.user)

class Classroom(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher")
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="students", blank=True)
    secret_code = models.CharField(max_length=6, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.secret_code:
            self.secret_code = self._generate_unique_code()
        super().save(*args, **kwargs)

    def _generate_unique_code(self):
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            if not Classroom.objects.filter(secret_code=code).exists():
                return code

    def __str__(self):
        return self.name

class Assignment(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    name = models.CharField(max_length=100)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    exam = models.ForeignKey(NceaExam, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    ends_at= models.DateTimeField(null=True, blank=True)

    status = models.IntegerField(default=0) #0, 1, 2 = pending, on-going, archived


    def __str__(self):
        return "%s, %s, %s, %s" % (self.teacher, self.name, self.classroom, self.exam)
    

class NceaUserDocument(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="nceadocument", null = True, blank = True)
    name = models.CharField(max_length=100)
    exam = models.ForeignKey(NceaExam, on_delete=models.CASCADE)
    
    mark = models.IntegerField(default=0) # out of 24
    marked_before = models.IntegerField(default=0) #1 for true, 0 for false
    
    credit_price = models.IntegerField(default=0)
    
    file = models.ForeignKey(File, on_delete=models.SET_NULL, null = True, blank = True)
    assignment = models.ForeignKey(Assignment, on_delete=models.SET_NULL, null=True, blank=True)

    editable = models.BooleanField(default=True)
    
    def __str__(self):
        return "%s, %s" % (self.name, self.exam)

    
class OCRImage(models.Model):
    document = models.ForeignKey(NceaUserDocument, on_delete=models.CASCADE)
    image = models.ImageField()
    text = models.TextField(null = True, blank = True, default=None)
    
class NceaUserQuestions(models.Model):
    document = models.ForeignKey(NceaUserDocument, on_delete=models.CASCADE)
    question = models.ForeignKey(NceaSecondaryQuestion, on_delete=models.CASCADE)  
    
    answer = models.TextField(max_length=1500)
    

    def __str__(self):
        return "%s, %s" % (self.document, self.question,)
        
    class Meta:
        ordering = ['document', 'question']
    
    
class NceaScores(models.Model):
    document = models.ForeignKey(NceaUserDocument, on_delete=models.CASCADE)
    QUESTION = models.ForeignKey(NceaQUESTION, on_delete=models.CASCADE)

    score = models.IntegerField(default=0)

    def __str__(self):
        return "%s, %s, score: %s" % (self.document, self.QUESTION, self.score)

    class Meta:
        ordering = ['document', 'QUESTION']
        
class HelpMessage(models.Model):
    message = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="help", null = True, blank = True)
    date = models.DateTimeField

class BulletPoint(models.Model):
    document = models.ForeignKey(NceaUserDocument, on_delete=models.CASCADE, null = True, blank = True)
    criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE, related_name="criteria", null = True, blank = True)
    confidence = models.IntegerField(default=0)
    explanation = models.TextField(null=True, blank=True)
    r = models.IntegerField(default=255)
    g = models.IntegerField(default=255)
    b = models.IntegerField(default=255)
    no = models.IntegerField(default=0)
    
    def __str__(self):
        return "%s, %s" % (self.document, self.criteria)


class Quoted(models.Model):
    secondary_question = models.ForeignKey(NceaSecondaryQuestion, on_delete=models.CASCADE, null = True, blank = True)
    bullet_point = models.ForeignKey(BulletPoint, on_delete=models.CASCADE, related_name="bullet_point", null = True, blank = True)
    quote = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return "%s, %s" % (self.secondary_question, self.bullet_point)


    
