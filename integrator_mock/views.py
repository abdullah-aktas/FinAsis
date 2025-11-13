import json
import uuid
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt

# Basit in-memory durum takibi (test sürecinde işlem yaşam döngüsü boyunca yeterli)
_STATE = {}


@csrf_exempt
def send(request: HttpRequest):
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)
    tracking_id = request.headers.get('Idempotency-Key') or str(uuid.uuid4())
    # İlk istekte PENDING, ikinci status sorgusunda ACCEPTED dönecek şekilde state yazalım
    _STATE[tracking_id] = 'PENDING'
    return JsonResponse({'tracking_id': tracking_id, 'status': 'PENDING'}, status=202)


def status(request: HttpRequest):
    tracking_id = request.GET.get('tracking_id')
    if not tracking_id:
        return JsonResponse({'error': 'tracking_id required'}, status=400)
    s = _STATE.get(tracking_id)
    if not s:
        return JsonResponse({'status': 'ERROR'}, status=404)
    if s == 'PENDING':
        _STATE[tracking_id] = 'ACCEPTED'
        return JsonResponse({'status': 'PENDING'}, status=200)
    return JsonResponse({'status': 'ACCEPTED'}, status=200)
