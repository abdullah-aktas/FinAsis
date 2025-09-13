from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.utils.crypto import salted_hmac
from .models import ChainRecord
import hashlib
from django.urls import reverse

# Create your views here.

def home(request):
    return render(request, 'blockchain/home.html')

@require_POST
def api_verify(request):
    reference = request.POST.get('reference')
    payload = request.POST.get('payload')
    if not reference or not payload:
        return HttpResponseBadRequest('reference and payload required')
    hash_hex = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    exists = ChainRecord.objects.filter(reference=reference, hash_hex=hash_hex).exists()
    return JsonResponse({'reference': reference, 'hash_hex': hash_hex, 'verified': exists})

def record_list(request):
    records = ChainRecord.objects.all()[:200]
    return render(request, 'blockchain/record_list.html', {'records': records})

def record_create(request):
    if request.method == 'POST':
        reference = request.POST.get('reference')
        payload = request.POST.get('payload')
        status = request.POST.get('status') or 'pending'
        if not reference or not payload:
            return HttpResponseBadRequest('reference and payload required')
        hash_hex = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        ChainRecord.objects.create(
            reference=reference,
            hash_hex=hash_hex,
            payload_preview=payload[:500],
            status=status,
        )
        return HttpResponseRedirect(reverse('blockchain:record_list'))
    return render(request, 'blockchain/record_create.html')

# --- Simple UI pages referenced from blockchain home ---
def transactions_list(request):
    # Placeholder: later wire to real transaction models/services
    example = [
        {"txid": "0x1234abcd", "status": "confirmed", "amount": 1.25, "asset": "BTC"},
        {"txid": "0x9876ef01", "status": "pending", "amount": 12.0, "asset": "ETH"},
    ]
    return render(request, 'blockchain/transactions_list.html', {"transactions": example})

def contracts_list(request):
    example = [
        {"name": "Varlık Token Sözleşmesi", "address": "0xa1b2...", "network": "testnet"},
        {"name": "Tedarik Zinciri", "address": "0xc3d4...", "network": "testnet"},
    ]
    return render(request, 'blockchain/contracts_list.html', {"contracts": example})

def assets_list(request):
    example = [
        {"symbol": "BTC", "balance": 0.52},
        {"symbol": "ETH", "balance": 14.7},
        {"symbol": "USDT", "balance": 1200},
    ]
    return render(request, 'blockchain/assets_list.html', {"assets": example})

def reports(request):
    # High-level links or summaries; can be expanded later
    return render(request, 'blockchain/reports.html')
