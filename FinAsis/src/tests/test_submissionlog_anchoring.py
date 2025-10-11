# pyright: reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from src.apps.advisors.models import AdvisorProfile, TaxpayerProfile, Engagement
from src.apps.submissions.models import Declaration, Submission, SubmissionLog
from src.apps.blockchain.models import ChainRecord


@pytest.mark.django_db
def test_submission_log_is_anchored_on_create():
    User = get_user_model()
    advisor = User.objects.create_user(username='advisor_anchor', password='pass')
    AdvisorProfile.objects.create(user=advisor, type='SMMM', verified_at=timezone.now())

    tp = TaxpayerProfile.objects.create(name='Gamma A.Ş.', vkn_tckn='55555555555')
    Engagement.objects.create(advisor=advisor.advisor_profile, taxpayer=tp, scope='both', status='active')

    creator = User.objects.create_user(username='creator_anchor', password='pass')
    decl = Declaration.objects.create(code='KDV1', period='2025-05', taxpayer_vkn_tckn=tp.vkn_tckn, payload={}, created_by=creator)

    client = APIClient()
    client.force_authenticate(user=advisor)
    resp = client.post('/api/v1/submissions/submissions/', {'declaration': decl.id}, format='json')
    assert resp.status_code in (200, 201)
    sub_id = resp.data['id']

    # Elle bir log ekleyelim ve anchor oluştu mu kontrol edelim
    log = SubmissionLog.objects.create(submission_id=sub_id, level='info', message='Anchor test', context={'x':'y'})

    # Signal senkron çalışıyor; referans kaydını bulabilmeliyiz
    ref_prefix = f"submission:{sub_id}:log:{log.pk}"
    assert ChainRecord.objects.filter(reference=ref_prefix).exists()
