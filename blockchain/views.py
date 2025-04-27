from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import BlockchainTransaction, BlockchainLog, BaseModel, TokenContract, TokenBalance, TokenTransaction
from virtual_company.models import VirtualCompany
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from .models import BlockchainNetwork, SmartContract, Transaction, Wallet, Token
from .serializers import (
    BlockchainNetworkSerializer,
    SmartContractSerializer,
    TransactionSerializer,
    WalletSerializer,
    TokenSerializer,
)
from .permissions import IsWalletOwner, IsContractOwner
from .tasks import sync_transaction_status, sync_wallet_balance, create_token_contract, mint_tokens, transfer_tokens
import logging
from web3 import Web3
from decimal import Decimal
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (
    Transaction, Wallet, SmartContract, TokenContract,
    TokenTransaction, BlockchainTransaction
)

logger = logging.getLogger(__name__)

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

class BaseModelListView(ListView):
    model = BaseModel
    template_name = 'blockchain/basemodel_list.html'
    context_object_name = 'models'

class BaseModelDetailView(DetailView):
    model = BaseModel
    template_name = 'blockchain/basemodel_detail.html'
    context_object_name = 'model'

class BaseModelCreateView(CreateView):
    model = BaseModel
    template_name = 'blockchain/basemodel_form.html'
    fields = ['name', 'description', 'is_active']
    success_url = reverse_lazy('blockchain:basemodel_list')

class BaseModelUpdateView(UpdateView):
    model = BaseModel
    template_name = 'blockchain/basemodel_form.html'
    fields = ['name', 'description', 'is_active']
    success_url = reverse_lazy('blockchain:basemodel_list')

class BaseModelDeleteView(DeleteView):
    model = BaseModel
    template_name = 'blockchain/basemodel_confirm_delete.html'
    success_url = reverse_lazy('blockchain:basemodel_list')

class BlockchainNetworkViewSet(viewsets.ModelViewSet):
    queryset = BlockchainNetwork.objects.filter(is_active=True)
    serializer_class = BlockchainNetworkSerializer
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(cache_page(60 * 15))  # 15 dakika önbellek
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 60))  # 1 saat önbellek
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class SmartContractViewSet(viewsets.ModelViewSet):
    queryset = SmartContract.objects.all()
    serializer_class = SmartContractSerializer
    permission_classes = [permissions.IsAuthenticated, IsContractOwner]

    def get_queryset(self):
        return SmartContract.objects.filter(
            Q(network__is_active=True) | Q(is_verified=True)
        )

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        contract = self.get_object()
        # Contract verification logic here
        contract.is_verified = True
        contract.save()
        return Response({'status': 'verified'})

    @action(detail=True, methods=['get'])
    def abi(self, request, pk=None):
        contract = self.get_object()
        return Response({'abi': contract.abi})

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(
            Q(from_address__in=user.wallets.values_list('address', flat=True)) |
            Q(to_address__in=user.wallets.values_list('address', flat=True))
        ).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def sync_status(self, request, pk=None):
        transaction = self.get_object()
        sync_transaction_status.delay(transaction.id)
        return Response({'status': 'syncing'})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Transaction validation
        try:
            web3 = Web3(Web3.HTTPProvider(serializer.validated_data['network'].rpc_url))
            if not web3.is_connected():
                return Response(
                    {'error': 'Network connection failed'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        except Exception as e:
            logger.error(f"Transaction validation failed: {str(e)}")
            return Response(
                {'error': 'Network validation failed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated, IsWalletOwner]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user, is_active=True)

    @action(detail=True, methods=['post'])
    def sync_balance(self, request, pk=None):
        wallet = self.get_object()
        sync_wallet_balance.delay(wallet.id)
        return Response({'status': 'syncing'})

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        wallet = self.get_object()
        transactions = Transaction.objects.filter(
            Q(from_address=wallet.address) | Q(to_address=wallet.address)
        ).order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

class TokenViewSet(viewsets.ModelViewSet):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Token.objects.filter(
            Q(owner__user=user) | Q(contract__network__is_active=True)
        )

    @action(detail=True, methods=['get'])
    def metadata(self, request, pk=None):
        token = self.get_object()
        return Response(token.metadata)

    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        token = self.get_object()
        to_address = request.data.get('to_address')
        amount = Decimal(request.data.get('amount', 0))

        if not to_address or amount <= 0:
            return Response(
                {'error': 'Invalid transfer parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Transfer logic here
        return Response({'status': 'transfer initiated'})

@login_required
def create_contract(request):
    """
    Yeni token sözleşmesi oluştur
    """
    if request.method == 'POST':
        token_name = request.POST.get('token_name')
        token_symbol = request.POST.get('token_symbol')
        total_supply = Decimal(request.POST.get('total_supply', '1000000'))
        
        # Sözleşme oluşturma işlemini başlat
        task = create_token_contract.delay(
            user_id=request.user.id,
            token_name=token_name,
            token_symbol=token_symbol,
            total_supply=total_supply
        )
        
        return JsonResponse({
            'status': 'success',
            'task_id': task.id,
            'message': 'Token sözleşmesi oluşturuluyor...'
        })
    
    return render(request, 'blockchain/create_contract.html')

@login_required
def mint_tokens_view(request, contract_id):
    """
    Token oluştur
    """
    contract = get_object_or_404(TokenContract, id=contract_id)
    
    if contract.user != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))
        
        # Token oluşturma işlemini başlat
        task = mint_tokens.delay(
            contract_id=contract.id,
            amount=amount
        )
        
        return JsonResponse({
            'status': 'success',
            'task_id': task.id,
            'message': 'Tokenlar oluşturuluyor...'
        })
    
    return render(request, 'blockchain/mint_tokens.html', {
        'contract': contract
    })

@login_required
def transfer_tokens_view(request, contract_id):
    """
    Token transferi
    """
    contract = get_object_or_404(TokenContract, id=contract_id)
    
    if request.method == 'POST':
        to_user_id = request.POST.get('to_user_id')
        amount = Decimal(request.POST.get('amount'))
        
        # Token transferi işlemini başlat
        task = transfer_tokens.delay(
            contract_id=contract.id,
            from_user_id=request.user.id,
            to_user_id=to_user_id,
            amount=amount
        )
        
        return JsonResponse({
            'status': 'success',
            'task_id': task.id,
            'message': 'Token transferi yapılıyor...'
        })
    
    return render(request, 'blockchain/transfer_tokens.html', {
        'contract': contract
    })

@login_required
def get_balance(request, contract_id):
    """
    Token bakiyesini getir
    """
    contract = get_object_or_404(TokenContract, id=contract_id)
    balance = TokenBalance.objects.filter(
        contract=contract,
        user=request.user
    ).first()
    
    if not balance:
        return JsonResponse({
            'status': 'error',
            'message': 'Bakiye bulunamadı'
        })
    
    return JsonResponse({
        'status': 'success',
        'balance': str(balance.balance),
        'locked_balance': str(balance.locked_balance)
    })

@login_required
def get_transactions(request, contract_id):
    """
    Token işlemlerini getir
    """
    contract = get_object_or_404(TokenContract, id=contract_id)
    transactions = TokenTransaction.objects.filter(
        contract=contract
    ).order_by('-created_at')[:50]
    
    return JsonResponse({
        'status': 'success',
        'transactions': [
            {
                'type': t.get_transaction_type_display(),
                'from': t.from_user.username,
                'to': t.to_user.username,
                'amount': str(t.amount),
                'hash': t.transaction_hash,
                'created_at': t.created_at.isoformat()
            }
            for t in transactions
        ]
    })

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'blockchain/transaction_list.html'
    context_object_name = 'transactions'
    
    def get_queryset(self):
        return Transaction.objects.filter(wallet__in=self.request.user.wallets.all())

class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'blockchain/transaction_detail.html'
    context_object_name = 'transaction'

    def get_queryset(self):
        return Transaction.objects.filter(wallet__in=self.request.user.wallets.all())

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    template_name = 'blockchain/transaction_form.html'
    fields = ['wallet', 'to_address', 'amount', 'gas_price', 'gas_limit', 'data']
    success_url = reverse_lazy('blockchain:transaction-list')
    
    def form_valid(self, form):
        user_wallet = get_object_or_404(Wallet, user=self.request.user)
        form.instance.from_address = user_wallet.address
        return super().form_valid(form)

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    template_name = 'blockchain/transaction_form.html'
    fields = ['gas_price', 'gas_limit', 'data']
    success_url = reverse_lazy('blockchain:transaction-list')

class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'blockchain/transaction_confirm_delete.html'
    success_url = reverse_lazy('blockchain:transaction-list')

class WalletListView(LoginRequiredMixin, ListView):
    model = Wallet
    template_name = 'blockchain/wallet_list.html'
    context_object_name = 'wallets'
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

class WalletDetailView(LoginRequiredMixin, DetailView):
    model = Wallet
    template_name = 'blockchain/wallet_detail.html'
    context_object_name = 'wallet'

class WalletCreateView(LoginRequiredMixin, CreateView):
    model = Wallet
    template_name = 'blockchain/wallet_form.html'
    fields = ['name', 'network']
    success_url = reverse_lazy('blockchain:wallet-list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class WalletUpdateView(LoginRequiredMixin, UpdateView):
    model = Wallet
    template_name = 'blockchain/wallet_form.html'
    fields = ['name']
    success_url = reverse_lazy('blockchain:wallet-list')

class WalletDeleteView(LoginRequiredMixin, DeleteView):
    model = Wallet
    template_name = 'blockchain/wallet_confirm_delete.html'
    success_url = reverse_lazy('blockchain:wallet-list')

class SmartContractListView(LoginRequiredMixin, ListView):
    model = SmartContract
    template_name = 'blockchain/smart_contract_list.html'
    context_object_name = 'smart_contracts'
    
    def get_queryset(self):
        return SmartContract.objects.filter(owner=self.request.user)

class SmartContractDetailView(LoginRequiredMixin, DetailView):
    model = SmartContract
    template_name = 'blockchain/smart_contract_detail.html'
    context_object_name = 'smart_contract'

class SmartContractCreateView(LoginRequiredMixin, CreateView):
    model = SmartContract
    template_name = 'blockchain/smart_contract_form.html'
    fields = ['name', 'network', 'abi', 'bytecode']
    success_url = reverse_lazy('blockchain:smart-contract-list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class SmartContractUpdateView(LoginRequiredMixin, UpdateView):
    model = SmartContract
    template_name = 'blockchain/smart_contract_form.html'
    fields = ['name', 'abi']
    success_url = reverse_lazy('blockchain:smart-contract-list')

class SmartContractDeleteView(LoginRequiredMixin, DeleteView):
    model = SmartContract
    template_name = 'blockchain/smart_contract_confirm_delete.html'
    success_url = reverse_lazy('blockchain:smart-contract-list')

class VerifyView(LoginRequiredMixin, CreateView):
    model = SmartContract
    template_name = 'blockchain/verify.html'
    fields = ['address', 'network']
    success_url = reverse_lazy('blockchain:smart-contract-list')

class DeployView(LoginRequiredMixin, CreateView):
    model = SmartContract
    template_name = 'blockchain/deploy.html'
    fields = ['name', 'network', 'abi', 'bytecode']
    success_url = reverse_lazy('blockchain:smart-contract-list')

class InteractView(LoginRequiredMixin, UpdateView):
    model = SmartContract
    template_name = 'blockchain/interact.html'
    fields = ['function_name', 'parameters']
    success_url = reverse_lazy('blockchain:smart-contract-list')

class TokenContractListView(LoginRequiredMixin, ListView):
    model = TokenContract
    template_name = 'blockchain/token_contract_list.html'
    context_object_name = 'token_contracts'

    def get_queryset(self):
        return TokenContract.objects.filter(user=self.request.user)

class TokenContractDetailView(LoginRequiredMixin, DetailView):
    model = TokenContract
    template_name = 'blockchain/token_contract_detail.html'
    context_object_name = 'token_contract'

    def get_queryset(self):
        return TokenContract.objects.filter(user=self.request.user)

class BlockchainTransactionListView(LoginRequiredMixin, ListView):
    model = BlockchainTransaction
    template_name = 'blockchain/blockchain_transaction_list.html'
    context_object_name = 'blockchain_transactions'

    def get_queryset(self):
        return BlockchainTransaction.objects.filter(virtual_company__user=self.request.user)

class BlockchainTransactionDetailView(LoginRequiredMixin, DetailView):
    model = BlockchainTransaction
    template_name = 'blockchain/blockchain_transaction_detail.html'
    context_object_name = 'blockchain_transaction'

    def get_queryset(self):
        return BlockchainTransaction.objects.filter(virtual_company__user=self.request.user)
