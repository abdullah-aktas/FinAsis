from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import BlockchainTransaction, BlockchainLog
from virtual_company.models import VirtualCompany

@login_required
def transaction_list(request):
    """Blockchain işlemlerini listeler"""
    virtual_company = get_object_or_404(VirtualCompany, user=request.user)
    transactions = BlockchainTransaction.objects.filter(
        virtual_company=virtual_company,
        is_deleted=False
    ).order_by('-created_at')
    
    return render(request, 'blockchain/transaction_list.html', {
        'transactions': transactions
    })

@login_required
def transaction_detail(request, pk):
    """Blockchain işlem detaylarını gösterir"""
    virtual_company = get_object_or_404(VirtualCompany, user=request.user)
    transaction = get_object_or_404(
        BlockchainTransaction,
        pk=pk,
        virtual_company=virtual_company,
        is_deleted=False
    )
    
    logs = BlockchainLog.objects.filter(
        transaction=transaction
    ).order_by('-created_at')
    
    return render(request, 'blockchain/transaction_detail.html', {
        'transaction': transaction,
        'logs': logs
    })

@login_required
def transaction_create(request):
    """Yeni blockchain işlemi oluşturur"""
    virtual_company = get_object_or_404(VirtualCompany, user=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        transaction_type = request.POST.get('transaction_type')
        reference_id = request.POST.get('reference_id')
        reference_model = request.POST.get('reference_model')
        notes = request.POST.get('notes')
        
        transaction = BlockchainTransaction.objects.create(
            virtual_company=virtual_company,
            title=title,
            transaction_type=transaction_type,
            reference_id=reference_id,
            reference_model=reference_model,
            notes=notes
        )
        
        # İşlem logu oluştur
        BlockchainLog.objects.create(
            transaction=transaction,
            status='pending',
            message='İşlem oluşturuldu'
        )
        
        messages.success(request, 'Blockchain işlemi başarıyla oluşturuldu.')
        return redirect('blockchain:transaction_detail', pk=transaction.pk)
    
    return render(request, 'blockchain/transaction_form.html')

@login_required
def transaction_update(request, pk):
    """Blockchain işlemini günceller"""
    virtual_company = get_object_or_404(VirtualCompany, user=request.user)
    transaction = get_object_or_404(
        BlockchainTransaction,
        pk=pk,
        virtual_company=virtual_company,
        is_deleted=False
    )
    
    if request.method == 'POST':
        transaction.title = request.POST.get('title')
        transaction.transaction_type = request.POST.get('transaction_type')
        transaction.reference_id = request.POST.get('reference_id')
        transaction.reference_model = request.POST.get('reference_model')
        transaction.notes = request.POST.get('notes')
        transaction.save()
        
        # İşlem logu oluştur
        BlockchainLog.objects.create(
            transaction=transaction,
            status='pending',
            message='İşlem güncellendi'
        )
        
        messages.success(request, 'Blockchain işlemi başarıyla güncellendi.')
        return redirect('blockchain:transaction_detail', pk=transaction.pk)
    
    return render(request, 'blockchain/transaction_form.html', {
        'transaction': transaction
    })

@login_required
def transaction_delete(request, pk):
    """Blockchain işlemini siler"""
    virtual_company = get_object_or_404(VirtualCompany, user=request.user)
    transaction = get_object_or_404(
        BlockchainTransaction,
        pk=pk,
        virtual_company=virtual_company,
        is_deleted=False
    )
    
    if request.method == 'POST':
        transaction.is_deleted = True
        transaction.save()
        
        messages.success(request, 'Blockchain işlemi başarıyla silindi.')
        return redirect('blockchain:transaction_list')
    
    return render(request, 'blockchain/transaction_confirm_delete.html', {
        'transaction': transaction
    })
