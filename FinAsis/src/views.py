from django.shortcuts import render, redirect
from datetime import datetime
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

def home(request):
    return render(request, 'home.html', {'year': datetime.now().year})

def privacy_policy(request):
    return render(request, 'privacy_policy.html', {'year': datetime.now().year})

def terms_view(request):
    return render(request, 'terms.html', {'year': datetime.now().year})

def dashboard(request):
    return render(request, 'dashboard.html', {'year': datetime.now().year})

def education(request):
    return render(request, 'education.html', {'year': datetime.now().year})

def pricing(request):
    # Eski fiyatlandırma sayfasını yeni planlar sayfasına yönlendir
    audience = request.GET.get('audience')
    period = request.GET.get('period')
    url = '/billing/plans/'
    params = []
    if audience in ('sme', 'edu'):
        params.append(f'audience={audience}')
    if period in ('month', 'year'):
        params.append(f'period={period}')
    if params:
        url = url + '?' + '&'.join(params)
    return redirect(url)

def legal(request):
    return render(request, 'legal.html', {'year': datetime.now().year})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message_text = request.POST.get('message', '').strip()

        if name and email and message_text:
            messages.success(request, 'Mesajınız alındı. Teşekkürler!')
            try:
                admin_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@finasis.local')
                send_mail(
                    subject=f"İletişim Formu: {name}",
                    message=f"Ad: {name}\nE-posta: {email}\nMesaj: {message_text}",
                    from_email=admin_email,
                    recipient_list=[getattr(settings, 'SUPPORT_EMAIL', admin_email)],
                    fail_silently=True,
                )
            except Exception:
                pass
            return redirect('contact')
        else:
            messages.error(request, 'Lütfen tüm gerekli alanları doldurun.')

    return render(request, 'contact.html', {'year': datetime.now().year})

def help_view(request):
    return render(request, 'help/index.html') 