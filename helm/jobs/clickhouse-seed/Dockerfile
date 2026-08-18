FROM python:3.12-slim

COPY ingest_clickhouse.py .

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python","ingest_clickhouse.py"]