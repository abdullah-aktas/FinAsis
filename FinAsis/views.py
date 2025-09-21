from django.shortcuts import render
from datetime import datetime

def home(request):
    return render(request, 'home.html', {'year': datetime.now().year})

def privacy_policy(request):
    return render(request, 'privacy_policy.html', {'year': datetime.now().year})



def dashboard(request):
    return render(request, 'dashboard.html', {'year': datetime.now().year})

def education(request):
    return render(request, 'education.html', {'year': datetime.now().year})

def pricing(request):
    return render(request, 'pricing.html', {'year': datetime.now().year})

def legal(request):
    return render(request, 'legal.html', {'year': datetime.now().year})

def contact(request):
    return render(request, 'contact.html', {'year': datetime.now().year})

def help_view(request):
    return render(request, 'help/index.html') 