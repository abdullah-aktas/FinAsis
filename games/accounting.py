from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import uuid
from .inventory import InventoryItem, InventoryManager
from .tax import TaxRecord, TaxManager
from .learning import LearningManager, LearningModule, Achievement, Lesson, Exercise
from .financials import FinancialRatios, FinancialReportManager


class AccountType(Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"
    INVENTORY = "inventory"  # Yeni hesap tipi


class TransactionType(Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    PAYMENT = "payment"
    RECEIPT = "receipt"
    ADJUSTMENT = "adjustment"
    TAX = "tax"  # Yeni işlem tipi
    INVENTORY = "inventory"  # Yeni işlem tipi


@dataclass
class Account:
    id: str
    name: str
    type: AccountType
    balance: float
    description: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Transaction:
    id: str
    date: datetime
    type: TransactionType
    description: str
    debit_account: str
    credit_account: str
    amount: float
    reference: str
    status: str


@dataclass
class TaxRecord:
    id: str
    type: str
    amount: float
    period: str
    due_date: datetime
    status: str
    payment_date: Optional[datetime]


class AccountingSystem:
    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.transactions: List[Transaction] = []
        self.learning_manager = LearningManager()  # Yeni LearningManager kullanımı
        self.current_level = 1
        self.experience = 0
        self.inventory_manager = InventoryManager()
        self.tax_manager = TaxManager()
        self.financial_ratios = {}

    def initialize_accounting_system(self):
        """Muhasebe sistemini başlatır ve temel hesapları oluşturur"""
        self.create_basic_accounts()
        self.load_learning_modules()
        self.initialize_achievements()
        self.initialize_inventory()  # Yeni envanter başlatma
        self.initialize_tax_system()  # Yeni vergi sistemi başlatma

    def create_basic_accounts(self):
        """Temel muhasebe hesaplarını oluşturur"""
        basic_accounts = [
            Account(
                "1001",
                "Kasa",
                AccountType.ASSET,
                0.0,
                "Nakit para",
                datetime.now(),
                datetime.now(),
            ),
            Account(
                "1201",
                "Alıcılar",
                AccountType.ASSET,
                0.0,
                "Müşteri alacakları",
                datetime.now(),
                datetime.now(),
            ),
            Account(
                "3201",
                "Satıcılar",
                AccountType.LIABILITY,
                0.0,
                "Tedarikçi borçları",
                datetime.now(),
                datetime.now(),
            ),
            Account(
                "5001",
                "Satış Gelirleri",
                AccountType.REVENUE,
                0.0,
                "Ürün satış gelirleri",
                datetime.now(),
                datetime.now(),
            ),
            Account(
                "6001",
                "Satış Maliyetleri",
                AccountType.EXPENSE,
                0.0,
                "Satılan ürünlerin maliyeti",
                datetime.now(),
                datetime.now(),
            ),
            Account(
                "1501",
                "Ticari Mallar",
                AccountType.INVENTORY,
                0.0,
                "Stokta bulunan mallar",
                datetime.now(),
                datetime.now(),
            ),
            Account(
                "7701",
                "Vergi Giderleri",
                AccountType.EXPENSE,
                0.0,
                "Dönemsel vergi giderleri",
                datetime.now(),
                datetime.now(),
            ),
        ]

        for account in basic_accounts:
            self.accounts[account.id] = account

    def load_learning_modules(self):
        """Muhasebe öğrenme modüllerini yükler"""
        # Örnek modül ekleme (daha fazlası eklenebilir)
        temel_kavramlar = LearningModule(
            id="temel_kavramlar",
            title="Temel Muhasebe Kavramları",
            lessons=[
                Lesson(
                    title="Muhasebenin Tanımı ve Amacı",
                    content="Muhasebenin temel kavramları ve işletme için önemi",
                    duration="30 dakika",
                    difficulty="Başlangıç",
                    video_url="https://example.com/muhasebe-temel",
                    quiz=[
                        {
                            "question": "Muhasebenin temel amacı nedir?",
                            "options": [
                                "Sadece kâr hesaplamak",
                                "İşletmenin finansal durumunu kaydetmek ve raporlamak",
                                "Sadece vergi hesaplamak",
                                "Sadece maaş ödemelerini takip etmek",
                            ],
                            "correct_answer": 1,
                        }
                    ],
                ),
                Lesson(
                    title="Temel Muhasebe Eşitliği",
                    content="Varlıklar = Borçlar + Özkaynaklar eşitliği ve uygulamaları",
                    duration="45 dakika",
                    difficulty="Başlangıç",
                    video_url="https://example.com/muhasebe-esitlik",
                    quiz=[
                        {
                            "question": "Temel muhasebe eşitliğinde hangisi yoktur?",
                            "options": ["Varlıklar", "Borçlar", "Özkaynaklar", "Kâr"],
                            "correct_answer": 3,
                        }
                    ],
                ),
            ],
            exercises=[
                Exercise(
                    title="Hesap Planı Oluşturma",
                    description="Örnek bir işletme için hesap planı oluştur",
                    scenario="Bir teknoloji mağazası için hesap planı hazırla",
                    expected_output="Teknoloji mağazasına uygun hesap kodları ve açıklamaları",
                    hints=[
                        "Teknoloji ürünleri için envanter hesapları",
                        "Satış ve pazarlama giderleri",
                        "Teknik servis gelirleri",
                    ],
                )
            ],
        )
        self.learning_manager.add_module(temel_kavramlar)
        # Diğer modüller de benzer şekilde eklenebilir

    def initialize_achievements(self):
        """Muhasebe başarılarını başlatır"""
        self.learning_manager.add_achievement(
            Achievement(
                id="muhasebe_uzmani",
                title="Muhasebe Uzmanı",
                description="Tüm muhasebe modüllerini tamamla",
                reward=1000,
                required_level=10,
            )
        )
        self.learning_manager.add_achievement(
            Achievement(
                id="kayit_ustasi",
                title="Kayıt Ustası",
                description="100 başarılı kayıt işlemi yap",
                reward=500,
                required_level=5,
            )
        )
        self.learning_manager.add_achievement(
            Achievement(
                id="analiz_uzmani",
                title="Finansal Analiz Uzmanı",
                description="Tüm finansal tabloları doğru analiz et",
                reward=750,
                required_level=8,
            )
        )

    def initialize_inventory(self):
        """Envanter sistemini başlatır"""
        self.inventory_manager.add_item(
            InventoryItem(
                "INV001",
                "Örnek Ürün 1",
                100,
                50.0,
                5000.0,
                "Elektronik",
                datetime.now(),
            )
        )
        self.inventory_manager.add_item(
            InventoryItem(
                "INV002", "Örnek Ürün 2", 200, 25.0, 5000.0, "Giyim", datetime.now()
            )
        )

    def initialize_tax_system(self):
        """Vergi sistemini başlatır"""
        self.tax_manager.add_record(
            TaxRecord(
                id=str(uuid.uuid4()),
                type="KDV",
                amount=0.0,
                period="2024-Q1",
                due_date=datetime(2024, 4, 15),
                status="pending",
                payment_date=None,
            )
        )
        self.tax_manager.add_record(
            TaxRecord(
                id=str(uuid.uuid4()),
                type="Gelir Vergisi",
                amount=0.0,
                period="2024-Q1",
                due_date=datetime(2024, 4, 15),
                status="pending",
                payment_date=None,
            )
        )

    def record_transaction(self, transaction: Transaction) -> bool:
        """İşlemi muhasebe sistemine kaydeder"""
        try:
            # İşlem doğrulama
            if not self._validate_transaction(transaction):
                return False

            # Hesapları güncelle
            self._update_account_balance(
                transaction.debit_account, transaction.amount, "debit"
            )
            self._update_account_balance(
                transaction.credit_account, transaction.amount, "credit"
            )

            # İşlemi kaydet
            self.transactions.append(transaction)

            # Öğrenme ilerlemesini güncelle
            self._update_learning_progress(transaction)

            return True
        except Exception as e:
            print(f"İşlem kayıt hatası: {str(e)}")
            return False

    def _validate_transaction(self, transaction: Transaction) -> bool:
        """İşlemin geçerliliğini kontrol eder"""
        # Hesap kontrolü
        if (
            transaction.debit_account not in self.accounts
            or transaction.credit_account not in self.accounts
        ):
            return False

        # Tutar kontrolü
        if transaction.amount <= 0:
            return False

        # İşlem tipi kontrolü
        if not isinstance(transaction.type, TransactionType):
            return False

        return True

    def _update_account_balance(self, account_id: str, amount: float, operation: str):
        """Hesap bakiyesini günceller"""
        if account_id in self.accounts:
            account = self.accounts[account_id]
            if operation == "debit":
                account.balance += amount
            else:  # credit
                account.balance -= amount

    def _update_learning_progress(self, transaction: Transaction):
        """Öğrenme ilerlemesini günceller"""
        # İşlem tipine göre ilerleme
        if transaction.type == TransactionType.SALE:
            self.learning_manager.complete_task("kayit_islemleri", "satis_kaydi")
        elif transaction.type == TransactionType.PURCHASE:
            self.learning_manager.complete_task("kayit_islemleri", "alis_kaydi")
        elif transaction.type == TransactionType.TAX:
            self.learning_manager.complete_task("vergi_hesaplama", "vergi_kaydi")

    def get_learning_progress(self) -> Dict:
        """Öğrenme ilerlemesini döndürür"""
        return {
            "modules": {k: v for k, v in self.learning_manager.modules.items()},
            "completed_tasks": self.learning_manager.get_completed_tasks(),
            "achievements": [
                a.__dict__ for a in self.learning_manager.get_achievements()
            ],
        }

    def update_inventory(self, item_id: str, quantity: int, unit_cost: float) -> bool:
        """Envanter güncellemesi yapar"""
        try:
            updated = self.inventory_manager.update_item(item_id, quantity, unit_cost)
            if updated:
                item = self.inventory_manager.get_item(item_id)
                # Muhasebe kaydı oluştur
                transaction = Transaction(
                    id=str(uuid.uuid4()),
                    date=datetime.now(),
                    type=TransactionType.INVENTORY,
                    description=f"Envanter güncelleme: {item.name}",
                    debit_account="1501",  # Ticari Mallar
                    credit_account="1001",  # Kasa
                    amount=item.total_cost,
                    reference=f"INV_{item_id}",
                    status="completed",
                )
                self.record_transaction(transaction)
                return True
            return False
        except Exception as e:
            print(f"Envanter güncelleme hatası: {str(e)}")
            return False

    def calculate_tax(self, period: str) -> Dict[str, float]:
        """Vergi hesaplamalarını yapar"""
        try:
            # KDV hesaplama
            sales = sum(
                account.balance
                for account in self.accounts.values()
                if account.type == AccountType.REVENUE
            )
            kdv_amount = sales * 0.18  # %18 KDV
            # Gelir vergisi hesaplama
            net_income = self.calculate_net_income()
            income_tax = net_income * 0.20  # %20 gelir vergisi
            # Vergi kayıtlarını güncelle
            self.tax_manager.update_record(period, "KDV", kdv_amount)
            self.tax_manager.update_record(period, "Gelir Vergisi", income_tax)
            return {
                "kdv": kdv_amount,
                "income_tax": income_tax,
                "total_tax": kdv_amount + income_tax,
            }
        except Exception as e:
            print(f"Vergi hesaplama hatası: {str(e)}")
            return {}

    def calculate_financial_ratios(self) -> Dict[str, float]:
        """Finansal oranları hesaplar"""
        try:
            statements = self.generate_financial_statements()
            return statements["financial_ratios"]
        except Exception as e:
            print(f"Finansal oran hesaplama hatası: {str(e)}")
            return {}

    def calculate_net_income(self) -> float:
        """Net kârı hesaplar"""
        total_revenue = sum(
            account.balance
            for account in self.accounts.values()
            if account.type == AccountType.REVENUE
        )
        total_expense = sum(
            account.balance
            for account in self.accounts.values()
            if account.type == AccountType.EXPENSE
        )
        return total_revenue - total_expense

    def generate_financial_report(self) -> Dict:
        """Detaylı finansal rapor oluşturur"""
        return {
            "balance_sheet": self.generate_financial_statements()["balance_sheet"],
            "income_statement": self.generate_financial_statements()[
                "income_statement"
            ],
            "financial_ratios": self.calculate_financial_ratios(),
            "inventory_status": {
                item.id: {
                    "name": item.name,
                    "quantity": item.quantity,
                    "total_value": item.total_cost,
                }
                for item in self.inventory_manager.all_items()
            },
            "tax_summary": {
                record.type: {
                    "amount": record.amount,
                    "status": record.status,
                    "due_date": record.due_date.strftime("%Y-%m-%d"),
                }
                for record in self.tax_manager.get_records()
            },
        }

    def generate_financial_statements(self) -> Dict:
        """Finansal tabloları oluşturur"""
        balance_sheet = FinancialReportManager.generate_balance_sheet(self.accounts)
        income_statement = FinancialReportManager.generate_income_statement(
            self.accounts
        )
        # Finansal oranları hesapla
        total_assets = sum(balance_sheet["assets"].values())
        total_liabilities = sum(balance_sheet["liabilities"].values())
        total_equity = sum(balance_sheet["equity"].values())
        net_income = income_statement["net_income"]
        total_revenue = sum(income_statement["revenues"].values())
        ratios = {
            "current_ratio": FinancialRatios.calculate_current_ratio(
                total_assets, total_liabilities
            ),
            "debt_to_equity": FinancialRatios.calculate_debt_to_equity(
                total_liabilities, total_equity
            ),
            "profit_margin": FinancialRatios.calculate_profit_margin(
                net_income, total_revenue
            ),
            "return_on_assets": FinancialRatios.calculate_return_on_assets(
                net_income, total_assets
            ),
            "return_on_equity": FinancialRatios.calculate_return_on_equity(
                net_income, total_equity
            ),
        }
        return {
            "balance_sheet": balance_sheet,
            "income_statement": income_statement,
            "financial_ratios": ratios,
        }
