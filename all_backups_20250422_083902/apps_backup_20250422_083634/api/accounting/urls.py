from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JournalEntryViewSet,
    AccountPlanViewSet,
    BalanceSheetViewSet
)

router = DefaultRouter()
router.register(r'journal-entries', JournalEntryViewSet, basename='journal-entry')
router.register(r'chart-of-accounts', AccountPlanViewSet, basename='account-plan')
router.register(r'balance-sheets', BalanceSheetViewSet, basename='balance-sheet')

urlpatterns = [
    path('', include(router.urls)),
] 