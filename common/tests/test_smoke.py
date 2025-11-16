import json
from pathlib import Path

import numpy as np
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import NoReverseMatch, get_resolver, reverse

from ai_assistant.services.ml_service import RiskScoringService


class SmokeTests(TestCase):
    """
    Projenin temel bileşenlerini hızlıca tarayan genel test:
    - URL'lerin büyük kısmına GET isteği
    - Template/render ve view'lerin 500/404 vermemesi
    - Admin panelinin ve AI servislerinin ulaşılabilirliği
    """

    @classmethod
    def setUpTestData(cls):
        # Ortamı ve demo verilerini hazırla
        call_command("setup_test_environment", verbosity=0)
        user_model = get_user_model()
        cls.admin_username = "demo_superadmin"
        cls.admin_password = "FinAsis!2025"
        cls.admin = user_model.objects.get(username=cls.admin_username)
        cls._ensure_ai_model_ready()

    @classmethod
    def _ensure_ai_model_ready(cls):
        """
        Risk skor modeli smoke testte kullanılacak durumda mı kontrol et.
        Model dosyası yoksa küçük bir demo veri seti ile eğitir.
        """
        base_dir = Path(getattr(settings, "BASE_DIR", Path.cwd()))
        model_path = base_dir / "risk_model.pkl"
        service = RiskScoringService(model_path=str(model_path))
        if service.model is None or not model_path.exists():
            X = np.array(
                [
                    [0.5, 1, 1500.0, 12, 10, 0.2],
                    [0.7, 3, 2200.0, 15, 20, 0.4],
                    [0.1, 0, 4800.0, 30, 5, 0.1],
                    [0.9, 5, 1200.0, 9, 35, 0.6],
                    [0.2, 1, 5100.0, 21, 7, 0.15],
                    [0.3, 0, 4500.0, 18, 8, 0.12],
                    [1.2, 6, 900.0, 8, 45, 0.75],
                    [0.4, 2, 2000.0, 14, 16, 0.28],
                    [0.8, 4, 1300.0, 10, 28, 0.52],
                    [0.6, 1, 3200.0, 17, 9, 0.24],
                ],
                dtype=float,
            )
            y = np.array([0, 0, 0, 1, 0, 0, 1, 0, 1, 0], dtype=int)
            service.train(X, y, user=cls.admin)

    def setUp(self):
        self.client = Client()

    def test_public_urls_do_not_crash(self):
        """
        URLConf içindeki "parametre gerektirmeyen" pattern'lere GET atar.
        404 ve 500 hatalarını yakalamak için hızlı bir tarama sağlar.
        Admin, API ve özel path'leri istersen filtreleyebilirsin.
        """

        resolver = get_resolver()
        checked_urls = []

        for pattern in resolver.url_patterns:
            try:
                pattern_str = str(pattern.pattern)
            except Exception:
                pattern_str = repr(pattern)

            if pattern_str.startswith("admin"):
                continue

            # Skip i18n set_language endpoint (POST only)
            if pattern_str.startswith("i18n"):
                continue

            if "<" in pattern_str and ">" in pattern_str:
                continue

            # Skip regex-based patterns like static/media catch-alls
            if "(?P<" in pattern_str or "(" in pattern_str:
                continue

            url = "/" + pattern_str.lstrip("^/").rstrip("$")

            if "{" in url or "}" in url:
                continue

            checked_urls.append(url)
            response = self.client.get(url)
            self.assertNotIn(
                response.status_code,
                [404, 500],
                msg=f"URL hata verdi: {url} (status={response.status_code})",
            )

        self.assertTrue(len(checked_urls) > 0, "Hiç URL test edilmedi, URLConf kontrol et.")

    def test_admin_login_and_index(self):
        """
        Admin paneli gerçekten çalışıyor mu?
        """

        resp_login = self.client.get("/admin/")
        self.assertIn(resp_login.status_code, [200, 302])

        logged_in = self.client.login(username=self.admin_username, password=self.admin_password)
        self.assertTrue(logged_in, "Hazırlık admin kullanıcısıyla login olunamadı.")

        resp_admin = self.client.get("/admin/")
        self.assertIn(
            resp_admin.status_code,
            [200, 302],
            msg=f"Admin index erişiminde sorun var, status={resp_admin.status_code}",
        )

    def test_example_button_in_homepage(self):
        """
        Örnek: Ana sayfanda belli bir butonun (örneğin 'Giriş Yap') varlığını test etmek.
        Bu testteki yazıyı kendi front-end’ine göre değiştir.
        """

        try:
            url = reverse("home")
        except NoReverseMatch:
            url = "/"

        resp = self.client.get(url, follow=True)
        self.assertIn(resp.status_code, [200, 302])
        expected_snippets = [
            'data-cta="nav-login"'.encode("utf-8"),
            "Giriş".encode("utf-8"),
        ]
        self.assertTrue(
            any(snippet in resp.content for snippet in expected_snippets),
            msg="Ana sayfada oturum açma çağrısı (data-cta=nav-login) bulunamadı.",
        )

    def test_ai_health_endpoint(self):
        """AI sağlık denetimi endpoint'i erişilebilir olmalı."""
        self.client.force_login(self.admin)
        url = reverse("ai_assistant:ai-health")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload.get("ok", False))

    def test_ai_risk_score_endpoint(self):
        """Risk skoru API'si eğitimli model ile 200 dönmeli."""
        self.client.force_login(self.admin)
        url = reverse("ai_assistant:ml-risk-score")
        features = [0.45, 2, 2100.0, 14, 18, 0.35]
        response = self.client.post(
            url,
            data=json.dumps({"features": features}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content[:200])
        payload = response.json()
        self.assertIn("risk_score", payload)
        self.assertGreaterEqual(payload["risk_score"], 0)
        self.assertLessEqual(payload["risk_score"], 1)
        self.assertIn("explanation", payload)
        self.assertIsInstance(payload["explanation"].get("features", []), list)


