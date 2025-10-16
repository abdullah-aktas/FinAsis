"""Quick test for audit pages"""
import pytest
from django.test import Client


def test_audit_landing_page():
    """Test /audit/ landing page"""
    c = Client()
    response = c.get('/audit/')
    assert response.status_code == 200
    # Check for key content on page
    assert b'denetim' in response.content.lower() or b'audit' in response.content.lower()
    print(f"✅ /audit/ -> Status: {response.status_code}, Size: {len(response.content)} bytes")


def test_audit_control_dashboard():
    """Test /audit/controls/dashboard/ page"""
    c = Client()
    response = c.get('/audit/controls/dashboard/')
    # May require login (302) or work (200)
    assert response.status_code in [200, 302]
    print(f"✅ /audit/controls/dashboard/ -> Status: {response.status_code}")


def test_audit_risk_assessment():
    """Test /audit/risk-assessment/ page"""
    c = Client()
    response = c.get('/audit/controls/risk-assessment/')
    # May require login (302) or work (200)
    assert response.status_code in [200, 302]
    print(f"✅ /audit/controls/risk-assessment/ -> Status: {response.status_code}")
