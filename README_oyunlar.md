# FinAsis Eğitim Platformu Oyunları

## Oyun Modülleri

1. **TradeSim** (Çok Oyunculu 3D Ticaret Simülasyonu)
   - Gerçek zamanlı çok oyunculu ticaret deneyimi
   - Sınıf modu ve serbest oyun modu
   - Öğretmen kontrol paneli
   - Dosya: `games/trade_sim/game.py`

2. **FinAsis Editor** (Eğitim İçeriği Oluşturma Aracı)
   - Sürükle-bırak arayüzü
   - Hazır şablonlar ve bileşenler
   - Özel görev ve senaryo oluşturma
   - Dosya: `editor/main.py`

3. **Marketplace** (İçerik Paylaşım Platformu)
   - Oyun/görev paylaşımı ve indirme
   - Puanlama ve yorum sistemi
   - İçerik moderasyonu
   - Sanal para birimi "FinCoin" ile alışveriş
   - İçerik oluşturuculara gelir modeli
   - Dosya: `marketplace/app.py`

4. **Öğretmen Kontrol Paneli**
   - Canlı sınıf yönetimi
   - Öğrenci ilerleme takibi
   - Anlık görev atamaları
   - Başarı rozetleri dağıtma
   - Dosya: `teacher/dashboard.py`

## Kurulum ve Çalıştırma

### Gereksinimler

Tüm gerekli paketleri tek seferde yüklemek için:

```bash
pip install -r requirements_for_games.txt
```

### Oyunları Çalıştırma

#### TradeSim (Çok Oyunculu 3D)

```bash
cd games/trade_sim
python game.py
```

#### FinAsis Editor

```bash
cd editor
python main.py
```

#### Marketplace

```bash
cd marketplace
python app.py
```

## Yaş Grubu Filtreleme

Oyunlar farklı yaş gruplarına göre içerikleri otomatik olarak uyarlamaktadır:

- **Çocuk (5-12)**: Temel para, tasarruf ve bütçe konseptleri
- **Genç (13-18)**: Bütçe planlama, tasarruf ve temel yatırım
- **Yetişkin (19-65)**: Borsa, yatırım, işletme finansmanı ve vergi
- **Yaşlı (65+)**: Emeklilik planlaması ve servet yönetimi

## Mobil ve Masaüstü Dağıtım

### Android APK Oluşturma

*Not: Bu işlem için buildozer kurulu olmalıdır.*

```bash
cd apps/games
buildozer android debug
```

Oluşturulan APK dosyasını `bin/` dizininde bulabilirsiniz.

### Masaüstü Uygulaması Oluşturma

```bash
python build_desktop.py
```

Bu işlem her oyun için çalıştırılabilir dosyalar oluşturacaktır.

## Sorun Giderme

- **OpenCV Hataları**: Kamera erişimi sorunlarında, `cv2.CAP_DSHOW` parametresini kullanmayı deneyin.
- **Ursina Hataları**: DirectX/OpenGL sorunu yaşarsanız, `ursina.application.development_mode = False` satırını ekleyin.
- **Pygame Display Hataları**: SDL ilişkili hatalarda pygame'i yeniden kurmayı deneyin.

## Eğitim İçeriği Güncelleme

Oyunlardaki eğitim içerikleri, aşağıdaki dosyalarda JSON formatında saklanmaktadır:

- `data/education_tips.json`
- `data/financial_concepts.json`
- `data/accounting_notes.json`

Bu dosyaları düzenleyerek eğitim içeriğini değiştirebilir ve genişletebilirsiniz.

## Katkıda Bulunma

Oyunlara katkıda bulunmak için:

1. Yeni görevler, senaryolar veya öğretici ipuçları ekleyebilirsiniz.
2. Grafikleri, ses efektlerini veya kullanıcı arayüzünü geliştirebilirsiniz.
3. Yeni yaş grupları veya eğitim seviyelerine göre içerik özelleştirebilirsiniz.

## Lisans

Bu oyunlar MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## Özellikler

### FinCoin Ekonomisi
- İçerik oluşturarak FinCoin kazanma
- Marketplace'de alışveriş
- Başarı rozetleri ile bonus kazanma

### Multiplayer Özellikleri
- 32 kişiye kadar eş zamanlı oyun
- Sesli sohbet desteği
- Ekip oluşturma sistemi
- Canlı ticaret görünümü