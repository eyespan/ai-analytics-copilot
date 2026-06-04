FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Install torch separately (correct way)
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# THEN install everything else from PyPI
RUN pip install \
    sentence-transformers==2.6.1 \
    transformers==4.41.1 \
    numpy==1.26.4 \
    scipy==1.11.4



