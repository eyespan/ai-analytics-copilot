# config/settings.py

import os


# -----------------------------------------------------
# AWS / BEDROCK
# -----------------------------------------------------

AWS_REGION = os.getenv(
    "AWS_REGION",
    "us-east-1"
)

BEDROCK_ENABLED = (
    os.getenv(
        "BEDROCK_ENABLED",
        "false"
    ).lower() == "true"
)

BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "anthropic.claude-3-haiku-20240307-v1:0"
)

BEDROCK_TIMEOUT = int(
    os.getenv(
        "BEDROCK_TIMEOUT",
        "120"
    )
)


# -----------------------------------------------------
# OLLAMA
# -----------------------------------------------------

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://ollama:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:7b"
)


# -----------------------------------------------------
# OPENAI
# -----------------------------------------------------

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4o-mini"
)


# -----------------------------------------------------
# ROUTING
# -----------------------------------------------------

DEFAULT_PROVIDER = os.getenv(
    "DEFAULT_PROVIDER",
    "ollama"
)