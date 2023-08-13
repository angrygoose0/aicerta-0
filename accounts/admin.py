from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', 'credits', 'plan',]

    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {'fields': ('plan', 'credits','stripe_customer_id')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)