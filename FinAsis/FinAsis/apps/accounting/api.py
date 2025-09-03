from rest_framework import serializers, viewsets, permissions
from .models import Invoice, Expense, BankTransaction, Company, Customer, Product, Sale, Payment, BankAccount, InvoiceItem
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .services.ai_service import (
    suggest_accounting_entry, analyze_financial_data, map_ocr_to_voucher_lines, create_voucher_from_lines, suggest_rules_from_samples
)
from FinAsis.apps.ai_assistant.services.ocr_service import OCRService
from django.conf import settings
from FinAsis.apps.ai_assistant.services import LocalSTTService
from .services.ai_service import map_text_to_voucher_lines
from FinAsis.apps.finance.accounting.models import AutoBookingRule
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
def ocr_preview_voucher(request):
    """Yüklenen belgeyi OCR ile okuyup TDHP uyumlu fiş taslağı döndürür."""
    company = request.user.company if hasattr(request.user, 'company') else None
    if not company:
        return Response({'error': 'Şirket bulunamadı.'}, status=status.HTTP_400_BAD_REQUEST)
    if 'file' not in request.FILES:
        return Response({'error': 'Dosya yüklenmedi.'}, status=status.HTTP_400_BAD_REQUEST)
    # Geçici kaydetmeden OCRService doğrudan path istiyor; basit kaydetme
    upload = request.FILES['file']
    import os, uuid
    from django.conf import settings as dj_settings
    temp_dir = os.path.join(dj_settings.MEDIA_ROOT, 'uploads')
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{upload.name}")
    with open(temp_path, 'wb+') as dest:
        for chunk in upload.chunks():
            dest.write(chunk)
    use_google = getattr(settings, 'USE_GOOGLE_VISION', False)
    ocr_service = OCRService(use_google_vision=use_google)
    ocr_data = ocr_service.process_invoice(temp_path)
    try:
        os.remove(temp_path)
    except Exception:
        pass
    mapped = map_ocr_to_voucher_lines(company, ocr_data)
    # JSON döndür: satırlar ve toplam
    lines = [
        {
            'account': l['account'].code,
            'account_name': l['account'].name,
            'description': l['description'],
            'debit': str(l['debit']),
            'credit': str(l['credit']),
        } for l in mapped['lines']
    ]
    return Response({'preview': {'date': mapped['date'], 'reference': mapped['reference'], 'total': str(mapped['total']), 'nature': mapped.get('nature'), 'rule_id': mapped.get('rule_id'), 'lines': lines}}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ocr_confirm_voucher(request):
    """Önizlenen fişi oluşturur (onay akışı)."""
    company = request.user.company if hasattr(request.user, 'company') else None
    mapped = request.data.get('mapped')
    if not company or not mapped:
        return Response({'error': 'Eksik veri.'}, status=status.HTTP_400_BAD_REQUEST)
    # account code'dan nesne çöz ve kaydet
    from FinAsis.apps.finance.accounting.models import Account
    resolved_lines = []
    for l in mapped.get('lines', []):
        try:
            acc = Account.objects.get(company=company, code=l['account'])
        except Account.DoesNotExist:
            return Response({'error': f"Hesap bulunamadı: {l['account']}"}, status=status.HTTP_400_BAD_REQUEST)
        from decimal import Decimal
        resolved_lines.append({
            'account': acc,
            'description': l.get('description', ''),
            'debit': Decimal(str(l.get('debit', '0'))),
            'credit': Decimal(str(l.get('credit', '0'))),
        })
    mapped_resolved = {
        'date': mapped.get('date'),
        'reference': mapped.get('reference'),
        'lines': resolved_lines,
        'total': mapped.get('total'),
    }
    voucher = create_voucher_from_lines(company, mapped_resolved)
    return Response({'status': 'created', 'voucher_id': voucher.id}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def nlp_preview_voucher(request):
    """Serbest metni TDHP uyumlu fiş taslağına dönüştürür."""
    company = request.user.company if hasattr(request.user, 'company') else None
    text = request.data.get('text')
    if not company or not text:
        return Response({'error': 'Eksik veri.'}, status=status.HTTP_400_BAD_REQUEST)
    mapped = map_text_to_voucher_lines(company, text)
    lines = [{
        'account': l['account'].code,
        'account_name': l['account'].name,
        'description': l['description'],
        'debit': str(l['debit']),
        'credit': str(l['credit']),
    } for l in mapped['lines']]
    return Response({'preview': {'date': mapped['date'], 'reference': mapped['reference'], 'total': str(mapped['total']), 'nature': mapped.get('nature'), 'rule_id': mapped.get('rule_id'), 'lines': lines}}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def stt_preview_voucher(request):
    """WAV sesini yerelde yazıya çevirip fiş taslağı üretir."""
    if not getattr(settings, 'STT_ENABLED', False):
        return Response({'error': 'STT devre dışı.'}, status=status.HTTP_400_BAD_REQUEST)
    company = request.user.company if hasattr(request.user, 'company') else None
    if not company or 'file' not in request.FILES:
        return Response({'error': 'Eksik veri.'}, status=status.HTTP_400_BAD_REQUEST)
    wav_bytes = request.FILES['file'].read()
    stt = LocalSTTService(settings.VOSK_MODEL_PATH)
    text = stt.transcribe(wav_bytes)
    mapped = map_text_to_voucher_lines(company, text)
    lines = [{
        'account': l['account'].code,
        'account_name': l['account'].name,
        'description': l['description'],
        'debit': str(l['debit']),
        'credit': str(l['credit']),
    } for l in mapped['lines']]
    return Response({'preview': {'text': text, 'date': mapped['date'], 'reference': mapped['reference'], 'total': str(mapped['total']), 'nature': mapped.get('nature'), 'rule_id': mapped.get('rule_id'), 'lines': lines}}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_autobook_rule(request):
    """Bir AutoBookingRule kuralını örnek metin/OCR üzerinde dener ve eşleşmeyi döndürür."""
    company = request.user.company if hasattr(request.user, 'company') else None
    data = request.data or {}
    rule_id = data.get('rule_id')
    sample_text = data.get('text', '')
    if not company or not rule_id:
        return Response({'error': 'Eksik veri.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        rule = AutoBookingRule.objects.get(id=rule_id, company=company)
    except AutoBookingRule.DoesNotExist:
        return Response({'error': 'Kural bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
    import re
    matched = False
    try:
        matched = bool(re.search(rule.keyword_pattern, sample_text or '', re.IGNORECASE))
    except re.error:
        matched = False
    return Response({'matched': matched}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def account_search(request):
    """Hesap planında kod/isim arama (autocomplete)."""
    company = request.user.company if hasattr(request.user, 'company') else None
    q = request.GET.get('q', '')
    if not company:
        return Response({'error': 'Şirket bulunamadı.'}, status=status.HTTP_400_BAD_REQUEST)
    from FinAsis.apps.finance.accounting.models import Account
    qs = Account.objects.filter(company=company)
    if q:
        from django.db.models import Q
        qs = qs.filter(Q(code__icontains=q) | Q(name__icontains=q))
    results = [{'code': a.code, 'name': a.name} for a in qs.order_by('code')[:20]]
    return Response({'results': results}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def derive_rule_from_preview(request):
    """Önizleme çıktısından regex ve hesap kodlarıyla kural oluşturur."""
    company = request.user.company if hasattr(request.user, 'company') else None
    data = request.data or {}
    preview = data.get('preview') or {}
    if not company or not preview:
        return Response({'error': 'Eksik veri.'}, status=status.HTTP_400_BAD_REQUEST)
    import re
    ref = preview.get('reference') or ''
    pattern = re.escape(ref) if ref else '.*'
    nature = preview.get('nature') or 'expense'
    lines = preview.get('lines') or []
    debit = next((l.get('account') for l in lines if float(l.get('debit', '0') or '0') > 0), None)
    credit = next((l.get('account') for l in lines if float(l.get('credit', '0') or '0') > 0), None)
    kdv = next((l.get('account') for l in lines if 'kdv' in (l.get('description','').lower())), None)
    rule = AutoBookingRule.objects.create(
        company=company,
        name=f"Preview-{nature}",
        keyword_pattern=pattern,
        nature=nature,
        debit_account_code=debit,
        credit_account_code=credit,
        kdv_account_code=kdv,
        priority=90,
        is_active=True,
    )
    return Response({'status': 'created', 'rule_id': rule.id}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def suggest_autobook_rules(request):
    """Örneklerden AutoBookingRule önerileri üretir."""
    company = request.user.company if hasattr(request.user, 'company') else None
    samples = request.data or {}
    if not company:
        return Response({'error': 'Şirket bulunamadı.'}, status=status.HTTP_400_BAD_REQUEST)
    suggestions = suggest_rules_from_samples(company, samples)
    return Response(suggestions, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def apply_autobook_rule(request):
    """Önerilen kuralı kaydeder."""
    company = request.user.company if hasattr(request.user, 'company') else None
    data = request.data or {}
    if not company:
        return Response({'error': 'Şirket bulunamadı.'}, status=status.HTTP_400_BAD_REQUEST)
    rule = AutoBookingRule.objects.create(
        company=company,
        name=data.get('name', 'Kural'),
        keyword_pattern=data.get('keyword_pattern', '.*'),
        nature=data.get('nature', 'expense'),
        debit_account_code=data.get('debit_account_code'),
        credit_account_code=data.get('credit_account_code'),
        kdv_account_code=data.get('kdv_account_code'),
        priority=int(data.get('priority', 100)),
        is_active=True,
    )
    return Response({'status': 'created', 'rule_id': rule.id}, status=status.HTTP_201_CREATED)

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