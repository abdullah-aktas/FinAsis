from datetime import datetime, timedelta
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField
from django.utils import timezone
from apps.finance.models import Transaction, Invoice
from apps.crm.models import Customer
from apps.stock_management.models import StockRequest

class KPIService:
    @staticmethod
    def get_cash_flow_summary(date_range=7):
        """Son 7 günlük nakit akışı özeti"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=date_range)
        
        cash_flow = Transaction.objects.filter(
            date__range=[start_date, end_date]
        ).aggregate(
            total_in=Sum('amount', filter=F('type') == 'IN'),
            total_out=Sum('amount', filter=F('type') == 'OUT')
        )
        
        return {
            'total_in': cash_flow['total_in'] or 0,
            'total_out': cash_flow['total_out'] or 0,
            'net_flow': (cash_flow['total_in'] or 0) - (cash_flow['total_out'] or 0)
        }

    @staticmethod
    def get_overdue_receivables(customer_id=None):
        """Vadesi geçmiş alacaklar"""
        query = Invoice.objects.filter(
            due_date__lt=timezone.now(),
            status='UNPAID'
        )
        
        if customer_id:
            query = query.filter(customer_id=customer_id)
            
        return query.aggregate(
            total_amount=Sum('total_amount'),
            count=Count('id')
        )

    @staticmethod
    def get_expense_trend(months=6):
        """Aylık gider trendi"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30*months)
        
        monthly_expenses = Transaction.objects.filter(
            date__range=[start_date, end_date],
            type='OUT'
        ).annotate(
            month=ExpressionWrapper(
                F('date__year') * 100 + F('date__month'),
                output_field=FloatField()
            )
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        return list(monthly_expenses)

    @staticmethod
    def get_sales_performance(limit=3):
        """En çok satan ürünler ve toplam ciro"""
        from apps.stock_management.models import Product, Sale
        
        top_products = Product.objects.annotate(
            total_sales=Sum('sale__quantity'),
            total_revenue=Sum(F('sale__quantity') * F('sale__unit_price'))
        ).order_by('-total_sales')[:limit]
        
        total_revenue = Sale.objects.aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )['total'] or 0
        
        return {
            'top_products': list(top_products.values('name', 'total_sales', 'total_revenue')),
            'total_revenue': total_revenue
        }

    @staticmethod
    def get_pending_invoices():
        """Bekleyen faturalar"""
        return Invoice.objects.filter(
            status='DRAFT'
        ).aggregate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        )

    @staticmethod
    def get_open_stock_requests():
        """Açık stok talepleri"""
        return StockRequest.objects.filter(
            status='PENDING'
        ).aggregate(
            count=Count('id'),
            total_items=Sum('quantity')
        ) 