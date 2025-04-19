from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("FinAsis Test Sayfası Açıldı - Tebrikler!") 