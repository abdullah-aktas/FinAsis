# FinAsis Mobil Uygulama

Bu klasör, FinAsis projesinin mobil uygulamasını (React Native tabanlı) içerecektir.

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