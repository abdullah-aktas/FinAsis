# -*- coding: utf-8 -*-
import logging
from typing import Dict, Any, List, Optional, cast
from django.contrib.auth.models import User
from ..models import UserInteraction
import os
from django.conf import settings
from .knowledge_service import KnowledgeIndex

# Optional dependency: OpenAI SDK (v1). Guard import to avoid import-time failures.
try:
    from openai import OpenAI  # type: ignore
    from openai.types.chat import ChatCompletionMessageParam  # type: ignore
except Exception:
    OpenAI = None  # will be validated at runtime when service is used
    ChatCompletionMessageParam = Dict[str, Any]  # fallback for typing

logger = logging.getLogger(__name__)


class ChatAIService:
    def __init__(self):
        """AI sohbet servisi başlatıcı"""
        # Mock modu: test/sunucuda anahtar yoksa basit yanıt üret
        self.mock_mode = os.getenv("FINASIS_AI_MOCK", "0") in ("1", "true", "True")
        # API istemcisi varsayılan olarak yok; uygun koşullarda oluşturulacak
        self.client: Optional[Any] = None

        # OpenAI paketi yoksa zorunlu mock moda geç ve uyarı logla
        if OpenAI is None:
            logger.warning(
                "OpenAI paketi bulunamadı; ChatAIService mock modunda çalışacak."
            )
            self.mock_mode = True
            self.api_key = None
        else:
            # API anahtarını al ve uygun ise istemciyi başlat
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                # API anahtarı yoksa mock moda düş
                self.mock_mode = True
            else:
                # Yeni SDK istemcisi
                try:
                    self.client = OpenAI(api_key=self.api_key)
                except Exception as e:
                    logger.error(f"OpenAI istemcisi başlatılırken hata: {e}")
                    self.client = None
                    self.mock_mode = True

        # Sistem rolü: Finansman/Muhasebe uzmanı ve FinAsis bağlam bilgesi
        assistant_name = os.getenv("FINASIS_AI_WIDGET_NAME", "FinAsis Bilgesi")
        default_prompt = self._build_comprehensive_system_prompt(assistant_name)
        self.system_prompt = os.getenv("FINASIS_AI_SYSTEM_PROMPT", default_prompt)
    
    def _get_role_based_guidance(self, user: User) -> List[str]:
        """Kullanıcının rolüne göre özelleştirilmiş rehberlik notları"""
        hints = []
        try:
            # Django groups'dan roller
            groups = list(getattr(user, "groups").all().values_list("name", flat=True))
            group_names_lower = [g.lower() for g in groups]
            
            # UserType kontrolü
            user_type_code = None
            try:
                if hasattr(user, 'user_type') and user.user_type:
                    user_type_code = user.user_type.code.lower()
                elif hasattr(user, 'role_profile') and user.role_profile:
                    if hasattr(user.role_profile, 'role') and user.role_profile.role:
                        user_type_code = user.role_profile.role.name.lower()
            except Exception:
                pass
            
            # Rol bazlı özelleştirmeler
            role_mappings = {
                # Yönetim Rolleri
                "super_admin": "Kullanıcı süper yöneticidir. Tüm sistem yetkilerine sahip. Sistem yönetimi, kullanıcı yönetimi ve tüm modüllere erişim konularında yardımcı ol.",
                "admin": "Kullanıcı sistem yöneticisidir. Sistem ayarları, kullanıcı yönetimi ve modül yapılandırmaları konularında destek ver.",
                "finance_manager": "Kullanıcı finans müdürüdür. Finansal raporlama, bütçe yönetimi, nakit akışı ve stratejik kararlar için özet ve aksiyon odaklı bilgi ver.",
                
                # İşletme Rolleri
                "kobi_owner": "Kullanıcı KOBİ sahibidir. Şirket yönetimi, finansal durum, büyüme stratejileri ve tüm modüllere erişim konularında yardımcı ol. Pratik ve uygulanabilir öneriler ver.",
                "kobi_employee": "Kullanıcı KOBİ çalışanıdır. Sınırlı yetkilerle çalışıyor. Erişebileceği modüller ve işlemler konusunda rehberlik et.",
                "muhasebe_elemani": "Kullanıcı muhasebe elemanıdır. Fatura oluşturma, gider takibi, mali tablolar ve raporlama konularında detaylı yardım sağla. Muhasebe modülü özelliklerini açıkla.",
                "satis_elemani": "Kullanıcı satış elemanıdır. Satış faturaları, müşteri yönetimi, tahsilat takibi ve satış performansı konularında destek ver.",
                "depo_elemani": "Kullanıcı depo elemanıdır. Stok takibi, giriş/çıkış işlemleri, sevkiyat yönetimi ve düşük stok uyarıları konularında yardımcı ol.",
                
                # Profesyonel Roller
                "accountant": "Kullanıcı muhasebecidir. TFRS/IFRS prensipleri, muhasebe kayıtları, mutabakat, mali tablolar ve raporlama konularında derinlemesine bilgi ver. Teknik detaylara girebilirsin.",
                "financial_advisor": "Kullanıcı mali müşavirdir. Vergi mevzuatı, uyumluluk, danışmanlık ve raporlama konularında uzman seviyesinde bilgi sağla.",
                "auditor": "Kullanıcı denetçidir. Denetim süreçleri, uyumluluk kontrolleri, anomali tespiti ve audit raporları konularında destek ver.",
                
                # Eğitim Rolleri
                "teacher": "Kullanıcı öğretmendir. LMS özellikleri, kurs yönetimi, öğrenci takibi, sınav oluşturma ve eğitim içerikleri konularında yardımcı ol.",
                "student": "Kullanıcı öğrencidir. Kurslara katılım, ödevler, sınavlar, rozetler ve oyunlaştırma özellikleri konularında rehberlik et.",
                "player": "Kullanıcı oyuncudur. Oyun modüllerine (TradeSim, FinQuest, Ticaretin İzinde) erişim, rozetler, turnuvalar ve liderlik tablosu konularında bilgi ver.",
                
                # Diğer
                "viewer": "Kullanıcı görüntüleyicidir. Sadece görüntüleme yetkisi var. Erişebileceği raporlar ve görünümler konusunda bilgi ver.",
            }
            
            # Group isimlerinden rol tespiti
            for group_name in group_names_lower:
                for role_key, role_guidance in role_mappings.items():
                    if role_key in group_name or any(alias in group_name for alias in [
                        "muhasebe", "accountant", "muhasebeci",
                        "yönetici", "manager", "admin",
                        "kobi", "owner", "sahip",
                        "öğretmen", "teacher", "eğitimci",
                        "öğrenci", "student",
                        "oyuncu", "player"
                    ]):
                        hints.append(role_guidance)
                        break
            
            # UserType kodundan rol tespiti
            if user_type_code:
                for role_key, role_guidance in role_mappings.items():
                    if role_key == user_type_code or any(alias in user_type_code for alias in [
                        "muhasebe", "accountant",
                        "satis", "sales",
                        "depo", "warehouse",
                        "kobi", "owner"
                    ]):
                        hints.append(role_guidance)
                        break
            
            # Staff kontrolü
            if user.is_staff or user.is_superuser:
                if not any("yönetici" in h.lower() or "admin" in h.lower() for h in hints):
                    hints.append("Kullanıcı sistem personelidir. Yönetici seviyesinde yetkilere sahip. Sistem yönetimi ve tüm modüllere erişim konularında destek ver.")
            
            # Özel durumlar
            if "accountant" in group_names_lower or "muhasebe" in (user_type_code or ""):
                hints.append("Muhasebe modülü özelliklerini detaylı açıkla: fatura yönetimi, gider takibi, mali tablolar, OCR ile fiş okuma.")
            
            if "teacher" in group_names_lower or "öğretmen" in (user_type_code or ""):
                hints.append("Eğitim modülü özelliklerini açıkla: LMS, kurs yönetimi, öğrenci takibi, sınav sistemi.")
            
            if "student" in group_names_lower or "öğrenci" in (user_type_code or ""):
                hints.append("Eğitim ve oyun modüllerini tanıt: kurslara katılım, rozetler, turnuvalar, oyunlaştırılmış öğrenme.")
            
        except Exception as e:
            logger.warning(f"Rol tespiti sırasında hata: {e}")
        
        return hints if hints else []
        """Kapsamlı sistem prompt'u oluştur - proje gereksinimleri, kullanıcı tipleri ve modüller"""
        return f"""Sen {assistant_name} — FinAsis platformunun deneyimli ve kapsamlı bir Yapay Zeka asistanısın.

## TEMEL KİMLİK
FinAsis, Türkiye'nin önde gelen finans ve muhasebe yönetim platformudur. Sen bu platformun uzman asistanısın ve tüm özelliklerini, modüllerini ve kullanıcı tiplerini derinlemesine biliyorsun.

## UZMANLIK ALANLARIN
1. **Muhasebe & Finans**: TFRS/IFRS prensipleri, genel muhasebe, mali tablolar, nakit akışı, bütçe, finansal analiz
2. **Vergi & Uyumluluk**: KDV, gelir vergisi, stopaj, e-Fatura, e-Arşiv, e-Defter, MASAK, KVKK uyumluluğu
3. **E-Dönüşüm**: e-Fatura entegrasyonu, GIB entegrasyonu, e-Defter, e-İmza
4. **Finansal Raporlama**: Gelir tablosu, bilanço, nakit akış tablosu, özkaynak değişim tablosu, KPI'lar
5. **İşletme Yönetimi**: KOBİ yönetimi, finansal planlama, risk analizi, tahmin modelleri
6. **Eğitim & Oyunlaştırma**: Finansal okuryazarlık, LMS, oyunlaştırılmış öğrenme, rozetler, turnuvalar

## FİNASİS MODÜLLERİ VE ÖZELLİKLERİ

### 1. MUHASEBE MODÜLÜ (accounting)
- Fatura yönetimi (alış/satış)
- Gider takibi
- Banka işlemleri
- Müşteri/Tedarikçi yönetimi
- Ürün/Stok yönetimi
- Mali tablolar ve raporlar
- OCR ile fiş okuma
- Otomatik muhasebe kayıtları

### 2. FİNANS MODÜLÜ (finance)
- Banka hesap yönetimi
- Nakit akış takibi
- Finansal raporlar
- Bütçe yönetimi
- Finansal tahminler
- Risk skorlama

### 3. AI ASİSTAN MODÜLÜ (ai_assistant)
- Doğal dil ile soru-cevap
- Finansal analiz ve öneriler
- OCR ile belge işleme
- Sentiment analizi
- Doküman özetleme
- Otomatik rapor üretimi
- Sesli komut desteği

### 4. EĞİTİM MODÜLÜ (education)
- LMS (Learning Management System)
- Kurs ve ders yönetimi
- Sınav ve değerlendirme
- Öğrenci portföyü
- Devam takibi
- E-Spor turnuvaları

### 5. OYUN MODÜLLERİ (games)
- TradeSim: Ticaret simülasyonu
- FinQuest: Finansal macera oyunu
- Ticaretin İzinde: İşletme simülasyonu
- Rozet ve başarı sistemi
- Liderlik tablosu
- Oyunlaştırılmış öğrenme

### 6. BLOCKCHAIN MODÜLÜ (blockchain)
- Blockchain kanıt sistemi
- İşlem kayıtlarının değişmezliği
- Akıllı sözleşmeler
- Dijital varlıklar
- Audit log'ları

### 7. DENETİM MODÜLÜ (audit)
- Anomali tespiti
- Uyumluluk kontrolleri
- Audit raporları
- Güvenlik olayları

### 8. KOBİ ANALİZ MODÜLÜ (kobi_analysis)
- KOBİ sağlık skoru
- Performans metrikleri
- Benchmark karşılaştırmaları
- İyileştirme önerileri

## KULLANICI TİPLERİ VE ROLLER

### Yönetim Rolleri
- **super_admin**: Tüm sistem yetkilerine sahip
- **admin**: Sistem yönetimi ve ayarları
- **finance_manager**: Finans ve muhasebe yönetimi

### İşletme Rolleri
- **kobi_owner**: KOBİ sahibi - Tüm şirket işlemleri
- **kobi_employee**: KOBİ çalışanı - Sınırlı yetkiler
- **muhasebe_elemani**: Muhasebe işlemleri, fatura, raporlama
- **satis_elemani**: Satış faturaları, müşteri yönetimi
- **depo_elemani**: Stok takibi, giriş/çıkış işlemleri

### Profesyonel Roller
- **accountant**: Muhasebeci - Kayıt, mutabakat, raporlama
- **financial_advisor**: Mali müşavir - Danışmanlık ve raporlama
- **auditor**: Denetçi - Denetim ve uyumluluk kontrolü

### Eğitim Rolleri
- **teacher**: Öğretmen - Kurs yönetimi, öğrenci takibi
- **student**: Öğrenci - Kurslara katılım, ödevler, sınavlar
- **player**: Oyuncu - Oyun modüllerine erişim

### Diğer
- **viewer**: Sadece görüntüleme yetkisi

## CEVAP VERME TARZI
1. **Net ve Pratik**: Adım adım, uygulanabilir öneriler
2. **Rol Odaklı**: Kullanıcının rolüne göre uygun seviyede bilgi
3. **Modül Yönlendirmesi**: İlgili FinAsis modüllerine yönlendir
4. **Örneklerle Destekle**: Somut örnekler ve senaryolar kullan
5. **Kısa ve Öz**: Mümkünse madde işaretleri kullan
6. **Türkçe Odaklı**: Türk muhasebe ve vergi mevzuatına uygun
7. **Güvenli**: Bilmediğin konularda varsayım yapma, alternatif öner

## ÖNEMLİ NOTLAR
- Kullanıcının rolüne göre erişebileceği modülleri bil
- FinAsis'in özelliklerini tanıt ve yönlendir
- Türk muhasebe standartlarına (TFRS) uygun bilgi ver
- E-dönüşüm süreçlerini (e-Fatura, e-Defter) açıkla
- KOBİ'ler için pratik çözümler öner
- Eğitim ve oyunlaştırma özelliklerini tanıt
- Blockchain kanıt sistemini açıkla
- API ve entegrasyon seçeneklerini belirt

Bilmediğin bir konuda varsayım yapma, kullanıcıyı ilgili FinAsis modülüne veya dokümantasyona yönlendir.

## ⚠️ KRİTİK: VERİ GİZLİLİĞİ VE KVKK UYUMLULUĞU

### VERİ GİZLİLİĞİ KURALLARI (MUTLAKA UYULMALI):
1. **KİŞİSEL VERİLERİ ASLA PAYLAŞMA**: TC Kimlik No, telefon, e-posta, adres gibi kişisel verileri hiçbir şekilde açıklama veya paylaşma.
2. **İŞLETME SIRLARINI KORU**: Finansal veriler, müşteri bilgileri, ticari sırlar, stratejik planlar gibi hassas bilgileri asla açıklama.
3. **KVKK UYUMLULUĞU**: 6698 sayılı KVKK Kanunu'na tam uyumlu davran. Kişisel veri işleme konusunda sadece genel bilgi ver, spesifik veri paylaşma.
4. **GÜVENLİK ÖNLEMLERİ**: FinAsis'in veri güvenliği önlemlerini (şifreleme, erişim kontrolü, audit log) açıkla ama sistem detaylarını verme.
5. **VERİ SAHİBİ HAKLARI**: KVKK Madde 11 kapsamındaki hakları (erişim, düzeltme, silme, itiraz) genel olarak açıkla ama kullanıcının spesifik verilerini işleme.
6. **VERİ İŞLEME AMAÇLARI**: Sadece yasal dayanaklar ve genel işleme amaçlarını açıkla, spesifik veri işleme faaliyetlerini detaylandırma.
7. **VERİ SAKLAMA SÜRELERİ**: Genel saklama sürelerini (örn: finansal kayıtlar 10 yıl) belirt ama kullanıcının spesifik verilerinin saklama durumunu açıklama.
8. **VERİ PAYLAŞIMI**: Üçüncü taraflarla veri paylaşımı konusunda sadece genel bilgi ver, spesifik paylaşımları açıklama.
9. **HASSAS BİLGİ FİLTRELEME**: Kullanıcıdan gelen sorgularda TC Kimlik No, IBAN, kredi kartı, şifre gibi hassas bilgiler varsa bunları işleme ve uyar.
10. **ANONİMLEŞTİRME**: Veri anonimleştirme süreçlerini genel olarak açıkla ama spesifik veri anonimleştirme işlemlerini detaylandırma.

### HASSAS BİLGİ TESPİTİ:
Eğer kullanıcı sorgusunda şunlar varsa DİKKATLİ OL:
- TC Kimlik No (11 haneli sayı)
- IBAN (TR ile başlayan 26 haneli)
- Kredi kartı numarası (16 haneli)
- Telefon numarası
- E-posta adresi
- Şifre veya parola
- Finansal tutarlar (müşteri/spesifik işletme verileri)
- Müşteri/tedarikçi isimleri (ticari sır)
- Şirket içi stratejik bilgiler

### UYARI MESAJLARI:
Hassas bilgi tespit edildiğinde şu mesajı kullan:
"Bu sorgu kişisel veri veya işletme sırrı içeriyor olabilir. KVKK uyumluluğu gereği bu tür bilgileri işleyemem. Lütfen genel bilgi taleplerinde bulunun veya ilgili modüle erişim sağlayın."

### VERİ GÜVENLİĞİ BİLGİSİ:
FinAsis'in veri güvenliği önlemlerini genel olarak açıklayabilirsin:
- AES-256 şifreleme
- Erişim kontrolü ve yetkilendirme
- Audit log kayıtları
- MFA/SSO desteği
- Coğrafi yedekleme
- KVKK uyumluluk kontrolleri

AMA: Sistem detaylarını, güvenlik açıklarını veya spesifik kullanıcı verilerini asla açıklama."""
        # Bilgi indeksi (varsa yükle)
        try:
            base_dir = (
                getattr(settings, "BASE_DIR", None)
                or os.getenv("FINASIS_BASE_DIR")
                or os.getcwd()
            )
        except Exception:
            base_dir = os.getenv("FINASIS_BASE_DIR") or os.getcwd()
        self.knowledge_path = os.path.join(base_dir, "var", "ai_knowledge.json")
        self.knowledge = KnowledgeIndex.load(self.knowledge_path)

    def _mask_sensitive_data(self, text: str) -> str:
        """Hassas verileri maskele (KVKK uyumluluğu için)"""
        import re
        
        # TC Kimlik No maskeleme
        text = re.sub(r'\b(\d{3})\d{5}(\d{3})\b', r'\1*****\2', text)
        
        # IBAN maskeleme
        text = re.sub(r'\b(TR\d{2})\d{20}(\d{2})\b', r'\1' + '*'*20 + r'\2', text, flags=re.IGNORECASE)
        
        # Kredi kartı maskeleme
        text = re.sub(r'\b(\d{4})[\s-]?\d{4}[\s-]?\d{4}[\s-]?(\d{4})\b', r'\1****\2', text)
        
        # Telefon maskeleme (Türkiye formatları)
        text = re.sub(r'(\+90|0)?[\s-]?([5][0-9]{2})[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}', r'\1 \2 *** **', text)
        
        return text
    
    def _detect_sensitive_data(self, text: str) -> tuple[bool, str]:
        """Hassas veri tespiti yapar (KVKK uyumluluğu için)"""
        import re
        
        # TC Kimlik No (11 haneli sayı)
        if re.search(r'\b\d{11}\b', text):
            return True, "TC Kimlik No tespit edildi"
        
        # IBAN (TR ile başlayan 26 haneli)
        if re.search(r'\bTR\d{24}\b', text, re.IGNORECASE):
            return True, "IBAN tespit edildi"
        
        # Kredi kartı (16 haneli, Luhn algoritması kontrolü olmadan basit tespit)
        if re.search(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', text):
            return True, "Kredi kartı numarası tespit edildi"
        
        # E-posta (basit tespit)
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            # E-posta genelde sorun değil ama çok hassas içerik varsa uyar
            pass
        
        # Telefon (Türkiye formatları)
        if re.search(r'(\+90|0)?[\s-]?[5][0-9]{2}[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}', text):
            return True, "Telefon numarası tespit edildi"
        
        # Şifre/parola kelimeleri
        sensitive_keywords = ['şifre', 'parola', 'password', 'pin', 'gizli', 'sır', 'confidential']
        if any(keyword in text.lower() for keyword in sensitive_keywords):
            # Sadece uyarı, engelleme değil
            pass
        
        return False, ""
    
    def get_response(
        self, user: User, query: str, context: Dict[str, Any] | None = None
    ) -> str:
        """
        Kullanıcı sorgusuna yanıt verir

        Args:
            user (User): Kullanıcı nesnesi
            query (str): Kullanıcı sorgusu
            context (dict|None): Opsiyonel sayfa/uygulama bağlamı (path, title, locale vb.)

        Returns:
            str: AI yanıtı
        """
        try:
            # Hassas veri kontrolü (KVKK uyumluluğu)
            has_sensitive, sensitive_type = self._detect_sensitive_data(query)
            if has_sensitive:
                logger.warning(f"Hassas veri tespit edildi: {sensitive_type} - Kullanıcı: {user.username}")
                return (
                    "⚠️ **KVKK Uyarısı**\n\n"
                    "Sorgunuzda kişisel veri veya hassas bilgi tespit edildi. "
                    "6698 sayılı KVKK Kanunu uyumluluğu gereği, bu tür bilgileri işleyemem.\n\n"
                    "**Lütfen:**\n"
                    "• Kişisel verileri (TC Kimlik No, IBAN, telefon vb.) sorgularınızdan çıkarın\n"
                    "• Genel bilgi taleplerinde bulunun\n"
                    "• Spesifik veri işlemleri için ilgili modüle erişim sağlayın\n"
                    "• Veri gizliliği konusunda genel bilgi almak isterseniz yardımcı olabilirim"
                )
            # Model adı (env ile override edilebilir)
            model_name = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

            # Son sohbet geçmişini al
            history = UserInteraction.objects.filter(
                user=user, interaction_type="chat"
            ).order_by("-created_at")[:5]

            # Sistem mesajını ve bağlamı hazırla
            system_content = self.system_prompt
            if context:
                try:
                    ctx_bits = []
                    page = context.get("page_path") or context.get("path")
                    title = context.get("page_title") or context.get("title")
                    if page:
                        ctx_bits.append(f"Sayfa: {page}")
                    if title:
                        ctx_bits.append(f"Başlık: {title}")
                    if ctx_bits:
                        system_content += "\nBağlam: " + " | ".join(ctx_bits)
                except Exception:
                    # Bağlam oluşturma hatasını yut, kritik değil
                    pass

            # Rol tabanlı rehberlik - kapsamlı kullanıcı tipi desteği
            role_hints = self._get_role_based_guidance(user)
            if role_hints:
                system_content += "\n\n[KULLANICI ROL BİLGİSİ]\n" + "\n".join(role_hints)

            messages: List[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_content}
            ]

            # Geçmiş mesajları ekle
            for interaction in reversed(history):
                if getattr(interaction, "content", None):
                    messages.append({"role": "user", "content": interaction.content})
                if getattr(interaction, "ai_response", None):
                    messages.append(
                        {"role": "assistant", "content": interaction.ai_response}
                    )

            # Bilgi tabanından ilgili parçaları getir ve kullanıcı mesajına ek bağlam olarak iliştir
            user_content = query
            if self.knowledge and isinstance(query, str):
                # Daha fazla sonuç al ve daha iyi filtreleme yap
                top_k = int(os.getenv("FINASIS_AI_RETRIEVE_K", "5"))
                tops = self.knowledge.search(query, top_k=top_k)
                if tops:
                    refs = "\n\n[İLGİLİ FİNASİS BİLGİ TABANI]\n"
                    for idx, chunk in enumerate(tops, 1):
                        # Daha fazla içerik göster (400 -> 600 karakter)
                        # Hassas bilgileri filtrele
                        content_preview = chunk.content[:600] + "..." if len(chunk.content) > 600 else chunk.content
                        # Hassas bilgileri maskele
                        content_preview = self._mask_sensitive_data(content_preview)
                        refs += f"\n{idx}. {chunk.title}\n   Kaynak: {chunk.path}\n   İçerik: {content_preview}\n"
                    user_content += refs
                    
                    # Kullanıcıya bilgi tabanından yararlandığını belirt
                    system_content += "\n\nNot: Yukarıdaki bilgi tabanı içeriklerini kullanarak kullanıcıya en doğru ve güncel bilgiyi ver. HASSAS BİLGİLERİ ASLA PAYLAŞMA."

            # Yeni sorguyu ekle
            messages.append({"role": "user", "content": user_content})

            # Mock yanıt (istemci yoksa da mock'a düş)
            if self.mock_mode or not getattr(self, "client", None):
                prefix = "[MOCK] FinAsis Cevap (Mock)"
                tips = (
                    "• Nakit akışı ve kârlılık metriklerini düzenli takip edin.\n"
                    "• Cari oranı >1.2, Borç/Özsermaye <2 hedefleyin.\n"
                    "• Bütçe-tahmin sapmalarını aylık analiz edin."
                )
                ctx = f"\n[Bağlam: {context}]" if context else ""
                return f"{prefix}: {query[:120]}...\n{tips}{ctx}"

            # OpenAI API'yi çağır (v1 SDK)
            # Bu noktada istemci mevcut olmalı; type checker için cast kullanıyoruz
            client = cast(Any, self.client)
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.4")),
                    max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "800")),
                    timeout=float(os.getenv("OPENAI_REQUEST_TIMEOUT", "20")),
                )

                # Yanıtı al
                ai_response = response.choices[0].message.content or ""  # type: ignore[assignment]
                return ai_response
            except Exception as call_err:
                # Bağlantı/istek hatalarında kullanıcıya yedek cevap dön
                logger.error(f"OpenAI sohbet isteği başarısız: {call_err}")
                prefix = "[FALLBACK] FinAsis Cevap (Yedek Mod)"
                tips = (
                    "• Şu an AI servisine bağlanırken bir sorun oluştu; geçici öneriler sunuluyor.\n"
                    "• Nakit akışı ve kârlılık metriklerini düzenli takip edin.\n"
                    "• Cari oranı >1.2, Borç/Özsermaye <2 hedefleyin.\n"
                    "• Bütçe-tahmin sapmalarını aylık analiz edin."
                )
                ctx = f"\n[Bağlam: {context}]" if context else ""
                return f"{prefix}: {query[:120]}...\n{tips}{ctx}"

        except Exception as e:
            # Genel beklenmeyen hatalarda da yedek cevap dön
            logger.error(f"AI sohbet hatası: {str(e)}")
            prefix = "[FALLBACK] FinAsis Cevap (Yedek Mod)"
            tips = (
                "• Şu an AI servisine bağlanırken bir sorun oluştu; geçici öneriler sunuluyor.\n"
                "• Nakit akışı ve kârlılık metriklerini düzenli takip edin.\n"
                "• Cari oranı >1.2, Borç/Özsermaye <2 hedefleyin.\n"
                "• Bütçe-tahmin sapmalarını aylık analiz edin."
            )
            ctx = f"\n[Bağlam: {context}]" if context else ""
            return f"{prefix}: {query[:120]}...\n{tips}{ctx}"
