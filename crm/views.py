from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Customer, Contact, Opportunity, Activity, Document
from .forms import CustomerForm, ContactForm, OpportunityForm, ActivityForm, DocumentForm

# Müşteri view'ları
@login_required
def customer_list(request):
    search_query = request.GET.get('search', '')
    customers = Customer.objects.all()
    
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

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    contacts = customer.contacts.all()
    opportunities = customer.opportunities.all()
    activities = customer.activities.all()
    documents = customer.documents.all()
    
    context = {
        'customer': customer,
        'contacts': contacts,
        'opportunities': opportunities,
        'activities': activities,
        'documents': documents,
    }
    return render(request, 'crm/customer_detail.html', context)

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, _('Müşteri başarıyla oluşturuldu.'))
            return redirect('crm:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    
    context = {
        'form': form,
        'title': _('Yeni Müşteri'),
    }
    return render(request, 'crm/customer_form.html', context)

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
