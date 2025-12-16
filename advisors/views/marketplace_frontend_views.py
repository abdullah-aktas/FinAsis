# -*- coding: utf-8 -*-
"""
Mali Müşavir Marketplace Frontend Views
Template-based views for marketplace UI
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from ..models_marketplace import (
    ConsultantProfile,
    ConsultantService,
    ConsultationBooking,
    ConsultantAvailability,
)
from ..forms import ConsultationBookingForm


def consultant_list(request):
    """Mali müşavir listesi (public)"""
    consultants = ConsultantProfile.objects.filter(
        approval_status='approved',
        accepts_new_clients=True
    ).select_related('advisor', 'advisor__user')
    
    # Filtreleme
    city = request.GET.get('city')
    if city:
        consultants = consultants.filter(city=city)
    
    specialization = request.GET.get('specialization')
    if specialization:
        consultants = consultants.filter(specializations__contains=[specialization])
    
    # Sıralama
    sort = request.GET.get('sort', 'rating')
    if sort == 'rating':
        consultants = consultants.order_by('-average_rating', '-total_reviews')
    elif sort == 'price':
        consultants = consultants.order_by('hourly_rate')
    elif sort == 'reviews':
        consultants = consultants.order_by('-total_reviews')
    else:
        consultants = consultants.order_by('-is_featured', '-average_rating')
    
    # Şehirler ve uzmanlıklar (filtre için)
    cities = ConsultantProfile.objects.filter(
        approval_status='approved'
    ).values_list('city', flat=True).distinct().order_by('city')
    
    all_specializations = set()
    for consultant in ConsultantProfile.objects.filter(approval_status='approved'):
        if consultant.specializations:
            all_specializations.update(consultant.specializations)
    specializations = sorted(list(all_specializations))
    
    # Sayfalama
    paginator = Paginator(consultants, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'consultants': page_obj,
        'cities': cities,
        'specializations': specializations,
        'page_obj': page_obj,
    }
    
    return render(request, 'advisors/marketplace/consultant_list.html', context)


def consultant_detail(request, consultant_id):
    """Mali müşavir detay sayfası"""
    consultant = get_object_or_404(
        ConsultantProfile.objects.select_related('advisor', 'advisor__user'),
        id=consultant_id,
        approval_status='approved'
    )
    
    # Hizmetler
    services = consultant.services.filter(is_active=True)
    
    # Müsaitlik
    availability = consultant.availability_slots.filter(is_available=True)
    
    # Değerlendirmeler
    reviews = consultant.reviews.filter(is_published=True).select_related('client')[:10]
    
    context = {
        'consultant': consultant,
        'services': services,
        'availability': availability,
        'reviews': reviews,
    }
    
    return render(request, 'advisors/marketplace/consultant_detail.html', context)


@login_required
def booking_create(request, consultant_id):
    """Randevu oluşturma formu"""
    consultant = get_object_or_404(
        ConsultantProfile.objects.select_related('advisor', 'advisor__user'),
        id=consultant_id,
        approval_status='approved',
        accepts_new_clients=True
    )
    
    if request.method == 'POST':
        form = ConsultationBookingForm(request.POST, consultant=consultant)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = request.user
            booking.consultant = consultant
            
            # Booking number oluştur
            from datetime import datetime
            booking.booking_number = f"BOOK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            booking.save()
            
            # Eğer instant_booking ise otomatik onayla
            if consultant.instant_booking:
                booking.confirm()
                messages.success(request, _("Randevunuz onaylandı!"))
            else:
                messages.success(request, _("Randevu talebiniz gönderildi. Onay bekleniyor."))
            
            return redirect('advisors:marketplace:booking-detail', booking_id=booking.id)
    else:
        form = ConsultationBookingForm(consultant=consultant)
    
    context = {
        'consultant': consultant,
        'form': form,
    }
    
    return render(request, 'advisors/marketplace/booking_form.html', context)


@login_required
def booking_detail(request, booking_id):
    """Randevu detay sayfası"""
    booking = get_object_or_404(
        ConsultationBooking.objects.select_related('consultant', 'client', 'service'),
        id=booking_id
    )
    
    # Sadece müşteri veya mali müşavir görebilir
    if booking.client != request.user and booking.consultant.advisor.user != request.user:
        messages.error(request, _("Bu randevuyu görüntüleme yetkiniz yok."))
        return redirect('advisors:marketplace:consultant-list')
    
    context = {
        'booking': booking,
        'is_client': booking.client == request.user,
        'is_consultant': booking.consultant.advisor.user == request.user,
    }
    
    return render(request, 'advisors/marketplace/booking_detail.html', context)

