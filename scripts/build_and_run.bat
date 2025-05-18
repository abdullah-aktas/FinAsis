@echo off
echo FinAsis Kurulum ve Çalıştırma Scripti
echo =================================
echo.

REM Python yüklü mü kontrol et
python --version 2>NUL
if errorlevel 1 (
    echo Python bulunamadı! Lütfen Python 3.9 veya üzerini yükleyin.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Sanal ortam var mı kontrol et
if not exist venv (
    echo Sanal ortam oluşturuluyor...
    python -m venv venv
    if errorlevel 1 (
        echo Sanal ortam oluşturulamadı!
        pause
        exit /b 1
    )
)

REM Sanal ortamı etkinleştir
echo Sanal ortam etkinleştiriliyor...
call venv\Scripts\activate
if errorlevel 1 (
    echo Sanal ortam etkinleştirilemedi!
    pause
    exit /b 1
)

REM Gerekli paketleri yükle
echo Gerekli paketler yükleniyor...
pip install -r requirements.txt
if errorlevel 1 (
    echo Paket yüklemesi başarısız oldu!
    pause
    exit /b 1
)

REM PyInstaller yüklü mü kontrol et
pip show pyinstaller >NUL
if errorlevel 1 (
    echo PyInstaller yükleniyor...
    pip install pyinstaller
    if errorlevel 1 (
        echo PyInstaller yüklenemedi!
        pause
        exit /b 1
    )
)

REM Masaüstü uygulaması derleme scripti var mı kontrol et
if not exist build_desktop.py (
    echo build_desktop.py bulunamadı!
    pause
    exit /b 1
)

echo.
echo Masaüstü uygulaması derleniyor...
python build_desktop.py
if errorlevel 1 (
    echo Masaüstü uygulaması derlenirken hata oluştu!
    pause
    exit /b 1
)

echo.
echo Derleme başarılı!
echo.

:MENU
echo Ne yapmak istersiniz?
echo 1 - Masaüstü uygulamasını çalıştır
echo 2 - Django geliştirme sunucusunu başlat
echo 3 - Veritabanını oluştur/güncelle
echo 4 - Çık
echo.

set /p choice=Seçiminiz: 

if "%choice%"=="1" (
    echo Masaüstü uygulaması başlatılıyor...
    start dist\FinAsis.exe
    goto MENU
)

if "%choice%"=="2" (
    echo Django geliştirme sunucusu başlatılıyor...
    python manage.py runserver
    goto MENU
)

if "%choice%"=="3" (
    echo Veritabanı oluşturuluyor/güncelleniyor...
    python manage.py migrate
    echo.
    echo İşlem tamamlandı!
    goto MENU
)

if "%choice%"=="4" (
    echo.
    echo Çıkılıyor...
    deactivate
    exit /b 0
)

echo.
echo Geçersiz seçim!
goto MENU 