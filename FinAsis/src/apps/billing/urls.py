from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('plans/', views.plans, name='plans'),
    path('checkout/paytr/<int:price_id>/', views.checkout_paytr, name='checkout_paytr'),
    path('checkout/bank/<int:price_id>/', views.checkout_bank_transfer, name='checkout_bank'),
    path('callback/paytr/', views.paytr_callback, name='paytr_callback'),
    path('portal/', views.portal, name='portal'),
    path('admin/confirm-bank/<str:reference_code>/', views.admin_confirm_bank_transfer, name='confirm_bank'),
]
