# FinAsis

FinAsis, dünya standartlarının üstünde, kullanıcı dostu, iş yürüten, eğiten ve eğlendiren modern bir finansal ekosistemdir. Proje; web, mobil ve masaüstü platformlarında çalışır, yapay zeka ve blockchain (Solidity) desteği sunar.

## Özellikler
- **Modern Web Arayüzü:** React tabanlı, hızlı ve kullanıcı dostu.
- **Mobil Uygulama:** React Native tabanlı, Android ve iOS desteği.
- **Masaüstü Uygulama:** Electron tabanlı, Windows/Mac/Linux desteği.
- **Yapay Zeka:** Akıllı asistan, öneri sistemi, otomasyon ve veri analizi.
- **Blockchain:** Solidity ile akıllı kontratlar, dijital varlık yönetimi.
- **Oyunlaştırma ve Eğitim:** Görevler, ödüller, simülasyonlar ve mini oyunlar.

## Kurulum ve Kullanım
Her platform için detaylı kurulum ve geliştirme adımları ilgili klasörlerin README dosyalarında açıklanmıştır:
- [Web Frontend](frontend/README.md)
- [Mobil Uygulama](mobile/README.md)
- [Masaüstü Uygulama](desktop_app/README.md)

## Katkı ve Geliştirme
- Kodunuzu modüler ve okunabilir şekilde yazın.
- Güvenlik, performans ve kullanıcı deneyimine öncelik verin.
- Yapay zeka ve blockchain entegrasyonlarını sürekli güncel tutun.

## Lisans
MIT

## 📖 Dokümantasyon

- [Türkçe](docs/tr/README.md)
- [English](docs/en/README.md)
- [Deutsch](docs/de/README.md)
- [Kurdî](docs/ku/README.md)

## 🚀 Özellikler

- 💰 Finansal Eğitim Platformu
- 🎮 TradeSim - Çok Oyunculu 3D Ticaret Simülasyonu
- 🛠️ FinAsis Editor - Özel Öğrenme Deneyimleri Oluşturma Aracı
- 🏪 Marketplace - Eğitim İçeriği Paylaşım Platformu
- 👥 Çok Oyunculu Sınıf Deneyimi
- 🤖 AI Destekli Finansal Asistan
- 📱 Çoklu Platform Desteği (Web, Mobil, Masaüstü)
- 🔗 Blockchain Entegrasyonu
- 📊 Gelişmiş Analitik Araçları

## 💻 Teknoloji Yığını

- **Backend:** Django 5.0.2, DRF 3.14.0
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Game Engine:** Ursina Engine 6.1.2
- **Editor:** PyQt6, Ursina Editor Framework
- **Mobil:** React Native
- **Masaüstü:** Electron
- **Veritabanı:** PostgreSQL
- **AI:** OpenAI GPT
- **Cache:** Redis
- **Multiplayer:** Photon Network

## 🛠️ Kurulum

Detaylı kurulum talimatları için [kurulum kılavuzunu](docs/tr/KURULUM.md) inceleyebilirsiniz.

## 👥 Katkıda Bulunma

1. Bu depoyu fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'feat: Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 🤝 İletişim

- Proje Yöneticisi: [İsim Soyisim](mailto:email@example.com)
- Website: [finasis.com](https://finasis.com)
- LinkedIn: [FinAsis](https://linkedin.com/company/finasis)

## API Entegrasyonları

### AI Asistanı
- Endpoint: `/api/v2/ai-assistant/assistant/chat/`
- Yöntem: `POST`
- Body: `{ "message": "Merhaba!" }`
- Yanıt: `{ "response": "AI: Merhaba! mesajını aldım. Size nasıl yardımcı olabilirim?" }`

### Oyunlaştırma
- Endpoint: `/api/v2/education/interactive-exercises/complete-task/`
- Yöntem: `POST`
- Body: `{ "task": "Giriş Yap" }`
- Yanıt: `{ "reward": "Hoşgeldin Rozeti" }`

Bu endpoint'ler web, mobil ve masaüstü uygulamalarınızdan kolayca çağrılabilir.
