from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F
from django.utils import timezone
from .models import Bank, Check, PromissoryNote, CheckTransaction, PromissoryNoteTransaction, CheckCategory, CheckType, CheckRule, CheckResult, CheckSchedule
from .forms import BankForm, CheckForm, PromissoryNoteForm, CheckTransactionForm, PromissoryNoteTransactionForm
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from .serializers import (
    CheckCategorySerializer, CheckTypeSerializer, CheckRuleSerializer,
    CheckResultSerializer, CheckScheduleSerializer
)
from .permissions import IsAdminOrReadOnly
from .tasks import run_check
import logging

logger = logging.getLogger(__name__)

@login_required
def bank_list(request):
    banks = Bank.objects.all()
    context = {
        'banks': banks,
    }
    return render(request, 'check_management/bank_list.html', context)

@login_required
def bank_create(request):
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            bank = form.save()
            messages.success(request, 'Banka başarıyla oluşturuldu.')
            return redirect('bank_list')
    else:
        form = BankForm()
    return render(request, 'check_management/bank_form.html', {'form': form})

@login_required
def check_list(request):
    checks = Check.objects.all()
    context = {
        'checks': checks,
    }
    return render(request, 'check_management/check_list.html', context)

@login_required
def check_detail(request, pk):
    check = get_object_or_404(Check, pk=pk)
    transactions = CheckTransaction.objects.filter(check=check)
    context = {
        'check': check,
        'transactions': transactions,
    }
    return render(request, 'check_management/check_detail.html', context)

@login_required
def check_create(request):
    if request.method == 'POST':
        form = CheckForm(request.POST)
        if form.is_valid():
            check = form.save()
            messages.success(request, 'Çek başarıyla oluşturuldu.')
            return redirect('check_detail', pk=check.pk)
    else:
        form = CheckForm()
    return render(request, 'check_management/check_form.html', {'form': form})

@login_required
def check_update(request, pk):
    check = get_object_or_404(Check, pk=pk)
    if request.method == 'POST':
        form = CheckForm(request.POST, instance=check)
        if form.is_valid():
            check = form.save()
            messages.success(request, 'Çek başarıyla güncellendi.')
            return redirect('check_detail', pk=check.pk)
    else:
        form = CheckForm(instance=check)
    return render(request, 'check_management/check_form.html', {'form': form})

@login_required
def check_delete(request, pk):
    check = get_object_or_404(Check, pk=pk)
    if request.method == 'POST':
        check.delete()
        messages.success(request, 'Çek başarıyla silindi.')
        return redirect('check_list')
    return render(request, 'check_management/check_confirm_delete.html', {'check': check})

@login_required
def check_transaction_create(request, check_pk):
    check = get_object_or_404(Check, pk=check_pk)
    if request.method == 'POST':
        form = CheckTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.check = check
            transaction.created_by = request.user
            transaction.save()
            messages.success(request, 'Çek işlemi başarıyla oluşturuldu.')
            return redirect('check_detail', pk=check_pk)
    else:
        form = CheckTransactionForm()
    return render(request, 'check_management/transaction_form.html', {'form': form, 'check': check})

@login_required
def promissory_note_list(request):
    notes = PromissoryNote.objects.all()
    context = {
        'notes': notes,
    }
    return render(request, 'check_management/promissory_note_list.html', context)

@login_required
def promissory_note_detail(request, pk):
    note = get_object_or_404(PromissoryNote, pk=pk)
    transactions = PromissoryNoteTransaction.objects.filter(promissory_note=note)
    context = {
        'note': note,
        'transactions': transactions,
    }
    return render(request, 'check_management/promissory_note_detail.html', context)

@login_required
def promissory_note_create(request):
    if request.method == 'POST':
        form = PromissoryNoteForm(request.POST)
        if form.is_valid():
            note = form.save()
            messages.success(request, 'Senet başarıyla oluşturuldu.')
            return redirect('promissory_note_detail', pk=note.pk)
    else:
        form = PromissoryNoteForm()
    return render(request, 'check_management/promissory_note_form.html', {'form': form})

@login_required
def promissory_note_update(request, pk):
    note = get_object_or_404(PromissoryNote, pk=pk)
    if request.method == 'POST':
        form = PromissoryNoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save()
            messages.success(request, 'Senet başarıyla güncellendi.')
            return redirect('promissory_note_detail', pk=note.pk)
    else:
        form = PromissoryNoteForm(instance=note)
    return render(request, 'check_management/promissory_note_form.html', {'form': form})

@login_required
def promissory_note_delete(request, pk):
    note = get_object_or_404(PromissoryNote, pk=pk)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Senet başarıyla silindi.')
        return redirect('promissory_note_list')
    return render(request, 'check_management/promissory_note_confirm_delete.html', {'note': note})

@login_required
def promissory_note_transaction_create(request, note_pk):
    note = get_object_or_404(PromissoryNote, pk=note_pk)
    if request.method == 'POST':
        form = PromissoryNoteTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.promissory_note = note
            transaction.created_by = request.user
            transaction.save()
            messages.success(request, 'Senet işlemi başarıyla oluşturuldu.')
            return redirect('promissory_note_detail', pk=note_pk)
    else:
        form = PromissoryNoteTransactionForm()
    return render(request, 'check_management/promissory_note_transaction_form.html', {'form': form, 'note': note})

@login_required
def dashboard(request):
    total_checks = Check.objects.count()
    total_notes = PromissoryNote.objects.count()
    total_check_amount = Check.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_note_amount = PromissoryNote.objects.aggregate(total=Sum('amount'))['total'] or 0
    pending_checks = Check.objects.filter(status='PENDING').count()
    pending_notes = PromissoryNote.objects.filter(status='PENDING').count()
    recent_transactions = CheckTransaction.objects.order_by('-transaction_date')[:5]
    context = {
        'total_checks': total_checks,
        'total_notes': total_notes,
        'total_check_amount': total_check_amount,
        'total_note_amount': total_note_amount,
        'pending_checks': pending_checks,
        'pending_notes': pending_notes,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'check_management/dashboard.html', context)

class CheckCategoryViewSet(viewsets.ModelViewSet):
    queryset = CheckCategory.objects.all()
    serializer_class = CheckCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'priority', 'is_active']

    @action(detail=True, methods=['get'])
    def types(self, request, pk=None):
        category = self.get_object()
        types = category.checktype_set.all()
        serializer = CheckTypeSerializer(types, many=True)
        return Response(serializer.data)

class CheckTypeViewSet(viewsets.ModelViewSet):
    queryset = CheckType.objects.select_related('category').all()
    serializer_class = CheckTypeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'code', 'category', 'severity', 'is_active']

    @action(detail=True, methods=['get'])
    def rules(self, request, pk=None):
        check_type = self.get_object()
        rules = check_type.checkrule_set.all()
        serializer = CheckRuleSerializer(rules, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        check_type = self.get_object()
        results = check_type.checkresult_set.all()
        serializer = CheckResultSerializer(results, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        check_type = self.get_object()
        try:
            result = run_check.delay(check_type.id)
            return Response({
                'task_id': result.id,
                'status': 'started',
                'message': f'{check_type.name} kontrolü başlatıldı'
            })
        except Exception as e:
            logger.error(f"Kontrol çalıştırma hatası: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CheckRuleViewSet(viewsets.ModelViewSet):
    queryset = CheckRule.objects.select_related('check_type').all()
    serializer_class = CheckRuleSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'check_type', 'is_active']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

class CheckResultViewSet(viewsets.ModelViewSet):
    queryset = CheckResult.objects.select_related('check_type').all()
    serializer_class = CheckResultSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['check_type', 'status', 'score']

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        cache_key = 'check_results_statistics'
        data = cache.get(cache_key)
        
        if not data:
            data = {
                'total_checks': self.queryset.count(),
                'passed_checks': self.queryset.filter(status='passed').count(),
                'failed_checks': self.queryset.filter(status='failed').count(),
                'warning_checks': self.queryset.filter(status='warning').count(),
                'error_checks': self.queryset.filter(status='error').count(),
                'average_score': self.queryset.aggregate(avg_score=Avg('score'))['avg_score'],
                'max_score': self.queryset.aggregate(max_score=Max('score'))['max_score'],
                'min_score': self.queryset.aggregate(min_score=Min('score'))['min_score'],
                'check_type_stats': self.queryset.values('check_type__name').annotate(
                    count=Count('id'),
                    avg_score=Avg('score')
                ),
                'status_trend': self.queryset.values('created_at__date').annotate(
                    passed=Count('id', filter=Q(status='passed')),
                    failed=Count('id', filter=Q(status='failed')),
                    warning=Count('id', filter=Q(status='warning')),
                    error=Count('id', filter=Q(status='error'))
                ).order_by('created_at__date')[:30]
            }
            cache.set(cache_key, data, 300)  # 5 dakika cache

        return Response(data)

class CheckScheduleViewSet(viewsets.ModelViewSet):
    queryset = CheckSchedule.objects.select_related('check_type').all()
    serializer_class = CheckScheduleSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['check_type', 'is_active']

    @action(detail=False, methods=['get'])
    def due(self, request):
        now = timezone.now()
        due_schedules = self.queryset.filter(
            is_active=True,
            next_run__lte=now
        )
        serializer = self.get_serializer(due_schedules, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        schedule = self.get_object()
        try:
            result = run_check.delay(schedule.check_type.id)
            schedule.last_run = timezone.now()
            schedule.save()
            return Response({
                'task_id': result.id,
                'status': 'started',
                'message': f'{schedule.check_type.name} kontrolü başlatıldı'
            })
        except Exception as e:
            logger.error(f"Zamanlanmış kontrol çalıştırma hatası: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
