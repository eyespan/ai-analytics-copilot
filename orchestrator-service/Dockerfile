FROM python:3.11-slim

WORKDIR /orchestrator-service

COPY . /orchestrator-service


RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/orchestrator-service

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

