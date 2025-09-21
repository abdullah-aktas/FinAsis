from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import translation
try:
    from src.apps.corporate.models import PressRelease, InvestorDocument, TeamMember
except Exception:
    PressRelease = InvestorDocument = TeamMember = None

def home(request):
    return render(request, 'home.html', {'year': datetime.now().year})

def privacy_policy(request):
    return render(request, 'privacy_policy.html', {'year': datetime.now().year})

def terms_view(request):
    return render(request, 'terms.html', {'year': datetime.now().year})

# --- Added static/marketing page views ---
def corporate(request):
    return render(request, 'corporate.html', {'year': datetime.now().year})

def corporate_about(request):
    return render(request, 'corporate/about.html', {'year': datetime.now().year})

def resources_view(request):
    return render(request, 'resources.html', {'year': datetime.now().year})

def corporate_team(request):
    members = TeamMember.objects.all() if TeamMember else []
    return render(request, 'corporate/team.html', {'year': datetime.now().year, 'members': members})

def support_view(request):
    return render(request, 'support.html', {'year': datetime.now().year})

def corporate_sustainability(request):
    return render(request, 'corporate/sustainability.html', {'year': datetime.now().year})

def corporate_careers(request):
    return render(request, 'corporate/careers.html', {'year': datetime.now().year})

def corporate_press(request):
    prs = PressRelease.objects.all()[:10] if PressRelease else []
    return render(request, 'corporate/press.html', {'year': datetime.now().year, 'press_releases': prs})

def corporate_investors(request):
    docs = InvestorDocument.objects.all()[:10] if InvestorDocument else []
    return render(request, 'corporate/investors.html', {'year': datetime.now().year, 'documents': docs})

def corporate_security(request):
    return render(request, 'corporate/security.html', {'year': datetime.now().year})

def products_finans(request):
    return render(request, 'products/finans.html', {'year': datetime.now().year})

def products_egitim(request):
    return render(request, 'products/egitim.html', {'year': datetime.now().year})

def products_blockchain(request):
    return render(request, 'products/blockchain.html', {'year': datetime.now().year})

def products_oyunlar(request):
    return render(request, 'products/oyunlar.html', {'year': datetime.now().year})

def solutions_enteg(request):
    return render(request, 'solutions/entegrasyon.html', {'year': datetime.now().year})

def solutions_raporlama(request):
    return render(request, 'solutions/raporlama.html', {'year': datetime.now().year})

def solutions_analitik(request):
    return render(request, 'solutions/analitik.html', {'year': datetime.now().year})

def virtual_company_placeholder(request):
    # TODO: Implement real virtual company dashboard
    return HttpResponse('<h1>Virtual Company Modülü Yakında</h1>', status=200)

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

@require_GET
def search_view(request):
    q = request.GET.get('q', '').strip()
    context = {
        'query': q,
        'results': [],  # TODO: implement real search
        'year': datetime.now().year,
    }
    # Fall back to a simple template; reuse resources.html if no dedicated one
    try:
        return render(request, 'search.html', context)
    except Exception:
        return render(request, 'resources.html', context)

def corporate_offer(request):
    if request.method == 'POST':
        company = request.POST.get('company', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message_text = request.POST.get('message', '').strip()

        messages.success(request, 'Talebiniz alındı. En kısa sürede dönüş yapacağız.')

        try:
            admin_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@finasis.local')
            send_mail(
                subject=f"Kurumsal Teklif Talebi: {company}",
                message=f"Şirket: {company}\nE-posta: {email}\nTelefon: {phone}\nMesaj: {message_text}",
                from_email=admin_email,
                recipient_list=[getattr(settings, 'SALES_EMAIL', admin_email)],
                fail_silently=True,
            )
        except Exception:
            pass

    return render(request, 'corporate_offer.html', {'year': datetime.now().year})

def set_language_compat(request):
    """
    Accept both GET and POST to change language.
    - GET: supports legacy `/i18n/setlang/?lang=tr&next=/...` links
    - POST: delegates to Django's built-in view for full behavior
    """
    next_url = request.GET.get('next') or request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
    lang_param = request.GET.get('lang') or request.GET.get('language') or request.POST.get('language')

    if request.method == 'GET' and lang_param:
        response = redirect(next_url)
        if hasattr(request, 'session'):
            request.session[translation.LANGUAGE_SESSION_KEY] = lang_param
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_param)
        return response

    # For non-GET (POST) or missing lang, defer to Django's set_language view
    from django.views.i18n import set_language as dj_set_language
    return dj_set_language(request)