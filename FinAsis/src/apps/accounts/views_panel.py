# -*- coding: utf-8 -*-
"""
Kullanıcı Kişisel Panel View
Giriş yapmış kullanıcının kendi verilerini görüntülediği güvenli dashboard.
Grafikler, son işlemler, öneri kartları ve rol bazlı widget'lar içerir.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import json


def _get_user_role_tags(user):
    """Kullanıcı rol etiketlerini döndür (yönetici/muhasebeci/operasyon)"""
    roles = set()
    try:
        user_groups = list(user.groups.all().values_list('name', flat=True))
        for g in user_groups:
            g_lower = g.lower()
            if 'manager' in g_lower or 'yonetici' in g_lower:
                roles.add('manager')
            if 'accountant' in g_lower or 'muhasebeci' in g_lower:
                roles.add('accountant')
            if 'operation' in g_lower or 'operasyon' in g_lower:
                roles.add('operation')
    except Exception:
        pass
    
    if user.is_staff or user.is_superuser:
        roles.add('manager')
    
    return list(roles)


@login_required
def user_panel(request):
    """
    Kullanıcı kişisel paneli.
    Sadece giriş yapmış kullanıcının kendi verilerini gösterir.
    Rol bazlı widget'lar ve grafiklerle zenginleştirilmiş.
    """
    user = request.user
    
    # Kullanıcıya ait şirket bilgisi (varsa)
    user_company = getattr(user, 'company', None)
    
    # Rol etiketleri
    user_roles = _get_user_role_tags(user)
    
    # Özet istatistikler (kullanıcıya özel)
    context = {
        'user': user,
        'company': user_company,
        'user_roles': user_roles,
        'panel_title': f"{user.get_full_name() or user.username} - Kişisel Panel",
    }
    
    # Muhasebe modülü istatistikleri (eğer kullanıcının şirketi varsa)
    if user_company:
        try:
            from src.apps.accounting.models import Invoice, Expense, BankTransaction
            
            # Son 30 günün verileri
            last_30_days = timezone.now() - timedelta(days=30)
            
            # Faturalar
            invoices_qs = Invoice.objects.filter(company=user_company)
            context['invoice_count'] = invoices_qs.count()
            context['recent_invoices'] = invoices_qs.order_by('-issue_date')[:5]
            
            # Son 6 aylık gelir trendi (grafik için)
            invoice_trend = []
            for i in range(5, -1, -1):
                month_start = timezone.now() - timedelta(days=30 * i)
                month_end = timezone.now() - timedelta(days=30 * (i - 1)) if i > 0 else timezone.now()
                month_total = invoices_qs.filter(
                    issue_date__gte=month_start,
                    issue_date__lt=month_end
                ).aggregate(total=Sum('total_amount'))['total'] or 0
                invoice_trend.append({
                    'month': month_start.strftime('%b'),
                    'total': float(month_total)
                })
            context['invoice_trend_json'] = json.dumps(invoice_trend)
            
            # Giderler
            expenses_qs = Expense.objects.filter(company=user_company)
            context['expense_count'] = expenses_qs.count()
            context['recent_expenses'] = expenses_qs.order_by('-date')[:5]
            
            # Son 6 aylık gider trendi
            expense_trend = []
            for i in range(5, -1, -1):
                month_start = timezone.now() - timedelta(days=30 * i)
                month_end = timezone.now() - timedelta(days=30 * (i - 1)) if i > 0 else timezone.now()
                month_total = expenses_qs.filter(
                    date__gte=month_start,
                    date__lt=month_end
                ).aggregate(total=Sum('amount'))['total'] or 0
                expense_trend.append({
                    'month': month_start.strftime('%b'),
                    'total': float(month_total)
                })
            context['expense_trend_json'] = json.dumps(expense_trend)
            
            # Banka işlemleri
            context['transaction_count'] = BankTransaction.objects.filter(
                bank_account__company=user_company
            ).count()
            
            # Son işlemler (gelir/gider karışık)
            recent_transactions = []
            for inv in context['recent_invoices'][:3]:
                recent_transactions.append({
                    'type': 'income',
                    'description': f"Fatura: {getattr(inv, 'invoice_no', getattr(inv, 'number', 'N/A'))}",
                    'amount': getattr(inv, 'total_amount', 0),
                    'date': getattr(inv, 'issue_date', timezone.now()),
                })
            for exp in context['recent_expenses'][:3]:
                recent_transactions.append({
                    'type': 'expense',
                    'description': f"Gider: {getattr(exp, 'description', getattr(exp, 'name', 'N/A'))}",
                    'amount': getattr(exp, 'amount', 0),
                    'date': getattr(exp, 'date', getattr(exp, 'created_at', timezone.now())),
                })
            # Tarihe göre sırala
            recent_transactions.sort(key=lambda x: x['date'], reverse=True)
            context['recent_transactions'] = recent_transactions[:5]
            
        except Exception:
            # Modül yüklü değilse sessizce geç
            pass
    
    # AI asistan etkileşim sayısı ve son öneriler
    try:
        from src.apps.ai_assistant.models import UserInteraction
        context['ai_interaction_count'] = UserInteraction.objects.filter(
            user=user
        ).count()
        
        # Son AI önerileri (varsa)
        ai_recommendations = UserInteraction.objects.filter(
            user=user,
            interaction_type='recommendation'
        ).order_by('-created_at')[:3]
        context['ai_recommendations'] = ai_recommendations
        
    except Exception:
        pass
    
    # Kullanıcı başarıları (gamification)
    try:
        from src.apps.accounts.models import Achievement
        context['achievement_count'] = user.achievements.count() if hasattr(user, 'achievements') else 0
        context['recent_achievements'] = user.achievements.all()[:3] if hasattr(user, 'achievements') else []
    except Exception:
        pass
    
    # Rol bazlı öneri kartları
    role_insights = []
    if 'manager' in user_roles:
        role_insights.append({
            'title': 'Yönetici İçgörüsü',
            'icon': 'bi-briefcase',
            'color': 'primary',
            'message': 'Nakit akışı görünürlüğünü artırmak için haftalık raporları inceleyin.',
        })
    if 'accountant' in user_roles:
        role_insights.append({
            'title': 'Muhasebe Uyarısı',
            'icon': 'bi-calculator',
            'color': 'warning',
            'message': 'Bekleyen mutabakat kayıtlarını kontrol edin.',
        })
    if 'operation' in user_roles:
        role_insights.append({
            'title': 'Operasyon',
            'icon': 'bi-gear',
            'color': 'info',
            'message': 'Geciken tahsilatlar için otomatik hatırlatma ayarlayın.',
        })
    
    context['role_insights'] = role_insights
    
    return render(request, 'panel/user_panel.html', context)

