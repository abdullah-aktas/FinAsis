from rest_framework import serializers, viewsets, permissions
from .models import Invoice, Expense, BankTransaction, Company, Customer, Product, Sale, Payment, BankAccount, InvoiceItem
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .services.ai_service import suggest_accounting_entry, analyze_financial_data
from .services.gamification_service import award_badge, increase_user_level
from .services.reports import (
    get_company_summary, export_report_to_pdf, export_report_to_excel, export_report_to_json, export_report_to_xml
)

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'issue_date', 'total_amount', 'currency', 'description']

class ExpenseSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    class Meta:
        model = Expense
        fields = ['id', 'category', 'category_display', 'amount', 'expense_date', 'description']

class BankTransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.bank_name', read_only=True)
    class Meta:
        model = BankTransaction
        fields = ['id', 'account_name', 'amount', 'transaction_type', 'description', 'date']

class CompanyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'company')
    def has_object_permission(self, request, view, obj):
        return hasattr(request.user, 'company') and obj.company == request.user.company

class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [CompanyPermission]
    def get_queryset(self):
        return Invoice.objects.filter(company=self.request.user.company)

class ExpenseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [CompanyPermission]
    def get_queryset(self):
        return Expense.objects.filter(company=self.request.user.company)

class BankTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BankTransactionSerializer
    permission_classes = [CompanyPermission]
    def get_queryset(self):
        company = self.request.user.company
        return BankTransaction.objects.filter(account__company=company)

# Company
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Company.objects.filter(is_active=True)

# Customer
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Customer.objects.filter(is_active=True)

# Product
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Product.objects.filter(is_active=True)

# Sale
class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'

class SaleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Sale.objects.filter(is_active=True)

# Payment
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Payment.objects.filter(is_active=True)

# BankAccount
class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'

class BankAccountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return BankAccount.objects.filter(is_active=True)

# InvoiceItem
class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = '__all__'

class InvoiceItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvoiceItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return InvoiceItem.objects.all()

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def webhook_receiver(request):
    """Webhook ile gelen veriyi işler (örnek endpoint)."""
    data = request.data
    # TODO: İşleme ve doğrulama
    return Response({'status': 'success', 'received': data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def sync_data(request):
    """Kullanıcıya ait verileri senkronize eder (örnek endpoint)."""
    # TODO: Gerçek senkronizasyon işlemleri
    return Response({'status': 'success', 'message': 'Veriler senkronize edildi.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ai_suggest_entry(request):
    """AI ile muhasebe kaydı önerisi üretir."""
    company = request.user.company if hasattr(request.user, 'company') else None
    context = request.data.get('context', {})
    suggestion = suggest_accounting_entry(company, context)
    return Response({'suggestion': suggestion}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ai_analyze_finance(request):
    """AI ile finansal analiz ve öneri sunar."""
    company = request.user.company if hasattr(request.user, 'company') else None
    data = request.data.get('data', {})
    analysis = analyze_financial_data(company, data)
    return Response({'analysis': analysis}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def award_user_badge(request):
    """Kullanıcıya rozet verir."""
    badge_type = request.data.get('badge_type')
    award_badge(request.user, badge_type)
    return Response({'status': 'success', 'badge': badge_type}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def level_up_user(request):
    """Kullanıcının seviyesini artırır."""
    increase_user_level(request.user)
    return Response({'status': 'success', 'message': 'Seviye artırıldı.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_summary_pdf(request):
    """Şirket özet raporunu PDF olarak dışa aktarır."""
    company = request.user.company if hasattr(request.user, 'company') else None
    data = get_company_summary(company)
    response = export_report_to_pdf(data, template_name="report/summary.html")
    return response

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_summary_excel(request):
    """Şirket özet raporunu Excel olarak dışa aktarır."""
    company = request.user.company if hasattr(request.user, 'company') else None
    data = get_company_summary(company)
    response = export_report_to_excel(data)
    return response

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_summary_json(request):
    """Şirket özet raporunu JSON olarak dışa aktarır."""
    company = request.user.company if hasattr(request.user, 'company') else None
    data = get_company_summary(company)
    response = export_report_to_json(data)
    return response

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_summary_xml(request):
    """Şirket özet raporunu XML olarak dışa aktarır."""
    company = request.user.company if hasattr(request.user, 'company') else None
    data = get_company_summary(company)
    response = export_report_to_xml(data)
    return response 