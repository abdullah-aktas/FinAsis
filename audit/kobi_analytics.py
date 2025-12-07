"""
KOBİ-Focused Audit Analytics Module
KOBİ Odaklı Audit Analiz ve Raporlama Sistemi
"""

from datetime import timedelta
from typing import Dict, List
from django.db.models import Sum, Q
from django.utils import timezone


class KOBIAuditAnalytics:
    """
    KOBİ'ler için özelleştirilmiş audit analytics
    - Basitleştirilmiş metrikler
    - Sektör benchmarking
    - Maliyet optimizasyonu
    - Uyumluluk kontrolleri
    """

    # Türkiye'de KOBİ sınıflandırması (Yıllık net satış hasılatı veya mali bilanço büyüklüğü)
    KOBI_CLASSIFICATIONS = {
        "mikro": {"max_revenue": 3000000, "max_employees": 10},  # 3M TL
        "kucuk": {"max_revenue": 25000000, "max_employees": 50},  # 25M TL
        "orta": {"max_revenue": 125000000, "max_employees": 250},  # 125M TL
    }

    @classmethod
    def get_kobi_health_score(
        cls, company, audit_events, financial_data: Dict = None
    ) -> Dict:
        """
        KOBİ'nin genel sağlık skorunu hesapla (0-100)

        Factors:
        - Audit trail kalitesi (20%)
        - Finansal sağlık (25%)
        - Uyumluluk durumu (25%)
        - Operasyonel verimlilik (15%)
        - Risk seviyesi (15%)
        """
        scores = {}

        # 1. Audit Trail Kalitesi (20%)
        audit_score = cls._calculate_audit_quality_score(audit_events)
        scores["audit_quality"] = audit_score * 0.20

        # 2. Finansal Sağlık (25%)
        if financial_data:
            financial_score = cls._calculate_financial_health_score(financial_data)
            scores["financial_health"] = financial_score * 0.25
        else:
            scores["financial_health"] = 50 * 0.25  # Default orta skor

        # 3. Uyumluluk Durumu (25%)
        compliance_score = cls._calculate_compliance_score(audit_events)
        scores["compliance"] = compliance_score * 0.25

        # 4. Operasyonel Verimlilik (15%)
        operational_score = cls._calculate_operational_efficiency(audit_events)
        scores["operational_efficiency"] = operational_score * 0.15

        # 5. Risk Seviyesi (15%) - Ters skala: düşük risk = yüksek skor
        risk_score = cls._calculate_risk_impact(audit_events)
        scores["risk_management"] = (100 - risk_score) * 0.15

        total_score = sum(scores.values())

        return {
            "overall_score": round(total_score, 1),
            "breakdown": {
                "audit_quality": round(audit_score, 1),
                "financial_health": round(financial_score if financial_data else 50, 1),
                "compliance": round(compliance_score, 1),
                "operational_efficiency": round(operational_score, 1),
                "risk_management": round(100 - risk_score, 1),
            },
            "grade": cls._score_to_grade(total_score),
            "status": cls._score_to_status(total_score),
            "recommendations": cls._generate_health_recommendations(
                scores, total_score
            ),
        }

    @classmethod
    def _calculate_audit_quality_score(cls, events) -> float:
        """Audit trail kalitesi skoru"""
        if not events.exists():
            return 30  # Hiç audit yoksa düşük skor

        recent_events = events.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        )

        score = 50  # Base score

        # Düzenli kayıt (+20)
        if recent_events.count() >= 50:
            score += 20
        elif recent_events.count() >= 20:
            score += 10

        # Detaylı kayıtlar (+15)
        detailed_events = recent_events.exclude(description="")
        if detailed_events.count() / max(recent_events.count(), 1) > 0.7:
            score += 15

        # Kritik olayların takibi (+15)
        critical_reviewed = recent_events.filter(
            severity__in=["high", "critical"], reviewed_by__isnull=False
        ).count()
        critical_total = recent_events.filter(severity__in=["high", "critical"]).count()

        if critical_total > 0 and (critical_reviewed / critical_total) > 0.8:
            score += 15

        return min(100, score)

    @classmethod
    def _calculate_financial_health_score(cls, financial_data: Dict) -> float:
        """Finansal sağlık skoru"""
        score = 50  # Base

        # Karlılık
        net_profit_margin = financial_data.get("net_profit_margin", 0)
        if net_profit_margin > 15:
            score += 20
        elif net_profit_margin > 5:
            score += 10
        elif net_profit_margin < 0:
            score -= 20

        # Likidite
        current_ratio = financial_data.get("current_ratio", 1)
        if current_ratio > 2:
            score += 15
        elif current_ratio > 1.5:
            score += 10
        elif current_ratio < 1:
            score -= 15

        # Borçluluk
        debt_ratio = financial_data.get("debt_ratio", 0.5)
        if debt_ratio < 0.3:
            score += 15
        elif debt_ratio < 0.5:
            score += 5
        elif debt_ratio > 0.7:
            score -= 15

        return max(0, min(100, score))

    @classmethod
    def _calculate_compliance_score(cls, events) -> float:
        """Uyumluluk skoru"""
        score = 70  # Base (varsayılan uyumlu)

        # Compliance kategorisindeki olaylar
        compliance_events = events.filter(category="compliance")

        if not compliance_events.exists():
            return 80  # Compliance sorunu yok

        # Kritik uyumluluk ihlalleri
        critical_compliance = compliance_events.filter(
            severity__in=["high", "critical"]
        )
        if critical_compliance.exists():
            score -= critical_compliance.count() * 10

        # Çözülmüş sorunlar
        resolved = compliance_events.filter(reviewed_by__isnull=False).count()
        total = compliance_events.count()

        if total > 0:
            resolution_rate = resolved / total
            score += resolution_rate * 20

        return max(0, min(100, score))

    @classmethod
    def _calculate_operational_efficiency(cls, events) -> float:
        """Operasyonel verimlilik skoru"""
        score = 60  # Base

        # Son 30 gündeki işlem hızı
        recent = events.filter(created_at__gte=timezone.now() - timedelta(days=30))

        if recent.count() > 100:
            score += 20  # Yüksek aktivite
        elif recent.count() < 20:
            score -= 10  # Düşük aktivite

        # Hata oranı
        error_events = recent.filter(severity__in=["high", "critical"])
        if recent.count() > 0:
            error_rate = error_events.count() / recent.count()
            if error_rate < 0.05:
                score += 20
            elif error_rate > 0.15:
                score -= 20

        return max(0, min(100, score))

    @classmethod
    def _calculate_risk_impact(cls, events) -> float:
        """Risk etki skoru (yüksek = kötü)"""
        risk = 20  # Base risk

        # Yüksek ciddiyet
        high_severity = events.filter(severity__in=["high", "critical"]).count()
        risk += high_severity * 5

        # Finansal etki
        total_financial_impact = (
            events.aggregate(total=Sum("financial_impact"))["total"] or 0
        )

        if total_financial_impact > 100000:
            risk += 30
        elif total_financial_impact > 50000:
            risk += 15

        return min(100, risk)

    @classmethod
    def _score_to_grade(cls, score: float) -> str:
        """Skor'u harf notuna çevir"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"

    @classmethod
    def _score_to_status(cls, score: float) -> str:
        """Skor'u durum mesajına çevir"""
        if score >= 85:
            return "Mükemmel"
        elif score >= 70:
            return "İyi"
        elif score >= 50:
            return "Orta"
        elif score >= 30:
            return "Zayıf"
        else:
            return "Kritik"

    @classmethod
    def _generate_health_recommendations(cls, scores: Dict, total: float) -> List[str]:
        """Sağlık skoruna göre öneriler"""
        recommendations = []

        if scores.get("audit_quality", 0) < 15:
            recommendations.append(
                "📋 Audit kayıtlarınızı düzenli tutun ve detaylandırın"
            )

        if scores.get("financial_health", 0) < 15:
            recommendations.append(
                "💰 Finansal göstergelerinizi iyileştirin, nakit akışını optimize edin"
            )

        if scores.get("compliance", 0) < 15:
            recommendations.append(
                "⚖️ Uyumluluk sorunlarını acilen çözün, yasal danışman desteği alın"
            )

        if scores.get("operational_efficiency", 0) < 10:
            recommendations.append(
                "⚙️ Operasyonel süreçlerinizi gözden geçirin, otomasyonu artırın"
            )

        if scores.get("risk_management", 0) < 10:
            recommendations.append(
                "🛡️ Risk yönetimi stratejinizi güçlendirin, sigorta değerlendirin"
            )

        if total >= 85:
            recommendations.append("✅ Harika! Mevcut performansınızı sürdürün")
        elif total < 50:
            recommendations.append("⚠️ Acil eylem gerekli! Profesyonel danışmanlık alın")

        return recommendations

    @classmethod
    def get_sector_benchmarking(
        cls, company, audit_events, sector: str = "genel"
    ) -> Dict:
        """
        Sektör karşılaştırması (benchmarking)
        """
        # Bu örnekte sabit veriler, production'da gerçek sektör verileri kullanılmalı
        sector_averages = {
            "genel": {
                "audit_quality": 65,
                "compliance_score": 72,
                "risk_score": 35,
                "operational_efficiency": 68,
            },
            "imalat": {
                "audit_quality": 70,
                "compliance_score": 75,
                "risk_score": 40,
                "operational_efficiency": 72,
            },
            "ticaret": {
                "audit_quality": 62,
                "compliance_score": 68,
                "risk_score": 32,
                "operational_efficiency": 65,
            },
            "hizmet": {
                "audit_quality": 68,
                "compliance_score": 73,
                "risk_score": 30,
                "operational_efficiency": 70,
            },
        }

        sector_avg = sector_averages.get(sector, sector_averages["genel"])

        # Şirket skorları
        company_audit = cls._calculate_audit_quality_score(audit_events)
        company_compliance = cls._calculate_compliance_score(audit_events)
        company_risk = cls._calculate_risk_impact(audit_events)
        company_operational = cls._calculate_operational_efficiency(audit_events)

        return {
            "sector": sector,
            "comparison": {
                "audit_quality": {
                    "company": round(company_audit, 1),
                    "sector_avg": sector_avg["audit_quality"],
                    "difference": round(company_audit - sector_avg["audit_quality"], 1),
                    "status": (
                        "üstünde"
                        if company_audit > sector_avg["audit_quality"]
                        else "altında"
                    ),
                },
                "compliance": {
                    "company": round(company_compliance, 1),
                    "sector_avg": sector_avg["compliance_score"],
                    "difference": round(
                        company_compliance - sector_avg["compliance_score"], 1
                    ),
                    "status": (
                        "üstünde"
                        if company_compliance > sector_avg["compliance_score"]
                        else "altında"
                    ),
                },
                "risk_management": {
                    "company": round(100 - company_risk, 1),
                    "sector_avg": 100 - sector_avg["risk_score"],
                    "difference": round(
                        (100 - company_risk) - (100 - sector_avg["risk_score"]), 1
                    ),
                    "status": (
                        "üstünde"
                        if company_risk < sector_avg["risk_score"]
                        else "altında"
                    ),
                },
                "operational_efficiency": {
                    "company": round(company_operational, 1),
                    "sector_avg": sector_avg["operational_efficiency"],
                    "difference": round(
                        company_operational - sector_avg["operational_efficiency"], 1
                    ),
                    "status": (
                        "üstünde"
                        if company_operational > sector_avg["operational_efficiency"]
                        else "altında"
                    ),
                },
            },
            "insights": cls._generate_benchmark_insights(
                company_audit,
                company_compliance,
                company_risk,
                company_operational,
                sector_avg,
            ),
        }

    @classmethod
    def _generate_benchmark_insights(
        cls, audit, compliance, risk, operational, sector_avg
    ) -> List[str]:
        """Benchmark karşılaştırma önerileri"""
        insights = []

        if audit > sector_avg["audit_quality"] + 10:
            insights.append("🌟 Audit kalitesi sektör ortalamasının üzerinde!")
        elif audit < sector_avg["audit_quality"] - 10:
            insights.append(
                "📊 Audit kayıtlarınızı sektör standardına yükseltmelisiniz"
            )

        if compliance > sector_avg["compliance_score"] + 5:
            insights.append("✅ Uyumluluk performansınız sektörün önünde")
        elif compliance < sector_avg["compliance_score"] - 5:
            insights.append("⚠️ Uyumluluk skorunuz sektör ortalamasının altında")

        if risk < sector_avg["risk_score"] - 5:
            insights.append("🛡️ Risk yönetiminiz sektörden daha iyi")
        elif risk > sector_avg["risk_score"] + 5:
            insights.append("⚡ Risk seviyeniz sektör ortalamasının üzerinde, dikkat!")

        return insights

    @classmethod
    def get_cost_optimization_opportunities(
        cls, audit_events, financial_data: Dict = None
    ) -> List[Dict]:
        """
        Maliyet optimizasyonu fırsatları
        """
        opportunities = []

        # 1. Manuel süreçler otomasyonu
        manual_events = audit_events.filter(
            Q(description__icontains="manuel") | Q(description__icontains="el ile")
        ).count()

        if manual_events > 20:
            opportunities.append(
                {
                    "title": "Süreç Otomasyonu",
                    "category": "efficiency",
                    "potential_saving": "15-25% zaman tasarrufu",
                    "description": f"{manual_events} adet manuel işlem tespit edildi. Otomasyon ile hızlandırılabilir.",
                    "priority": "high",
                    "estimated_impact": "Yılda 50-100 saat tasarruf",
                    "actions": [
                        "Tekrarlayan manuel işlemleri belirleyin",
                        "RPA (Robotic Process Automation) değerlendirin",
                        "Entegrasyon iyileştirmeleri yapın",
                    ],
                }
            )

        # 2. Uyumluluk maliyetleri
        compliance_issues = audit_events.filter(
            category="compliance", severity__in=["medium", "high", "critical"]
        ).count()

        if compliance_issues > 5:
            opportunities.append(
                {
                    "title": "Uyumluluk Maliyetlerini Azaltma",
                    "category": "compliance",
                    "potential_saving": "10-20% uyumluluk maliyeti",
                    "description": f"{compliance_issues} adet uyumluluk sorunu. Önleyici tedbirlerle maliyet azaltılabilir.",
                    "priority": "medium",
                    "estimated_impact": "Yıllık 20-40 bin TL tasarruf",
                    "actions": [
                        "Düzenli uyumluluk eğitimleri verin",
                        "Otomatik kontrol sistemleri kurun",
                        "Yasal danışman ile uzun vadeli anlaşma yapın",
                    ],
                }
            )

        # 3. Finansal süreç iyileştirme
        if financial_data:
            dso = financial_data.get("days_sales_outstanding", 45)
            if dso > 60:
                opportunities.append(
                    {
                        "title": "Alacak Tahsilat Süresi İyileştirme",
                        "category": "financial",
                        "potential_saving": f"{dso - 45} gün daha erken nakit girişi",
                        "description": f"Ortalama tahsilat süresi {dso} gün. Sektör ortalaması 45 gün.",
                        "priority": "high",
                        "estimated_impact": "İyileştirilmiş nakit akışı",
                        "actions": [
                            "Erken ödeme indirimleri sunun",
                            "Otomatik hatırlatma sistemleri kurun",
                            "Ödeme koşullarını gözden geçirin",
                        ],
                    }
                )

        # 4. Teknik borç ve sistem iyileştirme
        system_errors = audit_events.filter(
            severity="critical", category="operational"
        ).count()

        if system_errors > 10:
            opportunities.append(
                {
                    "title": "Sistem ve Altyapı İyileştirme",
                    "category": "technology",
                    "potential_saving": "20-30% operasyonel maliyet",
                    "description": f"{system_errors} adet kritik sistem hatası. Altyapı yatırımı gerekli.",
                    "priority": "high",
                    "estimated_impact": "Yıllık 30-60 bin TL tasarruf",
                    "actions": [
                        "Sistem güncellemeleri yapın",
                        "Bulut altyapısına geçişi değerlendirin",
                        "IT desteğini güçlendirin",
                    ],
                }
            )

        return sorted(
            opportunities,
            key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]],
            reverse=True,
        )

    @classmethod
    def generate_executive_summary(cls, company, audit_events, period_days=30) -> Dict:
        """
        Yönetim özeti raporu (Executive Summary)
        KOBİ yöneticileri için basitleştirilmiş
        """
        cutoff = timezone.now() - timedelta(days=period_days)
        recent_events = audit_events.filter(created_at__gte=cutoff)

        # Temel metrikler
        total_events = recent_events.count()
        critical_events = recent_events.filter(severity="critical").count()
        high_events = recent_events.filter(severity="high").count()

        # Finansal etki
        financial_impact = (
            recent_events.aggregate(total=Sum("financial_impact"))["total"] or 0
        )

        # Trend
        previous_period = audit_events.filter(
            created_at__gte=cutoff - timedelta(days=period_days), created_at__lt=cutoff
        ).count()

        trend = (
            "artış"
            if total_events > previous_period
            else "azalış" if total_events < previous_period else "stabil"
        )
        trend_percent = abs(
            ((total_events - previous_period) / max(previous_period, 1)) * 100
        )

        # Sağlık skoru
        health = cls.get_kobi_health_score(company, audit_events)

        return {
            "period": f"Son {period_days} gün",
            "summary": {
                "health_score": health["overall_score"],
                "grade": health["grade"],
                "status": health["status"],
                "total_events": total_events,
                "critical_events": critical_events,
                "high_priority_events": high_events,
                "financial_impact": float(financial_impact),
                "trend": trend,
                "trend_percentage": round(trend_percent, 1),
            },
            "key_highlights": [
                f"Genel sağlık skoru: {health['overall_score']}/100 ({health['status']})",
                f"Toplam {total_events} olay kaydedildi ({trend} trendi: %{trend_percent:.1f})",
                f"{'⚠️ ' if critical_events > 0 else '✅ '}{critical_events} kritik olay"
                + (" - Acil dikkat gerekli!" if critical_events > 5 else ""),
                f"Finansal etki: {financial_impact:,.2f} TL",
            ],
            "action_items": cls._generate_action_items(
                critical_events, high_events, health
            ),
            "next_steps": [
                "Kritik olayları inceleyin ve çözümleyin",
                "Aylık denetim raporunu hazırlayın",
                "Önerilen iyileştirmeleri uygulayın",
                "Bir sonraki performans değerlendirmesini planlayın",
            ],
        }

    @classmethod
    def _generate_action_items(
        cls, critical: int, high: int, health: Dict
    ) -> List[str]:
        """Aksiyon maddeleri oluştur"""
        actions = []

        if critical > 0:
            actions.append(f"🚨 ACIL: {critical} kritik olay çözülmeli")

        if high > 5:
            actions.append(
                f"⚠️ YÜKSEK ÖNCELİK: {high} yüksek öncelikli olay takip edilmeli"
            )

        if health["overall_score"] < 60:
            actions.append(
                "📊 DİKKAT: Genel performans düşük, iyileştirme planı hazırlayın"
            )

        if health["breakdown"]["compliance"] < 70:
            actions.append("⚖️ UYUMLULUK: Yasal uyumluluk kontrollerini artırın")

        if not actions:
            actions.append("✅ Durum iyi, rutin takiplere devam edin")

        return actions
