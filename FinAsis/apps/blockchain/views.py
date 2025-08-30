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
