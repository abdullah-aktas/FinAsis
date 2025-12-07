# -*- coding: utf-8 -*-
from __future__ import annotations

"""
RecommendationService: Kullanıcı tercihleri, piyasa/portföy verileri ve bağlamdan
aksiyon odaklı öneriler üretir; sonuçları AIInsight kayıtlarına işler.

Notlar:
- OpenAI kullanımı isteğe bağlıdır; yanıt üretimi başarısız olursa kural tabanlı
  minimal üretimle devam edilir.
- Testler, openai çağrısını mock'lar; bu nedenle çağrı yolu uyumludur.
"""

from typing import Any, Dict, List  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from django.db import transaction  # noqa: E402
from django.contrib.auth.models import AbstractBaseUser  # noqa: E402
import re  # noqa: E402

from ai_assistant.models import AIInsight, AIModel, UserPreference  # noqa: E402

# Not: get_user_model() çalışma zamanında model sınıfını döndürür; bunu tip ipucunda
# kullanmak Pyright/Pylance için geçerli değildir. Tip ipucu olarak AbstractBaseUser
# kullanmak en uyumlu yoldur.


@dataclass
class GeneratedRecommendation:
    title: str
    recommendations: List[str]
    category: str
    priority: str
    action_required: bool


class RecommendationService:
    async def generate_recommendations(
        self, user: AbstractBaseUser, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Kullanıcı için önerileri üretir ve kaydeder.
        Dönüş: [{'title','recommendations','category','priority','action_required'}]
        """
        from asgiref.sync import sync_to_async

        # Kullanıcı tercihleri
        prefs = await sync_to_async(
            lambda: UserPreference.objects.filter(user=user).first()
        )()

        # Prompt hazırla
        self._create_enhanced_recommendation_prompt(
            user_preferences=prefs,
            market_data=context.get("market_data") or "",
            portfolio_data=context.get("portfolio_data") or "",
            context=context,
        )

        # Dış bağımlılık olmadan yerel (kural/istatistik) üretim
        sections_text = self._local_generate_sections(
            user=user, prefs=prefs, context=context
        )

        recs = self._parse_recommendation_sections(sections_text)

        # Kaydet (AIInsight)
        await self._save_recommendations(user, recs)
        # Dict listesi olarak döndür
        return [
            {
                "title": r.title,
                "recommendations": r.recommendations,
                "category": r.category,
                "priority": r.priority,
                "action_required": r.action_required,
            }
            for r in recs
        ]

    # ---------- iç yardımcılar ----------
    def _parse_recommendation_sections(
        self, text: str
    ) -> List[GeneratedRecommendation]:
        """Basit başlık-bullet şemasını sözlüklere dönüştürür."""
        recs: List[GeneratedRecommendation] = []
        if not text:
            return recs

        # Bölümleri başlık satırlarına göre ayır
        parts = re.split(r"\n\s*\n", text.strip())
        for part in parts:
            lines = [line.strip() for line in part.splitlines() if line.strip()]
            if not lines:
                continue
            title = lines[0].rstrip(":")
            bullets = [
                line[1:].strip() if line.startswith("-") else line for line in lines[1:]
            ]
            if not bullets:
                # tek satırlık öneri de olabilir
                bullets = lines[1:] or [title]

            category = self._categorize_recommendation(title)
            priority = self._calculate_priority(title, bullets)
            action_required = self._requires_action(
                {"title": title, "recommendations": bullets}
            )
            recs.append(
                GeneratedRecommendation(
                    title=title,
                    recommendations=bullets,
                    category=category,
                    priority=priority,
                    action_required=action_required,
                )
            )
        return recs

    def _local_generate_sections(
        self, *, user: Any, prefs: Any, context: Dict[str, Any]
    ) -> str:
        """Yerel kurallar ve basit metriklerle bölümlü öneri metni üretir."""
        risk_tol = (getattr(prefs, "risk_tolerance", "medium") or "medium").lower()
        goals = context.get("investment_goals") or context.get("goals") or []
        if isinstance(goals, str):
            goals = [goals]
        goals = [str(g).lower() for g in goals]
        port_val = float(
            context.get("portfolio_value")
            or context.get("portfolio", {}).get("value")
            or 0
        )
        cash_ratio = float(context.get("cash_ratio") or 0.0)

        portfolio_lines: List[str] = []
        if risk_tol in ("high", "yüksek", "yuksek"):
            portfolio_lines.append("Hisse ağırlığını kademeli artırın (%60-70 bant)")
            portfolio_lines.append("Riskli pozisyonları stop seviyeleriyle yönetin")
        elif risk_tol in ("low", "düşük", "dusuk"):
            portfolio_lines.append(
                "Sabit getirili ve nakit benzerlerine ağırlık verin (%40-50)"
            )
            portfolio_lines.append(
                "Volatil sektörlerde pozisyon boyutlarını sınırlayın"
            )
        else:
            portfolio_lines.append(
                "Dengeli dağılım: Hisse %50-60, Tahvil %20-30, Alternatif %10-20"
            )

        if port_val and cash_ratio < 0.05:
            portfolio_lines.append(
                "Acil durum fonu için nakit oranını %5+ seviyesine çıkarın"
            )

        invest_lines: List[str] = []
        if "retirement" in goals or "emeklilik" in goals:
            invest_lines.append("Uzun vadeli endeks fonlarına kademeli alım (DCA)")
        if "growth" in goals or "büyüme" in goals:
            invest_lines.append("Büyüme odaklı teknolojide seçici pozisyon alın")
        if not invest_lines:
            invest_lines.append(
                "Temettü verimi yüksek ve nakit akışı güçlü şirketleri izleyin"
            )

        risk_lines = [
            "Stop-loss seviyeleri belirleyin ve disiplinle uygulayın",
            "Kur riskine maruz pozisyonlarda hedge seçeneklerini değerlendirin",
        ]

        # KOBİ / İşletme odaklı yönetim önerileri (mali müşavir bakışı)
        fin = context.get("financials") or {}
        revenue = float(
            fin.get("revenue_monthly") or context.get("revenue_monthly") or 0
        )
        expenses = float(
            fin.get("expenses_monthly") or context.get("expenses_monthly") or 0
        )
        cash = float(fin.get("cash_balance") or context.get("cash_balance") or 0)
        ar_total = float(fin.get("receivables") or context.get("receivables") or 0)
        ap_total = float(fin.get("payables") or context.get("payables") or 0)
        gross_margin = float(
            fin.get("gross_margin") or context.get("gross_margin") or 0
        )
        net_margin = float(fin.get("net_margin") or context.get("net_margin") or 0)
        vat_due = fin.get("vat_due_date") or context.get("vat_due_date")
        tax_due = fin.get("tax_due_date") or context.get("tax_due_date")
        ssk_due = fin.get("social_security_due_date") or context.get(
            "social_security_due_date"
        )
        payroll_due = fin.get("payroll_due_date") or context.get("payroll_due_date")

        sme_lines: List[str] = []
        if revenue and expenses:
            monthly_cf = revenue - expenses
            sme_lines.append(f"Aylık nakit akışı: {monthly_cf:,.0f} TL")
            if monthly_cf < 0:
                sme_lines.append(
                    "Giderleri %10-15 azaltma veya fiyat revizyonu ile nakit açığını kapatın"
                )
        if cash and (revenue or expenses):
            burn = max(expenses - revenue, 0)
            if burn > 0:
                runway = cash / burn if burn else 0
                sme_lines.append(f"Runway (ay): {runway:.1f}")
                if runway < 3:
                    sme_lines.append(
                        "Runway <3 ay; tahsilat hızlandırma ve kısa vadeli kredi limitlerini gözden geçirin"
                    )
        if gross_margin:
            sme_lines.append(f"Brüt marj: %{gross_margin:.1f}")
            if gross_margin < 25:
                sme_lines.append(
                    "Düşük brüt marj; tedarikçi pazarlığı ve ürün karmasını optimize edin"
                )
        if net_margin:
            sme_lines.append(f"Net marj: %{net_margin:.1f}")
        if ar_total or ap_total:
            sme_lines.append(
                f"Ticari alacaklar: {ar_total:,.0f} TL, borçlar: {ap_total:,.0f} TL"
            )
            if ar_total > ap_total * 1.5:
                sme_lines.append(
                    "DSO yüksek; vade kısaltma ve erken ödeme iskontosu uygulayın"
                )
        if vat_due or tax_due or ssk_due or payroll_due:
            deadlines = []
            if vat_due:
                deadlines.append(f"KDV: {vat_due}")
            if tax_due:
                deadlines.append(f"Beyannameler/Geçici Vergi: {tax_due}")
            if ssk_due:
                deadlines.append(f"SGK: {ssk_due}")
            if payroll_due:
                deadlines.append(f"Maaş/ Bordro: {payroll_due}")
            sme_lines.append("Yaklaşan yükümlülükler: " + ", ".join(deadlines))
        if not sme_lines:
            sme_lines.append(
                "Aylık gelir-gider, nakit, alacak-borç ve vergi takvimini izleyin; KPI'ları dashboard'a ekleyin"
            )

        sections = [
            "Portföy Optimizasyonu:\n- " + "\n- ".join(portfolio_lines),
            "Yatırım Fırsatları:\n- " + "\n- ".join(invest_lines),
            "Risk Yönetimi:\n- " + "\n- ".join(risk_lines),
            "İşletme Sağlığı:\n- " + "\n- ".join(sme_lines),
        ]
        return "\n\n".join(sections)

    def _categorize_recommendation(self, title: str) -> str:
        t = (title or "").lower()
        if any(k in t for k in ["portföy", "portfoy", "dağılım", "allocation"]):
            return "portfolio"
        if any(
            k in t for k in ["yatırım", "fırsat", "opportunity", "equity", "sector"]
        ):
            return "investment"
        if any(k in t for k in ["risk", "hedge", "koruma"]):
            return "risk"
        if any(k in t for k in ["vergi", "tax"]):
            return "tax"
        if any(k in t for k in ["piyasa", "market", "görünüm", "outlook"]):
            return "market"
        return "other"

    def _calculate_priority(self, title: str, items: List[str]) -> str:
        t = (title or "").lower()
        join = " ".join(items).lower()
        if (
            "acil" in t
            or "acil" in join
            or "yüksek risk" in join
            or "yuksek risk" in join
        ):
            return "urgent"
        if any(
            k in join for k in ["yüksek getiri", "yuksek getiri", "alpha", "anomal"]
        ):
            return "high"
        return "medium"

    def _requires_action(self, rec: Dict[str, Any]) -> bool:
        title = (rec.get("title") or "").lower()
        items = " ".join(rec.get("recommendations") or []).lower()
        verbs = [
            "al",
            "sat",
            "artır",
            "artir",
            "düşür",
            "dusur",
            "yeniden dengele",
            "hedge",
        ]
        if "portföy" in title or "portfoy" in title:
            return True
        return any(v in items for v in verbs)

    async def _save_recommendations(
        self, user: Any, recs: List[GeneratedRecommendation]
    ) -> None:
        """Önerileri AIInsight olarak kaydeder (varsayılan RecommendationEngine modeliyle)."""
        from asgiref.sync import sync_to_async

        if not recs:
            return

        @sync_to_async
        def _save_sync():
            # Varsayılan model (yoksa oluştur)
            model, _ = AIModel.objects.get_or_create(
                name="RecommendationEngine",
                defaults={
                    "model_type": "recommendation",
                    "version": "1.0",
                    "description": "Yerel öneri motoru",
                    "accuracy": 0.0,
                    "parameters": {},
                    "is_active": True,
                },
            )
            with transaction.atomic():
                for r in recs:
                    AIInsight.objects.create(
                        user=user,
                        insight_type="recommendation",
                        title=r.title,
                        content="\n".join(f"- {it}" for it in r.recommendations),
                        priority=r.priority,
                        action_required=r.action_required,
                        action_description="",
                        is_read=False,
                        is_archived=False,
                        model=model,
                        insight_data={
                            "category": r.category,
                            "items": r.recommendations,
                        },
                    )

        await _save_sync()

    def _create_enhanced_recommendation_prompt(
        self,
        *,
        user_preferences: UserPreference | None,
        market_data: Any,
        portfolio_data: Any,
        context: Dict[str, Any],
    ) -> str:
        prefs_block = (
            f"Risk Toleransı: {getattr(user_preferences, 'risk_tolerance', 'bilinmiyor')}\n"
            f"Yatırım Vadesi: {getattr(user_preferences, 'investment_horizon', 'bilinmiyor')}\n"
            f"Dil: {getattr(user_preferences, 'language', 'tr')}\n"
        )
        return (
            "KULLANICI PROFİLİ\n"
            + prefs_block
            + "\nPİYASA DURUMU\n"
            + str(market_data)
            + "\n\nPORTFÖY BİLGİLERİ\n"
            + str(portfolio_data)
            + "\n\nMEVCUT DURUM\n"
            + str(context)
        )
