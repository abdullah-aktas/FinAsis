# Ticaretin İzinde 3D

FinAsis projesi içinde yer alan "Ticaretin İzinde" oyununun 3 boyutlu versiyonu. Bu oyun, finansal eğitim ve muhasebe bilgilerini eğlenceli bir şekilde öğretmek için tasarlanmıştır.

## 📋 İçindekiler

- [Oyun Hakkında](#oyun-hakkında)
- [Kurulum](#kurulum)
- [Nasıl Oynanır](#nasıl-oynanır)
- [Yaş Grubu Özelleştirmeleri](#yaş-grubu-özelleştirmeleri)
- [Karakter Türleri](#karakter-türleri)
- [Görevler](#görevler)
- [Finansal İpuçları](#finansal-i̇puçları)
- [Dışa Aktarma](#dışa-aktarma)

## 🎮 Oyun Hakkında

"Ticaretin İzinde 3D", bir ticaret ve finansal yönetim simülasyonudur. Oyunda kendi şirketinizi kurabilir, ticaret yapabilir, bankacılık işlemlerini öğrenebilir ve finansal planlamayı deneyimleyebilirsiniz. Oyun, 5 yaşından 100 yaşına kadar her yaş grubundan oyuncuya hitap eden bir deneyim sunmak için tasarlanmıştır.

## 📥 Kurulum

### Gereksinimler
- Python 3.9+
- Ursina Engine
- Diğer bağımlılıklar (`requirements_for_games.txt` dosyasında listelenmiştir)

### Kurulum Adımları

1. FinAsis projesini klonlayın:
```bash
git clone https://github.com/abdullah-aktas/FinAsis.git
cd FinAsis
```

2. Gerekli bağımlılıkları yükleyin:
```bash
pip install -r requirements_for_games.txt
```

3. Oyunu başlatın:
```bash
python apps/games/ursina_game/main.py
```

## 🎯 Nasıl Oynanır

### Kontroller
- **W, A, S, D** - Hareket etme
- **Fare** - Etrafı bakma
- **E** - Etkileşim (binalara girme, nesnelerle etkileşim)
- **ESC** - Menü / Çıkış

### Oynanış Akışı

1. Yaş grubunuzu seçin (Çocuk, Genç, Yetişkin, Yaşlı)
2. Karakterinizi seçin (İş İnsanı, Öğrenci, Öğretmen, Emekli)
3. Şirket ismi ve türünü belirleyin
4. Eğitim modunu tamamlayın veya atlayın
5. Şehir merkezinde gezinerek binalarla etkileşime geçin:
   - **Market**: Alım-satım yaparak ticaret becerilerinizi geliştirin
   - **Banka**: Para yatırın, kredi çekin, yatırım yapın
   - **Ofis**: Şirketinizi yönetin, muhasebe kayıtlarını tutun
   - **Eğitim Merkezi**: Finansal bilgilerinizi artırın

6. Görevleri tamamlayarak seviye atlayın ve oyun ilerleyişini açın

## 👶👧👨👴 Yaş Grubu Özelleştirmeleri

Oyun, farklı yaş gruplarına göre içerik ve zorluk seviyesini otomatik olarak ayarlar:

- **Çocuk (5-12)**: Basit para yönetimi, tasarruf, temel alışveriş kavramları
- **Genç (13-18)**: Bütçe planlama, basit yatırımlar, kariyer hedefleri
- **Yetişkin (19-65)**: İşletme yönetimi, yatırım stratejileri, vergi planlaması
- **Yaşlı (65+)**: Emeklilik planlaması, miras yönetimi, uzun vadeli stratejiler

## 👤 Karakter Türleri

Her karakter türü farklı başlangıç avantajları ve zorlukları sunar:

- **İş İnsanı**: Yüksek başlangıç sermayesi (15.000₺), ticaret becerisi +2
- **Öğrenci**: Düşük başlangıç sermayesi (5.000₺), muhasebe becerisi +2
- **Öğretmen**: Orta başlangıç sermayesi (10.000₺), yönetim becerisi +2
- **Emekli**: En yüksek başlangıç sermayesi (20.000₺), ticaret becerisi +1

## 📝 Görevler

Oyun içindeki görevler şunları içerir:

- **Eğitim Görevleri**: Marketi ziyaret etme, bankaya gitme gibi temel bilgilendirme görevleri
- **Ticaret Görevleri**: İlk satışı yapma, çeşitli envanteri oluşturma
- **Muhasebe Görevleri**: Gelir tablosu ve bilanço oluşturma
- **Yaş Grubuna Özel Görevler**: Her yaş grubuna özel benzersiz görevler

## 💡 Finansal İpuçları

Oyun içinde, yaptığınız her işlem için açıklayıcı finansal ipuçları verilir. Örneğin:

- Alış işlemi yaptığınızda, bu işlemin muhasebe kaydı ve finansal etkileri hakkında bilgi alırsınız
- Kredi çektiğinizde, faiz hesaplamaları ve borç/özkaynak oranı hakkında bilgi verilir
- Yatırım yaptığınızda, risk ve getiri dengesi hakkında ipuçları alırsınız

## 📤 Dışa Aktarma

Oyunu dışa aktarmak için:

### Masaüstü (.exe)
```bash
python build_games.py --desktop-only
```

### Mobil (.apk)
```bash
python build_games.py --mobile-only
```

Dışa aktarılan dosyalar `dist/` dizininde oluşturulacaktır.

---

## 📃 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim

- Proje Websitesi: [https://finasis.com.tr](https://finasis.com.tr)
- E-posta: [info@finasis.com.tr](mailto:info@finasis.com.tr) 