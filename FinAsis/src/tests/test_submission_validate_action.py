# pyright: reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from src.apps.advisors.models import AdvisorProfile, TaxpayerProfile, Engagement
from src.apps.submissions.models import Declaration, SubmissionLog


@pytest.mark.django_db
def test_validate_action_returns_issues_and_logs():
    User = get_user_model()
    advisor = User.objects.create_user(username='advisor_val', password='pass')
    AdvisorProfile.objects.create(user=advisor, type='SMMM', verified_at=timezone.now())

    tp = TaxpayerProfile.objects.create(name='Delta A.Ş.', vkn_tckn='77777777777')
    Engagement.objects.create(advisor=advisor.advisor_profile, taxpayer=tp, scope='both', status='active')

    decl = Declaration.objects.create(code='KDV1', period='2025-07', taxpayer_vkn_tckn=tp.vkn_tckn, payload={'total': -5}, created_by=advisor)

    client = APIClient()
    client.force_authenticate(user=advisor)

    # Submission oluştur
    resp = client.post('/api/v1/submissions/submissions/', {'declaration': decl.id}, format='json')
    assert resp.status_code in (200, 201)
    sub_id = resp.data['id']

    # Validate action
    resp2 = client.post(f'/api/v1/submissions/submissions/{sub_id}/validate/', {}, format='json')
    assert resp2.status_code in (200, 202)
    assert resp2.data['ok'] is False
    assert 'Toplam tutar negatif olamaz' in resp2.data['issues']

    # Log atıldı mı?
    assert SubmissionLog.objects.filter(submission_id=sub_id, level__in=['warning','info']).exists()
