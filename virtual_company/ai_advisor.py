"""
AI Accounting Advisor for Virtual Companies
Sanal Şirketler için AI Muhasebe Danışmanı
"""
from typing import Dict, List, Any
from decimal import Decimal


class VirtualCompanyAIAdvisor:
    """
    Sanal şirketler için AI destekli muhasebe danışmanı
    - Finansal analiz
    - Otomatik öneriler
    - Risk tespiti
    - Eğitim rehberliği
    """

    @classmethod
    def analyze_company_health(cls, company) -> Dict[str, Any]:
        """
        Şirketin genel sağlık durumunu analiz et

        Returns:
            Skor, durum ve öneriler
        """
        score = 50  # Base score
        issues = []
        recommendations = []

        # 1. Bakiye kontrolü
        if company.balance < 0:
            score -= 20
            issues.append(
                {
                    "type": "negative_balance",
                    "severity": "high",
                    "message": "Şirket bakiyesi negatif! Acil nakit girişi gerekli.",
                }
            )
            recommendations.append(
                {
                    "title": "Nakit Akışını İyileştir",
                    "description": "Alacakları hızlandır, ödemeleri planla",
                    "priority": "high",
                    "icon": "💰",
                }
            )
        elif company.balance > 0:
            score += 15

        # 2. Stok kontrolü
        total_stock_value = company.total_stock_value()

        if total_stock_value == 0:
            score -= 10
            issues.append(
                {
                    "type": "no_inventory",
                    "severity": "medium",
                    "message": "Stoğunuz yok! Ürün ekleyin.",
                }
            )
            recommendations.append(
                {
                    "title": "Stok Oluştur",
                    "description": "Satış yapabilmek için ürün stoğu oluşturun",
                    "priority": "medium",
                    "icon": "📦",
                }
            )
        elif total_stock_value > company.balance * Decimal("2"):
            score -= 5
            issues.append(
                {
                    "type": "excess_inventory",
                    "severity": "low",
                    "message": "Stok değeri çok yüksek, nakit sıkışıklığı riski var.",
                }
            )
            recommendations.append(
                {
                    "title": "Stok Optimizasyonu",
                    "description": "Fazla stoğu satın, nakit döngüsünü hızlandır",
                    "priority": "low",
                    "icon": "🔄",
                }
            )
        else:
            score += 10

        # 3. Ürün çeşitliliği
        product_count = company.products.count()

        if product_count == 0:
            score -= 15
        elif product_count >= 5:
            score += 15
        elif product_count >= 3:
            score += 10

        # 4. İşlem geçmişi
        transaction_count = (
            company.transactions.count() if hasattr(company, "transactions") else 0
        )

        if transaction_count == 0:
            issues.append(
                {
                    "type": "no_transactions",
                    "severity": "low",
                    "message": "Henüz hiç işlem yapmadınız.",
                }
            )
            recommendations.append(
                {
                    "title": "İlk İşleminizi Yapın",
                    "description": "Bir gelir veya gider kaydı ekleyerek başlayın",
                    "priority": "medium",
                    "icon": "📝",
                }
            )
        elif transaction_count >= 20:
            score += 10

        # Skor sınırla
        score = max(0, min(100, score))

        # Durum belirleme
        if score >= 80:
            status = "Mükemmel"
            status_color = "#10b981"
        elif score >= 60:
            status = "İyi"
            status_color = "#3b82f6"
        elif score >= 40:
            status = "Orta"
            status_color = "#f59e0b"
        else:
            status = "Zayıf"
            status_color = "#ef4444"

        return {
            "score": score,
            "status": status,
            "status_color": status_color,
            "issues": issues,
            "recommendations": recommendations,
            "metrics": {
                "balance": float(company.balance),
                "stock_value": float(total_stock_value),
                "product_count": product_count,
                "transaction_count": transaction_count,
            },
        }

    @classmethod
    def suggest_accounting_entry(
        cls, company, transaction_type: str, amount: Decimal, description: str
    ) -> Dict[str, Any]:
        """
        AI destekli muhasebe kaydı önerisi

        Args:
            company: VirtualCompany instance
            transaction_type: 'INCOME' veya 'EXPENSE'
            amount: İşlem tutarı
            description: İşlem açıklaması

        Returns:
            Önerilen muhasebe kaydı (borç/alacak hesaplar)
        """

        if transaction_type == "INCOME":
            # Gelir işlemi
            if "satış" in description.lower() or "gelir" in description.lower():
                suggestion = {
                    "debit_account": "100 - Kasa",
                    "credit_account": "600 - Satış Gelirleri",
                    "description": f"Satış geliri: {description}",
                    "confidence": 0.92,
                }
            elif "hizmet" in description.lower():
                suggestion = {
                    "debit_account": "100 - Kasa",
                    "credit_account": "602 - Hizmet Gelirleri",
                    "description": f"Hizmet geliri: {description}",
                    "confidence": 0.88,
                }
            else:
                suggestion = {
                    "debit_account": "100 - Kasa",
                    "credit_account": "649 - Diğer Gelirler",
                    "description": description,
                    "confidence": 0.75,
                }

        else:  # EXPENSE
            # Gider işlemi
            if "maaş" in description.lower() or "bordro" in description.lower():
                suggestion = {
                    "debit_account": "770 - Personel Giderleri",
                    "credit_account": "100 - Kasa",
                    "description": f"Personel gideri: {description}",
                    "confidence": 0.95,
                }
            elif "kira" in description.lower():
                suggestion = {
                    "debit_account": "760 - Pazarlama Satış Dağıtım Giderleri",
                    "credit_account": "100 - Kasa",
                    "description": f"Kira gideri: {description}",
                    "confidence": 0.90,
                }
            elif "malzeme" in description.lower() or "hammadde" in description.lower():
                suggestion = {
                    "debit_account": "710 - Direkt İlk Madde ve Malzeme Giderleri",
                    "credit_account": "100 - Kasa",
                    "description": f"Malzeme gideri: {description}",
                    "confidence": 0.93,
                }
            else:
                suggestion = {
                    "debit_account": "770 - Genel Yönetim Giderleri",
                    "credit_account": "100 - Kasa",
                    "description": description,
                    "confidence": 0.70,
                }

        suggestion["amount"] = float(amount)
        suggestion["effect_on_balance"] = (
            "POSITIVE" if transaction_type == "INCOME" else "NEGATIVE"
        )

        # Alternatif öneriler
        suggestion["alternatives"] = cls._get_alternative_entries(
            transaction_type, description
        )

        return suggestion

    @classmethod
    def _get_alternative_entries(
        cls, transaction_type: str, description: str
    ) -> List[Dict]:
        """Alternatif muhasebe kayıtları öner"""
        alternatives = []

        if transaction_type == "INCOME":
            alternatives = [
                {
                    "debit": "100 - Kasa",
                    "credit": "600 - Satış Gelirleri",
                    "note": "Nakit satış",
                },
                {
                    "debit": "120 - Alıcılar",
                    "credit": "600 - Satış Gelirleri",
                    "note": "Vadeli satış",
                },
                {
                    "debit": "102 - Bankalar",
                    "credit": "600 - Satış Gelirleri",
                    "note": "Banka transferi",
                },
            ]
        else:
            alternatives = [
                {
                    "debit": "770 - Genel Gider",
                    "credit": "100 - Kasa",
                    "note": "Nakit ödeme",
                },
                {
                    "debit": "770 - Genel Gider",
                    "credit": "320 - Satıcılar",
                    "note": "Vadeli ödeme",
                },
                {
                    "debit": "770 - Genel Gider",
                    "credit": "102 - Bankalar",
                    "note": "Banka ödemesi",
                },
            ]

        return alternatives[:2]  # İlk 2 alternatif

    @classmethod
    def detect_financial_risks(cls, company) -> List[Dict[str, Any]]:
        """
        Finansal riskleri tespit et

        Returns:
            Risk listesi
        """
        risks = []

        # Negatif bakiye riski
        if company.balance < 0:
            risks.append(
                {
                    "type": "negative_balance",
                    "severity": "critical",
                    "title": "Negatif Bakiye",
                    "description": f"Şirket bakiyesi {company.balance} ₺. Acil önlem alın!",
                    "impact": "Ödeme yapamama riski",
                    "recommendation": "Nakit girişi sağlayın veya masrafları azaltın",
                }
            )

        # Düşük bakiye riski
        elif company.balance < 5000:
            risks.append(
                {
                    "type": "low_balance",
                    "severity": "medium",
                    "title": "Düşük Bakiye",
                    "description": f"Bakiye {company.balance} ₺. Minimum 5,000 ₺ olması önerilir.",
                    "impact": "Nakit sıkışıklığı riski",
                    "recommendation": "Nakit akışı planı yapın",
                }
            )

        # Stok riski
        total_stock = company.total_stock_value()

        if total_stock == 0:
            risks.append(
                {
                    "type": "no_stock",
                    "severity": "high",
                    "title": "Stok Yok",
                    "description": "Satış yapabilmek için stok gerekli.",
                    "impact": "Satış yapamama",
                    "recommendation": "Ürün satın alın veya üretin",
                }
            )

        # Fazla stok riski
        if total_stock > company.balance * Decimal("3"):
            risks.append(
                {
                    "type": "excess_stock",
                    "severity": "low",
                    "title": "Aşırı Stok",
                    "description": "Stok değeri bakiyenin 3 katından fazla.",
                    "impact": "Nakit sıkışıklığı, eskime riski",
                    "recommendation": "Stoğu azaltın, satışları artırın",
                }
            )

        return risks

    @classmethod
    def generate_learning_path(cls, student_profile) -> List[Dict[str, Any]]:
        """
        Öğrenci için kişiselleştirilmiş öğrenme yolu öner

        Returns:
            Önerilen modüller sırası
        """
        completed_modules = (
            student_profile.completed_modules.all()
            if hasattr(student_profile, "completed_modules")
            else []
        )
        completed_count = len(completed_modules)

        # Tüm modüller (öncelik sırasına göre)
        all_modules = [
            {
                "id": 1,
                "title": "Temel Muhasebe Kavramları",
                "description": "Borç-Alacak, Aktif-Pasif kavramları",
                "difficulty": "beginner",
                "duration_minutes": 30,
                "xp": 50,
                "icon": "📚",
            },
            {
                "id": 2,
                "title": "Fatura Oluşturma",
                "description": "Satış faturası ve muhasebe kaydı",
                "difficulty": "beginner",
                "duration_minutes": 20,
                "xp": 30,
                "icon": "🧾",
            },
            {
                "id": 3,
                "title": "Gider Yönetimi",
                "description": "Gider kaydı ve kategorizasyon",
                "difficulty": "beginner",
                "duration_minutes": 25,
                "xp": 40,
                "icon": "💸",
            },
            {
                "id": 4,
                "title": "Stok Takibi",
                "description": "Stok girişi, çıkışı ve değerleme",
                "difficulty": "intermediate",
                "duration_minutes": 35,
                "xp": 60,
                "icon": "📦",
            },
            {
                "id": 5,
                "title": "Gelir Tablosu Oluşturma",
                "description": "Dönem sonu gelir-gider raporu",
                "difficulty": "intermediate",
                "duration_minutes": 40,
                "xp": 70,
                "icon": "📊",
            },
            {
                "id": 6,
                "title": "Bilanço Hazırlama",
                "description": "Aktif-Pasif dengesi",
                "difficulty": "advanced",
                "duration_minutes": 50,
                "xp": 100,
                "icon": "⚖️",
            },
        ]

        # Tamamlananları işaretle
        for module in all_modules:
            module["completed"] = module["id"] in [m.id for m in completed_modules]
            module["locked"] = False

            # İlerleme gereksinimleri
            if module["difficulty"] == "intermediate" and completed_count < 2:
                module["locked"] = True
            elif module["difficulty"] == "advanced" and completed_count < 4:
                module["locked"] = True

        return all_modules

    @classmethod
    def suggest_next_action(cls, company) -> Dict[str, Any]:
        """
        Şirket durumuna göre bir sonraki aksiyon öner

        Returns:
            Önerilen aksiyon
        """
        product_count = company.products.count()
        transaction_count = (
            company.transactions.count() if hasattr(company, "transactions") else 0
        )

        # Hiç ürün yoksa
        if product_count == 0:
            return {
                "action": "add_product",
                "title": "İlk Ürününüzü Ekleyin",
                "description": "Satış yapabilmek için ürün kataloğunuzu oluşturun",
                "button_text": "Ürün Ekle",
                "button_url": "/virtual-company/products/create/",
                "icon": "📦",
                "priority": "high",
            }

        # Hiç işlem yoksa
        if transaction_count == 0:
            return {
                "action": "add_transaction",
                "title": "İlk Satışınızı Kaydedin",
                "description": "Bir gelir veya gider işlemi ekleyerek muhasebe defterinizi başlatın",
                "button_text": "İşlem Ekle",
                "button_url": "#",
                "icon": "💰",
                "priority": "high",
            }

        # Düşük bakiye
        if company.balance < 1000:
            return {
                "action": "increase_revenue",
                "title": "Gelir Artırma Fırsatı",
                "description": "Bakiyeniz düşük. Satış yaparak nakit girişi sağlayın",
                "button_text": "Satış Yap",
                "button_url": "#",
                "icon": "📈",
                "priority": "medium",
            }

        # Rapor oluşturma
        return {
            "action": "generate_report",
            "title": "Finansal Rapor Oluşturun",
            "description": "Şirketinizin performansını analiz edin",
            "button_text": "Rapor Oluştur",
            "button_url": "#",
            "icon": "📊",
            "priority": "low",
        }

    @classmethod
    def calculate_profitability_score(cls, company) -> Dict[str, Any]:
        """
        Karlılık skorunu hesapla

        Returns:
            Karlılık analizi
        """
        # Toplam gelir ve gider
        total_income = 0
        total_expense = 0

        if hasattr(company, "transactions"):
            for t in company.transactions.all():
                if t.transaction_type == "INCOME":
                    total_income += float(t.amount)
                else:
                    total_expense += float(t.amount)

        profit = total_income - total_expense

        if total_income > 0:
            profit_margin = (profit / total_income) * 100
        else:
            profit_margin = 0

        # Skor
        if profit_margin >= 20:
            score = 100
            grade = "A"
        elif profit_margin >= 15:
            score = 85
            grade = "B"
        elif profit_margin >= 10:
            score = 70
            grade = "C"
        elif profit_margin >= 5:
            score = 50
            grade = "D"
        else:
            score = 30
            grade = "F"

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "profit": profit,
            "profit_margin": profit_margin,
            "score": score,
            "grade": grade,
            "status": "Karlı" if profit > 0 else "Zararlı",
        }
