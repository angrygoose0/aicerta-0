from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from plans.models import Plan

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username',]
    
    fieldsets = UserAdmin.fieldsets + (
        ("Plan", {"fields": ("plan",)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)