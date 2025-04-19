# FinAsis Finansal Eğitim Oyunları

Bu belge, FinAsis projesi içindeki finansal eğitim ve muhasebe öğretici oyunlarının tanıtımını, kurulumunu ve nasıl kullanılacağını açıklar.

## Oyun Modülleri

Projede yer alan oyun modülleri:

1. **Finans Öğretici** (3D Eğitim Dünyası)
   - Yaş gruplarına göre uyarlanmış finansal öğretici oyun
   - 3D ortamda interaktif finansal eğitim
   - Karakter seçimi ve görev sistemi
   - Dosya: `apps/games/ursina_game/finans_ogretici.py`

2. **Ticaretin İzinde** (2D Ticaret Simülasyonu)
   - Basit 2D ticaret ve işletme simülasyonu
   - Alım-satım, stok yönetimi ve kâr/zarar hesaplama
   - Muhasebe ve finans prensiplerini pratik yapma
   - Dosya: `apps/games/game_app/game.py`

3. **Ticaretin İzinde AR** (Artırılmış Gerçeklik Versiyonu)
   - Artırılmış gerçeklik ile finansal eğitim
   - Kamera üzerinden işaretçi tanıma sistemi
   - Gerçek dünya ile entegre finansal simülasyon
   - Dosya: `apps/games/game_app/ar_trade_trail.py`

4. **Piyasa Simülasyonu** (Menkul Kıymet Ticaret Simülasyonu)
   - Borsada hisse senedi alım-satım simülasyonu
   - Portföy yönetimi ve çeşitlendirme
   - Risk/getiri konseptlerini öğrenme
   - Dosya: `apps/games/ursina_game/game.py`

## Kurulum ve Çalıştırma

### Gereksinimler

Tüm gerekli paketleri tek seferde yüklemek için:

```bash
pip install -r requirements_for_games.txt
```

### Oyunları Çalıştırma

#### Finans Öğretici (3D)

```bash
cd apps/games/ursina_game
python finans_ogretici.py
```

#### Ticaretin İzinde (2D)

```bash
cd apps/games/game_app
python game.py
```

#### Ticaretin İzinde AR 

*Not: Bu oyun için bilgisayarınızda çalışan bir kamera gereklidir.*

```bash
cd apps/games/game_app
python ar_trade_trail.py
```

#### Piyasa Simülasyonu

```bash
cd apps/games/ursina_game
python game.py
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