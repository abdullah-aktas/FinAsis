# FinAsis Modül Taşıma Rehberi

Bu rehber, FinAsis uygulamasındaki modüllerin `apps/` dizininden ana dizine taşınması işlemini açıklar.

## Genel Bakış

Bu işlem, Django uygulamasının yapısını daha modüler ve bağımsız hale getirmek için `apps/` altındaki tüm modülleri ana dizine taşır. Bu sayede:

- Her modül kendi başına bağımsız çalışabilir
- Modül yapısı daha düzenli olur
- Kod yeniden kullanımı ve test edilmesi kolaylaşır
- Modül tabanlı geliştirme daha etkin yapılabilir

## Taşıma Öncesi Hazırlık

1. Taşıma işlemi öncesi projenizin tam bir yedeğini alın
2. Tüm değişiklikleri commit edin, böylece gerekirse geri dönebilirsiniz
3. Sanal ortamınızın aktif olduğundan emin olun
4. Mevcut uygulamanızın sorunsuz çalıştığından emin olun

## Taşıma İşlemi

### Otomatik Taşıma İşlemi

Bu işlem için size sunulan betikleri kullanabilirsiniz:

1. Windows için: `migrate_apps.bat` dosyasını çalıştırın
   ```
   migrate_apps.bat
   ```

2. Linux/Mac için: `migrate_apps.sh` dosyasını çalıştırın
   ```
   chmod +x migrate_apps.sh
   ./migrate_apps.sh
   ```

Bu betikler sırasıyla:
- `apps/` dizini içeriğinin bir yedeğini alır
- Modülleri ana dizine kopyalar
- Her modülün `apps.py` dosyasındaki `name` değerini günceller
- `settings.py` dosyasındaki `INSTALLED_APPS` listesini günceller
- URL pattern'lerini günceller

### Manuel Taşıma İşlemi

Otomatik işlem çalışmazsa, şu adımları manuel olarak takip edebilirsiniz:

1. Her bir modülü `apps/` dizininden ana dizine kopyalayın
2. Her modülün `apps.py` dosyasında `name = 'apps.MODÜL_ADI'` değerini `name = 'MODÜL_ADI'` olarak güncelleyin
3. `config/settings/base.py` dosyasında `INSTALLED_APPS` listesini güncelleyin:
   - `'apps.users.apps.UsersConfig'` -> `'users.apps.UsersConfig'`
   - `'apps.finance'` -> `'finance'`
4. Modül içindeki import ifadelerini güncelleyin:
   - `from apps.users import ...` -> `from users import ...`
5. URL pattern'lerindeki import ve include ifadelerini güncelleyin

## Taşıma Sonrası Kontroller

1. Django sunucusunu başlatın:
   ```
   python manage.py runserver
   ```

2. İçe aktarma (import) hatalarını kontrol edin ve düzeltin
3. Veritabanı migrasyonlarının düzgün çalıştığından emin olun:
   ```
   python manage.py migrate --check
   ```

4. Admin paneline erişebildiğinizden emin olun
5. Temel işlevlerin (giriş, kayıt, temel sayfa görüntüleme) çalıştığını kontrol edin

## Sorun Giderme

- **Import Hataları**: Eğer `ModuleNotFoundError` hataları görüyorsanız, ilgili dosyadaki import ifadesini güncelleyin
- **URL Hataları**: URL pattern'lerindeki import ifadelerini kontrol edin
- **Veritabanı Hataları**: Django app yapılandırmasıyla ilgili sorunlar varsa migrations klasörlerini kontrol edin
- **Çalışmayan Moduller**: Her modülün `apps.py` dosyasındaki yapılandırmayı kontrol edin

## Eski Haline Dönme

Sorun yaşarsanız ve taşıma işlemi öncesine dönmek isterseniz:

1. Oluşturulan yedek dizinindeki dosyaları geri taşıyabilirsiniz:
   ```
   xcopy /E /I /Y apps_backup_XXXXXXXX\* apps\
   ```

2. Yeni oluşturulan modül dizinlerini kaldırın
3. Değişiklikleri revert edin veya önceki commit'e dönün

---

Herhangi bir sorunuz olursa, geliştirici ekibiyle iletişime geçin. 