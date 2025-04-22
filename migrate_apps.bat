@echo off
:: Bu script, apps/ dizinindeki modülleri ana dizine taşıma işlemini otomatize eder

echo FinAsis Modul Tasima Sistemi
echo ============================
echo.

:: Yedek dizini oluştur
set "BACKUP_DIR=apps_backup_%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_DIR=%BACKUP_DIR: =0%"
echo Apps dizininin yedegi olusturuluyor: %BACKUP_DIR%
mkdir "%BACKUP_DIR%"
xcopy /E /I /Y apps\* "%BACKUP_DIR%\"
echo Yedekleme tamamlandi.
echo.

:: 1. Modülleri taşı ve içerikleri güncelle
echo 1. Modulleri ana dizine tasima islemi baslatiliyor...
python migrate_modules.py
echo.

:: 2. settings.py dosyasını güncelle
echo 2. INSTALLED_APPS guncelleniyor...
python update_settings.py
echo.

:: 3. URL yapısını güncelle
echo 3. URL patternleri guncelleniyor...
python update_urls.py
echo.

:: Başarılı mesajı
echo Islem tamamlandi!
echo Tum moduller ana dizine tasindi ve baglantilar guncellendi.
echo Projenizi test etmek icin Django development sunucusunu baslatabilirsiniz:
echo python manage.py runserver
echo.
echo Not: Herhangi bir sorunda, yedekledigimiz %BACKUP_DIR% dizininden eski modullere erisebilirsiniz.
pause 