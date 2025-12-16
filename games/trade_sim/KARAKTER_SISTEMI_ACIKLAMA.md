# TradeSim Karakter Sistemi Açıklaması

## 📋 Karakter Modeli (Character Model)

Karakter, TradeSim oyununda her kullanıcının oyun içi temsilcisidir. Her kullanıcının bir karakteri vardır.

### Karakter Özellikleri:

```python
class Character(models.Model):
    user = ForeignKey(User)           # Hangi kullanıcıya ait
    name = CharField                  # Karakter adı (örn: "Ahmet Trader")
    city = ForeignKey(City)           # Hangi şehirde bulunuyor
    skills = JSONField                # Yetenekler: {'ticaret': 1, 'pazarlık': 2}
    story_state = JSONField           # Hikaye durumu: {'ana_gorev': 'basladi'}
    choices = JSONField               # Seçimler ve envanter: {'inventory': {...}}
    score = IntegerField              # Para (coin) miktarı
    level = IntegerField              # Seviye (1'den başlar)
```

## 🔄 Karakter Oluşturma Algoritması

### 1. Otomatik Oluşturma (Signal ile)

**Dosya:** `models.py` (satır 234-248)

```python
@receiver(post_save, sender=get_user_model())
def create_default_character_for_user(sender, instance, created, **kwargs):
    # Yeni kullanıcı oluşturulduğunda otomatik çalışır
    if not created:
        return

    # İlk şehri seç
    default_city = City.objects.order_by("id").first()

    # Karakter oluştur
    Character.objects.create(
        user=instance,
        name=f"{username} Trader",  # "Ahmet Trader" gibi
        city=default_city,           # İlk şehre atanır
        skills={},                    # Boş yetenekler
        story_state={},               # Boş hikaye durumu
        choices={},                   # Boş seçimler/envanter
    )
```

**Ne zaman çalışır?**

- Yeni bir kullanıcı kayıt olduğunda
- Django'nun `post_save` sinyali tetiklenir
- Otomatik olarak karakter oluşturulur

### 2. Manuel Oluşturma (API ile)

**Dosya:** `views.py` - `guest_onboarding()` ve `onboarding()` fonksiyonları

```python
# Eğer karakter yoksa oluştur
character = Character.objects.filter(user=user).first()
if character is None:
    default_city = City.objects.order_by("id").first()
    character = Character.objects.create(
        user=user,
        name=f"{user.username} Trader",
        city=default_city
    )
```

**Ne zaman çalışır?**

- Misafir kullanıcı oyuna başladığında (`guest_onboarding`)
- Giriş yapmış kullanıcı oyuna başladığında (`onboarding`)
- Karakter yoksa güvenlik kontrolü olarak oluşturulur

## 💰 Para (Score) Sistemi

### Başlangıç Parası

**Dosya:** `setup_tradesim.py` (satır 274-283)

```python
# Tüm karakterlere 10,000 lira başlangıç parası ver
characters = Character.objects.all()
characters.update(score=10000)
```

### Para Kullanımı

**Alışveriş:**

```python
# Ürün satın alma
total_cost = amount * price
if character.score < total_cost:
    return error("Yeterli paranız yok!")
character.score -= int(total_cost)
```

**Satış:**

```python
# Ürün satma
total_gain = amount * price
character.score += int(total_gain)
```

## 🎒 Envanter (Inventory) Sistemi

Envanter, karakterin `choices` JSONField'ında saklanır:

```python
# Envanter yapısı
character.choices = {
    "inventory": {
        "Bugday": 50,      # 50 kg buğday
        "Elma": 20,         # 20 kg elma
        "Peynir": 5         # 5 kg peynir
    },
    "badges": ["market_explorer"],  # Rozetler
    # ... diğer seçimler
}
```

### Envanter İşlemleri

**Ürün Ekleme (Satın Alma):**

```python
inventory = character.choices.get("inventory", {})
inventory[item_name] = inventory.get(item_name, 0) + amount
character.choices["inventory"] = inventory
character.save()
```

**Ürün Çıkarma (Satış):**

```python
inventory[item_name] = has_amount - amount
if inventory[item_name] <= 0:
    inventory.pop(item_name, None)  # Sıfır olursa sil
```

## 🏙️ Şehir Sistemi

### Şehir Atama

**İlk Atama:**

- Yeni karakter oluşturulduğunda ilk şehre atanır
- `City.objects.order_by("id").first()` ile ilk şehir seçilir

**Şehir Değiştirme:**

```python
# Karakterlerin şehirlere dağıtılması
cities = list(City.objects.all())
for idx, char in enumerate(characters):
    city = cities[idx % len(cities)]  # Döngüsel dağıtım
    char.city = city
    char.save()
```

**Seyahat:**

```python
# Şehir değiştirme (views.py - change_city)
travel_cost = float(req_data.get("cost", 0))
if character.score < travel_cost:
    return error("Seyahat için yeterli paranız yok!")
character.score -= int(travel_cost)
character.city = new_city
character.save()
```

## 📊 Karakter Dağıtım Algoritması

**Dosya:** `distribute_characters.py`

```python
# Karakterleri şehirlere döngüsel olarak dağıt
cities = list(City.objects.all())  # [Istanbul, Ankara, Izmir, ...]
characters = list(Character.objects.all())  # [Kar1, Kar2, Kar3, ...]

for idx, char in enumerate(characters):
    # Modulo operatörü ile döngüsel dağıtım
    city = cities[idx % len(cities)]
    # idx=0 -> Istanbul
    # idx=1 -> Ankara
    # idx=2 -> Izmir
    # idx=3 -> Istanbul (tekrar başlar)
    char.city = city
    char.save()
```

**Örnek:**

- 9 şehir, 16 karakter varsa:
  - Karakter 0-8: Şehir 0-8'e atanır
  - Karakter 9-15: Şehir 0-6'ya tekrar atanır (döngüsel)

## 🎮 Ticaret Algoritması

**Dosya:** `views.py` - `market_trade()` (satır 1034-1124)

### Alış İşlemi:

```python
1. Karakteri bul
2. Envanteri al (choices["inventory"])
3. Toplam maliyeti hesapla: total_cost = amount * price
4. Para kontrolü: character.score >= total_cost?
5. Para azalt: character.score -= total_cost
6. Envantere ekle: inventory[item_name] += amount
7. Kaydet: character.save()
```

### Satış İşlemi:

```python
1. Karakteri bul
2. Envanteri kontrol et: inventory[item_name] >= amount?
3. Toplam kazancı hesapla: total_gain = amount * price
4. Para ekle: character.score += total_gain
5. Envanterden çıkar: inventory[item_name] -= amount
6. Sıfır olursa sil: if inventory[item_name] <= 0: pop()
7. Kaydet: character.save()
```

## 🔍 Önemli Notlar

1. **Her kullanıcının tek karakteri var:**

   - `Character.objects.filter(user=user).first()` ile bulunur
   - Bir kullanıcı birden fazla karakter oluşturamaz

2. **Envanter JSONField'da:**

   - `character.choices["inventory"]` içinde saklanır
   - Dictionary formatında: `{"Ürün Adı": miktar}`

3. **Para (score) integer:**

   - Tüm para işlemleri integer'a çevrilir
   - `int(total_cost)` ve `int(total_gain)` kullanılır

4. **Şehir değiştirme maliyetli:**

   - Seyahat için para gereklidir
   - Aynı şehirdeyse hata verir

5. **Karakter otomatik oluşur:**
   - Kullanıcı kayıt olduğunda sinyal ile
   - API çağrılarında güvenlik kontrolü ile

## 📝 Örnek Kullanım Senaryosu

```
1. Kullanıcı kayıt olur
   → Signal tetiklenir
   → Karakter otomatik oluşturulur (İstanbul'a atanır)
   → Başlangıç parası: 0

2. setup_tradesim komutu çalıştırılır
   → Tüm karakterlere 10,000 lira verilir
   → Karakterler şehirlere dağıtılır

3. Kullanıcı oyuna girer
   → Karakteri bulunur
   → Envanteri: {}
   → Parası: 10,000
   → Şehri: İstanbul

4. Kullanıcı ürün satın alır
   → 50 kg Buğday, 30 lira/kg = 1,500 lira
   → Para: 10,000 - 1,500 = 8,500
   → Envanter: {"Bugday": 50}

5. Kullanıcı başka şehre gider
   → Seyahat maliyeti: 200 lira
   → Para: 8,500 - 200 = 8,300
   → Şehir: Ankara

6. Kullanıcı ürün satar
   → 50 kg Buğday, 35 lira/kg = 1,750 lira
   → Para: 8,300 + 1,750 = 10,050
   → Envanter: {} (boş)
```

## 🛠️ Yönetim Komutları

1. **Veri oluşturma:**

   ```bash
   python manage.py setup_tradesim
   ```

2. **Karakter dağıtma:**

   ```bash
   python manage.py distribute_characters
   ```

3. **Karakter kontrolü (Django shell):**
   ```python
   from games.trade_sim.models import Character
   char = Character.objects.get(user__username="ahmet")
   print(f"Para: {char.score}")
   print(f"Envanter: {char.choices.get('inventory', {})}")
   print(f"Şehir: {char.city.name}")
   ```
