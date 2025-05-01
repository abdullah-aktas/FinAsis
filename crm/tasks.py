# -*- coding: utf-8 -*-
from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from .models import (
    Customer,
    Opportunity,
    Activity,
    Communication,
    CustomerLoyalty,
    SeasonalCampaign
)
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_overdue_activities():
    """Gecikmiş aktiviteleri kontrol et"""
    try:
        overdue_activities = Activity.objects.filter(
            due_date__lt=timezone.now(),
            is_completed=False
        )
        
        for activity in overdue_activities:
            activity.is_overdue = True
            activity.save()
            
            logger.info(f"Gecikmiş aktivite tespit edildi: {activity}")
            
    except Exception as e:
        logger.error(f"Gecikmiş aktivite kontrolü sırasında hata: {str(e)}")


@shared_task
def update_customer_credit_scores():
    """Müşteri kredi skorlarını güncelle"""
    try:
        customers = Customer.objects.all()
        
        for customer in customers:
            # Kredi skoru hesaplama mantığı
            base_score = 500
            adjustments = 0
            
            # Fırsat bazlı ayarlamalar
            won_opportunities = Opportunity.objects.filter(
                customer=customer,
                stage='won'
            ).count()
            adjustments += won_opportunities * 10
            
            # İletişim bazlı ayarlamalar
            recent_communications = Communication.objects.filter(
                customer=customer,
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count()
            adjustments += recent_communications * 5
            
            # Aktivite bazlı ayarlamalar
            completed_activities = Activity.objects.filter(
                Q(opportunity__customer=customer) | Q(customer=customer),
                is_completed=True
            ).count()
            adjustments += completed_activities * 3
            
            # Gecikmiş aktiviteler için ceza
            overdue_activities = Activity.objects.filter(
                Q(opportunity__customer=customer) | Q(customer=customer),
                is_overdue=True
            ).count()
            adjustments -= overdue_activities * 15
            
            # Skoru güncelle
            new_score = min(max(base_score + adjustments, 300), 850)
            customer.credit_score = new_score
            customer.save()
            
            logger.info(f"Müşteri kredi skoru güncellendi: {customer} - Yeni skor: {new_score}")
            
    except Exception as e:
        logger.error(f"Kredi skoru güncelleme sırasında hata: {str(e)}")


@shared_task
def process_seasonal_campaigns():
    """Mevsimsel kampanyaları işle"""
    try:
        active_campaigns = SeasonalCampaign.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )
        
        for campaign in active_campaigns:
            # Kampanya hedef müşterileri
            target_customers = Customer.objects.filter(
                industry__in=campaign.target_industries.all()
            )
            
            for customer in target_customers:
                # Kampanya puanlarını ekle
                loyalty, created = CustomerLoyalty.objects.get_or_create(
                    customer=customer,
                    program=campaign.loyalty_program
                )
                
                loyalty.points += campaign.points
                loyalty.save()
                
                logger.info(
                    f"Kampanya puanları eklendi: {customer} - "
                    f"Kampanya: {campaign} - Puanlar: {campaign.points}"
                )
                
    except Exception as e:
        logger.error(f"Kampanya işleme sırasında hata: {str(e)}")


@shared_task
def send_opportunity_reminders():
    """Fırsat hatırlatmalarını gönder"""
    try:
        upcoming_opportunities = Opportunity.objects.filter(
            stage__in=['proposal', 'negotiation'],
            next_followup__lte=timezone.now() + timezone.timedelta(days=1)
        )
        
        for opportunity in upcoming_opportunities:
            # Hatırlatma gönderme mantığı
            logger.info(
                f"Fırsat hatırlatması gönderildi: {opportunity} - "
                f"Sonraki takip: {opportunity.next_followup}"
            )
            
    except Exception as e:
        logger.error(f"Fırsat hatırlatması gönderme sırasında hata: {str(e)}") 