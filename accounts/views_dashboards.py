"""
Kullanıcı tipine özel fonksiyonel dashboard view'ları
"""
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from accounting.models import Company
from finance.models import Invoice, Expense, BankAccount, BankTransaction
from accounts.models import Achievement
from ai_assistant.services import prompt_registry
from games import task_engine


@login_required
def kobi_dashboard(request):
    """KOBİ kullanıcıları için fonksiyonel dashboard"""
    company = getattr(request.user, 'company', None)
    
    # Finansal özet
    finans_ozet = {
        'toplam_gelir': 0,
        'toplam_gider': 0,
        'net_kar': 0,
        'banka_bakiye': 0,
    }
    
    if company:
        today = datetime.now().date()
        this_month_start = today.replace(day=1)
        
        # Gelirler (Faturalar)
        gelirler = Invoice.objects.filter(
            company=company, 
            issue_date__gte=this_month_start
        ).aggregate(toplam=Sum('total_amount'))
        finans_ozet['toplam_gelir'] = float(gelirler['toplam'] or 0)
        
        # Giderler
        giderler = Expense.objects.filter(
            company=company,
            expense_date__gte=this_month_start
        ).aggregate(toplam=Sum('amount'))
        finans_ozet['toplam_gider'] = float(giderler['toplam'] or 0)
        
        finans_ozet['net_kar'] = finans_ozet['toplam_gelir'] - finans_ozet['toplam_gider']
        
        # Banka bakiyesi
        banka_hesaplari = BankAccount.objects.filter(company=company)
        bakiye = banka_hesaplari.aggregate(toplam=Sum('balance'))
        finans_ozet['banka_bakiye'] = float(bakiye['toplam'] or 0)
    
    # Son işlemler
    son_faturalar = Invoice.objects.filter(company=company).order_by('-issue_date')[:5] if company else []
    son_giderler = Expense.objects.filter(company=company).order_by('-expense_date')[:5] if company else []
    
    context = {
        'finans_ozet': finans_ozet,
        'son_faturalar': son_faturalar,
        'son_giderler': son_giderler,
        'company': company,
    }
    
    return render(request, 'accounts/dashboard_kobi.html', context)


@login_required
def muhasebeci_dashboard(request):
    """Muhasebeci kullanıcıları için dashboard"""
    # Muhasebeciler birden fazla şirketi yönetebilir
    user_companies = Company.objects.all()[:10]  # İlk 10 şirket
    
    # İstatistikler
    stats = {
        'toplam_sirket': user_companies.count(),
        'bu_ay_fatura': 0,
        'bekleyen_islem': 0,
    }
    
    today = datetime.now().date()
    this_month_start = today.replace(day=1)
    
    stats['bu_ay_fatura'] = Invoice.objects.filter(
        issue_date__gte=this_month_start
    ).count()
    
    context = {
        'stats': stats,
        'companies': user_companies,
    }
    
    return render(request, 'accounts/dashboard_muhasebeci.html', context)


@login_required
def mali_musavir_dashboard(request):
    """Mali müşavir kullanıcıları için dashboard"""
    # Mali müşavirler analiz ve danışmanlık yapar
    companies = Company.objects.all()[:5]
    
    # Her şirket için özet
    company_summaries = []
    toplam_gelir = 0.0
    toplam_gider = 0.0
    for company in companies:
        today = datetime.now().date()
        this_month_start = today.replace(day=1)
        
        gelir = Invoice.objects.filter(
            company=company,
            issue_date__gte=this_month_start
        ).aggregate(toplam=Sum('total_amount'))['toplam'] or 0
        
        gider = Expense.objects.filter(
            company=company,
            expense_date__gte=this_month_start
        ).aggregate(toplam=Sum('amount'))['toplam'] or 0
        
        company_summaries.append({
            'company': company,
            'gelir': float(gelir),
            'gider': float(gider),
            'kar': float(gelir) - float(gider),
        })
        toplam_gelir += float(gelir)
        toplam_gider += float(gider)
    
    toplam_musteri = len(company_summaries)
    toplam_kar = toplam_gelir - toplam_gider
    ortalama_marj = toplam_kar / toplam_musteri if toplam_musteri else 0.0
    
    kpi_cards = [
        {
            'label': _('Aktif Müşteri'),
            'value': toplam_musteri,
            'icon': 'bi-people-fill',
            'meta': _('Portföydeki müşteri sayısı'),
            'accent': '#0AAE94',
        },
        {
            'label': _('Aylık Gelir'),
            'value': f"{toplam_gelir:,.0f} ₺",
            'icon': 'bi-bar-chart-line',
            'meta': _('Bu ay kesilen faturalar'),
            'accent': '#4c5fd4',
        },
        {
            'label': _('Uyumluluk Görevi'),
            'value': _('3 bekliyor'),
            'icon': 'bi-shield-check',
            'meta': _('MASAK & KVKK checklist'),
            'accent': '#f59e0b',
        },
        {
            'label': _('Ortalama Marj'),
            'value': f"{ortalama_marj:,.0f} ₺",
            'icon': 'bi-currency-exchange',
            'meta': _('Aylık kârlılık ortalaması'),
            'accent': '#10b981',
        },
    ]
    
    advisor_tasks = [
        {
            'title': _('KVKK veri saklama kontrolü'),
            'due': _('Bugün'),
            'status': 'warning',
            'icon': 'bi-shield-lock',
        },
        {
            'title': _('Nakit akışı raporu paylaş'),
            'due': _('Yarın'),
            'status': 'info',
            'icon': 'bi-graph-up',
        },
        {
            'title': _('Yeni müşteri onboarding toplantısı'),
            'due': _('2 gün içinde'),
            'status': 'default',
            'icon': 'bi-calendar-event',
        },
    ]
    
    ai_cards = prompt_registry.get_prompts_for_role('mali_musavir', limit=3) or [
        {
            'title': _('AI Asistan: Portföy Sağlığı'),
            'body': _('Son 30 gündeki nakit akışı düşen müşteriler için uyarı raporu hazır.'),
            'cta_label': _('Raporu Aç'),
            'cta_href': '/ai-assistant/reports/portfolio-health/',
            'icon': 'bi-stars',
        }
    ]
    
    context = {
        'company_summaries': company_summaries,
        'advisor_kpis': kpi_cards,
        'advisor_tasks': advisor_tasks,
        'ai_cards': ai_cards,
    }
    
    return render(request, 'accounts/dashboard_mali_musavir.html', context)


@login_required
def yatirimci_dashboard(request):
    """Yatırımcı kullanıcıları için dashboard"""
    # Yatırımcılar portföy ve performans takibi yapar
    context = {
        'portfolio_value': 0,
        'today_change': 0,
        'total_return': 0,
    }
    
    return render(request, 'accounts/dashboard_yatirimci.html', context)


# Eğitimci ve Öğrenci dashboard'ları zaten mevcut ama fonksiyonel hale getiriyoruz
@login_required
def egitimci_dashboard_new(request):
    """Eğitimci kullanıcıları için fonksiyonel dashboard"""
    from education.models import Course, Assignment
    
    # Eğitimcinin kursları
    my_courses = Course.objects.filter(instructor=request.user)[:5] if hasattr(Course, 'instructor') else []
    
    # İstatistikler
    stats = {
        'toplam_kurs': my_courses.count() if my_courses else 0,
        'toplam_ogrenci': 0,
        'bekleyen_odev': 0,
    }
    onboarding_steps = task_engine.get_tasks(audience='teacher', kind='onboarding', limit=3) or [
        {
            'title': _('İlk ders planını oluştur'),
            'description': _('Modül > Ders Yönetimi üzerinden yeni ders ekleyin.'),
            'icon': 'bi-journal-plus',
        }
    ]
    teacher_brief = task_engine.get_brief(audience='teacher')
    gamification = {
        'progress': min(100, teacher_brief.get('task_count', 0) * 15 or 30),
        'label': _('Görev motoru XP toplamı'),
        'delta': _('Toplam XP: %(xp)s') % {'xp': teacher_brief.get('total_reward_xp', 0)},
    }
    ai_cards = prompt_registry.get_prompts_for_role('egitimci', limit=3) or [
        {
            'title': _('AI Asistan: Ders özetleri'),
            'body': _('Son derslerin özetini öğrencilerle paylaşmaya hazır bir metin oluşturuldu.'),
            'cta_label': _('Özeti Kopyala'),
            'cta_href': '/ai-assistant/class-summaries/',
            'icon': 'bi-magic',
        }
    ]
    
    context = {
        'stats': stats,
        'my_courses': my_courses,
        'teacher_onboarding': onboarding_steps,
        'teacher_gamification': gamification,
        'ai_cards': ai_cards,
    }
    
    return render(request, 'accounts/dashboard_egitimci.html', context)


@login_required
def ogrenci_dashboard_new(request):
    """Öğrenci kullanıcıları için fonksiyonel dashboard"""
    from education.models import Course, Assignment
    
    # Öğrencinin kursları
    my_courses = []  # Course modelinden çekilecek
    
    # İstatistikler
    stats = {
        'aktif_kurs': 0,
        'tamamlanan': 0,
        'bekleyen_odev': 0,
    }
    onboarding_steps = task_engine.get_tasks(audience='student', kind='onboarding', limit=3) or [
        {
            'title': _('Profilini tamamla'),
            'description': _('Avatar seç ve ilgi alanlarını ekle.'),
            'icon': 'bi-person-check',
        }
    ]
    student_brief = task_engine.get_brief(audience='student')
    gamification = {
        'progress': min(100, student_brief.get('task_count', 0) * 12 or 20),
        'label': _('Görev ilerlemesi'),
        'delta': _('Toplam XP: %(xp)s') % {'xp': student_brief.get('total_reward_xp', 0)},
    }
    ai_cards = prompt_registry.get_prompts_for_role('ogrenci', limit=3) or [
        {
            'title': _('AI Asistan: Çalışma planı'),
            'body': _('Bu hafta tamamlaman gereken dersler için günlük plan önerisi hazır.'),
            'cta_label': _('Planı Aç'),
            'cta_href': '/ai-assistant/study-plan/',
            'icon': 'bi-list-task',
        }
    ]
    
    context = {
        'stats': stats,
        'my_courses': my_courses,
        'student_onboarding': onboarding_steps,
        'student_gamification': gamification,
        'ai_cards': ai_cards,
    }
    
    return render(request, 'accounts/dashboard_ogrenci.html', context)

