# Mali Müşavir Sistemi - Zorunlu Belge ve Blockchain Anlaşma Güncellemesi

## 🎯 Yeni Özellikler

### 1. Zorunlu Belge Sistemi

Mali müşavirler sisteme kayıt olurken **zorunlu** olarak aşağıdaki belgeleri yüklemek zorundadır:

#### Zorunlu Belgeler

- ✅ **Diploma/Mezuniyet Belgesi** (diploma_document)
- ✅ **Mezuniyet Belgesi/Transkript** (graduation_document)

#### Belge Doğrulama Akışı

```
1. Mali Müşavir Kayıt Olur
   ↓
   Diploma ve mezuniyet belgelerini yükler (ZORUNLU)
   ↓
2. Admin Panelden Belgeler İncelenir
   ↓
   Admin belgeleri doğrular (verify_documents action)
   ↓
3. Belgeler Doğrulandıktan Sonra
   ↓
   Mali müşavir onaylanabilir
   ↓
4. Onay Verilince Otomatik
   ↓
   BLOCKCHAIN ANLAŞMASI OLUŞTURULUR
```

### 2. Blockchain Anlaşma Sistemi

Mali müşavir onaylandığında, platform ile mali müşavir arasında **blockchain üzerinde değiştirilemez bir anlaşma** oluşturulur.

#### Blockchain Anlaşması İçeriği

```python
{
    'platform': 'FinAsis Mali Müşavir Marketplace',
    'consultant_id': 123,
    'consultant_name': 'Ahmet Yılmaz SMMM',
    'advisor_chamber_no': '123456',
    'commission_rate': 15.0,
    'agreement_date': '2025-11-14T10:30:00',
    'approved_by': 'admin_user',

    'terms': {
        'commission': {
            'rate': 15.0,
            'description': 'Platform her randevudan %15 komisyon alır',
            'calculation': 'Müşteri ödemesinden otomatik kesilir'
        },
        'payment': {
            'frequency': 'monthly',
            'minimum_payout': 500.00,
            'currency': 'TRY'
        },
        'platform_rules': {
            'must_maintain_rating': 3.0,
            'response_time_hours': 24,
            'cancellation_policy': 'En az 24 saat önceden'
        },
        'termination': {
            'notice_period_days': 30,
            'can_terminate_by_consultant': True,
            'can_terminate_by_platform': True
        }
    },

    'documents_verified': {
        'diploma': True,
        'graduation': True,
        'verified_at': '2025-11-14T09:00:00',
        'verified_by': 'admin_user'
    }
}
```

## 🔧 Teknik Değişiklikler

### Model Güncellemeleri (ConsultantProfile)

```python
# Yeni alanlar eklendi:
diploma_document = FileField(...)  # Zorunlu
graduation_document = FileField(...)  # Zorunlu
diploma_verified = BooleanField(...)
graduation_verified = BooleanField(...)
documents_verified_at = DateTimeField(...)
documents_verified_by = ForeignKey(User)

# Blockchain alanları
blockchain_contract_address = CharField(...)
blockchain_transaction_hash = CharField(...)
blockchain_contract_created_at = DateTimeField(...)
blockchain_contract_terms = JSONField(...)
```

### Yeni Metodlar

```python
consultant.documents_complete()      # Belgeler yüklendi mi?
consultant.documents_all_verified()  # Tüm belgeler doğrulandı mı?
consultant.can_be_approved()         # Onaylanabilir mi?
consultant.is_available()            # Artık blockchain kontrolü de yapar
```

### Blockchain Servisi

Yeni dosya: `advisors/services/blockchain_service.py`

#### Ana Fonksiyonlar

**1. Anlaşma Oluşturma**

```python
from advisors.services.blockchain_service import create_agreement_on_approval

# Mali müşavir onaylandığında
result = create_agreement_on_approval(consultant, admin_user)

# Dönen bilgiler:
{
    'contract': SmartContract instance,
    'transaction': Transaction instance,
    'contract_address': '0xabc123...',
    'transaction_hash': '0xdef456...',
    'terms': {...}  # Anlaşma şartları
}
```

**2. Anlaşma Doğrulama**

```python
from advisors.services.blockchain_service import verify_agreement

result = verify_agreement(consultant)

# Dönen bilgiler:
{
    'valid': True,
    'contract': SmartContract instance,
    'transaction': Transaction instance,
    'block_number': 12345
}
```

**3. Komisyon Güncelleme**

```python
from advisors.services.blockchain_service import ConsultantBlockchainService

# Komisyon oranını değiştir (blockchain'e kaydedilir)
result = ConsultantBlockchainService.update_commission_rate(
    consultant_profile=consultant,
    new_rate=Decimal('18.00'),
    admin_user=admin
)
```

**4. Anlaşmayı Feshetme**

```python
result = ConsultantBlockchainService.terminate_agreement(
    consultant_profile=consultant,
    reason='Profesyonel davranış ihlali',
    terminated_by=admin_user
)
```

**5. Anlaşma Geçmişi**

```python
history = ConsultantBlockchainService.get_agreement_history(consultant)

# Tüm blockchain işlemlerini görüntüle
for entry in history:
    print(f"{entry['type']}: {entry['transaction_hash']}")
```

## 📋 Admin Panel Kullanımı

### 1. Belge Doğrulama

Admin panelde `ConsultantProfile` listesinde:

1. Mali müşaviri seç
2. **"Seçili mali müşavirlerin belgelerini doğrula"** action'ını seç
3. Belgeler otomatik doğrulanır

### 2. Mali Müşavir Onaylama (Blockchain ile)

1. Belgeleri doğrulanmış mali müşaviri seç
2. **"Seçili mali müşavirleri onayla ve blockchain anlaşması yap"** action'ını seç
3. Sistem:
   - Mali müşaviri onaylar
   - Blockchain smart contract oluşturur
   - Transaction kaydı yapar
   - ConsultantProfile'a blockchain bilgilerini kaydeder

### Başarılı Onay Mesajı

```
Ali Yılmaz SMMM: Onaylandı ve blockchain anlaşması oluşturuldu.
Contract: 0x1a2b3c4d5e6f...
```

## 🔐 Güvenlik ve Şeffaflık

### Blockchain'in Avantajları

1. **Değiştirilemezlik**: Anlaşma sonradan değiştirilemez
2. **Şeffaflık**: Tüm taraflar anlaşmayı görebilir
3. **Kanıt**: Hukuki süreçlerde kanıt olarak kullanılabilir
4. **Zaman Damgası**: Her değişiklik tarihli
5. **Denetlenebilirlik**: Tüm işlemler izlenebilir

### Anlaşma Doğrulama

Herhangi bir zamanda anlaşmanın geçerliliği kontrol edilebilir:

```python
result = verify_agreement(consultant)

if result['valid']:
    print(f"✅ Anlaşma geçerli")
    print(f"Block: #{result['block_number']}")
    print(f"Hash: {result['contract'].contract_hash}")
else:
    print(f"❌ Geçersiz: {result['error']}")
```

## 🚀 API Güncellemeleri

### Kayıt Endpoint'i (POST)

```python
POST /advisors/marketplace/api/consultants/

# Body (multipart/form-data)
{
    "display_name": "Ahmet Yılmaz SMMM",
    "bio": "15 yıllık deneyim...",
    "city": "İstanbul",
    "phone": "05321234567",
    "hourly_rate": 750.00,
    # ... diğer alanlar

    # ZORUNLU BELGELER
    "diploma_document": <file>,
    "graduation_document": <file>
}

# Başarılı Response
{
    "id": 123,
    "display_name": "Ahmet Yılmaz SMMM",
    "approval_status": "pending",
    "diploma_verified": false,
    "graduation_verified": false,
    ...
}
```

### Belge Kontrolü

```python
GET /advisors/marketplace/api/consultants/{id}/

# Response
{
    ...
    "diploma_verified": true,
    "graduation_verified": true,
    "blockchain_contract_address": "0x1a2b3c...",
    "blockchain_transaction_hash": "0x9f8e7d...",
    "blockchain_contract_created_at": "2025-11-14T10:30:00Z"
}
```

## 📊 İş Akışı Diyagramı

```
┌─────────────────────────────────────────────────────────┐
│  MALI MÜŞAVİR KAYIT VE ONAY SÜRECİ                     │
└─────────────────────────────────────────────────────────┘

1. KAYIT
   ├─ Profil bilgileri girişi
   ├─ Diploma yükleme (ZORUNLU)
   └─ Mezuniyet belgesi yükleme (ZORUNLU)

2. BEKLEME
   ├─ approval_status: 'pending'
   ├─ diploma_verified: False
   └─ graduation_verified: False

3. ADMIN İNCELEME
   ├─ Belgeleri görüntüle
   ├─ Doğrula (verify_documents action)
   ├─ diploma_verified: True
   └─ graduation_verified: True

4. ADMIN ONAY
   ├─ Onayla (approve_consultants action)
   ├─ approval_status: 'approved'
   └─ BLOCKCHAIN ANLAŞMASI OLUŞTUR
       ├─ Smart Contract deploy
       ├─ Transaction oluştur
       ├─ Block'a ekle
       └─ Hash'leri kaydet

5. AKTİF
   ├─ blockchain_contract_address: Set
   ├─ blockchain_transaction_hash: Set
   ├─ is_available(): True
   └─ Randevu almaya hazır!
```

## 🧪 Test Senaryoları

### Test 1: Belge Yükleme Kontrolü

```python
# Belge olmadan kayıt deneyin
serializer = ConsultantProfileCreateSerializer(data={
    'display_name': 'Test',
    # diploma_document YOK
    # graduation_document YOK
})

# Beklenen sonuç: ValidationError
assert not serializer.is_valid()
assert 'diploma_document' in serializer.errors
assert 'graduation_document' in serializer.errors
```

### Test 2: Blockchain Anlaşma Oluşturma

```python
from advisors.services.blockchain_service import create_agreement_on_approval

consultant = ConsultantProfile.objects.get(id=1)
admin = User.objects.get(username='admin')

# Anlaşma oluştur
result = create_agreement_on_approval(consultant, admin)

# Kontroller
assert result['contract_address']
assert result['transaction_hash']
assert consultant.blockchain_contract_address
```

### Test 3: is_available() Kontrolü

```python
consultant = ConsultantProfile.objects.create(...)

# Başlangıçta müsait değil
assert not consultant.is_available()

# Belgeleri doğrula
consultant.diploma_verified = True
consultant.graduation_verified = True

# Hala müsait değil (onay yok)
assert not consultant.is_available()

# Onayla ve blockchain oluştur
consultant.approval_status = 'approved'
create_agreement_on_approval(consultant, admin)

# Şimdi müsait!
assert consultant.is_available()
```

## 📝 Migration

```bash
# Migration oluştur
python manage.py makemigrations advisors

# Migration çıktısı:
# - Add field diploma_document to consultantprofile
# - Add field graduation_document to consultantprofile
# - Add field diploma_verified to consultantprofile
# - Add field graduation_verified to consultantprofile
# - Add field documents_verified_at to consultantprofile
# - Add field documents_verified_by to consultantprofile
# - Add field blockchain_contract_address to consultantprofile
# - Add field blockchain_transaction_hash to consultantprofile
# - Add field blockchain_contract_created_at to consultantprofile
# - Add field blockchain_contract_terms to consultantprofile

# Migrate
python manage.py migrate advisors
```

## 🎯 Sonuç

✅ Mali müşavirler diploma ve mezuniyet belgesi olmadan kayıt olamaz  
✅ Belgeler admin tarafından doğrulanmalı  
✅ Onay verildiğinde otomatik blockchain anlaşması oluşur  
✅ Anlaşma değiştirilemez ve şeffaftır  
✅ Tüm işlemler blockchain'de kayıtlıdır  
✅ Hukuki güvence sağlanmıştır

**Sistem artık hem güvenli, hem şeffaf, hem de tamamen otomatik!** 🎉

---

**Oluşturulma:** 14 Kasım 2025  
**Versiyon:** 1.1.0  
**Güncelleme:** Zorunlu Belge ve Blockchain Entegrasyonu
