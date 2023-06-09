from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
#from account.models import CustomUser

# Create your models here.

class NceaExam(models.Model):
    standard = models.IntegerField()
    year = models.IntegerField()
    exam_name = models.TextField(null = True, blank = True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="nceaexam", null = True, blank = True)
    
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
    CHOICES = (
    ("n", "QUESTION"),
    ("a", "Achieved"),
    ("m", "Merit"),
    ("e", "Excellence"),
    )
    
    QUESTION = models.ForeignKey(NceaQUESTION, on_delete=models.CASCADE)
    secondary_question = models.ForeignKey(NceaSecondaryQuestion, on_delete=models.CASCADE, null = True, blank = True)
    
    text = models.TextField()
    order = models.IntegerField()
    
    type = models.CharField(max_length=20, choices=CHOICES) #achievement, merit, or excellence, null means not a bulletpoint.
    
    class Meta:
        ordering = ['QUESTION', 'order']
        
    def __str__(self):
        return "%s, %s" % (self.QUESTION, self.type)


class NceaUserDocument(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="nceadocument", null = True, blank = True)
    exam = models.ForeignKey(NceaExam, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    mark = models.IntegerField(default=0) # out of 24
    marked_before = models.IntegerField(default=0) #1 for true, 0 for false
    
    def __str__(self):
        return "%s, %s" % (self.name, self.exam)

    

    
class NceaUserQuestions(models.Model):
    document = models.ForeignKey(NceaUserDocument, on_delete=models.CASCADE)
    question = models.ForeignKey(NceaSecondaryQuestion, on_delete=models.CASCADE)  
    
    answer = models.TextField()
    answer_html = models.TextField(null = True, blank = True)
    
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

class HelpMessage(models.Model):
    message = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="help", null = True, blank = True)
    date = models.DateTimeField