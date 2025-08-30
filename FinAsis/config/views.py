from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime
from django.http import JsonResponse

def home(request):
    return render(request, 'home.html', {'year': datetime.now().year})

def privacy_policy(request):
    return render(request, 'privacy_policy.html', {'year': datetime.now().year})

def terms_view(request):
    return render(request, 'terms.html', {'year': datetime.now().year})

def help_content_api(request):
    role = request.GET.get('role', 'genel')
    data = {
        'role': role,
        'items': [
            {
                'title': 'Hoş geldiniz',
                'content': 'FinAsis yardım içeriği geliştirme ortamında yüklenmedi. Bu bir yer tutucudur.',
            }
        ],
    }
    return JsonResponse(data)

def kvkk_view(request):
    # KVKK için ayrı bir sayfa şablonu varsa kullan, yoksa gizlilik politikasını göster
    template_candidates = ['kvkk.html', 'privacy_policy.html']
    for template_name in template_candidates:
        try:
            return render(request, template_name, {'year': datetime.now().year})
        except Exception:
            # Django template loader uygun şablon bulunamazsa denemeye devam ederiz
            continue
    return render(request, 'legal.html', {'year': datetime.now().year})