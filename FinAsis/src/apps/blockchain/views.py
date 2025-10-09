from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST
from django.utils.crypto import salted_hmac
from .models import ChainRecord
import hashlib
from django.urls import reverse
import re

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
    q = request.GET.get('q', '').strip()
    qs = ChainRecord.objects.all()
    if q:
        qs = qs.filter(reference__icontains=q)
    records = qs[:200]
    return render(request, 'blockchain/record_list.html', {'records': records, 'q': q})

def record_export_csv(request):
    q = request.GET.get('q', '').strip()
    qs = ChainRecord.objects.all()
    if q:
        qs = qs.filter(reference__icontains=q)
    rows = [
        ['reference','hash_hex','status','created_at']
    ]
    for r in qs.iterator():
        rows.append([r.reference, r.hash_hex, r.status, r.created_at.isoformat()])
    content = '\n'.join([','.join([str(c).replace('\n',' ').replace('\r',' ') for c in row]) for row in rows])
    resp = HttpResponse(content, content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = 'attachment; filename="chain_records.csv"'
    return resp

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

# --- KOBİ dostu hızlı kanıt ---
def anchor_wizard(request):
    return render(request, 'blockchain/anchor_wizard.html')

@require_POST
def api_anchor(request):
    """Accept precomputed SHA-256 hex and reference; create anchored record.
    Useful for client-side file hashing (privacy-friendly).
    """
    reference = (request.POST.get('reference') or '').strip()
    hash_hex = (request.POST.get('hash_hex') or '').strip().lower()
    status = (request.POST.get('status') or 'anchored').strip()
    if not reference or not hash_hex:
        return HttpResponseBadRequest('reference and hash_hex required')
    if not re.fullmatch(r"[0-9a-f]{64}", hash_hex):
        return HttpResponseBadRequest('hash_hex must be 64 hex chars')
    rec = ChainRecord.objects.create(
        reference=reference,
        hash_hex=hash_hex,
        payload_preview='',
        status=status or 'anchored',
    )
    return JsonResponse({'created': True, 'reference': rec.reference, 'hash_hex': rec.hash_hex, 'status': rec.status})

# --- KOBİ dostu doğrulama (hash ile) ---
def verify_wizard(request):
    return render(request, 'blockchain/verify_wizard.html')

@require_POST
def api_verify_hash(request):
    """Verify by provided SHA-256 hex (and optional reference)."""
    reference = (request.POST.get('reference') or '').strip()
    hash_hex = (request.POST.get('hash_hex') or '').strip().lower()
    if not hash_hex:
        return HttpResponseBadRequest('hash_hex required')
    if not re.fullmatch(r"[0-9a-f]{64}", hash_hex):
        return HttpResponseBadRequest('hash_hex must be 64 hex chars')
    qs = ChainRecord.objects.filter(hash_hex=hash_hex)
    if reference:
        qs = qs.filter(reference=reference)
    exists = qs.exists()
    return JsonResponse({'reference': reference, 'hash_hex': hash_hex, 'verified': exists, 'count': qs.count()})
