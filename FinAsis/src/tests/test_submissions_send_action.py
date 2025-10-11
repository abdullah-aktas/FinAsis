# pyright: reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from src.apps.advisors.models import AdvisorProfile, TaxpayerProfile, Engagement
from src.apps.submissions.models import Declaration, Submission


@pytest.mark.django_db
def test_send_action_transitions_to_accepted():
    User = get_user_model()
    advisor = User.objects.create_user(username='advisor_send', password='pass')
    AdvisorProfile.objects.create(user=advisor, type='SMMM', verified_at=timezone.now())

    tp = TaxpayerProfile.objects.create(name='Beta A.Ş.', vkn_tckn='44444444444')
    Engagement.objects.create(advisor=advisor.advisor_profile, taxpayer=tp, scope='both', status='active')

    creator = User.objects.create_user(username='creator_send', password='pass')
    decl = Declaration.objects.create(code='KDV1', period='2025-04', taxpayer_vkn_tckn=tp.vkn_tckn, payload={}, created_by=creator)

    client = APIClient()
    client.force_authenticate(user=advisor)
    # Create submission
    resp = client.post('/api/v1/submissions/submissions/', {'declaration': decl.id}, format='json')
    assert resp.status_code in (200, 201)
    sub_id = resp.data['id']

    # Trigger send action
    resp2 = client.post(f'/api/v1/submissions/submissions/{sub_id}/send/', {}, format='json')
    assert resp2.status_code in (200, 202)
    assert resp2.data['status'] == 'accepted'

    sub = Submission.objects.get(pk=sub_id)
    assert sub.status == 'accepted'
    assert sub.external_id.startswith('SIM-')
