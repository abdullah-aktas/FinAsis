# FinAsis Mobil Uygulama

## Kurulum ve Yayınlama

### 1. Geliştirme Ortamı
- Node.js ve npm yüklü olmalı
- Expo CLI: `npm install -g expo-cli`
- Proje dizininde: `npm install`

### 2. Uygulamayı Çalıştırma
- Geliştirme: `expo start`
- Android/iOS cihazda QR kod ile test edebilirsiniz (Expo Go uygulaması ile)

### 3. Native Build (Google Play & App Store için)
- Expo EAS ile build alın:
  - Android (APK/AAB): `eas build -p android --profile production`
  - iOS (IPA): `eas build -p ios --profile production`
- [EAS Build dokümantasyonu](https://docs.expo.dev/build/introduction/)

### 4. Mağazalara Yükleme
- Google Play Console üzerinden .aab dosyasını yükleyin
- Apple App Store Connect üzerinden .ipa dosyasını yükleyin

### 5. Doğrudan İndirme
- Android için .apk dosyasını build edip doğrudan paylaşabilirsiniz
- iOS için TestFlight ile test edebilirsiniz

### 6. PWA (Web üzerinden erişim)
- `expo build:web` ile PWA olarak build alın
- Web sunucusuna yükleyin

## Eğitim Modülü
- Eğitim sekmesinden kurs ve derslere erişebilirsiniz
- Tüm platformlarda (web, android, ios) aynı eğitim içeriği kullanılabilir

## Sıkça Sorulanlar
- Girişte sorun yaşarsanız, internet bağlantınızı ve güncel Expo Go uygulamasını kontrol edin
- Bildirimler için cihaz izinlerini açmayı unutmayın

Daha fazla bilgi için: [Expo Dokümantasyonu](https://docs.expo.dev/)

## Kurulum

1. Node.js, npm ve React Native CLI kurulu olmalıdır.
2. Klasöre gelin:
   ```bash
   cd mobile
   ```
3. React Native projesi başlatın:
   ```bash
   npx react-native init FinAsisMobile
   ```
4. Gerekli kütüphaneleri yükleyin (ör. axios, react-navigation, vs.):
   ```bash
   npm install axios @react-navigation/native
   ```
5. API URL'sini .env dosyasına ekleyin.

## Geliştirme

- `src/` altında ekranlarınızı ve bileşenlerinizi oluşturun.
- API çağrıları için `axios` kullanabilirsiniz.

## Derleme

- Android için:
  ```bash
  npx react-native run-android
  ```
- iOS için:
  ```bash
  npx react-native run-ios
  ``` 