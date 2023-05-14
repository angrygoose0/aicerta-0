from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
#from account.models import CustomUser

# Create your models here.

class NceaExam(models.Model):
    standard = models.IntegerField()
    year = models.IntegerField()
    
    def __str__(self):
        return "%s, %s" % (self.standard, self.year,)
    
class NceaQUESTION(models.Model):
    exam = models.ForeignKey(NceaExam, on_delete=models.CASCADE)
    QUESTION = models.IntegerField()
    
    system = models.TextField()
    
    n0 = models.IntegerField()
    a1 = models.IntegerField()
    n2 = models.IntegerField()
    a3 = models.IntegerField()
    a4 = models.IntegerField()
    m5 = models.IntegerField()
    m6 = models.IntegerField()
    e7 = models.IntegerField()
    e8 = models.IntegerField()
    
    def __str__(self):
        return "%s, %s" % (self.exam, self.QUESTION)
    
    

class Specifics(models.Model):
    order = models.IntegerField()
    type = models.IntegerField() #0 for assistant, 1 for Human
    text = models.IntegerField()

class NceaSecondaryQuestion(models.Model):
    QUESTION = models.ForeignKey(NceaQUESTION, on_delete=models.CASCADE)

    primary = models.IntegerField()
    secondary = models.IntegerField()
    
    specifics = models.ForeignKey(Specifics, on_delete=models.CASCADE)
    
    def __str__(self):
        return "%s, %s, %s" % (self.QUESTION, self.primary, self.secondary)
    



class NceaUserDocument(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="nceadocument", null = True, blank = True)
    exam = models.ForeignKey(NceaExam, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    mark = models.IntegerField() # out of 24
    
    def __str__(self):
        return "%s, %s" % (self.name, self.exam)
    
class NceaUserQuestions(models.Model):
    document = models.ForeignKey(NceaUserDocument, on_delete=models.CASCADE)
    question = models.ForeignKey(NceaSecondaryQuestion, on_delete=models.CASCADE)  
    
    answer = models.TextField()
    
    def __str__(self):
        return "%s, %s" % (self.document, self.question,)
    
    
