# -*- coding: utf-8 -*-
import re
from typing import Dict, Any
from django.contrib.auth import get_user_model
from src.apps.accounting.services.reports import (
    get_company_summary,
    generate_gelir_tablosu,
    generate_bilanco,
    generate_nakit_akisi_tablosu,
)
from django.conf import settings
from src.apps.ai_assistant.models import SectorBenchmark
import math

User = get_user_model()


class LocalNLPService:
    """
    Yerel, bağımsız doğal dil yorumlayıcısı.
    Basit niyet/varlık çıkarımı ve mevcut servislerle entegrasyon yapar.
    """

    INTENT_PATTERNS = [
        ("cash_flow", r"nakit(\s|-)ak(ı|i)\s*\w*|cash flow"),
        ("income_statement", r"gelir\s*tablosu|income\s*statement"),
        ("balance_sheet", r"bilanç(o|ö)|balance\s*sheet"),
        ("summary", r"özet|durum|summary"),
        ("invoice_help", r"fatura|e-?fatura|e-?arşiv"),
        ("rules_help", r"kural|otomatik fiş|auto\s*book"),
        ("explain", r"analiz|yorumla|aç(ı|i)kla|explain|öneri"),
    ]

    def parse_intent(self, text: str) -> str:
        t = (text or '').lower()
        for intent, pattern in self.INTENT_PATTERNS:
            if re.search(pattern, t):
                return intent
        return "summary"

    def _parse_period(self, text: str):
        """YYYY-MM veya basit Türkçe kalıplardan (bu ay/geçen ay) yıl-ay döndür."""
        import datetime
        today = datetime.date.today()
        t = (text or '').lower()
        # YYYY-MM
        m = re.search(r"(20\d{2})[-/.](0?[1-9]|1[0-2])", t)
        if m:
            return int(m.group(1)), int(m.group(2))
        # geçen ay
        if 'geçen ay' in t or 'gecen ay' in t:
            first = today.replace(day=1)
            prev_last = first - datetime.timedelta(days=1)
            return prev_last.year, prev_last.month
        # bu ay
        if 'bu ay' in t:
            return today.year, today.month
        return today.year, today.month

    def respond(self, user: User, query: str) -> Dict[str, Any]:
        intent = self.parse_intent(query)
        company = getattr(user, 'company', None)
        year, month = self._parse_period(query)

        if intent == 'cash_flow':
            df = generate_nakit_akisi_tablosu(company, year, month)
            data = df.to_dict(orient='records')
            guidance = []
            try:
                row = data[0]
                if float(row.get('Net Nakit Akışı', 0)) < 0:
                    guidance.append('Net nakit akışı negatif; tahsilatları hızlandırın ve kısa vadeli çıkışları erteleyin.')
            except Exception:
                pass
            actions = self._actions_for_reports()
            return {"type": "cash_flow", "period": f"{year}-{month:02d}", "data": data, "guidance": guidance, "actions": actions}

        if intent == 'income_statement':
            df = generate_gelir_tablosu(company, year, month)
            analysis = self._analyze_income_statement(df)
            actions = self._actions_for_reports()
            return {"type": "income_statement", "period": f"{year}-{month:02d}", "data": df.to_dict(orient='records'), "analysis": analysis, "actions": actions}

        if intent == 'balance_sheet':
            df = generate_bilanco(company, year, month)
            analysis = self._analyze_balance_sheet(df)
            actions = self._actions_for_reports()
            return {"type": "balance_sheet", "period": f"{year}-{month:02d}", "data": df.to_dict(orient='records'), "analysis": analysis, "actions": actions}

        if intent == 'invoice_help':
            return {
                "type": "help",
                "message": "Belgenizi yükleyerek otomatik fiş önizleme için 'Muhasebe > Otomatik Fiş Önizleme' ekranını kullanın.",
                "endpoints": {
                    "ocr_preview": "accounting/api/ocr/preview-voucher/",
                    "ocr_confirm": "accounting/api/ocr/confirm-voucher/",
                },
            }

        if intent == 'rules_help':
            return {
                "type": "help",
                "message": "Kural önerme/uygulama için 'Muhasebe > Kural Yöneticisi' ekranını veya API uçlarını kullanın.",
                "endpoints": {
                    "suggest": "accounting/api/ai/rules/suggest/",
                    "apply": "accounting/api/ai/rules/apply/",
                },
            }

        # summary
        summary = get_company_summary(company)
        guidance = self._generate_guidance_from_summary(summary)
        actions = self._actions_for_reports()
        return {"type": "summary", **summary, "guidance": guidance, "actions": actions}

    def _analyze_income_statement(self, df):
        # df: rows with keys like Gelir Türü / Tutar; fallback simple calculations
        try:
            records = df.to_dict(orient='records')
        except Exception:
            return {}
        totals = {r.get('Gelir Türü','row'): float(r.get('Tutar',0)) for r in records}
        sales = totals.get('Satış Geliri', 0.0)
        opex = abs(totals.get('Faaliyet Gideri', 0.0))
        net = totals.get('Net Kar', sales - opex)
        margin = (net / sales * 100) if sales else 0
        advice = []
        if margin < 10:
            advice.append('Net kar marjınız düşük; maliyetleri gözden geçirin ve fiyatlandırmayı optimize edin.')
        if opex > sales * 0.4:
            advice.append('Faaliyet giderleri yüksek görünüyor; gider kalemlerini yeniden yapılandırın.')
        # Sektör bazlı kıyas
        benchmarks = self._sector_benchmarks()
        target_margin = benchmarks.get('margin_min')
        target_opex = benchmarks.get('opex_ratio_max')
        cmp_notes = []
        if target_margin is not None and margin < target_margin:
            cmp_notes.append(f"Sektör hedef marj {target_margin}% üzeri. Marjınızı yükseltmek için fiyat/portföy ve maliyetleri optimize edin.")
        if target_opex is not None and sales and (opex/sales) > target_opex:
            cmp_notes.append(f"Sektör hedef faaliyet gider oranı %{int(target_opex*100)} altı. Gider oranınız yüksek görünüyor.")
        advice.extend(cmp_notes)
        return {"sales": sales, "opex": opex, "net": net, "margin_pct": round(margin,2), "benchmarks": benchmarks, "advice": advice}

    def _analyze_balance_sheet(self, df):
        try:
            records = df.to_dict(orient='records')
        except Exception:
            return {}
        assets = sum(float(r.get('Tutar',0)) for r in records if r.get('Aktif'))
        liabilities = sum(float(r.get('Tutar',0)) for r in records if r.get('Pasif'))
        equity = max(assets - liabilities, 0)
        debt_to_equity = (liabilities / equity) if equity else math.inf
        current_ratio = (assets / liabilities) if liabilities else math.inf
        advice = []
        if debt_to_equity > 1:
            advice.append('Borç/Özsermaye oranı yüksek; borçluluğu azaltmayı veya özkaynak artırmayı değerlendirin.')
        if current_ratio != math.inf and current_ratio < 1.5:
            advice.append('Likidite zayıf (Cari oran düşük); kısa vadeli yükümlülükleri azaltın veya dönen varlıkları artırın.')
        # Sektör bazlı kıyas
        benchmarks = self._sector_benchmarks()
        target_cr = benchmarks.get('current_ratio_min')
        target_dte = benchmarks.get('dte_max')
        if target_cr is not None and current_ratio != math.inf and current_ratio < target_cr:
            advice.append(f"Sektör hedef cari oran {target_cr}+; işletme sermayesini güçlendirin.")
        if target_dte is not None and debt_to_equity != math.inf and debt_to_equity > target_dte:
            advice.append(f"Sektör hedef Borç/Özkaynak {target_dte} altı; borç oranınızı düşürmeyi planlayın.")
        return {"assets": assets, "liabilities": liabilities, "equity": equity, "debt_to_equity": None if debt_to_equity==math.inf else round(debt_to_equity,2), "current_ratio": None if current_ratio==math.inf else round(current_ratio,2), "benchmarks": benchmarks, "advice": advice}

    def _generate_guidance_from_summary(self, summary):
        total_income = float(summary.get('total_income',0))
        total_expense = float(summary.get('total_expense',0))
        net = float(summary.get('net_profit',0))
        advice = []
        if net < 0:
            advice.append('Net zarar mevcut; kısa vadede nakit akışını güçlendirecek önlemler alın.')
        elif net < total_income * 0.05:
            advice.append('Kar marjı düşük; yüksek maliyetli giderleri azaltın ve tahsilat süreçlerini hızlandırın.')
        else:
            advice.append('Kar marjı sağlıklı; büyüme yatırımlarını planlayabilirsiniz.')
        return {"advice": advice}

    def _actions_for_reports(self):
        return [
            {"label": "Gelir Tablosu", "url": "accounting/finansal/gelir-tablosu/"},
            {"label": "Bilanço", "url": "accounting/finansal/bilanco/"},
            {"label": "Nakit Akışı", "url": "accounting/finansal/nakit-akisi/"},
            {"label": "Otomatik Fiş", "url": "accounting/auto-book/"},
        ]

    def _sector_benchmarks(self):
        """Şirket sektörüne göre hedef oranlar. Admin’den yönetilen kayıtlar kullanılır; yoksa genel varsayılan."""
        sector = getattr(getattr(self, 'company', None), 'sector', None)
        key = (sector or 'genel').strip().lower()
        try:
            sb = SectorBenchmark.objects.get(sector_key=key, is_active=True)
            return {
                'margin_min': sb.margin_min,
                'current_ratio_min': sb.current_ratio_min,
                'dte_max': sb.dte_max,
                'opex_ratio_max': sb.opex_ratio_max,
            }
        except SectorBenchmark.DoesNotExist:
            # Genel varsayılan
            return { 'margin_min': 10.0, 'current_ratio_min': 1.5, 'dte_max': 1.0, 'opex_ratio_max': 0.40 }


