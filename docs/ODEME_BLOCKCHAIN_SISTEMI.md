# Ödeme ve Blockchain Sözleşme Sistemi

## 📋 Genel Bakış

FinAsis platformunda, 10.000₺ ve üzeri abonelikler ile beta üyelikler için otomatik blockchain sözleşme oluşturma sistemi entegre edilmiştir. Ödeme onaylandığında otomatik olarak:

1. Blockchain sözleşmesi oluşturulur (10.000₺+ veya beta üye ise)
2. Kullanıcıya bildirim gönderilir
3. E-posta ile fatura, kullanıcı bilgileri ve sözleşme gönderilir

## 🔗 Blockchain Sözleşme Oluşturma

### Koşullar

Blockchain sözleşmesi aşağıdaki durumlarda otomatik oluşturulur:

1. **10.000₺ ve üzeri abonelikler**: Aylık veya yıllık fiyat 10.000₺ veya üzeri ise
2. **Beta üyelikler**: Plan `is_beta_plan=True` ise

### Sözleşme İçeriği

Sözleşme aşağıdaki bilgileri içerir:

- Abonelik bilgileri (plan, kullanıcı, tarihler)
- Fiyatlandırma detayları
- Beta üyelik avantajları (varsa)
- Ortaklık şartları (beta üyeler için)
- Yasal hükümler

### Kullanım

```python
from billing.services.blockchain_contract import SubscriptionBlockchainService

# Sözleşme oluştur
contract_result = SubscriptionBlockchainService.create_subscription_contract(
    subscription_profile,
    transaction=transaction  # Opsiyonel
)

if contract_result:
    contract = contract_result["contract"]
    contract_address = contract_result["contract_address"]
```

## 📧 Otomatik Bildirim ve E-posta Sistemi

### Ödeme Onayı

Ödeme onaylandığında (`Transaction.status = "completed"`):

1. **Bildirim**: Kullanıcıya platform içi bildirim gönderilir
2. **E-posta**: Ödeme onayı e-postası gönderilir
3. **Fatura**: Fatura e-postası gönderilir (varsa)
4. **Sözleşme**: Blockchain sözleşme bildirimi gönderilir (varsa)

### E-posta Şablonları

- `billing/templates/billing/emails/payment_confirmation.html` - Ödeme onayı
- `billing/templates/billing/emails/contract_created.html` - Sözleşme oluşturuldu
- `billing/templates/billing/emails/invoice.html` - Fatura

### Kullanım

```python
from billing.services.notification_service import BillingNotificationService

# Ödeme onayı bildirimi
BillingNotificationService.send_payment_confirmation(
    subscription_profile,
    transaction,
    invoice  # Opsiyonel
)

# Sözleşme bildirimi
BillingNotificationService.send_contract_notification(
    user,
    contract
)

# Fatura e-postası
BillingNotificationService.send_invoice_email(
    user,
    invoice
)
```

## 🔄 Signal Handlers

### Transaction Signal

`billing/signals.py` içinde `Transaction` modeli için signal handler:

```python
@receiver(post_save, sender=Transaction)
def handle_payment_confirmation(sender, instance, created, **kwargs):
    # Ödeme onaylandığında otomatik çalışır
    # - Blockchain sözleşme oluşturur
    # - Bildirim gönderir
    # - E-posta gönderir
```

### Invoice Signal

Fatura oluşturulduğunda otomatik e-posta gönderilir:

```python
@receiver(post_save, sender=Invoice)
def handle_invoice_created(sender, instance, created, **kwargs):
    # Fatura oluşturulduğunda otomatik e-posta gönderir
```

## 🎯 Beta Üyelik ve Ortaklık

### Beta Üyelik Özellikleri

Beta planlar (`Plan.is_beta_plan = True`) için:

- Erken özellik erişimi
- Öncelikli destek
- Beta indirimleri
- Ortaklık fırsatları

### Ortaklık Süreçleri

Beta üyeler otomatik olarak ortak sayılır ve şu avantajlara sahiptir:

- Gelir paylaşımı (enterprise planlar için)
- Referans bonusu (%10 komisyon)
- Ortak pazarlama fırsatları

## 📝 FinQuest Game URL Yönlendirmesi

`/finquest/game/` URL'si için yönlendirme eklendi. Oyun geliştirme aşamasında olduğu için kullanıcılar diğer oyunlara yönlendirilir.

```python
# games/finquest/views.py
def game_redirect(request):
    """FinQuest game URL yönlendirmesi"""
    messages.info(request, "FinQuest 3D oyunu şu anda geliştirme aşamasındadır...")
    return redirect("game_app:games")
```

## 🚀 Kurulum ve Yapılandırma

### Gereksinimler

- `blockchain` app yüklü olmalı
- `accounts` app yüklü olmalı (UserNotification için)
- E-posta ayarları yapılandırılmalı

### Ayarlar

`settings.py` içinde:

```python
# E-posta ayarları
DEFAULT_FROM_EMAIL = "noreply@finasis.com.tr"
SUPPORT_EMAIL = "destek@finasis.com.tr"
SITE_URL = "https://finasis.com.tr"
```

## 📊 İstatistikler ve Takip

### Blockchain Sözleşmeleri

Kullanıcının tüm sözleşmelerini görüntüleme:

```python
from billing.services.blockchain_contract import SubscriptionBlockchainService

contracts = SubscriptionBlockchainService.get_user_contracts(user)
```

### Sözleşme Doğrulama

```python
is_verified = SubscriptionBlockchainService.verify_contract(subscription_profile)
```

## 🔒 Güvenlik

- Tüm sözleşmeler blockchain'de değiştirilemez şekilde saklanır
- Sözleşme adresleri SHA-256 hash ile oluşturulur
- Kullanıcı bilgileri şifrelenmiş olarak saklanır

## 📞 Destek

Sorularınız için:
- E-posta: destek@finasis.com.tr
- Dokümantasyon: `/docs/ODEME_BLOCKCHAIN_SISTEMI.md`

