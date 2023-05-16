from django.contrib import admin
from .models import NceaExam, NceaQUESTION, Specifics, NceaSecondaryQuestion, NceaUserDocument, NceaUserQuestions

# Register your models here.

admin.site.register(NceaExam)
admin.site.register(NceaQUESTION)
admin.site.register(Specifics)
admin.site.register(NceaSecondaryQuestion)
admin.site.register(NceaUserDocument)
admin.site.register(NceaUserQuestions)
