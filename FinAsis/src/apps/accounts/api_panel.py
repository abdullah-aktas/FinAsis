# -*- coding: utf-8 -*-
"""
Kullanıcı Panel API
Mobil ve SPA desteği için RESTful endpoint'ler.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def panel_data_api(request):
    """
    Kullanıcı panel verisi API.
    GET /api/v1/panel/ - Kullanıcının kişisel panel verilerini döner.
    
    Response:
    {
        "user": {...},
        "company": {...},
        "roles": [...],
        "stats": {...},
        "charts": {...},
        "recent_transactions": [...],
        "ai_recommendations": [...],
        "role_insights": [...]
    }
    """
    user = request.user
    user_company = getattr(user, 'company', None)
    
    # Rol etiketleri
    user_roles = []
    try:
        user_groups = list(user.groups.all().values_list('name', flat=True))
        for g in user_groups:
            g_lower = g.lower()
            if 'manager' in g_lower or 'yonetici' in g_lower:
                user_roles.append('manager')
            if 'accountant' in g_lower or 'muhasebeci' in g_lower:
                user_roles.append('accountant')
            if 'operation' in g_lower or 'operasyon' in g_lower:
                user_roles.append('operation')
    except Exception:
        pass
    
    if user.is_staff or user.is_superuser:
        user_roles.append('manager')
    
    user_roles = list(set(user_roles))
    
    # Response verisi
    data = {
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name() or user.username,
            'email': user.email,
        },
        'company': None,
        'roles': user_roles,
        'stats': {},
        'charts': {},
        'recent_transactions': [],
        'ai_recommendations': [],
        'role_insights': [],
    }
    
    # Şirket bilgisi
    if user_company:
        data['company'] = {
            'id': user_company.id,
            'name': user_company.name,
        }
        
        # İstatistikler
        try:
            from src.apps.accounting.models import Invoice, Expense, BankTransaction
            
            data['stats']['invoice_count'] = Invoice.objects.filter(
                company=user_company
            ).count()
            
            data['stats']['expense_count'] = Expense.objects.filter(
                company=user_company
            ).count()
            
            data['stats']['transaction_count'] = BankTransaction.objects.filter(
                bank_account__company=user_company
            ).count()
            
            # Grafik verileri (son 6 ay)
            invoice_trend = []
            expense_trend = []
            for i in range(5, -1, -1):
                month_start = timezone.now() - timedelta(days=30 * i)
                month_end = timezone.now() - timedelta(days=30 * (i - 1)) if i > 0 else timezone.now()
                
                invoice_total = Invoice.objects.filter(
                    company=user_company,
                    issue_date__gte=month_start,
                    issue_date__lt=month_end
                ).aggregate(total=Sum('total_amount'))['total'] or 0
                
                expense_total = Expense.objects.filter(
                    company=user_company,
                    date__gte=month_start,
                    date__lt=month_end
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                invoice_trend.append({
                    'month': month_start.strftime('%b'),
                    'total': float(invoice_total)
                })
                expense_trend.append({
                    'month': month_start.strftime('%b'),
                    'total': float(expense_total)
                })
            
            data['charts']['income_trend'] = invoice_trend
            data['charts']['expense_trend'] = expense_trend
            
            # Son işlemler
            recent_invoices = Invoice.objects.filter(
                company=user_company
            ).order_by('-issue_date')[:3]
            
            recent_expenses = Expense.objects.filter(
                company=user_company
            ).order_by('-date')[:3]
            
            for inv in recent_invoices:
                data['recent_transactions'].append({
                    'type': 'income',
                    'description': f"Fatura: {getattr(inv, 'invoice_no', getattr(inv, 'number', 'N/A'))}",
                    'amount': float(getattr(inv, 'total_amount', 0)),
                    'date': getattr(inv, 'issue_date', timezone.now()).isoformat(),
                })
            
            for exp in recent_expenses:
                data['recent_transactions'].append({
                    'type': 'expense',
                    'description': f"Gider: {getattr(exp, 'description', getattr(exp, 'name', 'N/A'))}",
                    'amount': float(getattr(exp, 'amount', 0)),
                    'date': getattr(exp, 'date', getattr(exp, 'created_at', timezone.now())).isoformat(),
                })
            
            # Tarihe göre sırala
            data['recent_transactions'].sort(key=lambda x: x['date'], reverse=True)
            data['recent_transactions'] = data['recent_transactions'][:5]
            
        except Exception as e:
            data['stats']['error'] = str(e)
    
    # AI önerileri
    try:
        from src.apps.ai_assistant.models import UserInteraction
        
        data['stats']['ai_interaction_count'] = UserInteraction.objects.filter(
            user=user
        ).count()
        
        ai_recs = UserInteraction.objects.filter(
            user=user,
            interaction_type='recommendation'
        ).order_by('-created_at')[:3]
        
        data['ai_recommendations'] = [{
            'created_at': rec.created_at.isoformat(),
            'response': rec.ai_response[:150],
        } for rec in ai_recs]
        
    except Exception:
        pass
    
    # Rol bazlı içgörüler
    if 'manager' in user_roles:
        data['role_insights'].append({
            'title': 'Yönetici İçgörüsü',
            'icon': 'briefcase',
            'color': 'primary',
            'message': 'Nakit akışı görünürlüğünü artırmak için haftalık raporları inceleyin.',
        })
    if 'accountant' in user_roles:
        data['role_insights'].append({
            'title': 'Muhasebe Uyarısı',
            'icon': 'calculator',
            'color': 'warning',
            'message': 'Bekleyen mutabakat kayıtlarını kontrol edin.',
        })
    if 'operation' in user_roles:
        data['role_insights'].append({
            'title': 'Operasyon',
            'icon': 'gear',
            'color': 'info',
            'message': 'Geciken tahsilatlar için otomatik hatırlatma ayarlayın.',
        })
    
    return Response(data, status=status.HTTP_200_OK)
