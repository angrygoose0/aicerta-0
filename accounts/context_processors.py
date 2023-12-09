from .models import CustomUser
from main.models import Classroom

def classroom_list(request):
    if request.user.is_authenticated:
        # Replace 'UserClass' with your actual model
        class_list = Classroom.objects.filter(teacher=request.user)
        return {'class_list': class_list}
    return {'class_list': []}