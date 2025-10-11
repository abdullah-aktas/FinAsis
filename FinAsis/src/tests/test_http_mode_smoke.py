# pyright: reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
import os
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from src.apps.advisors.models import AdvisorProfile, TaxpayerProfile, Engagement
from src.apps.submissions.models import Declaration, Submission


@pytest.mark.django_db
def test_http_mode_smoke_with_mock_endpoints(live_server):
    # Configure HTTP mode to use the Django live test server mock endpoints
    os.environ['EDOC_GIB_MODE'] = 'http'
    os.environ['EDOC_GIB_BASE_URL'] = live_server.url + '/gib-mock'
    os.environ['GIB_TEST_BASE_URL'] = os.environ['EDOC_GIB_BASE_URL']

    User = get_user_model()
    advisor = User.objects.create_user(username='advisor_http', password='pass')
    AdvisorProfile.objects.create(user=advisor, type='SMMM', verified_at=timezone.now())

    tp = TaxpayerProfile.objects.create(name='HTTP A.Ş.', vkn_tckn='66666666666')
    Engagement.objects.create(advisor=advisor.advisor_profile, taxpayer=tp, scope='both', status='active')

    creator = User.objects.create_user(username='creator_http', password='pass')
    decl = Declaration.objects.create(code='KDV1', period='2025-06', taxpayer_vkn_tckn=tp.vkn_tckn, payload={}, created_by=creator)

    client = APIClient()
    client.force_authenticate(user=advisor)

    # Create submission
    resp = client.post('/api/v1/submissions/submissions/', {'declaration': decl.id}, format='json')
    assert resp.status_code in (200, 201)
    sub_id = resp.data['id']

    # Send via HTTP adapter using mock endpoints
    resp2 = client.post(f'/api/v1/submissions/submissions/{sub_id}/send/', {}, format='json')
    assert resp2.status_code in (200, 202)
    assert resp2.data['status'] in ('ACCEPTED', 'accepted')

    sub = Submission.objects.get(pk=sub_id)
    assert sub.external_id
    assert sub.status in ('accepted', 'sent')  # accepted expected; sent tolerated for eventual consistency
