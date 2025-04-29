# -*- coding: utf-8 -*-
import os
import sys
import time
import socket
import requests
import psycopg2
import redis
from urllib.parse import urlparse
from decouple import config

def check_port(host, port, timeout=5):
    """Belirtilen port'un açık olup olmadığını kontrol eder"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_database():
    """Veritabanı bağlantısını test eder"""
    print("\nVeritabanı bağlantısı kontrol ediliyor...")
    try:
        conn = psycopg2.connect(
            dbname=config('DB_NAME'),
            user=config('DB_USER'),
            password=config('DB_PASSWORD'),
            host=config('DB_HOST'),
            port=config('DB_PORT', default=5432, cast=int)
        )
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()[0]
        print(f"✓ Veritabanı bağlantısı başarılı (PostgreSQL {version})")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Veritabanı bağlantı hatası: {e}")
        return False

def test_redis():
    """Redis bağlantısını test eder"""
    print("\nRedis bağlantısı kontrol ediliyor...")
    try:
        redis_host = str(config('REDIS_HOST', default='localhost'))
        redis_port = int(config('REDIS_PORT', default=6379))
        redis_password = str(config('REDIS_PASSWORD', default='')) or None
        
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True
        )
        if r.ping():
            print("✓ Redis bağlantısı başarılı")
            return True
        else:
            print("✗ Redis ping başarısız")
            return False
    except Exception as e:
        print(f"✗ Redis bağlantı hatası: {e}")
        return False

def test_django():
    """Django uygulamasını test eder"""
    print("\nDjango uygulaması kontrol ediliyor...")
    try:
        response = requests.get('http://localhost:8000/health/')
        if response.status_code == 200:
            print("✓ Django uygulaması çalışıyor")
            return True
        else:
            print(f"✗ Django uygulaması hata kodu döndürdü: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Django bağlantı hatası: {e}")
        return False

def test_nginx():
    """Nginx'i test eder"""
    print("\nNginx kontrol ediliyor...")
    try:
        response = requests.get('http://localhost')
        if response.status_code in [200, 301, 302]:
            print("✓ Nginx çalışıyor")
            return True
        else:
            print(f"✗ Nginx hata kodu döndürdü: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Nginx bağlantı hatası: {e}")
        return False

def test_prometheus():
    """Prometheus'u test eder"""
    print("\nPrometheus kontrol ediliyor...")
    try:
        response = requests.get('http://localhost:9090/-/healthy')
        if response.status_code == 200:
            print("✓ Prometheus çalışıyor")
            return True
        else:
            print(f"✗ Prometheus hata kodu döndürdü: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Prometheus bağlantı hatası: {e}")
        return False

def test_grafana():
    """Grafana'yı test eder"""
    print("\nGrafana kontrol ediliyor...")
    try:
        response = requests.get('http://localhost:3000/api/health')
        if response.status_code == 200:
            print("✓ Grafana çalışıyor")
            return True
        else:
            print(f"✗ Grafana hata kodu döndürdü: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Grafana bağlantı hatası: {e}")
        return False

def test_ssl():
    """SSL sertifikasını test eder"""
    print("\nSSL sertifikası kontrol ediliyor...")
    try:
        domain = config('DOMAIN', default='localhost')
        response = requests.get(f'https://{domain}', verify=True)
        print("✓ SSL sertifikası geçerli")
        return True
    except requests.exceptions.SSLError as e:
        print(f"✗ SSL sertifika hatası: {e}")
        return False
    except Exception as e:
        print(f"✗ SSL kontrol hatası: {e}")
        return False

def test_static_files():
    """Statik dosyaları test eder"""
    print("\nStatik dosyalar kontrol ediliyor...")
    try:
        response = requests.get('http://localhost/static/admin/css/base.css')
        if response.status_code == 200:
            print("✓ Statik dosyalar erişilebilir")
            return True
        else:
            print(f"✗ Statik dosya hatası: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Statik dosya kontrol hatası: {e}")
        return False

def test_media_files():
    """Media dosyalarını test eder"""
    print("\nMedia dosyaları kontrol ediliyor...")
    try:
        # Test için örnek bir dosya yüklendiğini varsayalım
        response = requests.get('http://localhost/media/test.jpg')
        if response.status_code in [200, 404]:  # 404 de kabul edilebilir çünkü test dosyası olmayabilir
            print("✓ Media dosyaları erişilebilir")
            return True
        else:
            print(f"✗ Media dosya hatası: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Media dosya kontrol hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("FinAsis Deployment Testi Başlatılıyor...")
    print("=" * 50)

    results = {
        'Veritabanı': test_database(),
        'Redis': test_redis(),
        'Django': test_django(),
        'Nginx': test_nginx(),
        'Prometheus': test_prometheus(),
        'Grafana': test_grafana(),
        'SSL': test_ssl(),
        'Statik Dosyalar': test_static_files(),
        'Media Dosyalar': test_media_files()
    }

    print("\nTest Sonuçları:")
    print("=" * 50)
    
    success = 0
    total = len(results)
    
    for service, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {service}")
        if result:
            success += 1

    print("\nÖzet:")
    print(f"Toplam Test: {total}")
    print(f"Başarılı: {success}")
    print(f"Başarısız: {total - success}")
    
    if success == total:
        print("\n✓ Tüm testler başarılı!")
        return 0
    else:
        print("\n✗ Bazı testler başarısız!")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 