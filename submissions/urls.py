from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeclarationViewSet, SubmissionLogViewSet, SubmissionViewSet

app_name = 'submissions'


def submissions_list_view(request):
    from .models import Submission

    qs = (
        Submission.objects.select_related('declaration')
        .filter(submitted_by=request.user)
        .order_by('-submitted_at', '-id')
        if request.user.is_authenticated
        else []
    )
    return render(request, 'submissions/list.html', {'submissions': qs})


router = DefaultRouter()
router.register(r'declarations', DeclarationViewSet, basename='declaration')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'submission-logs', SubmissionLogViewSet, basename='submission-log')

urlpatterns = [
    path('', include(router.urls)),
    path('my/', login_required(submissions_list_view), name='submissions-list'),
]
