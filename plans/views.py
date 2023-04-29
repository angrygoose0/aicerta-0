from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Plan
from django.conf import settings




# Create your views here.
@login_required(login_url="login/")    
def account(response):
    plans = Plan.objects.all()
    return render(response, "plans/account.html", {'plans': plans, 'user': response.user})
