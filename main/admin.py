from django.contrib import admin
from .models import NceaExam, AssesmentSchedule, NceaScores, NceaQUESTION, NceaSecondaryQuestion, NceaUserDocument, NceaUserQuestions, File, OCRImage, HelpMessage, Criteria, BulletPoint, Quoted

# Register your models here.

class CriteriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'type', 'image', 'order', 'display_secondary_questions')

    def display_secondary_questions(self, obj):
        return ", ".join([str(question) for question in obj.secondary_questions.all()])
    display_secondary_questions.short_description = 'Secondary Questions'


class BulletPointAdmin(admin.ModelAdmin):
    list_display = ('document', 'display_criteria_secondary_questions', 'confidence')

    def display_criteria_secondary_questions(self, obj):
        if obj.criteria:
            return ", ".join([str(question) for question in obj.criteria.secondary_questions.all()])
        return "None"
    display_criteria_secondary_questions.short_description = 'Secondary Questions'

class QuotedAdmin(admin.ModelAdmin):
    list_display = ('secondary_question', 'display_related_bullet_point_criteria_secondary_questions', 'quote')

    def display_related_bullet_point_criteria_secondary_questions(self, obj):
        if obj.bullet_point and obj.bullet_point.criteria:
            return ", ".join([str(question) for question in obj.bullet_point.criteria.secondary_questions.all()])
        return "None"
    display_related_bullet_point_criteria_secondary_questions.short_description = 'Related Secondary Questions'

admin.site.register(Quoted, QuotedAdmin)
admin.site.register(BulletPoint, BulletPointAdmin)
admin.site.register(Criteria, CriteriaAdmin)


admin.site.register(NceaExam)
admin.site.register(NceaQUESTION)
admin.site.register(NceaSecondaryQuestion)
admin.site.register(NceaUserDocument)
admin.site.register(NceaUserQuestions)
admin.site.register(AssesmentSchedule)
admin.site.register(NceaScores)
admin.site.register(File)
admin.site.register(OCRImage)
admin.site.register(HelpMessage)




