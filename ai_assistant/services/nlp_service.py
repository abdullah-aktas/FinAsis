# -*- coding: utf-8 -*-
import re
from typing import Dict, Any
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth import get_user_model
from accounting.services.reports import (
    get_company_summary,
    generate_gelir_tablosu,
    generate_bilanco,
    generate_nakit_akisi_tablosu,
)
from ai_assistant.models import SectorBenchmark
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
        t = (text or "").lower()
        for intent, pattern in self.INTENT_PATTERNS:
            if re.search(pattern, t):
                return intent
        return "summary"

    def _parse_period(self, text: str):
        """YYYY-MM veya basit Türkçe kalıplardan (bu ay/geçen ay) yıl-ay döndür."""
        import datetime

        today = datetime.date.today()
        t = (text or "").lower()
        # YYYY-MM
        m = re.search(r"(20\d{2})[-/.](0?[1-9]|1[0-2])", t)
        if m:
            return int(m.group(1)), int(m.group(2))
        # geçen ay
        if "geçen ay" in t or "gecen ay" in t:
            first = today.replace(day=1)
            prev_last = first - datetime.timedelta(days=1)
            return prev_last.year, prev_last.month
        # bu ay
        if "bu ay" in t:
            return today.year, today.month
        return today.year, today.month

    def respond(self, user: AbstractBaseUser | Any, query: str) -> Dict[str, Any]:
        intent = self.parse_intent(query)
        company = getattr(user, "company", None)
        # ensure sub-methods can access company context (e.g., sector benchmarks)
        # expose to helper methods (e.g., _sector_benchmarks)
        try:
            self.company = company
        except Exception:
            # non-fatal
            pass
        year, month = self._parse_period(query)

        if intent == "cash_flow":
            df = generate_nakit_akisi_tablosu(company, year, month)
            # to_dict may raise on unexpected df; be defensive
            try:
                data = df.to_dict(orient="records")
            except Exception:
                try:
                    # minimal fallback for objects exposing records
                    data = list(getattr(df, "records", []))
                except Exception:
                    data = []

            guidance = []

            # try to locate a "net cash flow" like value from the first row or any row
            def _find_net_cash_value(rows):
                candidates = {
                    "net nakit akis",
                    "net nakit akisi",
                    "net nakit akışı",
                    "net cash flow",
                    "net cash",
                    "net nakit",
                    "net cashflow",
                }
                for r in rows or []:
                    # build a normalized key map for the row
                    norm_map = {self._normalize_key(k): k for k in (r or {}).keys()}
                    # direct candidate lookup
                    for cand in candidates:
                        if cand in norm_map:
                            val = r.get(norm_map[cand])
                            num = self._parse_number(val)
                            if num is not None:
                                return num
                    # fuzzy: pick first key that contains both tokens net and (nakit|cash) and (ak|flow)
                    for nk, orig in norm_map.items():
                        if (
                            "net" in nk
                            and ("nakit" in nk or "cash" in nk)
                            and ("ak" in nk or "flow" in nk)
                        ):
                            num = self._parse_number(r.get(orig))
                            if num is not None:
                                return num
                return None

            try:
                net_cash = _find_net_cash_value(data)
                if net_cash is not None and net_cash < 0:
                    guidance.append(
                        "Net nakit akışı negatif; tahsilatları hızlandırın ve kısa vadeli çıkışları erteleyin."
                    )
            except Exception:
                # do not block response on guidance errors
                pass
            actions = self._actions_for_reports()
            return {
                "type": "cash_flow",
                "period": f"{year}-{month:02d}",
                "data": data,
                "guidance": guidance,
                "actions": actions,
            }

        if intent == "income_statement":
            df = generate_gelir_tablosu(company, year, month)
            analysis = self._analyze_income_statement(df)
            actions = self._actions_for_reports()
            return {
                "type": "income_statement",
                "period": f"{year}-{month:02d}",
                "data": df.to_dict(orient="records"),
                "analysis": analysis,
                "actions": actions,
            }

        if intent == "balance_sheet":
            df = generate_bilanco(company, year, month)
            analysis = self._analyze_balance_sheet(df)
            actions = self._actions_for_reports()
            return {
                "type": "balance_sheet",
                "period": f"{year}-{month:02d}",
                "data": df.to_dict(orient="records"),
                "analysis": analysis,
                "actions": actions,
            }

        if intent == "invoice_help":
            return {
                "type": "help",
                "message": "Belgenizi yükleyerek otomatik fiş önizleme için 'Muhasebe > Otomatik Fiş Önizleme' ekranını kullanın.",
                "endpoints": {
                    "ocr_preview": "accounting/api/ocr/preview-voucher/",
                    "ocr_confirm": "accounting/api/ocr/confirm-voucher/",
                },
            }

        if intent == "rules_help":
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

    # ---- helpers ----
    def _normalize_key(self, key: Any) -> str:
        """Lowercase, strip accents/diacritics, keep alnum and spaces, collapse spaces.
        Example: 'Net Nakit Akışı (TL)' -> 'net nakit akis tl' -> we further drop currency tokens when matching.
        """
        try:
            s = str(key).lower()
        except Exception:
            return ""
        # replace Turkish diacritics
        repl = {
            "ı": "i",
            "ş": "s",
            "ğ": "g",
            "ü": "u",
            "ö": "o",
            "ç": "c",
            "İ": "i",
            "Ş": "s",
            "Ğ": "g",
            "Ü": "u",
            "Ö": "o",
            "Ç": "c",
            "â": "a",
            "ê": "e",
            "î": "i",
            "ô": "o",
            "û": "u",
        }
        s = "".join(repl.get(ch, ch) for ch in s)
        # remove non-alnum except spaces
        import re as _re

        s = _re.sub(r"[^a-z0-9\s]", " ", s)
        # collapse spaces
        s = " ".join(s.split())
        return s

    def _parse_number(self, val: Any) -> float | None:
        """Parse numeric values robustly.
        - Accept int/float directly
        - Strings with thousand separators '.' or ' ', decimal ',' or '.'
        - Strip currency symbols like TL, ₺
        """
        try:
            if val is None:
                return None
            if isinstance(val, (int, float)):
                return float(val)
            s = str(val).strip()
            if not s:
                return None
            # remove currency symbols and letters
            import re as _re

            s_clean = _re.sub(
                r"[\s\u20BA₺TLtl]", "", s
            )  # remove spaces and TL symbols/letters
            # normalize separators
            # If both ',' and '.' exist, assume European style: '.' thousands, ',' decimal
            if "," in s_clean and "." in s_clean:
                s_norm = s_clean.replace(".", "").replace(",", ".")
            else:
                # if only comma present, treat as decimal
                if "," in s_clean and "." not in s_clean:
                    s_norm = s_clean.replace(",", ".")
                else:
                    s_norm = s_clean
            return float(s_norm)
        except Exception:
            return None

    def _analyze_income_statement(self, df):
        # df: rows with keys like Gelir Türü / Tutar; fallback simple calculations
        try:
            records = df.to_dict(orient="records")
        except Exception:
            return {}
        totals = {r.get("Gelir Türü", "row"): float(r.get("Tutar", 0)) for r in records}
        sales = totals.get("Satış Geliri", 0.0)
        opex = abs(totals.get("Faaliyet Gideri", 0.0))
        net = totals.get("Net Kar", sales - opex)
        margin = (net / sales * 100) if sales else 0
        advice = []
        if margin < 10:
            advice.append(
                "Net kar marjınız düşük; maliyetleri gözden geçirin ve fiyatlandırmayı optimize edin."
            )
        if opex > sales * 0.4:
            advice.append(
                "Faaliyet giderleri yüksek görünüyor; gider kalemlerini yeniden yapılandırın."
            )
        # Sektör bazlı kıyas
        benchmarks = self._sector_benchmarks()
        target_margin = benchmarks.get("margin_min")
        target_opex = benchmarks.get("opex_ratio_max")
        cmp_notes = []
        if target_margin is not None and margin < target_margin:
            cmp_notes.append(
                f"Sektör hedef marj {target_margin}% üzeri. Marjınızı yükseltmek için fiyat/portföy ve maliyetleri optimize edin."
            )
        if target_opex is not None and sales and (opex / sales) > target_opex:
            cmp_notes.append(
                f"Sektör hedef faaliyet gider oranı %{int(target_opex*100)} altı. Gider oranınız yüksek görünüyor."
            )
        advice.extend(cmp_notes)
        return {
            "sales": sales,
            "opex": opex,
            "net": net,
            "margin_pct": round(margin, 2),
            "benchmarks": benchmarks,
            "advice": advice,
        }

    def _analyze_balance_sheet(self, df):
        try:
            records = df.to_dict(orient="records")
        except Exception:
            return {}
        assets = sum(float(r.get("Tutar", 0)) for r in records if r.get("Aktif"))
        liabilities = sum(float(r.get("Tutar", 0)) for r in records if r.get("Pasif"))
        equity = max(assets - liabilities, 0)
        debt_to_equity = (liabilities / equity) if equity else math.inf
        current_ratio = (assets / liabilities) if liabilities else math.inf
        advice = []
        if debt_to_equity > 1:
            advice.append(
                "Borç/Özsermaye oranı yüksek; borçluluğu azaltmayı veya özkaynak artırmayı değerlendirin."
            )
        if current_ratio != math.inf and current_ratio < 1.5:
            advice.append(
                "Likidite zayıf (Cari oran düşük); kısa vadeli yükümlülükleri azaltın veya dönen varlıkları artırın."
            )
        # Sektör bazlı kıyas
        benchmarks = self._sector_benchmarks()
        target_cr = benchmarks.get("current_ratio_min")
        target_dte = benchmarks.get("dte_max")
        if (
            target_cr is not None
            and current_ratio != math.inf
            and current_ratio < target_cr
        ):
            advice.append(
                f"Sektör hedef cari oran {target_cr}+; işletme sermayesini güçlendirin."
            )
        if (
            target_dte is not None
            and debt_to_equity != math.inf
            and debt_to_equity > target_dte
        ):
            advice.append(
                f"Sektör hedef Borç/Özkaynak {target_dte} altı; borç oranınızı düşürmeyi planlayın."
            )
        return {
            "assets": assets,
            "liabilities": liabilities,
            "equity": equity,
            "debt_to_equity": None
            if debt_to_equity == math.inf
            else round(debt_to_equity, 2),
            "current_ratio": None
            if current_ratio == math.inf
            else round(current_ratio, 2),
            "benchmarks": benchmarks,
            "advice": advice,
        }

    def _generate_guidance_from_summary(self, summary):
        total_income = float(summary.get("total_income", 0))
        float(summary.get("total_expense", 0))
        net = float(summary.get("net_profit", 0))
        advice = []
        if net < 0:
            advice.append(
                "Net zarar mevcut; kısa vadede nakit akışını güçlendirecek önlemler alın."
            )
        elif net < total_income * 0.05:
            advice.append(
                "Kar marjı düşük; yüksek maliyetli giderleri azaltın ve tahsilat süreçlerini hızlandırın."
            )
        else:
            advice.append(
                "Kar marjı sağlıklı; büyüme yatırımlarını planlayabilirsiniz."
            )
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
        sector = getattr(getattr(self, "company", None), "sector", None)
        key = (sector or "genel").strip().lower()
        try:
            sb = SectorBenchmark.objects.get(sector_key=key, is_active=True)
            return {
                "margin_min": sb.margin_min,
                "current_ratio_min": sb.current_ratio_min,
                "dte_max": sb.dte_max,
                "opex_ratio_max": sb.opex_ratio_max,
            }
        except SectorBenchmark.DoesNotExist:
            # Genel varsayılan
            return {
                "margin_min": 10.0,
                "current_ratio_min": 1.5,
                "dte_max": 1.0,
                "opex_ratio_max": 0.40,
            }
