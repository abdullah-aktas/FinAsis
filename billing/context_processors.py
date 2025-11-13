from django.conf import settings

def billing_settings(request):
    return {
        'BANK_TRANSFER_ENABLED': getattr(settings, 'BANK_TRANSFER_ENABLED', True),
    }
