# AI Assistant Uygulaması

Bu modül, FinAsis platformunda yapay zeka destekli finansal asistan, analiz, öneri ve otomasyon işlemlerini yönetir.

## Kapsam
- AI tabanlı asistan fonksiyonları
- Doğal dil işleme ve yanıt üretimi
- API ve servis entegrasyonları
- Çoklu dil desteği (en, ku, ar)

## Klasör Yapısı
- `models/` ve `models.py`: Veri modelleri
- `views/`: Fonksiyonel view dosyaları
- `services/`: Servis ve yardımcı fonksiyonlar
- `serializers/`: API için serializerlar
- `templates/ai_assistant/`: Web arayüzü şablonları
- `static/ai_assistant/`: Statik dosyalar
- `api/`: API endpointleri ve urls
- `urls/`: Web ve API için ayrı URL dosyaları
- `tests/`: Birim testler

## Geliştirme Notları
- Kodlar modüler ve fonksiyonel olarak ayrılmıştır.
- API ve web endpointleri ayrıdır.
- Testler `tests/` klasöründe yer alır.

## Test
- Tüm önemli fonksiyon ve sınıflar için testler `tests.py` ve `tests/` klasöründe yer alır.
- Testleri çalıştırmak için:
  ```bash
  pytest ai_assistant/
  ```

## Çeviri
- Çoklu dil desteği için `locale/` klasörü kullanılır.
- Çeviri dosyalarını güncellemek için:
  ```bash
  python manage.py makemessages -a
  python manage.py compilemessages
  ```

## Katkı
- Kodda fonksiyon ve sınıf açıklamaları bulunmalıdır.
- Kod standartlarına ve proje dokümantasyonuna uyulmalıdır.
- Kodunuzu göndermeden önce testlerinizi çalıştırın ve PEP8'e uygun kod yazmaya özen gösterin. 

## OCR (Fatura) Özelliği – Kurulum ve Kullanım (Windows)

Bu modülde yer alan Fatura OCR özelliği, yüklenen görüntülerden (JPG/PNG) fatura bilgilerini çıkarır. Windows üzerinde çalıştırmak için aşağıdaki adımları izleyin.

### Gerekli Bağımlılıklar
- Python paketleri:
  - `pytesseract`
  - `opencv-python`
  - `Pillow`
- Sistem uygulaması:
  - Tesseract OCR (Windows için kurulmalıdır)

Python paketlerini sanal ortamda kurun (örnek):

```powershell
# (Opsiyonel) Sanal ortamınızı etkinleştirin
.\n+# Paketleri kurun
pip install pytesseract opencv-python Pillow
```

Tesseract OCR kurulumu (Windows):
- İndir ve kur: https://github.com/UB-Mannheim/tesseract/wiki
- Kurulumdan sonra, tesseract.exe yolunu doğrulayın. Örnek konumlar:
  - `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`

Uygulama Tesseract yolunu otomatik bulamazsa, aşağıdakilerden birini yapın:
- Ortam değişkeni ekleyin: `TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe`
- veya uygulama başlangıcında `pytesseract.pytesseract.tesseract_cmd` değişkenini bu yola ayarlayın.

PDF Desteği hakkında:
- Varsayılan akış görüntüler (JPG/PNG) içindir. PDF dosyaları için rasterizasyona ihtiyaç vardır.
- PDF’ler için `pdf2image` + Poppler gibi ek araçlar gereklidir. Alternatif olarak PDF’i önce görüntüye dönüştürüp yükleyin.

### Nasıl Denerim?
1. Uygulamayı çalıştırın ve oturum açın.
2. Tarayıcıda `/ai-assistant/ocr/` sayfasını açın.
3. Bir fatura görselini (JPG/PNG) sürükleyip bırakın veya dosya seçin.
4. “OCR’yi Çalıştır” düğmesine tıklayın; sonuçlar sayfada özet tabloya yansır.

### API Sözleşmesi
- Endpoint: `POST /ai-assistant/ocr/process/`
- İstek: `multipart/form-data` içinde `file`
- Yanıt (başarı): `{ "success": true, "data": { ...çıkarılan alanlar... } }`
- Yanıt (hata): `{ "success": false, "error": "Mesaj" }`

### Sorun Giderme
- “tesseract.exe bulunamadı” veya benzeri hata:
  - Tesseract’ı kurduğunuzdan emin olun ve `tesseract_cmd` yolunu doğru ayarlayın.
  - Komut satırında `tesseract --version` çalışıyor olmalı.
- “ModuleNotFoundError: cv2 / PIL / pytesseract”:
  - İlgili Python paketlerini kurun ve doğru sanal ortamın aktif olduğundan emin olun.
- PDF yüklendiğinde uyarı geliyor:
  - PDF rasterizasyonu yoksa, dosyayı önce JPG/PNG’ye dönüştürüp tekrar deneyin veya `pdf2image` + Poppler kurulumunu yapın.
- CSRF hataları:
  - İstemci tarafında CSRF token başlığının gönderildiğini doğrulayın; uygulamada CSRF koruması aktiftir.

### Testler
- Birim testler `tests/test_ocr_api.py` içinde mevcuttur ve `OCRService.process_invoice` mock’larıyla başarı/başarısızlık senaryolarını kapsar.
- Hızlı çalışma:
  ```powershell
  pytest -q
  ```