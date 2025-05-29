from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime

def home(request):
    return render(request, 'home.html', {'year': datetime.now().year})

def privacy_policy(request):
    return render(request, 'privacy_policy.html', {'year': datetime.now().year})

def terms_view(request):
    return render(request, 'terms.html', {'year': datetime.now().year})