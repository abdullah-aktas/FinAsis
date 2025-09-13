FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_DISABLE_PIP_VERSION_CHECK=on \
	PIP_NO_CACHE_DIR=off \
	POETRY_VERSION=0

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY FinAsis/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY FinAsis /app/FinAsis

ENV DJANGO_SETTINGS_MODULE=config.settings

EXPOSE 8000

CMD ["python", "FinAsis/manage.py", "runserver", "0.0.0.0:8000"]
