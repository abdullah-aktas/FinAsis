# FinAsis PostgreSQL Kurulum ve Ayarlama PowerShell Betiği

Write-Host "===== FinAsis PostgreSQL Kurulum ve Ayarlama Betiği =====" -ForegroundColor Yellow

# 1. PostgreSQL kurulumunu kontrol et
Write-Host "`nPostgreSQL kurulumu kontrol ediliyor..." -ForegroundColor Yellow
$psqlExists = $null -ne (Get-Command "psql" -ErrorAction SilentlyContinue)

if ($psqlExists) {
    Write-Host "PostgreSQL zaten kurulu." -ForegroundColor Green
} else {
    Write-Host "PostgreSQL kurulu değil." -ForegroundColor Red
    Write-Host "Lütfen PostgreSQL'i https://www.postgresql.org/download/windows/ adresinden indirip kurun." -ForegroundColor Yellow
    Write-Host "Kurulumdan sonra bu betiği tekrar çalıştırın." -ForegroundColor Yellow
    Exit
}

# 2. .env dosyasını kontrol et ve oluştur
Write-Host "`n.env dosyası kontrol ediliyor..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host ".env dosyası zaten mevcut." -ForegroundColor Green
} else {
    Write-Host ".env dosyası oluşturuluyor..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" -Destination ".env"
        Write-Host ".env dosyası .env.example'dan kopyalandı." -ForegroundColor Green
    } else {
        Write-Host ".env.example dosyası bulunamadı. Lütfen manuel olarak bir .env dosyası oluşturun." -ForegroundColor Red
        Exit
    }
}

# 3. .env dosyasından veritabanı bilgilerini oku
Write-Host "`nVeritabanı bilgileri okunuyor..." -ForegroundColor Yellow
if (Test-Path ".env") {
    # .env dosyasını oku ve değişkenleri ayarla
    $envContent = Get-Content ".env" -Raw
    $envLines = $envContent -split "`n"
    
    $dbName = "finasis"
    $dbUser = "postgres"
    $dbPassword = "postgres"
    $dbHost = "localhost"
    $dbPort = "5432"
    
    foreach ($line in $envLines) {
        if ($line -match "^DB_NAME=(.*)$") { $dbName = $matches[1] }
        if ($line -match "^DB_USER=(.*)$") { $dbUser = $matches[1] }
        if ($line -match "^DB_PASSWORD=(.*)$") { $dbPassword = $matches[1] }
        if ($line -match "^DB_HOST=(.*)$") { $dbHost = $matches[1] }
        if ($line -match "^DB_PORT=(.*)$") { $dbPort = $matches[1] }
    }
    
    Write-Host "Veritabanı: $dbName" -ForegroundColor Green
    Write-Host "Kullanıcı: $dbUser" -ForegroundColor Green
    Write-Host "Host: $dbHost" -ForegroundColor Green
    Write-Host "Port: $dbPort" -ForegroundColor Green
} else {
    Write-Host ".env dosyası bulunamadı. Lütfen manuel olarak bir .env dosyası oluşturun." -ForegroundColor Red
    Exit
}

# 4. PostgreSQL veritabanı ve kullanıcı oluştur
Write-Host "`nVeritabanı ve kullanıcı oluşturuluyor..." -ForegroundColor Yellow

$sqlScript = @"
-- Kullanıcıyı oluştur
DO `$`$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$dbUser') THEN
        CREATE ROLE $dbUser WITH LOGIN PASSWORD '$dbPassword' CREATEDB;
    END IF;
END
`$`$;

-- Veritabanını oluştur
CREATE DATABASE $dbName WITH OWNER $dbUser;

-- Yetkileri ata
GRANT ALL PRIVILEGES ON DATABASE $dbName TO $dbUser;
"@

$sqlFile = New-TemporaryFile
$sqlScript | Out-File $sqlFile -Encoding UTF8

try {
    # psql kullanarak SQL komutlarını çalıştır
    $env:PGPASSWORD = "postgres"
    psql -U postgres -f $sqlFile.FullName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Veritabanı ve kullanıcı başarıyla oluşturuldu." -ForegroundColor Green
    } else {
        Write-Host "Veritabanı ve kullanıcı oluşturulurken hata oluştu." -ForegroundColor Red
        Exit
    }
} catch {
    Write-Host "Veritabanı ve kullanıcı oluşturulurken hata oluştu: $_" -ForegroundColor Red
    Exit
} finally {
    # Geçici dosyayı temizle
    Remove-Item $sqlFile -Force
    $env:PGPASSWORD = ""
}

# 5. Django migrasyonlarını çalıştır
Write-Host "`nDjango migrasyonları çalıştırılıyor..." -ForegroundColor Yellow
python manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migrasyonlar başarıyla tamamlandı." -ForegroundColor Green
} else {
    Write-Host "Migrasyon sırasında hata oluştu." -ForegroundColor Red
    Exit
}

# 6. Superuser oluştur
Write-Host "`nDjango superuser oluşturmak ister misiniz? (E/H)" -ForegroundColor Yellow
$createSuperuser = Read-Host

if ($createSuperuser -eq "E" -or $createSuperuser -eq "e") {
    Write-Host "Superuser oluşturuluyor..." -ForegroundColor Yellow
    python manage.py createsuperuser
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Superuser başarıyla oluşturuldu." -ForegroundColor Green
    } else {
        Write-Host "Superuser oluşturulurken hata oluştu." -ForegroundColor Red
    }
}

Write-Host "`n===== FinAsis PostgreSQL Kurulum ve Ayarlama İşlemi Tamamlandı =====" -ForegroundColor Green
Write-Host "Django development sunucusunu başlatmak için: python manage.py runserver" -ForegroundColor Yellow
Write-Host "Docker ile tüm servisleri başlatmak için: docker-compose up -d" -ForegroundColor Yellow 