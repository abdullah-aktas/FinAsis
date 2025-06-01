from django.http import JsonResponse
from django.views.decorators.csrf import requires_csrf_token

@requires_csrf_token
def custom_error_500(request, *args, **argv):
    return JsonResponse({'error': 'Sunucuda bir hata oluştu. Lütfen daha sonra tekrar deneyin.'}, status=500)

# ... existing code ... 