from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F
from django.utils import timezone
from .models import Bank, Check, PromissoryNote, CheckTransaction, PromissoryNoteTransaction
from .forms import BankForm, CheckForm, PromissoryNoteForm, CheckTransactionForm, PromissoryNoteTransactionForm

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
