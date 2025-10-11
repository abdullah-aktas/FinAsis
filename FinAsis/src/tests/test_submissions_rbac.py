# pyright: reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from src.apps.advisors.models import AdvisorProfile, TaxpayerProfile, Engagement
from src.apps.submissions.models import Declaration, Submission, SubmissionLog


@pytest.mark.django_db
def test_non_advisor_cannot_submit_when_flag_off():
    User = get_user_model()
    user = User.objects.create_user(username='user1', password='pass')

    client = APIClient()
    client.force_authenticate(user=user)

    decl = Declaration.objects.create(code='KDV1', period='2025-01', taxpayer_vkn_tckn='11111111111', payload={}, created_by=user)

    resp = client.post('/api/v1/submissions/submissions/', {'declaration': decl.id}, format='json')
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_advisor_with_active_engagement_can_submit():
    User = get_user_model()
    advisor_user = User.objects.create_user(username='advisor1', password='pass')

    # Advisor profile (verified)
    ap = AdvisorProfile.objects.create(user=advisor_user, type='SMMM', verified_at=timezone.now())

    # Taxpayer and engagement
    tp = TaxpayerProfile.objects.create(name='Acme A.Ş.', vkn_tckn='22222222222')
    Engagement.objects.create(advisor=ap, taxpayer=tp, scope='both', status='active')

    # Declaration could be created by another user or the same one
    creator = User.objects.create_user(username='creator1', password='pass')
    decl = Declaration.objects.create(code='KDV1', period='2025-02', taxpayer_vkn_tckn=tp.vkn_tckn, payload={}, created_by=creator)

    client = APIClient()
    client.force_authenticate(user=advisor_user)

    resp = client.post('/api/v1/submissions/submissions/', {'declaration': decl.id}, format='json')
    assert resp.status_code in (200, 201)
    # Ensure status updated and a log created
    sub_id = resp.data.get('id') if hasattr(resp, 'data') and isinstance(resp.data, dict) else None
    if sub_id:
        sub = Submission.objects.get(pk=sub_id)
    else:
        sub = Submission.objects.latest('id')
    assert sub.status == 'sent'
    assert SubmissionLog.objects.filter(submission=sub).exists()


@pytest.mark.django_db
def test_advisor_without_engagement_is_forbidden_and_logs_error():
    User = get_user_model()
    advisor_user = User.objects.create_user(username='advisor2', password='pass')
    AdvisorProfile.objects.create(user=advisor_user, type='SMMM', verified_at=timezone.now())

    # Declaration for a taxpayer with no engagement
    creator = User.objects.create_user(username='creator2', password='pass')
    decl = Declaration.objects.create(code='KDV1', period='2025-03', taxpayer_vkn_tckn='33333333333', payload={}, created_by=creator)

    client = APIClient()
    client.force_authenticate(user=advisor_user)

    resp = client.post('/api/v1/submissions/submissions/', {'declaration': decl.id}, format='json')
    assert resp.status_code in (401, 403)

    # Find the latest submission (may have been created then marked rejected before raising)
    sub = Submission.objects.order_by('-id').first()
    assert sub is not None
    assert sub.status == 'rejected'
    # Error log exists
    assert SubmissionLog.objects.filter(submission=sub, level='error').exists()
