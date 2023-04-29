from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
#from account.models import CustomUser

# Create your models here.

class NceaOne(models.Model):
    standard = models.IntegerField()
    year = models.IntegerField()
    
    def __str__(self):
        return "%s, %s" % (self.standard, self.year,)
    
class NceaTwo(models.Model):
    exam = models.ForeignKey(NceaOne, on_delete=models.CASCADE)
    QUESTION = models.IntegerField()
    primary = models.IntegerField()
    secondary = models.IntegerField()
    achieved = models.TextField()
    merit = models.TextField()
    excellence = models.TextField()
    
    def __str__(self):
        return "%s, %s, %s, %s" % (self.exam, self.QUESTION, self.primary, self.secondary)
    
class NceaThree(models.Model):
    exam = models.ForeignKey(NceaOne, on_delete=models.CASCADE)
    QUESTION = models.IntegerField()
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
            

class NceaDocument(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="nceadocument", null = True, blank = True)
    exam = models.ForeignKey(NceaOne, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    mark = models.IntegerField() # out of 24
    
    
    def __str__(self):
        return "%s, %s" % (self.name, self.exam)
    
class NceaQuestions(models.Model):
    document = models.ForeignKey(NceaDocument, on_delete=models.CASCADE)
    QUESTION = models.IntegerField()
    primary = models.IntegerField()
    secondary = models.IntegerField()
    
    text = models.TextField()
    
    mark = models.IntegerField() # 112 = 1 achieved, 1 merit, 2 excellence
    
    def __str__(self):
        return "%s, %s, %s, %s," % (self.document, self.QUESTION, self.primary, self.secondary)
    
    
