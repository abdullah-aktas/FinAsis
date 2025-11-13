from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from ..models import Company, CompanyDeleteLog, EDefter
from ..forms import CompanyForm
from django.utils import timezone
from django.contrib import messages
from django.core.cache import cache
from django.template.loader import render_to_string
from django.http import FileResponse
import io
from django.contrib.auth.decorators import login_required
from ..services.edefter_service import send_edefter_to_gib, get_edefter_berat

def company_list(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(is_active=True)
    return render(request, 'accounting/company_list.html', {'companies': companies})

def company_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('accounting:company_list')
    else:
        form = CompanyForm()
    return render(request, 'accounting/company_form.html', {'form': form})

def company_detail(request: HttpRequest, slug: str) -> HttpResponse:
    company = get_object_or_404(Company, slug=slug)
    delete_logs = CompanyDeleteLog.objects.filter(company=company).order_by('-deleted_at')[:5]
    ai_summary = request.GET.get('ai_summary')  # Geçici olarak, AI özetini context'e ekle
    return render(request, 'accounting/company_detail.html', {
        'company': company,
        'delete_logs': delete_logs,
        'ai_summary': ai_summary,
    })

def company_update(request: HttpRequest, slug: str) -> HttpResponse:
    company = get_object_or_404(Company, slug=slug)
    if request.method == 'POST':
        if request.POST.get('reactivate'):
            company.is_active = True
            company.save()
            messages.success(request, 'Şirket yeniden aktifleştirildi.')
            return redirect('accounting:company_list')
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect('accounting:company_detail', slug=company.slug)
    else:
        form = CompanyForm(instance=company)
    return render(request, 'accounting/company_form.html', {'form': form, 'company': company})

def company_delete(request: HttpRequest, slug: str) -> HttpResponse:
    company = get_object_or_404(Company, slug=slug)
    if request.method == 'POST':
        reason = request.POST.get('delete_reason')
        # Rate limiting: 1dk içinde tekrar silme engeli
        cache_key = f"delete_company_{request.user.id}"
        if cache.get(cache_key):
            messages.error(request, "Çok hızlı silme işlemi! Lütfen 1 dakika sonra tekrar deneyin.")
            return redirect('accounting:company_list')
        if not reason:
            messages.error(request, "Silme gerekçesi zorunludur.")
            return render(request, 'accounting/company_confirm_delete.html', {'company': company})
        company.is_active = False
        company.save()
        CompanyDeleteLog.objects.create(company=company, user=request.user, reason=reason)
        cache.set(cache_key, True, timeout=60)  # 1 dakika
        messages.success(request, "Şirket başarıyla pasif hale getirildi ve silme gerekçesi kaydedildi.")
        return redirect('accounting:company_list')
    return render(request, 'accounting/company_confirm_delete.html', {'company': company})


def company_detail_redirect(request: HttpRequest, pk: int) -> HttpResponse:
    company = get_object_or_404(Company, pk=pk)
    return redirect('accounting:company_detail', slug=company.slug, permanent=True)


def company_update_redirect(request: HttpRequest, pk: int) -> HttpResponse:
    company = get_object_or_404(Company, pk=pk)
    return redirect('accounting:company_update', slug=company.slug, permanent=True)


def company_delete_redirect(request: HttpRequest, pk: int) -> HttpResponse:
    company = get_object_or_404(Company, pk=pk)
    return redirect('accounting:company_delete', slug=company.slug, permanent=True)


def company_pdf_redirect(request: HttpRequest, pk: int) -> HttpResponse:
    company = get_object_or_404(Company, pk=pk)
    return redirect('accounting:company_pdf', slug=company.slug, permanent=True)


def company_ai_summary_redirect(request: HttpRequest, pk: int) -> HttpResponse:
    company = get_object_or_404(Company, pk=pk)
    return redirect('accounting:company_ai_summary', slug=company.slug, permanent=True)


def company_pdf(request: HttpRequest, slug: str) -> HttpResponse:
    company = get_object_or_404(Company, slug=slug)
    html = render_to_string('accounting/company_pdf.html', {'company': company})
    try:
        import weasyprint
        pdf_file = weasyprint.HTML(string=html).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="sirket_{company.id}.pdf"'
        return response
    except ImportError:
        return HttpResponse('PDF oluşturmak için weasyprint yüklü değil.', status=500)

@login_required
def company_ai_summary(request, slug):
    # Dummy/örnek özet, gerçek AI entegrasyonu burada yapılabilir
    company = get_object_or_404(Company, slug=slug)
    summary = f"{company.name} şirketinin son 1 yıldaki gelir/gider oranı %72, net kârı 1.200.000₺, toplam müşteri sayısı 18. Finansal risk seviyesi: Düşük."
    return JsonResponse({"summary": summary})

def edefter_send_gib(request, pk):
    edefter = get_object_or_404(EDefter, pk=pk)
    response = send_edefter_to_gib(edefter)
    if response.status_code == 200:
        messages.success(request, "e-Defter GİB'e başarıyla gönderildi.")
    else:
        messages.error(request, f"GİB gönderim hatası: {response.text}")
    return redirect('admin:accounting_edefter_change', object_id=pk)

def edefter_get_berat(request, pk):
    edefter = get_object_or_404(EDefter, pk=pk)
    response = get_edefter_berat(edefter)
    if response.status_code == 200:
        messages.success(request, "Berat başarıyla alındı.")
    else:
        messages.error(request, f"Berat alma hatası: {response.text}")
    return redirect('admin:accounting_edefter_change', object_id=pk) 