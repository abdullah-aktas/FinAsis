# -*- coding: utf-8 -*-
"""
Makine Öğrenmesi Servisleri
- Risk Skorlama (Logistic Regression)
- Finansal Tahmin (Prophet)
- Öneri Sistemi (kural tabanlı/ML)
"""
from typing import Any, Dict, Optional, List
import numpy as np
import joblib
import os
from sklearn.linear_model import LogisticRegression

# Optional dependency: prophet (may be incompatible with NumPy 2.x). Guard import.
try:
    from prophet import Prophet  # type: ignore
except Exception:
    Prophet = None  # will be validated at runtime
import pandas as pd
import datetime
from django.utils import timezone
from ..models import AIModel, UserInteraction
from django.conf import settings
from .knowledge_service import KnowledgeIndex
from django.contrib.auth import get_user_model

User = get_user_model()


class RiskScoringService:
    """
    Müşteri risk skoru için Logistic Regression tabanlı servis
    """

    log_file = "risk_model.log"

    def __init__(self, model_path: str = "risk_model.pkl"):
        self.model_path = model_path
        self.model: Optional[LogisticRegression] = self.load_model()

    def train(self, X: np.ndarray, y: np.ndarray, user=None) -> None:
        """Modeli eğitir ve kaydeder."""
        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X, y)
        self.save_model()
        accuracy = self.model.score(X, y)
        params = self.model.get_params()
        # AIModel güncelle
        model_obj, created = AIModel.objects.update_or_create(
            name="RiskScoringModel",
            model_type="risk",
            defaults={
                "version": timezone.now().strftime("%Y%m%d%H%M%S"),
                "accuracy": accuracy,
                "parameters": params,
                "last_trained": timezone.now(),
                "is_active": True,
                "description": "Logistic Regression tabanlı risk skorlama modeli.",
            },
        )
        self.log_event("Model yeniden eğitildi. Doğruluk: %.4f" % accuracy, user)

    def save_model(self) -> None:
        if self.model:
            joblib.dump(self.model, self.model_path)
            self.log_event("Model kaydedildi.")

    def load_model(self) -> Optional[LogisticRegression]:
        if os.path.exists(self.model_path):
            self.log_event("Model yüklendi.")
            return joblib.load(self.model_path)
        return None

    def predict(self, features: np.ndarray, user=None) -> dict:
        if self.model is None:
            raise Exception("Model eğitilmemiş!")
        score = float(self.model.predict_proba(features.reshape(1, -1))[0, 1])
        # AIModel'den versiyon ve parametre çek
        try:
            model_obj = AIModel.objects.get(name="RiskScoringModel", model_type="risk")
            version = model_obj.version
            params = model_obj.parameters
        except AIModel.DoesNotExist:
            version = None
            params = None
        # Feature importances (Logistic Regression coef)
        feature_names = [
            "Ortalama Gecikme",
            "Gecikme Sayısı",
            "Ortalama İşlem Tutarı",
            "İşlem Sayısı",
            "Son Ödemeden Geçen Gün",
            "Sektör Risk Skoru",
        ]
        importances = np.abs(self.model.coef_[0])
        total = importances.sum() if importances.sum() > 0 else 1
        norm_importances = importances / total
        explanation = {
            "features": [
                {"name": n, "value": float(v), "importance": float(i)}
                for n, v, i in zip(feature_names, features, norm_importances)
            ],
            "summary": f"En çok etki eden faktör: {feature_names[int(np.argmax(norm_importances))]}",
        }
        self.log_event(f"Tahmin yapıldı. Skor: {score:.4f}", user)
        return {
            "risk_score": score,
            "model_version": version,
            "model_parameters": params,
            "explanation": explanation,
        }

    def log_event(self, message: str, user=None) -> None:
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {message}\n")
        if user:
            UserInteraction.objects.create(
                user=user,
                interaction_type="analysis",
                content=message,
                ai_response="",
                processing_time=0.0,
            )


class FinancialForecastService:
    """
    Prophet tabanlı finansal tahmin servisi
    """

    log_file = "forecast_model.log"

    def __init__(self):
        self.model = None

    def train(self, df: pd.DataFrame, user=None) -> None:
        """Prophet ile modeli eğitir. df: ['ds', 'y'] sütunları olmalı."""
        if Prophet is None:
            raise RuntimeError(
                "'prophet' paketi kullanılamıyor. NumPy 2.x ile uyumsuz olabilir. Lütfen 'pip install numpy<2 prophet' ile uygun sürümleri kurun."
            )
        self.model = Prophet(yearly_seasonality=True, weekly_seasonality=True)  # type: ignore[arg-type]
        self.model.fit(df)
        # AIModel güncelle
        params = {"yearly_seasonality": True, "weekly_seasonality": True}
        model_obj, created = AIModel.objects.update_or_create(
            name="FinancialForecastModel",
            model_type="financial",
            defaults={
                "version": timezone.now().strftime("%Y%m%d%H%M%S"),
                "accuracy": 0.0,  # Prophet için cross-val eklenebilir
                "parameters": params,
                "last_trained": timezone.now(),
                "is_active": True,
                "description": "Prophet tabanlı finansal tahmin modeli.",
            },
        )
        self.log_event("Prophet modeli yeniden eğitildi.", user)

    def forecast(self, periods: int = 90, user=None) -> dict:
        if self.model is None:
            raise Exception("Model eğitilmemiş!")
        future = self.model.make_future_dataframe(periods=periods)
        forecast = self.model.predict(future)
        try:
            model_obj = AIModel.objects.get(
                name="FinancialForecastModel", model_type="financial"
            )
            version = model_obj.version
            params = model_obj.parameters
        except AIModel.DoesNotExist:
            version = None
            params = None
        self.log_event(f"{periods} gün için tahmin üretildi.", user)
        # Prophet explainability (örnek): trend, seasonality, en yüksek tahmin günü
        max_idx = forecast["yhat"].idxmax()
        # idxmax bir label döndürebilir; .loc ile erişelim
        max_row = forecast.loc[max_idx]
        max_date = str(getattr(max_row, "ds", max_row["ds"]))
        max_yhat_val = getattr(max_row, "yhat", max_row["yhat"])
        try:
            max_yhat = float(max_yhat_val)  # type: ignore[arg-type]
        except Exception:
            max_yhat = float(
                getattr(max_yhat_val, "iloc", [0])[-1]
                if hasattr(max_yhat_val, "iloc")
                else 0
            )
        explanation = {
            "features": [
                {
                    "name": "Trend",
                    "value": float(forecast["trend"].iloc[-1]),
                    "importance": 0.4,
                },
                {
                    "name": "Yearly Seasonality",
                    "value": (
                        float(forecast["yearly"].iloc[-1])
                        if "yearly" in forecast
                        else 0
                    ),
                    "importance": 0.3,
                },
                {
                    "name": "Weekly Seasonality",
                    "value": (
                        float(forecast["weekly"].iloc[-1])
                        if "weekly" in forecast
                        else 0
                    ),
                    "importance": 0.2,
                },
                {
                    "name": "En Yüksek Tahmin Günü",
                    "value": str(max_date),
                    "importance": 0.1,
                },
            ],
            "summary": f"Tahmin edilen en yüksek değer: {max_yhat:.2f} ({max_date})",
        }
        return {
            "dates": forecast["ds"].dt.strftime("%Y-%m-%d").tolist(),
            "predictions": forecast["yhat"].round(2).tolist(),
            "lower_bound": forecast["yhat_lower"].round(2).tolist(),
            "upper_bound": forecast["yhat_upper"].round(2).tolist(),
            "model_version": version,
            "model_parameters": params,
            "explanation": explanation,
        }

    def log_event(self, message: str, user=None) -> None:
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {message}\n")
        if user:
            UserInteraction.objects.create(
                user=user,
                interaction_type="analysis",
                content=message,
                ai_response="",
                processing_time=0.0,
            )


class RecommendationService:
    """
    Kural tabanlı + bilgi destekli öneri sistemi (rol farkındalığı ile).
    """

    def __init__(self):
        try:
            base_dir = getattr(settings, "BASE_DIR", None) or os.getcwd()
        except Exception:
            base_dir = os.getcwd()
        self.knowledge = KnowledgeIndex.load(
            os.path.join(base_dir, "var", "ai_knowledge.json")
        )

    def _role_hints(self, user=None) -> List[str]:
        hints: List[str] = []
        try:
            if user is not None:
                roles = list(getattr(user, "groups").all().values_list("name", flat=True))  # type: ignore
                rl = [r.lower() for r in roles]
                if "accountant" in rl:
                    hints.append(
                        "Muhasebe odaklı: kayıt doğruluğu, mutabakat ve raporlama sürekliliği."
                    )
                if "manager" in rl or getattr(user, "is_staff", False):
                    hints.append(
                        "Yönetim odaklı: özet KPI, aksiyon ve riskleri önceliklendir."
                    )
        except Exception:
            pass
        return hints

    def _basic_metrics(
        self, income: float, expenses: float, savings: float
    ) -> Dict[str, float]:
        net = float(income) - float(expenses)
        savings_rate = (float(savings) / float(income)) if income else 0.0
        expense_ratio = (float(expenses) / float(income)) if income else 0.0
        return {
            "net": net,
            "savings_rate": round(savings_rate, 3),
            "expense_ratio": round(expense_ratio, 3),
        }

    def _knowledge_tips(self, query: str, top_k: int = 2) -> List[Dict[str, str]]:
        tips: List[Dict[str, str]] = []
        if not self.knowledge:
            return tips
        tops = self.knowledge.search(query, top_k=top_k)
        for t in tops:
            tips.append(
                {
                    "title": t.title,
                    "path": t.path,
                    "snippet": t.content[:280]
                    + ("..." if len(t.content) > 280 else ""),
                }
            )
        return tips

    def generate(
        self, data: Dict[str, Any], user=None, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Kullanıcı verilerine göre öneri paketi döner."""
        income = float(data.get("income", 0) or 0)
        expenses = float(data.get("expenses", 0) or 0)
        savings = float(data.get("savings", 0) or 0)
        goal = (data.get("goals") or "").strip().lower()
        # Opsiyonel finansal oranlar (varsa değerlendir)
        current_ratio = data.get("current_ratio")
        debt_to_equity = data.get("debt_to_equity") or data.get("de_ratio")
        gross_margin = data.get("gross_margin")
        operating_margin = data.get("operating_margin")
        cash_buffer_months = data.get("cash_buffer_months")

        metrics = self._basic_metrics(income, expenses, savings)
        role_hints = self._role_hints(user)

        recs: List[Dict[str, Any]] = []

        # 1) Bütçe ve nakit akışı
        if metrics["net"] < 0:
            recs.append(
                {
                    "title": "Bütçe Dengesi Negatif",
                    "priority": "high",
                    "recommendation": "Giderlerinizi %10 azaltmayı hedefleyin ve değişken giderlerde tasarruf planı oluşturun.",
                    "actions": [
                        "Aylık gider kalemlerini sınıflandırın",
                        "Değişken giderlerde tavan belirleyin",
                        "3 ay trend takibi yapın",
                    ],
                    "kpis": {
                        "net": metrics["net"],
                        "expense_ratio": metrics["expense_ratio"],
                    },
                }
            )
        else:
            recs.append(
                {
                    "title": "Pozitif Nakit Akışı",
                    "priority": "medium",
                    "recommendation": "Artı veren bütçeyi güçlendirin; gelir çeşitlendirmesi ve maliyet optimizasyonu planlayın.",
                    "actions": [
                        "Gelir kaynaklarını çeşitlendirin",
                        "Sabit giderlerde sözleşme iyileştirme",
                    ],
                    "kpis": {
                        "net": metrics["net"],
                        "savings_rate": metrics["savings_rate"],
                    },
                }
            )

        # 2) Finansal oranlara göre uyarılar/öneriler
        if isinstance(current_ratio, (int, float)):
            try:
                cr = float(current_ratio)
                if cr < 1.2:
                    recs.append(
                        {
                            "title": "Cari Oran Düşük",
                            "priority": "high",
                            "recommendation": "Kısa vadeli yükümlülüklere karşı likiditeyi güçlendirin. Alacak tahsil sürelerini kısaltın, stok devir hızını artırın.",
                            "actions": [
                                "Erken ödeme iskonto politikası",
                                "Stok optimizasyonu",
                                "Kısa vadeli borç yapılandırma",
                            ],
                            "kpis": {"current_ratio": round(cr, 2), "target": 1.2},
                        }
                    )
            except Exception:
                pass
        if isinstance(debt_to_equity, (int, float)):
            try:
                de = float(debt_to_equity)
                if de > 2.0:
                    recs.append(
                        {
                            "title": "Borç/Özsermaye Yüksek",
                            "priority": "high",
                            "recommendation": "Kaldıraç yüksek. Nakit yaratmayan borçları azaltın; özsermaye güçlendirme veya uzun vade yeniden finansman düşünün.",
                            "actions": [
                                "Vade uzatma görüşmeleri",
                                "Özsermaye katkısı planı",
                                "Varlık satışı değerlendirmesi",
                            ],
                            "kpis": {"debt_to_equity": round(de, 2), "target_max": 2.0},
                        }
                    )
            except Exception:
                pass
        if isinstance(gross_margin, (int, float)):
            try:
                gm = float(gross_margin)
                if gm < 0.2:
                    recs.append(
                        {
                            "title": "Brüt Marj Düşük",
                            "priority": "medium",
                            "recommendation": "Fiyatlandırma ve tedarik maliyetlerini gözden geçirin. Kârlı ürün/müşteri segmentlerine odaklanın.",
                            "actions": [
                                "Maliyet düşürme planı",
                                "Segment bazlı fiyat güncelleme",
                            ],
                            "kpis": {"gross_margin": round(gm, 3), "target_min": 0.25},
                        }
                    )
            except Exception:
                pass
        if isinstance(operating_margin, (int, float)):
            try:
                om = float(operating_margin)
                if om < 0.1:
                    recs.append(
                        {
                            "title": "Faaliyet Marjı Zayıf",
                            "priority": "medium",
                            "recommendation": "Faaliyet giderlerini (OPEX) kontrol altına alın, verimlilik projeleri başlatın.",
                            "actions": [
                                "Gider tavanları",
                                "Süreç otomasyonu",
                                "Satın alma sözleşmeleri revizyonu",
                            ],
                            "kpis": {
                                "operating_margin": round(om, 3),
                                "target_min": 0.12,
                            },
                        }
                    )
            except Exception:
                pass
        if isinstance(cash_buffer_months, (int, float)):
            try:
                cb = float(cash_buffer_months)
                if cb < 3:
                    recs.append(
                        {
                            "title": "Nakit Yastığı Yetersiz",
                            "priority": "high",
                            "recommendation": "En az 3-6 aylık işletme giderini karşılayacak nakit yastığı oluşturun.",
                            "actions": [
                                "Acil durum fonu planı",
                                "Kredi limitleri gözden geçirme",
                            ],
                            "kpis": {
                                "cash_buffer_months": round(cb, 2),
                                "target_min": 3,
                            },
                        }
                    )
            except Exception:
                pass

        # 3) Hedefe göre öneriler
        if goal == "investment":
            recs.append(
                {
                    "title": "Yatırım Disiplini",
                    "priority": "medium",
                    "recommendation": "Düşük/orta riskli enstrümanlarla hedef bazlı portföy. Stop-loss ve dönemsel rebalancing uygulayın.",
                    "actions": [
                        "Hedef-vadeye göre dağılım belirleyin",
                        "Aylık otomatik alım planı",
                    ],
                }
            )
        elif goal == "savings":
            recs.append(
                {
                    "title": "Birikim Oranı Artışı",
                    "priority": "medium",
                    "recommendation": "Tasarruf oranını kademeli olarak %5-%10 artırmayı hedefleyin.",
                    "actions": [
                        "Otomatik aktarım talimatı",
                        "Gereksiz abonelikleri gözden geçirin",
                    ],
                }
            )
        elif goal == "debt":
            recs.append(
                {
                    "title": "Borç Azaltma Planı",
                    "priority": "high",
                    "recommendation": "Faizi yüksek borçları önceliklendirerek kademeli ödeme planı oluşturun.",
                    "actions": [
                        "Borç listesi ve faiz oranı bazlı sıralama",
                        "Ödeme planı oluşturma",
                    ],
                }
            )
        elif goal == "retirement":
            recs.append(
                {
                    "title": "Emeklilik Stratejisi",
                    "priority": "medium",
                    "recommendation": "Uzun vadeli fonlar ve vergi avantajlarından faydalanarak düzenli katkı yapın.",
                    "actions": [
                        "Bireysel emeklilik katkı planı",
                        "Yıllık gözden geçirme",
                    ],
                }
            )

        # 4) Bilgi destekli ipuçları
        kb_tips = self._knowledge_tips(goal or "bütçe nakit akışı")
        if kb_tips:
            recs.append(
                {
                    "title": "İlgili Dokümanlar",
                    "priority": "low",
                    "recommendation": "Aşağıdaki içeriği gözden geçirerek planınızı güçlendirin.",
                    "references": kb_tips,
                }
            )

        # Rol uyarlaması: yöneticiye özet, muhasebeye detaylı aksiyon vurgusu
        if role_hints:
            if any("Yönetim" in h for h in role_hints):
                # Yönetici için en kritik 3 öneri
                recs = sorted(
                    recs,
                    key=lambda r: (
                        0
                        if r.get("priority") == "high"
                        else (1 if r.get("priority") == "medium" else 2)
                    ),
                )[:3]

        package = {
            "recommendations": recs,
            "metrics": metrics,
            "role_hints": role_hints,
            "model_version": "v2.0.0",
            "model_parameters": {"type": "rule+kb", "rules": len(recs)},
        }
        return package


class SimpleVoucherClassifier:
    """
    Basit anahtar kelime tabanlı sınıflandırıcı: alış/satış/gider/banka.
    Yerel, hızlı ve açıklanabilir.
    """

    def predict(self, text: str) -> str:
        t = (text or "").lower()
        if any(k in t for k in ["satış", "satis", "fatura satış", "e-fatura satış"]):
            return "sales"
        if any(k in t for k in ["alış", "alis", "satın alma", "supplier", "tedarikçi"]):
            return "purchase"
        if any(k in t for k in ["gider", "fatura gider", "harcama", "expense"]):
            return "expense"
        if any(k in t for k in ["banka", "havale", "eft", "pos"]):
            return "bank"
        return "expense"
