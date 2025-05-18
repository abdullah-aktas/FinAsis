# FinAsis Modern Web Frontend

Bu klasör, FinAsis projesinin modern web arayüzünü (React tabanlı) içerecektir.

## Kurulum

1. Node.js ve npm kurulu olmalıdır.
2. Klasöre gelin:
   ```bash
   cd frontend
   ```
3. React projesi başlatın:
   ```bash
   npx create-react-app .
   ```
4. Gerekli kütüphaneleri yükleyin (ör. axios, material-ui, vs.):
   ```bash
   npm install axios @mui/material @emotion/react @emotion/styled
   ```
5. Django backend ile API entegrasyonu için .env dosyasına API URL'sini ekleyin.

## Geliştirme

- `src/` altında bileşenlerinizi oluşturun.
- API çağrıları için `axios` kullanabilirsiniz.
- Responsive ve kullanıcı dostu tasarımlar için Material UI veya benzeri bir kütüphane kullanın.

## Build ve Dağıtım

```bash
npm run build
```
Oluşan `build/` klasörünü Django'nun statik dosyalarına ekleyebilirsiniz. 