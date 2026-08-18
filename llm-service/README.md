# LLM Service

## Current Status

The `llm-service` directory exists in the repository, but its Python implementation is currently empty.

```text
llm-service/
├── base.py       # currently empty
├── router.py     # currently empty
└── README.md
```

Therefore this directory must **not** be documented as the active runtime LLM implementation.

## Where LLM Execution Actually Lives

The current active LLM abstraction and routing implementation is inside:

```text
orchestrator-service/router/model_router.py
```

Provider clients are inside:

```text
orchestrator-service/clients/
├── bedrock_client.py
└── ollama_client.py
```

The runtime architecture is therefore:

```text
OrchestrationPipeline
        |
        v
ModelRouter
        |
        +--------------------+
        |                    |
        v                    v
  OllamaModel          BedrockModel
        |                    |
        v                    v
 OllamaClient          BedrockClient
        |                    |
        v                    v
     Ollama              AWS Bedrock
```

## Model Abstraction

`orchestrator-service/router/model_router.py` defines:

```python
class BaseModel:
    generate(prompt)
    stream(prompt)
```

Concrete wrappers are:

```text
OllamaModel
BedrockModel
OpenAIModel
```

## Active Providers

### Ollama

Configured with:

```text
OLLAMA_HOST
OLLAMA_MODEL
```

Default:

```text
http://ollama:11434
qwen2.5:3b
```

### AWS Bedrock

Configured with:

```text
AWS_REGION
BEDROCK_ENABLED
BEDROCK_MODEL_ID
```

Default model ID:

```text
anthropic.claude-3-haiku-20240307-v1:0
```

### OpenAI

An `OpenAIModel` class exists in `model_router.py`, using the OpenAI client interface and defaulting to:

```text
gpt-4o-mini
```

However, the current `ModelRouter.get_model()` only handles:

```text
BEDROCK
OLLAMA
```

and raises `RuntimeError` for other providers.

Consequently OpenAI should currently be regarded as a model wrapper present in source, not as an active routed provider.

## Why This Directory Exists

The empty `llm-service` package can serve as a future boundary if LLM execution is later extracted from the orchestrator.

At the current Level 7 implementation, moving the runtime classes into this directory would be an architectural refactor and should not be assumed to have happened.

## Design Principle

Documentation must distinguish the intended architecture from the active implementation:

```text
CURRENT
Orchestrator -> ModelRouter -> provider clients

POTENTIAL FUTURE
Orchestrator -> LLM Service -> ModelRouter -> provider clients
```

No runtime dependency on an external `llm-service` HTTP API is present in the current source.
