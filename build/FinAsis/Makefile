.PHONY: install test lint clean run build docker-up docker-down docker-build

# Kurulum
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

# Test
test:
	pytest tests/ --cov=FinAsis --cov-report=term-missing

# Kod kalitesi
lint:
	black .
	isort .
	flake8 .
	mypy .
	bandit -r .

# Temizleme
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} +

# Çalıştırma
run:
	python manage.py runserver

# Docker
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose build

# Veritabanı
migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

# Statik dosyalar
collectstatic:
	python manage.py collectstatic --noinput

# Çeviri
makemessages:
	python manage.py makemessages -l tr
	python manage.py makemessages -l en

compilemessages:
	python manage.py compilemessages

# Dokümantasyon
docs:
	cd docs && make html

# Dağıtım
build:
	python setup.py sdist bdist_wheel

# Yardım
help:
	@echo "Kullanılabilir komutlar:"
	@echo "  install        - Gerekli paketleri yükle"
	@echo "  test          - Testleri çalıştır"
	@echo "  lint          - Kod kalitesi kontrollerini çalıştır"
	@echo "  clean         - Geçici dosyaları temizle"
	@echo "  run           - Geliştirme sunucusunu başlat"
	@echo "  docker-up     - Docker konteynerlerini başlat"
	@echo "  docker-down   - Docker konteynerlerini durdur"
	@echo "  docker-build  - Docker imajlarını oluştur"
	@echo "  migrate       - Veritabanı migrasyonlarını uygula"
	@echo "  makemigrations - Yeni migrasyonlar oluştur"
	@echo "  collectstatic - Statik dosyaları topla"
	@echo "  makemessages  - Çeviri dosyalarını oluştur"
	@echo "  compilemessages - Çeviri dosyalarını derle"
	@echo "  docs          - Dokümantasyon oluştur"
	@echo "  build         - Dağıtım paketlerini oluştur"
	@echo "  help          - Bu yardım mesajını göster" 