from django.contrib import admin
from .models import NceaDocument, NceaQuestions, NceaOne, NceaTwo, NceaThree

# Register your models here.

admin.site.register(NceaDocument)
admin.site.register(NceaQuestions)
admin.site.register(NceaOne)
admin.site.register(NceaTwo)
admin.site.register(NceaThree)
