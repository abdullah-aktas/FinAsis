from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CheckCategoryViewSet, CheckTypeViewSet, CheckRuleViewSet,
    CheckResultViewSet, CheckScheduleViewSet
)

app_name = 'checks'

router = DefaultRouter()
router.register(r'categories', CheckCategoryViewSet, basename='check-category')
router.register(r'types', CheckTypeViewSet, basename='check-type')
router.register(r'rules', CheckRuleViewSet, basename='check-rule')
router.register(r'results', CheckResultViewSet, basename='check-result')
router.register(r'schedules', CheckScheduleViewSet, basename='check-schedule')

urlpatterns = [
    path('api/', include(router.urls)),
] 