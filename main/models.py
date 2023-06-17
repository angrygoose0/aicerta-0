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
    
    n0 = models.IntegerField()
    n1 = models.IntegerField()
    n2 = models.IntegerField()
    a3 = models.IntegerField()
    a4 = models.IntegerField()
    m5 = models.IntegerField()
    m6 = models.IntegerField()
    e7 = models.IntegerField()
    e8 = models.IntegerField()
    
    system = models.TextField(null = True, blank = True)
    system_html = models.TextField(null = True, blank = True)
    
    def __str__(self):
        return "%s, %s" % (self.exam, self.QUESTION)
    
class NceaSecondaryQuestion(models.Model):
    QUESTION = models.ForeignKey(NceaQUESTION, on_delete=models.CASCADE)

    primary = models.IntegerField()
    secondary = models.IntegerField()

    
    def __str__(self):
        return "%s, %s, %s" % (self.QUESTION, self.primary, self.secondary)
    
    class Meta:
        ordering = ['primary', 'secondary']
        
    
class AssesmentSchedule(models.Model):
    QUESTION = models.ForeignKey(NceaQUESTION, on_delete=models.CASCADE)
    
    text = models.TextField()
    order = models.IntegerField()
    
    type = models.CharField(max_length=20,) #achievement, merit, or excellence, null means not a bulletpoint.
    
    class Meta:
        ordering = ['QUESTION', 'order']
        
    def __str__(self):
        return "%s, %s" % (self.QUESTION, self.type)


class NceaUserDocument(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="nceadocument", null = True, blank = True)
    exam = models.ForeignKey(NceaExam, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    mark = models.IntegerField(default=0) # out of 24
    
    def __str__(self):
        return "%s, %s" % (self.name, self.exam)

    

    
class NceaUserQuestions(models.Model):
    document = models.ForeignKey(NceaUserDocument, on_delete=models.CASCADE)
    question = models.ForeignKey(NceaSecondaryQuestion, on_delete=models.CASCADE)  
    
    answer = models.TextField()
    
    achievement = models.IntegerField(default=0)
    merit = models.IntegerField(default=0)
    excellence = models.IntegerField(default=0)
    
    def __str__(self):
        return "%s, %s" % (self.document, self.question,)
    
    
class NceaScores(models.Model):
    document = models.ForeignKey(NceaUserDocument, on_delete=models.CASCADE)
    QUESTION = models.ForeignKey(NceaQUESTION, on_delete=models.CASCADE)

    score = models.IntegerField(default=0)

    def __str__(self):
        return "%s, %s, score: %s" % (self.document, self.QUESTION, self.score)

