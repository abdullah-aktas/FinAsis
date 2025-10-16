#!/usr/bin/env python
"""Quick test script for audit pages"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import Client

def test_audit_pages():
    c = Client()
    
    pages = [
        '/audit/',
        '/audit/controls/dashboard/',
        '/audit/risk-assessment/',
    ]
    
    print("Testing audit pages:")
    print("=" * 60)
    
    for url in pages:
        try:
            r = c.get(url)
            status = r.status_code
            template = r.templates[0].name if r.templates else "None"
            size = len(r.content)
            
            status_icon = "✅" if status == 200 else "❌"
            print(f"{status_icon} {url}")
            print(f"   Status: {status} | Template: {template} | Size: {size} bytes")
            
            if status != 200:
                print(f"   Error: {r.content.decode('utf-8')[:200]}")
        except Exception as e:
            print(f"❌ {url}")
            print(f"   Exception: {str(e)[:200]}")
        print()

if __name__ == '__main__':
    test_audit_pages()
