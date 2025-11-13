# 🔗 FinAsis Blockchain Modülü - Kapsamlı Kullanım Rehberi

## 📋 İçindekiler

1. [Giriş](#giriş)
2. [Temel Kavramlar](#temel-kavramlar)
3. [Kurulum ve Başlangıç](#kurulum-ve-başlangıç)
4. [Sistem Özellikleri](#sistem-özellikleri)
5. [Kullanım Senaryoları](#kullanım-senaryoları)
6. [API Referansı](#api-referansı)
7. [Güvenlik ve Best Practices](#güvenlik-ve-best-practices)
8. [Sorun Giderme](#sorun-giderme)

---

## 🎯 Giriş

FinAsis Blockchain Modülü, muhasebe ve finans kayıtlarınızın **değişmezliğini, şeffaflığını ve izlenebilirliğini** garanti altına alan enterprise-grade bir blockchain çözümüdür.

### ✨ Neden Blockchain?

- ✅ **Veri Bütünlüğü**: Kayıtlar değiştirilemez, her işlem kalıcı olarak saklanır
- ✅ **Şeffaflık**: Tüm işlemler izlenebilir ve denetlenebilir
- ✅ **Güvenlik**: Kriptografik hash'ler ile korunan veriler
- ✅ **Uyumluluk**: Mali denetim ve yasal gereklilikler için tam kayıt
- ✅ **Otomasyon**: Akıllı sözleşmeler ile otomatik iş süreçleri

---

## 📚 Temel Kavramlar

### 1. Block (Blok)

Blockchain'in temel yapı taşıdır. Her blok şunları içerir:

```
Blok Yapısı:
├─ Block Number (Blok Numarası): 0, 1, 2, ...
├─ Previous Hash (Önceki Bloğun Hash'i)
├─ Block Hash (Bu Bloğun Hash'i)
├─ Transactions (İçerdiği Transaction'lar)
├─ Merkle Root (Transaction'ların özeti)
├─ Timestamp (Oluşturulma zamanı)
├─ Nonce (Mining için kullanılan sayı)
└─ Difficulty (Mining zorluğu)
```

**Örnek:**
```
Block #12
Hash: 0000a1b2c3d4e5f6...
Previous Hash: 0000f9e8d7c6b5a4...
Transactions: 15
Mined by: admin@finasis.com
```

### 2. Transaction (İşlem)

Blockchain üzerinde kaydedilen her finansal veya operasyonel işlemdir.

**Transaction Tipleri:**
- 📄 `invoice` - Fatura kayıtları
- 💰 `payment` - Ödeme işlemleri
- 💸 `expense` - Gider kayıtları
- 📝 `voucher` - Muhasebe fişleri
- 📜 `contract` - Akıllı sözleşme işlemleri
- 🎁 `asset_transfer` - Dijital varlık transferleri
- 🔍 `audit` - Denetim kayıtları
- 📊 `edefter` - E-Defter kayıtları

**Transaction Durumları:**
- ⏳ `pending` - Beklemede (henüz bloğa eklenmedi)
- ✅ `confirmed` - Onaylandı (bloğa eklendi)
- ❌ `failed` - Başarısız
- 🚫 `cancelled` - İptal edildi

### 3. Smart Contract (Akıllı Sözleşme)

Otomatik çalışan, şartlara bağlı iş kurallarıdır.

**Sözleşme Tipleri:**
- `invoice_auto` - Otomatik faturalama
- `payment_schedule` - Ödeme planı
- `multi_signature` - Çoklu imza gerektiren işlemler
- `escrow` - Emanet hesap yönetimi
- `subscription` - Abonelik yönetimi

### 4. Digital Asset (Dijital Varlık)

Blockchain üzerinde token'ize edilmiş değerlerdir.

**Varlık Tipleri:**
- `utility` - Kullanım token'ları
- `security` - Menkul kıymet token'ları
- `nft` - Benzersiz dijital varlıklar
- `currency` - Para birimi token'ları
- `governance` - Yönetim token'ları

---

## ⚙️ Kurulum ve Başlangıç

### 1. Migration İşlemleri

```bash
# Blockchain modülü migration'larını oluştur
python manage.py makemigrations blockchain

# Migration'ları uygula
python manage.py migrate blockchain

# Tüm migration'ları kontrol et
python manage.py showmigrations blockchain
```

### 2. İlk Genesis Bloğu Oluşturma

```python
# Django shell'de
python manage.py shell

from src.apps.blockchain.services import BlockchainManager

# Genesis bloğu oluştur
genesis = BlockchainManager.create_genesis_block()
print(f"Genesis Block #{genesis.block_number} oluşturuldu!")
```

### 3. Super Admin Erişimi

```
URL: http://127.0.0.1:8000/yonetim/modules/blockchain/
```

Blockchain modülüne super admin panelinden erişebilirsiniz.

---

## 🚀 Sistem Özellikleri

### 1. Blockchain Dashboard

**Erişim:** `/blockchain/`

**Özellikler:**
- 📊 Anlık istatistikler (blok sayısı, transaction sayısı)
- 📈 Son 7 günlük transaction grafiği
- 🔗 Son bloklar listesi
- 💼 Son transaction'lar
- ✅ Zincir sağlığı kontrolü

### 2. Block Explorer

**Erişim:** `/blockchain/blocks/`

**Özellikler:**
- 🔍 Blok arama (numara veya hash ile)
- 📋 Tüm blokları listeleme
- 🔗 Blok detayları görüntüleme
- ⛏️ Yeni blok mining (oluşturma)

**Blok Detayı:**
```
/blockchain/blocks/12/
```
- Blok bilgileri
- İçerdiği transaction'lar
- Hash doğrulama
- Previous ve next blok bağlantıları

### 3. Transaction Yönetimi

**Erişim:** `/blockchain/transactions/`

**Özellikler:**
- 📝 Yeni transaction oluşturma
- 🔍 Transaction arama ve filtreleme
- 📊 Transaction tiplerine göre gruplama
- 💳 Transaction detayları ve doğrulama

**Transaction Oluşturma:**
```python
from src.apps.blockchain.services import TransactionManager

tx = TransactionManager.create_transaction(
    transaction_type='invoice',
    from_address='company:123',
    to_address='customer:456',
    amount=1500.00,
    payload={
        'invoice_number': 'INV-2024-001',
        'issue_date': '2024-01-15',
        'due_date': '2024-02-15'
    },
    created_by=request.user
)
```

### 4. Smart Contract Sistemi

**Erişim:** `/blockchain/contracts/`

**Contract Deploy Etme:**
```python
from src.apps.blockchain.services import SmartContractManager

contract = SmartContractManager.deploy_contract(
    contract_name='Aylık Fatura Otomasyonu',
    contract_type='invoice_auto',
    code='''
    {
        "trigger": "monthly",
        "day": 1,
        "action": "create_invoice",
        "amount": 1000,
        "customer_id": 123
    }
    ''',
    deployed_by=request.user,
    parameters={'frequency': 'monthly'}
)
```

**Contract Çalıştırma:**
```python
result = SmartContractManager.execute_contract(
    contract_address='a1b2c3d4...',
    execution_params={'month': '2024-01'}
)
```

### 5. Digital Asset Yönetimi

**Asset Oluşturma:**
```python
from src.apps.blockchain.services import AssetManager

asset = AssetManager.create_asset(
    asset_name='FinAsis Loyalty Points',
    asset_symbol='FASLP',
    asset_type='utility',
    total_supply=1000000,
    owner=request.user,
    metadata={
        'description': 'FinAsis sadakat puanları',
        'icon_url': '/static/assets/faslp.png'
    }
)
```

**Asset Transfer:**
```python
success, message = AssetManager.transfer_asset(
    asset=asset,
    from_user=sender_user,
    to_user=receiver_user,
    amount=100,
    created_by=request.user
)
```

---

## 💼 Kullanım Senaryoları

### Senaryo 1: Fatura Blockchain'e Kaydetme

```python
# signals.py içinde otomatik
from src.apps.blockchain.services import TransactionManager, payload_for_invoice

def save_invoice_to_blockchain(invoice):
    payload_str = payload_for_invoice(invoice)
    
    tx = TransactionManager.create_transaction(
        transaction_type='invoice',
        from_address=f"company:{invoice.company_id}",
        to_address=f"customer:{invoice.customer_id}",
        amount=invoice.total_amount,
        payload={
            'invoice_number': invoice.invoice_number,
            'payload_preview': payload_str[:200]
        },
        reference_model='invoice',
        reference_id=invoice.id
    )
    
    return tx
```

### Senaryo 2: Ödeme Doğrulama

```python
from src.apps.blockchain.services import TransactionManager

# Transaction doğrula
is_valid, message = TransactionManager.verify_transaction(
    transaction_id='abc123...'
)

if is_valid:
    print("✅ Ödeme blockchain'de doğrulandı!")
else:
    print(f"❌ Doğrulama hatası: {message}")
```

### Senaryo 3: Otomatik Ödeme Planı

```python
# Akıllı sözleşme ile aylık otomatik ödemeler
contract = SmartContractManager.deploy_contract(
    contract_name='Kiralama Ödeme Planı',
    contract_type='payment_schedule',
    code=json.dumps({
        'schedule': [
            {'day': 1, 'month': 'every', 'amount': 5000},
        ],
        'duration_months': 12
    }),
    deployed_by=tenant_user
)
```

### Senaryo 4: Çoklu İmza Onayı

```python
# Büyük tutarlı işlemlerde çoklu onay
contract = SmartContractManager.deploy_contract(
    contract_name='Yatırım Onayı',
    contract_type='multi_signature',
    code=json.dumps({
        'required_signatures': 3,
        'signers': ['ceo@company.com', 'cfo@company.com', 'coo@company.com'],
        'threshold_amount': 100000
    }),
    deployed_by=admin_user
)
```

---

## 📡 API Referansı

### REST API Endpoints

#### 1. Transaction Doğrulama (POST)
```
POST /blockchain/api/verify/
Content-Type: application/x-www-form-urlencoded

reference=invoice:123
payload=INVOICE|123|INV-001|2024-01-15|1500.00
```

**Response:**
```json
{
    "reference": "invoice:123",
    "hash_hex": "a1b2c3...",
    "verified": true
}
```

#### 2. Hash ile Doğrulama (POST)
```
POST /blockchain/api/verify-hash/
Content-Type: application/x-www-form-urlencoded

hash_hex=a1b2c3d4e5f6...
reference=invoice:123 (optional)
```

#### 3. Kayıt Oluşturma (POST)
```
POST /blockchain/api/anchor/
Content-Type: application/x-www-form-urlencoded

reference=invoice:123
hash_hex=a1b2c3d4...
status=anchored
```

### Python Service API

#### BlockchainManager

```python
from src.apps.blockchain.services import BlockchainManager

# Son bloğu al
latest_block = BlockchainManager.get_latest_block()

# Yeni blok oluştur
new_block = BlockchainManager.create_new_block(
    transactions=[tx1, tx2, tx3],
    mined_by=user,
    difficulty=4
)

# Zinciri doğrula
is_valid, errors = BlockchainManager.verify_chain()
```

#### TransactionManager

```python
from src.apps.blockchain.services import TransactionManager

# Transaction oluştur
tx = TransactionManager.create_transaction(
    transaction_type='payment',
    from_address='company:1',
    to_address='vendor:5',
    amount=2500.00,
    payload={'invoice_ref': 'INV-001'},
    created_by=user
)

# Transaction doğrula
is_valid, msg = TransactionManager.verify_transaction(tx.transaction_id)
```

---

## 🔒 Güvenlik ve Best Practices

### 1. Hash Güvenliği

✅ **YAPIN:**
- SHA-256 kullanın (256-bit güvenlik)
- Deterministik payload'lar oluşturun
- Payload'ları sort_keys=True ile JSON'a çevirin

❌ **YAPMAYIN:**
- MD5 veya SHA-1 kullanmayın (güvensiz)
- Rastgele veri eklemeyin (doğrulama başarısız olur)
- Timestamp veya random değerler eklemeyin

### 2. Transaction Güvenliği

✅ **YAPIN:**
- Her transaction'a benzersiz ID atayın
- Payload hash'ini ayrıca saklayın
- Gas fee hesaplayın
- Signature ekleyin (dijital imza)

### 3. Smart Contract Güvenliği

✅ **YAPIN:**
- Contract kodunu denetleyin
- Execution sayısını limitleyın
- Timeout mekanizması ekleyin
- Error handling yapın

❌ **YAPMAYIN:**
- Güvenilmeyen kaynaklardancode çalıştırmayın
- Sınırsız loop'lara izin vermeyin

### 4. Access Control

```python
# View'lerde her zaman login_required kullanın
@login_required
def sensitive_blockchain_operation(request):
    # Sadece authorized kullanıcılar
    if not request.user.has_perm('blockchain.add_transaction'):
        return HttpResponseForbidden()
    
    # İşlem...
```

---

## 🛠️ Sorun Giderme

### Problem 1: Migration Hatası

**Hata:**
```
django.db.utils.IntegrityError: UNIQUE constraint failed
```

**Çözüm:**
```bash
# Migration'ları sıfırla
python manage.py migrate blockchain zero

# Tekrar uygula
python manage.py migrate blockchain
```

### Problem 2: Hash Uyumsuzluğu

**Hata:**
```
Hash mismatch: calculated != stored
```

**Çözüm:**
```python
# Bloğu yeniden hesapla
block = Block.objects.get(block_number=X)
block.block_hash = block.calculate_hash()
block.save()
```

### Problem 3: Zincir Bozulması

**Kontrol:**
```python
is_valid, errors = BlockchainManager.verify_chain()
if not is_valid:
    for error in errors:
        print(f"❌ {error}")
```

**Çözüm:**
- Bozuk bloğu tespit edin
- O bloktan sonraki tüm blokları yeniden mine edin
- Previous hash'leri düzeltin

### Problem 4: Transaction Pending Kalıyor

**Çözüm:**
```python
# Manuel olarak blok oluştur
block = BlockchainManager.create_new_block(difficulty=2)
print(f"✅ {block.transactions_count} transaction confirmed")
```

---

## 📊 Performans İpuçları

### 1. Database Indexleme

```python
# models.py'de zaten ekli:
class Meta:
    indexes = [
        models.Index(fields=['transaction_type', 'status']),
        models.Index(fields=['timestamp']),
    ]
```

### 2. Query Optimization

```python
# ❌ Kötü
transactions = Transaction.objects.all()
for tx in transactions:
    print(tx.block.block_number)  # N+1 problem!

# ✅ İyi
transactions = Transaction.objects.select_related('block').all()
for tx in transactions:
    print(tx.block.block_number)  # Tek query!
```

### 3. Mining Difficulty

- Test için: `difficulty=2` (hızlı)
- Production için: `difficulty=4` (güvenli)
- Enterprise için: `difficulty=6` (çok güvenli)

---

## 📞 Destek ve Yardım

### Dokümantasyon

- **Modül README:** `/src/apps/blockchain/README.md`
- **Bu Rehber:** `/src/apps/blockchain/BLOCKCHAIN_GUIDE_TR.md`
- **Admin Panel:** `/yonetim/modules/blockchain/`

### Topluluk

- **FinAsis Destek:** support@finasis.local
- **GitHub Issues:** [FinAsis/issues](https://github.com/finasis/issues)

---

## 🎓 Sonuç

FinAsis Blockchain Modülü ile:

✅ Tüm finansal kayıtlarınız blockchain güvencesinde
✅ Otomatik akıllı sözleşmelerle iş süreçlerinizi hızlandırın
✅ Dijital varlıklarınızı güvenle yönetin
✅ Denetim ve uyumluluk gereksinimlerinizi karşılayın

**Başarılı Kullanımlar!** 🚀

---

*Son Güncelleme: 2 Kasım 2025*
*Versiyon: 2.0 (Enterprise Edition)*

