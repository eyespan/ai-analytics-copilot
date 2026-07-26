ARG ECR_REGISTRY
FROM ${ECR_REGISTRY}/ml-base:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ingest_embeddings.py .

CMD ["python", "ingest_embeddings.py"]