# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from ai_assistant.services.knowledge_service import KnowledgeCrawler
import os

SAFE_DIRS = [
    os.path.join(settings.BASE_DIR, "docs"),
    os.path.join(settings.BASE_DIR, "ai_assistant", "docs"),
    os.path.join(settings.BASE_DIR, "ai_assistant", "README.md"),
    os.path.join(settings.BASE_DIR, "README.md"),
    os.path.join(settings.BASE_DIR, "blockchain", "README.md"),
    os.path.join(settings.BASE_DIR, "games", "README.md"),
    os.path.join(settings.BASE_DIR, "education", "docs"),
    os.path.join(settings.BASE_DIR, "accounting", "README.md"),
    os.path.join(settings.BASE_DIR, "finance", "README.md"),
]

OUT_PATH = os.path.join(settings.BASE_DIR, "var", "ai_knowledge.json")


def iter_safe_files():
    for p in SAFE_DIRS:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for fn in files:
                    if fn.lower().endswith((".md", ".txt", ".csv")):
                        yield os.path.join(root, fn)
        elif os.path.isfile(p):
            yield p


class Command(BaseCommand):
    help = "Builds a comprehensive searchable knowledge index for AI assistant including project docs, modules, user types, and features."

    def add_arguments(self, parser):
        parser.add_argument(
            '--include-modules',
            action='store_true',
            help='Include module information in knowledge base',
        )
        parser.add_argument(
            '--include-user-types',
            action='store_true',
            help='Include user types and roles information',
        )

    def handle(self, *args, **options):
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        crawler = KnowledgeCrawler(OUT_PATH)
        
        # 1. Dokümantasyon dosyalarını ekle
        self.stdout.write("Dokümantasyon dosyaları ekleniyor...")
        doc_count = 0
        for path in iter_safe_files():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                title = os.path.basename(path).replace(".md", "").replace("_", " ").title()
                rel_path = os.path.relpath(path, settings.BASE_DIR)
                
                crawler.add_local_docs([{
                    "path": rel_path,
                    "title": f"Dokümantasyon: {title}",
                    "content": text
                }])
                doc_count += 1
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"Skip {path}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"✓ {doc_count} dokümantasyon dosyası eklendi"))
        
        # 2. Modül bilgilerini ekle
        if options.get('include_modules', True):
            self.stdout.write("Modül bilgileri ekleniyor...")
            module_info = self._get_module_information()
            crawler.add_local_docs(module_info)
            self.stdout.write(self.style.SUCCESS(f"✓ {len(module_info)} modül bilgisi eklendi"))
        
        # 3. Kullanıcı tipleri ve roller bilgisini ekle
        if options.get('include_user_types', True):
            self.stdout.write("Kullanıcı tipleri ve roller bilgisi ekleniyor...")
            user_type_info = self._get_user_type_information()
            crawler.add_local_docs(user_type_info)
            self.stdout.write(self.style.SUCCESS(f"✓ {len(user_type_info)} kullanıcı tipi bilgisi eklendi"))
        
        # 4. Proje özellikleri bilgisini ekle
        self.stdout.write("Proje özellikleri ekleniyor...")
        feature_info = self._get_feature_information()
        crawler.add_local_docs(feature_info)
        self.stdout.write(self.style.SUCCESS(f"✓ {len(feature_info)} özellik bilgisi eklendi"))
        
        # Sonuç
        current = crawler.add_local_docs([])  # Sadece mevcut sayıyı al
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Knowledge base başarıyla oluşturuldu: {OUT_PATH}\n"
                f"  Toplam {current} bilgi parçası eklendi."
            )
        )
    
    def _get_module_information(self):
        """FinAsis modüllerinin bilgilerini döndür"""
        modules = [
            {
                "path": "modules/accounting",
                "title": "Muhasebe Modülü",
                "content": """
Muhasebe Modülü (accounting) - FinAsis'in temel muhasebe yönetim modülü.

Özellikler:
- Fatura yönetimi: Alış ve satış faturaları oluşturma, düzenleme, listeleme
- Gider takibi: İşletme giderlerinin kaydı ve kategorilendirilmesi
- Banka işlemleri: Banka hesap hareketleri, mutabakat
- Müşteri/Tedarikçi yönetimi: CRM özellikleri
- Ürün/Stok yönetimi: Envanter takibi
- Mali tablolar: Gelir tablosu, bilanço, nakit akış tablosu
- OCR entegrasyonu: Fiş ve fatura okuma
- Otomatik muhasebe kayıtları: AI destekli kayıt önerileri

URL: /accounting/
"""
            },
            {
                "path": "modules/finance",
                "title": "Finans Modülü",
                "content": """
Finans Modülü (finance) - Gelişmiş finansal yönetim ve analiz.

Özellikler:
- Banka hesap yönetimi: Çoklu banka hesabı takibi
- Nakit akış yönetimi: Günlük, haftalık, aylık nakit akış takibi
- Finansal raporlar: Detaylı finansal analiz raporları
- Bütçe yönetimi: Bütçe oluşturma ve takibi
- Finansal tahminler: AI destekli finansal tahmin modelleri
- Risk skorlama: Finansal risk analizi

URL: /finance/
"""
            },
            {
                "path": "modules/ai_assistant",
                "title": "AI Asistan Modülü",
                "content": """
AI Asistan Modülü (ai_assistant) - Yapay zeka destekli asistan ve analiz.

Özellikler:
- Doğal dil soru-cevap: Türkçe dil desteği ile akıllı asistan
- Finansal analiz: Otomatik finansal analiz ve öneriler
- OCR: Belge okuma ve işleme
- Sentiment analizi: Müşteri geri bildirimlerini analiz
- Doküman özetleme: Uzun dokümanları otomatik özetleme
- Otomatik rapor üretimi: AI destekli rapor oluşturma
- Sesli komut: Ses ile komut verme

URL: /ai-assistant/
"""
            },
            {
                "path": "modules/education",
                "title": "Eğitim Modülü",
                "content": """
Eğitim Modülü (education) - Learning Management System (LMS).

Özellikler:
- Kurs yönetimi: Kurs oluşturma, ders ekleme
- Öğrenci takibi: Devam, performans, portföy
- Sınav sistemi: Online sınav oluşturma ve değerlendirme
- Rozet sistemi: Başarı rozetleri
- E-Spor turnuvaları: Yarışmalar ve liderlik tablosu
- Öğretmen dashboard: Eğitimci paneli
- Öğrenci dashboard: Öğrenci paneli

URL: /education/
"""
            },
            {
                "path": "modules/games",
                "title": "Oyun Modülleri",
                "content": """
Oyun Modülleri (games) - Oyunlaştırılmış öğrenme ve simülasyon.

Oyunlar:
- TradeSim: Ticaret simülasyonu oyunu
- FinQuest: Finansal macera oyunu
- Ticaretin İzinde: İşletme simülasyonu

Özellikler:
- Rozet ve başarı sistemi
- Liderlik tablosu
- Turnuvalar
- Oyunlaştırılmış öğrenme
- Finansal okuryazarlık eğitimi

URL: /games/
"""
            },
            {
                "path": "modules/blockchain",
                "title": "Blockchain Modülü",
                "content": """
Blockchain Modülü (blockchain) - Enterprise blockchain çözümü.

Özellikler:
- Blockchain kanıt sistemi: İşlem kayıtlarının değişmezliği
- Block mining: Proof of Work algoritması
- Transaction management: Tüm finansal işlemlerin blockchain'e kaydı
- Smart contracts: Otomatik iş süreçleri
- Digital assets: Token ve NFT yönetimi
- Chain verification: Zincir bütünlüğü kontrolü
- Audit logs: Blockchain aktivite log'ları

URL: /blockchain/
"""
            },
            {
                "path": "modules/audit",
                "title": "Denetim Modülü",
                "content": """
Denetim Modülü (audit) - Uyumluluk ve denetim araçları.

Özellikler:
- Anomali tespiti: AI destekli anomali algılama
- Uyumluluk kontrolleri: MASAK, KVKK uyumluluk kontrolleri
- Audit raporları: Detaylı denetim raporları
- Güvenlik olayları: Güvenlik olay takibi

URL: /audit/
"""
            },
            {
                "path": "modules/kobi_analysis",
                "title": "KOBİ Analiz Modülü",
                "content": """
KOBİ Analiz Modülü (kobi_analysis) - KOBİ sağlık ve performans analizi.

Özellikler:
- KOBİ sağlık skoru: İşletme sağlığı değerlendirmesi
- Performans metrikleri: Detaylı performans göstergeleri
- Benchmark karşılaştırmaları: Sektör karşılaştırmaları
- İyileştirme önerileri: AI destekli öneriler

URL: /kobi-analysis/
"""
            }
        ]
        return modules
    
    def _get_user_type_information(self):
        """Kullanıcı tipleri ve roller hakkında bilgi"""
        return [
            {
                "path": "user_types/management",
                "title": "Yönetim Rolleri",
                "content": """
Yönetim Rolleri:
- super_admin: Tüm sistem yetkilerine sahip, sistem yönetimi
- admin: Sistem yönetimi ve ayarları, kullanıcı yönetimi
- finance_manager: Finans ve muhasebe yönetimi, stratejik kararlar
"""
            },
            {
                "path": "user_types/business",
                "title": "İşletme Rolleri",
                "content": """
İşletme Rolleri:
- kobi_owner: KOBİ sahibi, tüm şirket işlemleri, büyüme stratejileri
- kobi_employee: KOBİ çalışanı, sınırlı yetkiler
- muhasebe_elemani: Muhasebe işlemleri, fatura, raporlama
- satis_elemani: Satış faturaları, müşteri yönetimi, tahsilat
- depo_elemani: Stok takibi, giriş/çıkış, sevkiyat
"""
            },
            {
                "path": "user_types/professional",
                "title": "Profesyonel Roller",
                "content": """
Profesyonel Roller:
- accountant: Muhasebeci, TFRS/IFRS, muhasebe kayıtları, mutabakat
- financial_advisor: Mali müşavir, vergi mevzuatı, danışmanlık
- auditor: Denetçi, denetim süreçleri, uyumluluk kontrolleri
"""
            },
            {
                "path": "user_types/education",
                "title": "Eğitim Rolleri",
                "content": """
Eğitim Rolleri:
- teacher: Öğretmen, LMS, kurs yönetimi, öğrenci takibi
- student: Öğrenci, kurslara katılım, ödevler, sınavlar
- player: Oyuncu, oyun modülleri, rozetler, turnuvalar
"""
            }
        ]
    
    def _get_feature_information(self):
        """Proje özellikleri hakkında bilgi"""
        return [
            {
                "path": "features/kvkk-compliance",
                "title": "KVKK Uyumluluk ve Veri Gizliliği",
                "content": """
KVKK (6698 sayılı Kişisel Verilerin Korunması Kanunu) Uyumluluk:

VERİ GİZLİLİĞİ PRENSİPLERİ:
- Kişisel verilerin korunması: TC Kimlik No, telefon, e-posta, adres gibi kişisel veriler korunur
- İşletme sırlarının korunması: Finansal veriler, müşteri bilgileri, ticari sırlar korunur
- Veri işleme amaçları: Sadece yasal dayanaklar ve genel işleme amaçları
- Veri saklama süreleri: Finansal kayıtlar 10 yıl, destek talepleri 3 yıl
- Veri sahibi hakları: KVKK Madde 11 kapsamında erişim, düzeltme, silme, itiraz hakları
- Veri güvenliği: AES-256 şifreleme, erişim kontrolü, audit log, MFA/SSO
- Veri paylaşımı: Üçüncü taraflarla veri paylaşımı sadece yasal zorunluluklar dahilinde
- Veri anonimleştirme: Kişisel veriler anonimleştirilebilir
- Veri silme: KVKK uyumlu veri silme süreçleri

HASSAS BİLGİ KORUMA:
- TC Kimlik No, IBAN, kredi kartı, telefon gibi hassas bilgiler şifrelenir
- İşletme sırları ve ticari bilgiler korunur
- Finansal veriler sadece yetkili kullanıcılara açılır
- Audit log ile tüm veri erişimleri kaydedilir

KVKK BAŞVURU:
- KVKK başvuruları: kvkk@finasis.com.tr
- Başvuru süresi: En geç 30 gün içinde yanıtlanır
- Başvuru yöntemi: İmzalı dilekçe veya KEP (Kayıtlı Elektronik Posta)

VERİ GÜVENLİĞİ ÖNLEMLERİ:
- Şifreleme: AES-256
- Erişim kontrolü: Rol tabanlı yetkilendirme
- Audit log: Tüm veri erişimleri kaydedilir
- MFA/SSO: Çok faktörlü kimlik doğrulama
- Coğrafi yedekleme: Veriler güvenli lokasyonlarda yedeklenir
- Veri maskeleme: Loglarda hassas bilgiler maskelenir
"""
            },
            {
                "path": "features/e-transformation",
                "title": "E-Dönüşüm Özellikleri",
                "content": """
E-Dönüşüm Özellikleri:
- e-Fatura: GIB entegrasyonu, e-fatura gönderimi/alımı
- e-Arşiv: E-arşiv fatura yönetimi
- e-Defter: Elektronik defter kayıtları
- e-İmza: Elektronik imza desteği
- GIB Entegrasyonu: Gümrük ve Ticaret Bakanlığı entegrasyonu
"""
            },
            {
                "path": "features/financial-reporting",
                "title": "Finansal Raporlama",
                "content": """
Finansal Raporlama:
- Gelir Tablosu: Dönem kar/zarar raporu
- Bilanço: Varlık ve yükümlülük raporu
- Nakit Akış Tablosu: Nakit hareketleri
- Özkaynak Değişim Tablosu: Özkaynak hareketleri
- KPI Dashboard: Temel performans göstergeleri
- Bütçe vs Gerçekleşen: Bütçe analizi
"""
            },
            {
                "path": "features/ai-features",
                "title": "AI Özellikleri",
                "content": """
AI Özellikleri:
- Doğal dil işleme: Türkçe soru-cevap
- OCR: Belge okuma ve işleme
- Finansal tahmin: AI destekli tahmin modelleri
- Risk skorlama: Otomatik risk analizi
- Sentiment analizi: Duygu analizi
- Doküman özetleme: Otomatik özet
- Otomatik rapor: AI destekli rapor üretimi
"""
            },
            {
                "path": "features/compliance",
                "title": "Uyumluluk Özellikleri",
                "content": """
Uyumluluk Özellikleri:
- MASAK: MASAK uyumluluk kontrolleri
- KVKK: Kişisel verilerin korunması uyumluluğu
- TFRS/IFRS: Muhasebe standartları uyumluluğu
- Vergi mevzuatı: Güncel vergi mevzuatı takibi
- Audit trail: Denetim izi kayıtları
"""
            }
        ]
