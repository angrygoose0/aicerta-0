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




class NceaQUESTION(models.Model):
    exam = models.ForeignKey(NceaExam, on_delete=models.CASCADE)
    QUESTION = models.IntegerField(editable = False)

    def save(self, *args, **kwargs):
        if not self.pk:  # Checking if this is a new instance
            # Retrieve the highest QUESTION number for the current exam
            last_question = NceaQUESTION.objects.filter(exam=self.exam).order_by('-QUESTION').first()
            self.QUESTION = 1 if not last_question else last_question.QUESTION + 1
        super(NceaQUESTION, self).save(*args, **kwargs)
    
    def __str__(self):
        return "%s, %s" % (self.exam, self.QUESTION)
    
    class Meta:
            ordering = ['exam', 'QUESTION']
    
class NceaQUESTIONcalc(models.Model):
    
    QUESTION = models.ForeignKey(NceaQUESTION, on_delete=models.CASCADE)
    type = models.IntegerField(default=0) #n0,n1,n2,a3,a4,m5,m6,e7,e8

    a = models.IntegerField(default=0, null=True, blank=True)
    m = models.IntegerField(default=0, null=True, blank=True)
    e = models.IntegerField(default=0, null=True, blank=True)
    
    class Meta:
        ordering = ['QUESTION', '-type']

    
    
class NceaSecondaryQuestion(models.Model):
    QUESTION = models.ForeignKey(NceaQUESTION, on_delete=models.CASCADE)
    
    thequestion = models.TextField(null=True, blank=True)

    primary = models.IntegerField() #a=1, b=2, c=3, d=4
    secondary = models.IntegerField() #i=1, ii=2, iii=3, iv=4
    
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
    
    class Meta:
        ordering = ['order']


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
    secret_code = models.CharField(max_length=6, unique=True, editable=False,)

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
    
    starts_at= models.DateTimeField(null=True, blank=True)
    ends_at= models.DateTimeField(null=True, blank=True)

    status = models.IntegerField(default=0) #0, 1, 2 = pending, on-going, archived

    strict = models.BooleanField(default=False)


    def __str__(self):
        return "%s, %s, %s, %s" % (self.teacher, self.name, self.classroom, self.exam)
    

class NceaUserDocument(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="nceadocument")
    name = models.CharField(max_length=100)
    exam = models.ForeignKey(NceaExam, on_delete=models.CASCADE)
    
    mark = models.IntegerField(default=0) # out of 24
    marked_before = models.IntegerField(default=0) #1 for true, 0 for false
    
    credit_price = models.IntegerField(default=0)
    
    file = models.ForeignKey(File, on_delete=models.SET_NULL, null = True, blank = True)
    assignment = models.ForeignKey(Assignment, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=100, null=True, blank=True)
    
    
    
    #pending, started, paused, locked, submitted.
    
    
    def __str__(self):
        return "%s, %s" % (self.name, self.exam)
    

class OCRImage(models.Model):
    document = models.ForeignKey(NceaUserDocument, on_delete=models.CASCADE)
    image = models.ImageField()
    text = models.TextField(null = True, blank = True, default=None)
    
class NceaUserQuestions(models.Model):
    document = models.ForeignKey(NceaUserDocument, on_delete=models.CASCADE)
    question = models.ForeignKey(NceaSecondaryQuestion, on_delete=models.CASCADE)  
    
    answer = models.TextField(max_length=1500, null=True, blank=True)
    

    def __str__(self):
        return "%s, %s" % (self.document, self.question,)
        
    class Meta:
        ordering = ['document', 'question']
        
class NceaUserImages(models.Model):
    user_question = models.ForeignKey(NceaUserQuestions, on_delete=models.CASCADE)
    image = models.ImageField()
    
    def __str__(self):
        return "%s image" % (self.user_question,)
    
    class Meta:
        ordering = ['user_question']
    
    
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
    confidence = models.IntegerField(default=0) #0-100
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


class MarkedChunks(models.Model):
    document = models.ForeignKey(NceaUserDocument, on_delete=models.CASCADE)
    
    common_questions = models.ManyToManyField(NceaSecondaryQuestion, related_name="chunkquestions")
    criterias = models.ManyToManyField(Criteria, related_name="chunkcriteria")
    
    
    
