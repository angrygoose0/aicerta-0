from django.contrib import admin
from .models import NceaExam, AssesmentSchedule, NceaScores, NceaQUESTION, NceaSecondaryQuestion, NceaUserDocument, NceaUserQuestions, File, OCRImage

# Register your models here.

admin.site.register(NceaExam)
admin.site.register(NceaQUESTION)
admin.site.register(NceaSecondaryQuestion)
admin.site.register(NceaUserDocument)
admin.site.register(NceaUserQuestions)
admin.site.register(AssesmentSchedule)
admin.site.register(NceaScores)
admin.site.register(File)
admin.site.register(OCRImage)

