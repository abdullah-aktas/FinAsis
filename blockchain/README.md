# 🔗 FinAsis Blockchain Modülü

Enterprise-grade blockchain çözümü - Finansal kayıtlarınızın değişmezliği, şeffaflığı ve izlenebilirliği için.

## 🚀 Özellikler

### ✅ Tam Blockchain Sistemi
- **Block Mining** - Proof of Work algoritması ile blok oluşturma
- **Transaction Management** - Tüm finansal işlemlerin blockchain'e kaydı
- **Smart Contracts** - Otomatik iş süreçleri ve kurallar
- **Digital Assets** - Token ve NFT oluşturma/yönetimi
- **Chain Verification** - Zincir bütünlüğü kontrolü

### 📦 6 Ana Modül

| Modül | Açıklama |
|-------|----------|
| **Block** | Blockchain blok yapısı, mining ve doğrulama |
| **Transaction** | Tüm işlem kayıtları (fatura, ödeme, gider, vb.) |
| **SmartContract** | Akıllı sözleşmeler ve otomatik çalıştırma |
| **DigitalAsset** | Token'lar ve dijital varlıklar |
| **AssetBalance** | Kullanıcı varlık bakiyeleri |
| **AuditLog** | Blockchain aktivite log'ları |

## 📊 Kullanım

### Dashboard
```
http://127.0.0.1:8000/blockchain/
```

### Explorer
```
http://127.0.0.1:8000/blockchain/blocks/
http://127.0.0.1:8000/blockchain/transactions/
```

### API
```python
# Transaction oluştur
from src.apps.blockchain.services import TransactionManager

tx = TransactionManager.create_transaction(
    transaction_type='invoice',
    from_address='company:1',
    to_address='customer:5',
    amount=1500.00,
    payload={'invoice_number': 'INV-001'}
)

# Yeni blok mine et
from src.apps.blockchain.services import BlockchainManager

block = BlockchainManager.create_new_block(difficulty=4)
print(f"Block #{block.block_number} created with {block.transactions_count} transactions")

# Zinciri doğrula
is_valid, errors = BlockchainManager.verify_chain()
```

## 🎯 Transaction Tipleri

- 📄 `invoice` - Fatura kayıtları
- 💰 `payment` - Ödeme işlemleri
- 💸 `expense` - Gider kayıtları
- 📝 `voucher` - Muhasebe fişleri
- 📜 `contract` - Akıllı sözleşme işlemleri
- 🎁 `asset_transfer` - Dijital varlık transferleri
- 🔍 `audit` - Denetim kayıtları
- 📊 `edefter` - E-Defter kayıtları

## 🔒 Güvenlik

- ✅ SHA-256 kriptografik hash
- ✅ Proof of Work (PoW) mining
- ✅ Merkle Tree doğrulama
- ✅ İmmutable kayıtlar
- ✅ Chain bütünlük kontrolü

## 📚 Dokümantasyon

Kapsamlı Türkçe rehber için:
```
/src/apps/blockchain/BLOCKCHAIN_GUIDE_TR.md
```

## 🛠️ Kurulum

```bash
# Migration'ları uygula
python manage.py migrate blockchain

# Genesis bloğu oluştur
python manage.py shell
>>> from src.apps.blockchain.services import BlockchainManager
>>> BlockchainManager.create_genesis_block()
```

## 📞 Destek

- **Admin Panel:** `/yonetim/modules/blockchain/`
- **Dashboard:** `/blockchain/`
- **Rehber:** `BLOCKCHAIN_GUIDE_TR.md`

---

**FinAsis Blockchain - Enterprise Edition v2.0**
