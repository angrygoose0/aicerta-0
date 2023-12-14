from .models import CustomUser
from main.models import Classroom
from main.forms import ClassroomJoin

def classroom_list(request):
    if request.user.is_authenticated:
        if request.user.student == False:
            class_list = Classroom.objects.filter(teacher=request.user)
            return {'class_list': class_list}
        if request.user.student == True:
            class_list = Classroom.objects.filter(students=request.user)
            return {'class_list': class_list}
    return {'class_list': []}

def classroom_form(request):
    if request.user.is_authenticated:
        classroom_form = ClassroomJoin()
        return {'classroom_form': classroom_form}

def user(request):
    if request.user.is_authenticated:
        user = request.user
        return {'user': user}
    return {'user': []}
