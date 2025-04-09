from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def company_home(request):
    return render(request, 'virtual_company/home.html')

@login_required
def create_company(request):
    return render(request, 'virtual_company/create_company.html')

@login_required
def my_company(request):
    return render(request, 'virtual_company/my_company.html')

@login_required
def market(request):
    return render(request, 'virtual_company/market.html')

@login_required
def competitors(request):
    return render(request, 'virtual_company/competitors.html') 