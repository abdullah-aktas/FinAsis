FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	POETRY_VIRTUALENVS_CREATE=false \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
	build-essential \
	libpq-dev \
	curl \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better layer caching)
COPY FinAsis/requirements.base.txt /app/requirements.txt
RUN pip install --upgrade pip \
 && pip install -r /app/requirements.txt \
 && pip install gunicorn whitenoise

# Copy project
COPY . /app

# Environment
ENV DJANGO_SETTINGS_MODULE=src.config.settings \
	USE_SQLITE=1 \
	DEBUG=0

# Static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "src.config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
