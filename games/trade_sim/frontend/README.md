# 🎮 TradeSim 3D - Dünya Çapında Ticaret Oyunu

<div align="center">
  
![TradeSim 3D](https://img.shields.io/badge/TradeSim-3D-blue?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.0.0-green?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-orange?style=for-the-badge)

**Modern Three.js tabanlı, çok oyunculu 3D ticaret ve ekonomi simülasyonu**

[🎮 Oyna](#kurulum) • [📖 Dokümantasyon](#özellikler) • [🤝 Katkıda Bulun](#geliştirme)

</div>

---

## 🌟 Özellikler

### 🎨 Modern Grafikler
- **Three.js** ile gerçek zamanlı 3D grafik
- **React Three Fiber** entegrasyonu
- Dinamik ışıklandırma ve gölgeler
- Parçacık efektleri
- Atmospheric fog ve skybox

### 🌍 Çok Oyunculu Deneyim
- WebSocket ile gerçek zamanlı senkronizasyon
- Canlı oyuncu pozisyonları
- Küresel sohbet sistemi
- Lonca ve takım sistemleri
- Turnuvalar ve yarışmalar

### 💼 Derin Ticaret Mekaniği
- Şehirler arası ticaret
- Dinamik pazar ekonomisi
- Arz-talep sistemi
- Pazar olayları ve fırsatları
- Yatırım ve borsa sistemi

### 🎯 Görev ve Başarım Sistemi
- Ana hikaye görevleri
- Yan görevler
- Günlük ve haftalık görevler
- 100+ başarım
- Ödül sistemi

### 🎭 Karakter Özelleştirme
- Kozmetik eşyalar
- Yetenekler ve seviye sistemi
- Envanter yönetimi
- İhtiyaç sistemi (enerji, mutluluk, açlık)

### 📱 Mobil Uyumlu
- Progressive Web App (PWA)
- Touch kontroller
- Responsive tasarım
- Offline destek

### 🔊 İmmersif Ses Sistemi
- 3D spatial audio
- Arkaplan müziği
- Ses efektleri
- Dinamik ses kontrolü

---

## 🚀 Kurulum

### Gereksinimler
- Node.js 18+
- npm veya yarn
- Modern web tarayıcı (Chrome, Firefox, Safari, Edge)

### Hızlı Başlangıç

```bash
# 1. Repository'yi klonlayın
git clone https://github.com/abdullah-aktas/FinAsis.git
cd FinAsis/FinAsis/src/apps/games/trade_sim/frontend

# 2. Bağımlılıkları yükleyin
npm install

# 3. Development server'ı başlatın
npm run dev

# 4. Tarayıcınızda açın
# http://localhost:3000
```

### Production Build

```bash
# Build için
npm run build

# Preview için
npm run preview
```

---

## 🎮 Nasıl Oynanır

### Temel Kontroller

| Tuş | Aksiyon |
|-----|---------|
| **W/A/S/D** | Hareket |
| **Mouse** | Kamera kontrolü |
| **I** | Envanter |
| **Q** | Görevler |
| **M** | Harita |
| **C** | Sohbet |
| **ESC** | Menü |

### Oyun Modları

#### 👤 Misafir Modu
Hızlıca başla, kayıt olmadan oyna. İlerleme kaydedilmez.

#### 🔐 Kayıtlı Oyuncu
Hesap oluştur, ilerlemeni kaydet, tüm özelliklere eriş.

#### 🎓 Sınıf Modu
Öğretmen kontrolü ile grup oyunu. Eğitim senaryoları.

### İlk Adımlar

1. **Şehir Seç** - Haritadan bir şehir seçerek başla
2. **İlk Görevi Tamamla** - "İlk Ticaret" görevini tamamla
3. **Ticaret Yap** - Şehirler arası ucuz al, pahalı sat
4. **Seviye Atla** - XP kazan ve yeni özellikler aç
5. **Lonca Kur** - Arkadaşlarınla birlikte oyna

---

## 🏗️ Mimari

### Teknoloji Stack

**Frontend:**
- React 18
- Three.js / React Three Fiber
- Vite (Build tool)
- Tailwind CSS
- Framer Motion (Animations)
- Zustand (State management)
- Socket.io-client (WebSocket)
- Howler.js (Audio)

**Backend:**
- Django 4+
- Django Channels (WebSocket)
- PostgreSQL
- Redis (Cache & Sessions)

### Proje Yapısı

```
frontend/
├── src/
│   ├── game/           # 3D game engine
│   │   └── GameWorld.jsx
│   ├── components/     # UI components
│   │   ├── GameUI.jsx
│   │   ├── HUD.jsx
│   │   ├── Inventory.jsx
│   │   ├── QuestPanel.jsx
│   │   ├── ChatPanel.jsx
│   │   └── ...
│   ├── utils/          # Utilities
│   │   ├── store.js
│   │   ├── NetworkManager.js
│   │   └── AudioManager.js
│   ├── assets/         # Static assets
│   ├── App.jsx         # Main app
│   └── index.jsx       # Entry point
├── public/             # Public assets
├── package.json
└── vite.config.js
```

---

## 🎯 Geliştirme Roadmap

### v1.0 (Mevcut) ✅
- [x] Temel 3D dünya
- [x] Çok oyunculu altyapı
- [x] Ticaret sistemi
- [x] Görev sistemi
- [x] UI/UX

### v1.1 (Planlanan) 🚧
- [ ] Crafting sistemi
- [ ] PvP arena
- [ ] Guild wars
- [ ] Marketplace
- [ ] Achievement ödülleri

### v1.2 (Gelecek) 🔮
- [ ] NFT entegrasyonu
- [ ] Blockchain kayıtları
- [ ] AI NPC'ler
- [ ] Prosedürel şehir üretimi
- [ ] VR desteği

---

## 📊 Performans

### Optimizasyonlar
- Code splitting
- Lazy loading
- Asset compression
- LOD (Level of Detail)
- Object pooling
- Frustum culling

### Hedef Performans
- **60 FPS** on modern devices
- **30 FPS** on mobile
- **< 3s** initial load time
- **< 100ms** server latency

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! 

### Nasıl Katkıda Bulunulur

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'feat: Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

### Kod Standartları
- ESLint rules'a uyun
- Prettier ile format edin
- Anlamlı commit mesajları

---

## 🐛 Bug Raporu

Bug bulduysanız lütfen [issue açın](https://github.com/abdullah-aktas/FinAsis/issues) ve şunları ekleyin:

- Bug açıklaması
- Tekrar etme adımları
- Beklenen davranış
- Ekran görüntüleri (varsa)
- Tarayıcı/cihaz bilgisi

---

## 📜 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](../../../LICENSE) dosyasına bakın.

---

## 👥 Ekip

**FinAsis Geliştirme Ekibi**
- Lead Developer: [Abdullah Aktaş](https://github.com/abdullah-aktas)

---

## 🙏 Teşekkürler

- [Three.js](https://threejs.org/)
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber)
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

---

<div align="center">

**⭐ Projeyi beğendiyseniz star vermeyi unutmayın! ⭐**

Made with ❤️ by FinAsis Team

</div>
