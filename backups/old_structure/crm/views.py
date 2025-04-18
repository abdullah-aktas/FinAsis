from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch, Count, Sum
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, JsonResponse
from django.db import transaction
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.views.decorators.http import require_POST
from django.urls import reverse
import json
import decimal
import logging
import requests
from datetime import datetime
from django.utils import timezone

from .models import Customer, Contact, Opportunity, Activity, Document, Sale, SaleItem, EDocumentStatus, CustomerAcquisitionAnalytics, Campaign, CampaignUsage, ReferralProgram, PremiumPackage, ConsultingService, TrainingProgram, APIPricing, ServiceSubscription
from .forms import CustomerForm, ContactForm, OpportunityForm, ActivityForm, DocumentForm, SaleForm
from .services import EDocumentService, AccountingIntegrationService, CustomerAcquisitionService, CustomerAnalyticsService, CampaignService

def check_object_permission(user, obj):
    """Kullanıcının nesne üzerinde işlem yapma yetkisini kontrol eder."""
    if hasattr(obj, 'assigned_to'):
        return user == obj.assigned_to or user.is_staff
    return user.is_staff

# Müşteri view'ları
@login_required
@cache_page(60 * 15)  # 15 dakika cache
def customer_list(request):
    try:
        search_query = request.GET.get('search', '')
        customers = Customer.objects.select_related('created_by').prefetch_related(
            Prefetch('contacts', queryset=Contact.objects.select_related('customer')),
            Prefetch('opportunities', queryset=Opportunity.objects.select_related('customer'))
        ).annotate(
            contact_count=Count('contacts'),
            opportunity_count=Count('opportunities'),
            total_opportunity_value=Sum('opportunities__value')
        )
        
        if search_query:
            customers = customers.filter(
                Q(name__icontains=search_query) |
                Q(tax_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        paginator = Paginator(customers, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query,
        }
        return render(request, 'crm/customer_list.html', context)
    except Exception as e:
        messages.error(request, _('Müşteri listesi alınırken bir hata oluştu.'))
        return redirect('home')

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    opportunities = Opportunity.objects.filter(customer=customer).order_by('-created_at')
    activities = Activity.objects.filter(customer=customer).order_by('-created_at')
    sales = Sale.objects.filter(customer=customer).order_by('-date')
    documents = Document.objects.filter(customer=customer).order_by('-created_at')
    
    context = {
        'customer': customer,
        'opportunities': opportunities,
        'activities': activities,
        'sales': sales,
        'documents': documents,
    }
    
    return render(request, 'crm/customer_detail.html', context)

@login_required
@transaction.atomic
def customer_create(request):
    try:
        if request.method == 'POST':
            form = CustomerForm(request.POST)
            if form.is_valid():
                customer = form.save(commit=False)
                customer.created_by = request.user
                customer.save()
                messages.success(request, _('Müşteri başarıyla oluşturuldu.'))
                return redirect('crm:customer_detail', pk=customer.pk)
        else:
            form = CustomerForm()
        
        context = {
            'form': form,
            'title': _('Yeni Müşteri'),
        }
        return render(request, 'crm/customer_form.html', context)
    except Exception as e:
        messages.error(request, _('Müşteri oluşturulurken bir hata oluştu.'))
        return redirect('crm:customer_list')

@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            messages.success(request, _('Müşteri başarıyla güncellendi.'))
            return redirect('crm:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    
    context = {
        'form': form,
        'customer': customer,
        'title': _('Müşteri Düzenle'),
    }
    return render(request, 'crm/customer_form.html', context)

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer.delete()
        messages.success(request, _('Müşteri başarıyla silindi.'))
        return redirect('crm:customer_list')
    
    context = {
        'customer': customer,
    }
    return render(request, 'crm/customer_delete.html', context)

# İletişim view'ları
@login_required
def contact_list(request):
    search_query = request.GET.get('search', '')
    contacts = Contact.objects.all()
    
    if search_query:
        contacts = contacts.filter(
            Q(name__icontains=search_query) |
            Q(customer__name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    paginator = Paginator(contacts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'crm/contact_list.html', context)

@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    context = {'contact': contact}
    return render(request, 'crm/contact_detail.html', context)

@login_required
def contact_create(request):
    customer_id = request.GET.get('customer')
    initial = {}
    if customer_id:
        customer = get_object_or_404(Customer, pk=customer_id)
        initial['customer'] = customer
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, _('İletişim kişisi başarıyla oluşturuldu.'))
            return redirect('crm:contact_detail', pk=contact.pk)
    else:
        form = ContactForm(initial=initial)
    
    context = {
        'form': form,
        'title': _('Yeni İletişim Kişisi'),
    }
    return render(request, 'crm/contact_form.html', context)

@login_required
def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            messages.success(request, _('İletişim kişisi başarıyla güncellendi.'))
            return redirect('crm:contact_detail', pk=contact.pk)
    else:
        form = ContactForm(instance=contact)
    
    context = {
        'form': form,
        'contact': contact,
        'title': _('İletişim Kişisi Düzenle'),
    }
    return render(request, 'crm/contact_form.html', context)

@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    
    if request.method == 'POST':
        customer_pk = contact.customer.pk
        contact.delete()
        messages.success(request, _('İletişim kişisi başarıyla silindi.'))
        return redirect('crm:customer_detail', pk=customer_pk)
    
    context = {
        'contact': contact,
    }
    return render(request, 'crm/contact_delete.html', context)

# Fırsat view'ları
@login_required
def opportunity_list(request):
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    opportunities = Opportunity.objects.all()
    
    if search_query:
        opportunities = opportunities.filter(
            Q(name__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    
    if status:
        opportunities = opportunities.filter(status=status)
    
    paginator = Paginator(opportunities, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status': status,
        'status_choices': Opportunity.STATUS_CHOICES,
    }
    return render(request, 'crm/opportunity_list.html', context)

@login_required
def opportunity_detail(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    activities = opportunity.activities.all()
    documents = opportunity.documents.all()
    
    context = {
        'opportunity': opportunity,
        'activities': activities,
        'documents': documents,
    }
    return render(request, 'crm/opportunity_detail.html', context)

@login_required
def opportunity_create(request):
    customer_id = request.GET.get('customer')
    initial = {}
    if customer_id:
        customer = get_object_or_404(Customer, pk=customer_id)
        initial['customer'] = customer
    
    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.save(commit=False)
            opportunity.assigned_to = request.user
            opportunity.save()
            messages.success(request, _('Fırsat başarıyla oluşturuldu.'))
            return redirect('crm:opportunity_detail', pk=opportunity.pk)
    else:
        form = OpportunityForm(initial=initial)
    
    context = {
        'form': form,
        'title': _('Yeni Fırsat'),
    }
    return render(request, 'crm/opportunity_form.html', context)

@login_required
def opportunity_update(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    if request.method == 'POST':
        form = OpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            opportunity = form.save()
            messages.success(request, _('Fırsat başarıyla güncellendi.'))
            return redirect('crm:opportunity_detail', pk=opportunity.pk)
    else:
        form = OpportunityForm(instance=opportunity)
    
    context = {
        'form': form,
        'opportunity': opportunity,
        'title': _('Fırsat Düzenle'),
    }
    return render(request, 'crm/opportunity_form.html', context)

@login_required
def opportunity_delete(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    if request.method == 'POST':
        customer_pk = opportunity.customer.pk
        opportunity.delete()
        messages.success(request, _('Fırsat başarıyla silindi.'))
        return redirect('crm:customer_detail', pk=customer_pk)
    
    context = {
        'opportunity': opportunity,
    }
    return render(request, 'crm/opportunity_delete.html', context)

# Aktivite view'ları
@login_required
def activity_list(request):
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    type = request.GET.get('type', '')
    activities = Activity.objects.all()
    
    if search_query:
        activities = activities.filter(
            Q(subject__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    
    if status:
        activities = activities.filter(status=status)
    
    if type:
        activities = activities.filter(type=type)
    
    paginator = Paginator(activities, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status': status,
        'type': type,
        'status_choices': Activity.STATUS_CHOICES,
        'type_choices': Activity.TYPE_CHOICES,
    }
    return render(request, 'crm/activity_list.html', context)

@login_required
def activity_detail(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    context = {'activity': activity}
    return render(request, 'crm/activity_detail.html', context)

@login_required
def activity_create(request):
    customer_id = request.GET.get('customer')
    initial = {}
    if customer_id:
        customer = get_object_or_404(Customer, pk=customer_id)
        initial['customer'] = customer
    
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.assigned_to = request.user
            activity.save()
            messages.success(request, _('Aktivite başarıyla oluşturuldu.'))
            return redirect('crm:activity_detail', pk=activity.pk)
    else:
        form = ActivityForm(initial=initial)
    
    context = {
        'form': form,
        'title': _('Yeni Aktivite'),
    }
    return render(request, 'crm/activity_form.html', context)

@login_required
def activity_update(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            activity = form.save()
            messages.success(request, _('Aktivite başarıyla güncellendi.'))
            return redirect('crm:activity_detail', pk=activity.pk)
    else:
        form = ActivityForm(instance=activity)
    
    context = {
        'form': form,
        'activity': activity,
        'title': _('Aktivite Düzenle'),
    }
    return render(request, 'crm/activity_form.html', context)

@login_required
def activity_delete(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    
    if request.method == 'POST':
        customer_pk = activity.customer.pk
        activity.delete()
        messages.success(request, _('Aktivite başarıyla silindi.'))
        return redirect('crm:customer_detail', pk=customer_pk)
    
    context = {
        'activity': activity,
    }
    return render(request, 'crm/activity_delete.html', context)

# Belge view'ları
@login_required
def document_list(request):
    search_query = request.GET.get('search', '')
    type = request.GET.get('type', '')
    documents = Document.objects.all()
    
    if search_query:
        documents = documents.filter(
            Q(name__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    
    if type:
        documents = documents.filter(type=type)
    
    paginator = Paginator(documents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'type': type,
        'type_choices': Document.TYPE_CHOICES,
    }
    return render(request, 'crm/document_list.html', context)

@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    context = {'document': document}
    return render(request, 'crm/document_detail.html', context)

@login_required
def document_create(request):
    customer_id = request.GET.get('customer')
    initial = {}
    if customer_id:
        customer = get_object_or_404(Customer, pk=customer_id)
        initial['customer'] = customer
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save()
            messages.success(request, _('Belge başarıyla yüklendi.'))
            return redirect('crm:document_detail', pk=document.pk)
    else:
        form = DocumentForm(initial=initial)
    
    context = {
        'form': form,
        'title': _('Yeni Belge'),
    }
    return render(request, 'crm/document_form.html', context)

@login_required
def document_update(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            document = form.save()
            messages.success(request, _('Belge başarıyla güncellendi.'))
            return redirect('crm:document_detail', pk=document.pk)
    else:
        form = DocumentForm(instance=document)
    
    context = {
        'form': form,
        'document': document,
        'title': _('Belge Düzenle'),
    }
    return render(request, 'crm/document_form.html', context)

@login_required
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    if request.method == 'POST':
        customer_pk = document.customer.pk
        document.delete()
        messages.success(request, _('Belge başarıyla silindi.'))
        return redirect('crm:customer_detail', pk=customer_pk)
    
    context = {
        'document': document,
    }
    return render(request, 'crm/document_delete.html', context)

@login_required
def sale_list(request):
    """Satışları listele"""
    sales = Sale.objects.all().select_related('customer', 'created_by')
    
    # Filtreleme
    status_filter = request.GET.get('status')
    if status_filter:
        sales = sales.filter(status=status_filter)
    
    # Arama
    search_query = request.GET.get('search')
    if search_query:
        sales = sales.filter(
            Q(number__icontains=search_query) |
            Q(customer__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Sıralama
    order_by = request.GET.get('order_by', '-date')
    sales = sales.order_by(order_by)
    
    # Sayfalama
    paginator = Paginator(sales, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_count': sales.count(),
        'total_amount': sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'crm/sale_list.html', context)

@login_required
def sale_detail(request, pk):
    """Satış detaylarını görüntüle"""
    sale = get_object_or_404(Sale, pk=pk)
    items = sale.items.all()
    e_documents = sale.e_documents.all().order_by('-created_at')
    
    context = {
        'sale': sale,
        'items': items,
        'e_documents': e_documents,
    }
    
    return render(request, 'crm/sale_detail.html', context)

@login_required
def sale_create(request, customer_id=None):
    """Yeni satış oluştur"""
    customer = None
    if customer_id:
        customer = get_object_or_404(Customer, pk=customer_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer_id = data.get('customer_id')
            date = data.get('date')
            payment_method = data.get('payment_method')
            payment_date = data.get('payment_date')
            description = data.get('description', '')
            items_data = data.get('items', [])
            
            if not customer_id or not date or not items_data:
                return JsonResponse({'status': 'error', 'message': _('Eksik bilgi')}, status=400)
            
            customer = get_object_or_404(Customer, pk=customer_id)
            
            with transaction.atomic():
                # Satış toplamları hesapla
                amount = decimal.Decimal('0.00')
                tax_amount = decimal.Decimal('0.00')
                total_amount = decimal.Decimal('0.00')
                
                for item in items_data:
                    quantity = decimal.Decimal(item.get('quantity', '0'))
                    unit_price = decimal.Decimal(item.get('unit_price', '0'))
                    tax_rate = decimal.Decimal(item.get('tax_rate', '18'))
                    
                    item_amount = quantity * unit_price
                    item_tax = item_amount * (tax_rate / decimal.Decimal('100'))
                    item_total = item_amount + item_tax
                    
                    amount += item_amount
                    tax_amount += item_tax
                    total_amount += item_total
                
                # Satış kaydı oluştur
                sale = Sale.objects.create(
                    customer=customer,
                    date=date,
                    payment_method=payment_method,
                    payment_date=payment_date or None,
                    description=description,
                    amount=amount,
                    tax_amount=tax_amount,
                    total_amount=total_amount,
                    created_by=request.user,
                    status='draft'
                )
                
                # Satış kalemleri ekle
                for item in items_data:
                    quantity = decimal.Decimal(item.get('quantity', '0'))
                    unit_price = decimal.Decimal(item.get('unit_price', '0'))
                    tax_rate = decimal.Decimal(item.get('tax_rate', '18'))
                    
                    item_amount = quantity * unit_price
                    item_tax = item_amount * (tax_rate / decimal.Decimal('100'))
                    item_total = item_amount + item_tax
                    
                    SaleItem.objects.create(
                        sale=sale,
                        product_name=item.get('product_name', ''),
                        description=item.get('description', ''),
                        quantity=quantity,
                        unit_price=unit_price,
                        tax_rate=tax_rate,
                        amount=item_amount,
                        tax_amount=item_tax,
                        total_amount=item_total
                    )
                
                return JsonResponse({
                    'status': 'success', 
                    'message': _('Satış başarıyla oluşturuldu'),
                    'sale_id': sale.id,
                    'redirect_url': reverse('sale_detail', args=[sale.id])
                })
                
        except Exception as e:
            logging.error(f"Satış oluşturma hatası: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    # GET isteği - form görüntüle
    customers = Customer.objects.all()
    context = {
        'customers': customers,
        'customer': customer,
    }
    
    return render(request, 'crm/sale_create.html', context)

@login_required
def sale_update(request, pk):
    """Satış kaydını güncelle"""
    sale = get_object_or_404(Sale, pk=pk)
    
    # Sadece taslak durumundaki satışlar düzenlenebilir
    if not sale.is_editable:
        messages.error(request, _('Onaylanmış satışlar düzenlenemez'))
        return redirect('sale_detail', pk=sale.pk)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date = data.get('date')
            payment_method = data.get('payment_method')
            payment_date = data.get('payment_date')
            description = data.get('description', '')
            items_data = data.get('items', [])
            
            if not date or not items_data:
                return JsonResponse({'status': 'error', 'message': _('Eksik bilgi')}, status=400)
            
            with transaction.atomic():
                # Mevcut kalemleri sil
                sale.items.all().delete()
                
                # Satış toplamları hesapla
                amount = decimal.Decimal('0.00')
                tax_amount = decimal.Decimal('0.00')
                total_amount = decimal.Decimal('0.00')
                
                for item in items_data:
                    quantity = decimal.Decimal(item.get('quantity', '0'))
                    unit_price = decimal.Decimal(item.get('unit_price', '0'))
                    tax_rate = decimal.Decimal(item.get('tax_rate', '18'))
                    
                    item_amount = quantity * unit_price
                    item_tax = item_amount * (tax_rate / decimal.Decimal('100'))
                    item_total = item_amount + item_tax
                    
                    amount += item_amount
                    tax_amount += item_tax
                    total_amount += item_total
                
                # Satış kaydını güncelle
                sale.date = date
                sale.payment_method = payment_method
                sale.payment_date = payment_date or None
                sale.description = description
                sale.amount = amount
                sale.tax_amount = tax_amount
                sale.total_amount = total_amount
                sale.save()
                
                # Satış kalemleri ekle
                for item in items_data:
                    quantity = decimal.Decimal(item.get('quantity', '0'))
                    unit_price = decimal.Decimal(item.get('unit_price', '0'))
                    tax_rate = decimal.Decimal(item.get('tax_rate', '18'))
                    
                    item_amount = quantity * unit_price
                    item_tax = item_amount * (tax_rate / decimal.Decimal('100'))
                    item_total = item_amount + item_tax
                    
                    SaleItem.objects.create(
                        sale=sale,
                        product_name=item.get('product_name', ''),
                        description=item.get('description', ''),
                        quantity=quantity,
                        unit_price=unit_price,
                        tax_rate=tax_rate,
                        amount=item_amount,
                        tax_amount=item_tax,
                        total_amount=item_total
                    )
                
                return JsonResponse({
                    'status': 'success', 
                    'message': _('Satış başarıyla güncellendi'),
                    'redirect_url': reverse('sale_detail', args=[sale.id])
                })
                
        except Exception as e:
            logging.error(f"Satış güncelleme hatası: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    # GET isteği - form görüntüle
    items = list(sale.items.all().values())
    context = {
        'sale': sale,
        'items_json': json.dumps(items, cls=DecimalEncoder),
    }
    
    return render(request, 'crm/sale_update.html', context)

@login_required
def sale_confirm(request, pk):
    """Satışı onayla"""
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == 'POST':
        if not sale.is_editable:
            messages.error(request, _('Bu satış zaten onaylanmış veya iptal edilmiş'))
        else:
            sale.status = 'confirmed'
            sale.save()
            messages.success(request, _('Satış başarıyla onaylandı'))
            
            # Aktivite kaydı oluştur
            Activity.objects.create(
                customer=sale.customer,
                activity_type='sale_confirmed',
                subject=_('Satış onaylandı: {}').format(sale.number),
                description=_('Toplam tutar: {}').format(sale.total_amount),
                created_by=request.user
            )
    
    return redirect('sale_detail', pk=pk)

@login_required
def sale_cancel(request, pk):
    """Satışı iptal et"""
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        if sale.invoice_created:
            messages.error(request, _('Fatura oluşturulmuş satışlar iptal edilemez'))
        else:
            sale.status = 'cancelled'
            sale.description += f"\n\n{_('İptal nedeni')}: {reason}"
            sale.save()
            messages.success(request, _('Satış başarıyla iptal edildi'))
            
            # Aktivite kaydı oluştur
            Activity.objects.create(
                customer=sale.customer,
                activity_type='sale_cancelled',
                subject=_('Satış iptal edildi: {}').format(sale.number),
                description=_('İptal nedeni: {}').format(reason),
                created_by=request.user
            )
    
    return redirect('sale_detail', pk=pk)

@login_required
def create_invoice(request, pk):
    """Satıştan e-fatura/e-arşiv oluştur"""
    sale = get_object_or_404(Sale, pk=pk)
    
    if not sale.is_confirmed:
        messages.error(request, _('Sadece onaylanmış satışlar için fatura oluşturulabilir'))
        return redirect('sale_detail', pk=pk)
    
    if sale.invoice_created:
        messages.error(request, _('Bu satış için zaten bir fatura oluşturulmuş'))
        return redirect('sale_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            # E-fatura mı, e-arşiv mi?
            document_type = request.POST.get('document_type')
            
            if document_type not in ['einvoice', 'earchive']:
                messages.error(request, _('Geçersiz belge tipi'))
                return redirect('sale_detail', pk=pk)
            
            # E-belge servisi entegrasyonu - burada dış API'ye istek gönderilecek
            # Bu örnek için sadece bir simülasyon yapılıyor
            # Gerçek uygulamada API anahtarı ve diğer bilgiler settings veya env'den alınmalı
            api_url = "https://api.ebelge-servisi.com/v1/documents"
            
            # Satış verilerini hazırla
            payload = {
                'documentType': document_type,
                'customer': {
                    'identifier': sale.customer.tax_number or sale.customer.id_number,
                    'name': sale.customer.name,
                    'address': sale.customer.address,
                    'taxOffice': sale.customer.tax_office
                },
                'date': sale.date.strftime('%Y-%m-%d'),
                'items': [
                    {
                        'name': item.product_name,
                        'quantity': float(item.quantity),
                        'unitPrice': float(item.unit_price),
                        'taxRate': float(item.tax_rate),
                        'totalAmount': float(item.total_amount)
                    } for item in sale.items.all()
                ],
                'totalAmount': float(sale.total_amount),
                'taxAmount': float(sale.tax_amount),
                'description': sale.description
            }
            
            # API isteği simülasyonu
            # response = requests.post(api_url, json=payload, headers={'Authorization': 'Bearer API_KEY'})
            # response_data = response.json()
            
            # Simülasyon için başarılı sonuç dönelim
            response_data = {
                'success': True,
                'documentId': f"SIM-{document_type}-{sale.number}",
                'documentNumber': f"DOC-{sale.number}"
            }
            
            # E-belge durumunu kaydet
            e_document = EDocumentStatus.objects.create(
                sale=sale,
                document_type=document_type,
                document_number=response_data['documentNumber'],
                external_id=response_data['documentId'],
                status='processing',
                status_message=_('İşleme alındı')
            )
            
            # Satışı güncelle
            sale.invoice_created = True
            sale.save()
            
            messages.success(request, _('E-belge talebi başarıyla oluşturuldu'))
            
            # Aktivite kaydı oluştur
            Activity.objects.create(
                customer=sale.customer,
                activity_type='document_created',
                subject=_('E-belge oluşturuldu: {}').format(e_document.document_number),
                description=_('Belge tipi: {}').format(e_document.get_document_type_display()),
                created_by=request.user
            )
            
            return redirect('sale_detail', pk=pk)
            
        except Exception as e:
            logging.error(f"E-belge oluşturma hatası: {str(e)}")
            messages.error(request, _('E-belge oluşturulamadı: {}').format(str(e)))
            return redirect('sale_detail', pk=pk)
    
    # GET isteği - form görüntüle
    context = {
        'sale': sale,
    }
    
    return render(request, 'crm/create_invoice.html', context)

@login_required
def update_document_status(request, pk):
    """E-belge durumunu güncelle"""
    e_document = get_object_or_404(EDocumentStatus, pk=pk)
    
    if request.method == 'POST':
        try:
            # E-belge servisi entegrasyonu - durum kontrolü
            # Bu örnek için sadece bir simülasyon yapılıyor
            api_url = f"https://api.ebelge-servisi.com/v1/documents/{e_document.external_id}/status"
            
            # API isteği simülasyonu
            # response = requests.get(api_url, headers={'Authorization': 'Bearer API_KEY'})
            # response_data = response.json()
            
            # Simülasyon için durum değişikliği yapalım
            current_status = e_document.status
            next_status = current_status
            
            if current_status == 'processing':
                next_status = 'sent'
            elif current_status == 'sent':
                next_status = 'delivered'
            elif current_status == 'delivered':
                next_status = 'accepted'
                
            response_data = {
                'success': True,
                'status': next_status,
                'message': _('Durum güncellendi: {}').format(next_status)
            }
            
            # Durum güncelleme
            e_document.status = response_data['status']
            e_document.status_message = response_data['message']
            e_document.save()
            
            messages.success(request, _('E-belge durumu başarıyla güncellendi'))
            
            # Aktivite kaydı oluştur
            Activity.objects.create(
                customer=e_document.sale.customer,
                activity_type='document_status_update',
                subject=_('E-belge durumu güncellendi: {}').format(e_document.document_number),
                description=_('Yeni durum: {}').format(e_document.get_status_display()),
                created_by=request.user
            )
            
        except Exception as e:
            logging.error(f"E-belge durum güncelleme hatası: {str(e)}")
            messages.error(request, _('E-belge durumu güncellenemedi: {}').format(str(e)))
    
    return redirect('sale_detail', pk=e_document.sale.pk)

@login_required
def check_customer_einvoice(request, pk):
    """Müşterinin e-fatura mükellefiyetini kontrol et"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if not customer.tax_number:
        messages.error(request, _('Müşterinin vergi numarası belirtilmemiş'))
        return redirect('customer_detail', pk=pk)
    
    try:
        # E-fatura mükellefiyeti kontrolü
        # Bu örnek için sadece bir simülasyon yapılıyor
        api_url = f"https://api.ebelge-servisi.com/v1/taxpayers/{customer.tax_number}"
        
        # API isteği simülasyonu
        # response = requests.get(api_url, headers={'Authorization': 'Bearer API_KEY'})
        # response_data = response.json()
        
        # Simülasyon için vergi numarası son hanesine göre karar verelim
        tax_number = customer.tax_number.strip()
        is_einvoice_taxpayer = tax_number[-1] in ['0', '2', '4', '6', '8']
        
        response_data = {
            'success': True,
            'isEInvoiceTaxpayer': is_einvoice_taxpayer,
            'registryDate': '2023-01-01' if is_einvoice_taxpayer else None
        }
        
        # Müşteri bilgilerini güncelle
        customer.is_einvoice_user = response_data['isEInvoiceTaxpayer']
        customer.einvoice_registry_date = datetime.strptime(response_data['registryDate'], '%Y-%m-%d') if response_data['registryDate'] else None
        customer.save()
        
        if customer.is_einvoice_user:
            messages.success(request, _('Müşteri e-fatura mükellefidir'))
        else:
            messages.info(request, _('Müşteri e-fatura mükellefi değildir'))
        
        # Aktivite kaydı oluştur
        Activity.objects.create(
            customer=customer,
            activity_type='einvoice_check',
            subject=_('E-fatura mükellefiyeti kontrolü'),
            description=_('Sonuç: {}').format(_('Mükellef') if customer.is_einvoice_user else _('Mükellef değil')),
            created_by=request.user
        )
        
    except Exception as e:
        logging.error(f"E-fatura mükellefiyet kontrolü hatası: {str(e)}")
        messages.error(request, _('E-fatura mükellefiyet kontrolü başarısız: {}').format(str(e)))
    
    return redirect('customer_detail', pk=pk)

@login_required
def sync_accounting(request, pk):
    """Satışı muhasebe sistemi ile senkronize et"""
    sale = get_object_or_404(Sale, pk=pk)
    
    if not sale.is_confirmed:
        messages.error(request, _('Sadece onaylanmış satışlar muhasebe ile senkronize edilebilir'))
        return redirect('sale_detail', pk=pk)
    
    if sale.accounting_synced:
        messages.error(request, _('Bu satış zaten muhasebe ile senkronize edilmiş'))
        return redirect('sale_detail', pk=pk)
    
    try:
        # Muhasebe entegrasyonu - örneğin entegre bir muhasebe yazılımı API'si ile
        # Bu örnek için sadece bir simülasyon yapılıyor
        api_url = "https://api.muhasebe-yazilimi.com/v1/sales"
        
        # API isteği simülasyonu
        payload = {
            'documentNumber': sale.number,
            'date': sale.date.strftime('%Y-%m-%d'),
            'customerId': sale.customer.id,
            'customerName': sale.customer.name,
            'customerTaxNumber': sale.customer.tax_number,
            'amount': float(sale.amount),
            'taxAmount': float(sale.tax_amount),
            'totalAmount': float(sale.total_amount),
            'items': [
                {
                    'description': item.product_name,
                    'quantity': float(item.quantity),
                    'unitPrice': float(item.unit_price),
                    'taxRate': float(item.tax_rate),
                    'amount': float(item.amount),
                    'taxAmount': float(item.tax_amount),
                    'totalAmount': float(item.total_amount)
                } for item in sale.items.all()
            ]
        }
        
        # response = requests.post(api_url, json=payload, headers={'Authorization': 'Bearer API_KEY'})
        # response_data = response.json()
        
        # Simülasyon için başarılı sonuç dönelim
        response_data = {
            'success': True,
            'reference': f"ACC-{sale.number}",
            'message': 'Başarıyla muhasebe sistemine kaydedildi'
        }
        
        # Satışı güncelle
        sale.accounting_synced = True
        sale.save()
        
        messages.success(request, _('Satış muhasebe sistemi ile başarıyla senkronize edildi'))
        
        # Aktivite kaydı oluştur
        Activity.objects.create(
            customer=sale.customer,
            activity_type='accounting_sync',
            subject=_('Muhasebe entegrasyonu: {}').format(sale.number),
            description=_('Referans: {}').format(response_data['reference']),
            created_by=request.user
        )
        
    except Exception as e:
        logging.error(f"Muhasebe entegrasyonu hatası: {str(e)}")
        messages.error(request, _('Muhasebe entegrasyonu başarısız: {}').format(str(e)))
    
    return redirect('sale_detail', pk=pk)

@login_required
def sync_customer_accounting(request, pk):
    """Müşteri bilgilerini muhasebe sistemi ile senkronize et"""
    customer = get_object_or_404(Customer, pk=pk)
    
    try:
        # Muhasebe entegrasyonu - örneğin entegre bir muhasebe yazılımı API'si ile
        # Bu örnek için sadece bir simülasyon yapılıyor
        api_url = "https://api.muhasebe-yazilimi.com/v1/customers"
        
        # API isteği simülasyonu
        payload = {
            'name': customer.name,
            'taxNumber': customer.tax_number,
            'idNumber': customer.id_number,
            'address': customer.address,
            'taxOffice': customer.tax_office,
            'phone': customer.phone,
            'email': customer.email,
            'isCompany': customer.is_company
        }
        
        # response = requests.post(api_url, json=payload, headers={'Authorization': 'Bearer API_KEY'})
        # response_data = response.json()
        
        # Simülasyon için başarılı sonuç dönelim
        response_data = {
            'success': True,
            'reference': f"CUST-{customer.id}",
            'message': 'Müşteri bilgileri muhasebe sistemine aktarıldı'
        }
        
        messages.success(request, _('Müşteri bilgileri muhasebe sistemi ile başarıyla senkronize edildi'))
        
        # Aktivite kaydı oluştur
        Activity.objects.create(
            customer=customer,
            activity_type='accounting_sync',
            subject=_('Müşteri muhasebe entegrasyonu'),
            description=_('Referans: {}').format(response_data['reference']),
            created_by=request.user
        )
        
    except Exception as e:
        logging.error(f"Müşteri muhasebe entegrasyonu hatası: {str(e)}")
        messages.error(request, _('Müşteri muhasebe entegrasyonu başarısız: {}').format(str(e)))
    
    return redirect('customer_detail', pk=pk)

@login_required
def acquisition_dashboard(request):
    """Müşteri edinme stratejileri dashboard'u"""
    
    # Servis örneği oluştur
    acquisition_service = CustomerAcquisitionService()
    
    # Son 30 günlük metrikleri al
    metrics = acquisition_service.get_acquisition_metrics()
    
    # Kanal metriklerini al
    channel_metrics = CustomerAcquisitionAnalytics.objects.all()
    
    # Grafik için veri hazırla
    channel_labels = [channel.get_channel_display() for channel in channel_metrics]
    channel_data = [channel.total_customers for channel in channel_metrics]
    
    context = {
        'total_customers': metrics['total_customers'],
        'conversion_rate': metrics['conversion_rate'],
        'acquisition_cost': metrics['acquisition_cost'],
        'lifetime_value': sum(c.average_lifetime_value for c in channel_metrics) / len(channel_metrics) if channel_metrics else 0,
        'channel_metrics': channel_metrics,
        'channel_labels': json.dumps(channel_labels),
        'channel_data': json.dumps(channel_data)
    }
    
    return render(request, 'crm/acquisition_dashboard.html', context)

@login_required
def analytics_dashboard(request):
    analytics_service = CustomerAnalyticsService()
    
    context = {
        'value_segments': analytics_service.get_detailed_customer_segments()['value_segments'],
        'behavior_segments': analytics_service.get_detailed_customer_segments()['behavior_segments'],
        'demographic_segments': analytics_service.get_detailed_customer_segments()['demographic_segments'],
        'engagement_segments': analytics_service.get_detailed_customer_segments()['engagement_segments'],
        'market_analysis': analytics_service.get_market_analysis(),
        'competitor_analysis': analytics_service.get_competitor_analysis(),
        'predictive_analytics': analytics_service.get_predictive_analytics(),
        'revenue_forecast': {
            'labels': ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran'],
            'data': [10000, 12000, 15000, 14000, 16000, 18000]
        }
    }
    
    return render(request, 'crm/analytics_dashboard.html', context)

@login_required
def campaign_list(request):
    """Kampanya listesini görüntüler"""
    campaign_service = CampaignService()
    active_campaigns = campaign_service.get_active_campaigns()
    expired_campaigns = campaign_service.get_expired_campaigns()
    
    context = {
        'active_campaigns': active_campaigns,
        'expired_campaigns': expired_campaigns,
    }
    return render(request, 'crm/campaign_list.html', context)

@login_required
def campaign_detail(request, pk):
    """Kampanya detaylarını görüntüler"""
    campaign = get_object_or_404(Campaign, pk=pk)
    campaign_service = CampaignService()
    performance = campaign_service.get_campaign_performance(campaign)
    
    context = {
        'campaign': campaign,
        'performance': performance,
    }
    return render(request, 'crm/campaign_detail.html', context)

@login_required
def campaign_create(request):
    """Yeni kampanya oluşturur"""
    campaign_service = CampaignService()
    
    if request.method == 'POST':
        campaign_type = request.POST.get('campaign_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        try:
            if campaign_type == 'student':
                campaign = campaign_service.create_student_campaign(start_date, end_date)
            elif campaign_type == 'startup':
                campaign = campaign_service.create_startup_campaign(start_date, end_date)
            elif campaign_type == 'referral':
                campaign = campaign_service.create_referral_campaign(start_date, end_date)
            else:
                messages.error(request, 'Geçersiz kampanya tipi')
                return redirect('campaign_list')
            
            messages.success(request, 'Kampanya başarıyla oluşturuldu')
            return redirect('campaign_detail', pk=campaign.pk)
            
        except Exception as e:
            messages.error(request, f'Kampanya oluşturulurken hata oluştu: {str(e)}')
            return redirect('campaign_list')
    
    return render(request, 'crm/campaign_form.html')

@login_required
def campaign_update(request, pk):
    """Kampanya bilgilerini günceller"""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    if request.method == 'POST':
        try:
            campaign.name = request.POST.get('name')
            campaign.description = request.POST.get('description')
            campaign.start_date = request.POST.get('start_date')
            campaign.end_date = request.POST.get('end_date')
            campaign.status = request.POST.get('status')
            campaign.save()
            
            messages.success(request, 'Kampanya başarıyla güncellendi')
            return redirect('campaign_detail', pk=campaign.pk)
            
        except Exception as e:
            messages.error(request, f'Kampanya güncellenirken hata oluştu: {str(e)}')
            return redirect('campaign_detail', pk=campaign.pk)
    
    context = {
        'campaign': campaign,
    }
    return render(request, 'crm/campaign_form.html', context)

@login_required
def campaign_delete(request, pk):
    """Kampanyayı siler"""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    if request.method == 'POST':
        try:
            campaign.delete()
            messages.success(request, 'Kampanya başarıyla silindi')
            return redirect('campaign_list')
            
        except Exception as e:
            messages.error(request, f'Kampanya silinirken hata oluştu: {str(e)}')
            return redirect('campaign_detail', pk=campaign.pk)
    
    context = {
        'campaign': campaign,
    }
    return render(request, 'crm/campaign_confirm_delete.html', context)

@login_required
def campaign_performance(request, pk):
    """Kampanya performans analizini görüntüler"""
    campaign = get_object_or_404(Campaign, pk=pk)
    campaign_service = CampaignService()
    performance = campaign_service.get_campaign_performance(campaign)
    
    context = {
        'campaign': campaign,
        'performance': performance,
    }
    return render(request, 'crm/campaign_performance.html', context)

class DecimalEncoder(json.JSONEncoder):
    """Decimal türündeki değerleri JSON'a dönüştürmek için encoder"""
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)
