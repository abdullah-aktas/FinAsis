from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TransactionViewSet,
    CashFlowViewSet,
    IncomeStatementViewSet
)

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'cashflow', CashFlowViewSet, basename='cashflow')
router.register(r'income-statements', IncomeStatementViewSet, basename='income-statement')

urlpatterns = [
    path('', include(router.urls)),
] 