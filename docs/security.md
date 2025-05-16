# .zap/rules.tsv Dosyası Hakkında

Bu dosya, projenin güvenlik ve kod kalitesi taramaları için özel kuralları içerir.

## Amaç
- Otomatik güvenlik taramaları (ör. OWASP ZAP) veya özel kod denetimleri için kullanılır.
- Her satır bir kuralı veya eşleşmeyi temsil eder.
- CI/CD süreçlerinde veya manuel olarak kullanılabilir.

## Format
- Dosya, Tab ile ayrılmış sütunlardan oluşur (TSV).
- Her satırda genellikle: kural adı, açıklama, eşleşme paterni, aksiyon gibi alanlar bulunur.

## Kullanım
- CI/CD sürecinde otomatik olarak çalıştırılabilir.
- Manuel tarama için örnek komut: `python scripts/zap_scan.py`
- Kuralların güncel ve proje ihtiyaçlarına uygun olduğundan emin olun.

## Örnek Satır
```
KURAL_ADI	Açıklama	Patern	Aksiyon
```

## Notlar
- Kurallar düzenli olarak gözden geçirilmeli ve güncellenmelidir.
- Proje ekibi, bu dosyanın nasıl güncelleneceği ve kullanılacağı konusunda bilgilendirilmelidir. 