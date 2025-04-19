@echo off
setlocal enabledelayedexpansion

:: Yedekleme dizinine git
cd /d "%~dp0.."

:: Log dizinini oluştur
if not exist logs mkdir logs

:: Ortam değişkenlerini ayarla
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\service-account-key.json
set BACKUP_BUCKET_NAME=finasis-backups
set DB_HOST=localhost
set DB_USER=postgres
set DB_NAME=finasis
set DB_PASSWORD=your_db_password

:: Tarih ve saat bilgisini al
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2% %datetime:~8,2%:%datetime:~10,2%:%datetime:~12,2%

:: Log dosyası
set LOG_FILE=logs\cron_backup.log

:: Log fonksiyonu
:log
echo [%TIMESTAMP%] %~1 >> "%LOG_FILE%"
echo [%TIMESTAMP%] %~1
goto :eof

:: Başlangıç logu
call :log "Yedekleme işlemi başlatılıyor..."

:: Veritabanı yedeği
call :log "Veritabanı yedeği alınıyor..."
python scripts/backup.py --backup-db
if errorlevel 1 (
    call :log "HATA: Veritabanı yedeği alınamadı"
    exit /b 1
)
call :log "Veritabanı yedeği başarıyla alındı"

:: Media dosyaları yedeği
call :log "Media dosyaları yedeği alınıyor..."
python scripts/backup.py --backup-media
if errorlevel 1 (
    call :log "HATA: Media dosyaları yedeği alınamadı"
    exit /b 1
)
call :log "Media dosyaları yedeği başarıyla alındı"

:: Bitiş logu
call :log "Tüm yedekleme işlemleri başarıyla tamamlandı"

:: Eski log dosyalarını temizle (30 günden eski)
forfiles /p logs /s /m cron_backup.log.* /d -30 /c "cmd /c del @path" 2>nul

endlocal 