def finance_home(request):
    return render(request, 'finance/home.html', {'year': datetime.now().year})

def finance_reports(request):
    return render(request, 'finance/reports.html', {'year': datetime.now().year})

def education_index(request):
    return render(request, 'education/index.html', {'year': datetime.now().year})

def games_all(request):
    return render(request, 'games/all.html', {'year': datetime.now().year})

def tradesim_play(request):
    return render(request, 'games/tradesim_play.html', {'year': datetime.now().year})

def tradesim_detail(request):
    return render(request, 'games/tradesim_detail.html', {'year': datetime.now().year})

def blockchain(request):
    return render(request, 'blockchain/home.html', {'year': datetime.now().year})

def profile(request):
    return render(request, 'accounts/profile.html', {'year': datetime.now().year})

def investor_info_form(request):
    return render(request, 'investor_info_form.html', {'year': datetime.now().year})
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