FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY financial_exporter.py .

EXPOSE 9091

CMD ["python", "financial_exporter.py"] 