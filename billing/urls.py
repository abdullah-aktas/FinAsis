from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'billing'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='billing:plans', permanent=False), name='billing_home'),
    path('plans/', views.plans_index, name='plans_index'),  # Main plans index page
    path('plans/', views.plans_index, name='plans'),  # Alias for backward compatibility
    path('plans/kobi/', views.plans_kobi, name='plans_kobi'),
    path('plans/education/', views.plans_education, name='plans_education'),
    path('plans/games/', views.plans_games, name='plans_games'),
    path('plans/select/<str:plan_code>/', views.select_plan, name='select_plan'),
    path('plans/enterprise-inquiry/<str:plan_code>/', views.enterprise_inquiry, name='enterprise_inquiry'),
    path('checkout/paytr/<int:price_id>/', views.checkout_paytr, name='checkout_paytr'),
    path('checkout/bank/<int:price_id>/', views.checkout_bank_transfer, name='checkout_bank'),
    path('callback/paytr/', views.paytr_callback, name='paytr_callback'),
    path('portal/', views.portal, name='portal'),
    path('admin/confirm-bank/<str:reference_code>/', views.admin_confirm_bank_transfer, name='confirm_bank'),
]
