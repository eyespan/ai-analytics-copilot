# Providers

## Current Status

The `providers` directory currently contains documentation only.

```text
providers/
└── README.md
```

There are no provider implementation modules in this directory in the supplied Level 7 source tree.

## Actual Provider Implementations

The active provider implementations live under:

```text
orchestrator-service/
├── router/
│   ├── model_router.py
│   └── policy.py
└── clients/
    ├── bedrock_client.py
    └── ollama_client.py
```

This distinction is important when navigating or extending the project.

## Current Runtime Provider Architecture

```text
OrchestrationPipeline
        |
        v
    ModelRouter
        |
        +--> RoutingPolicy
        |
        +--> OllamaModel
        |       |
        |       v
        |   OllamaClient
        |
        +--> BedrockModel
                |
                v
           BedrockClient
```

## Provider Enumeration

`router/policy.py` defines:

```python
class ModelProvider(str, Enum):
    BEDROCK = "bedrock"
    OLLAMA = "ollama"
    OPENAI = "openai"
```

The enumeration therefore represents three provider names, but current executable model selection supports Bedrock and Ollama.

## Ollama

Client:

```text
orchestrator-service/clients/ollama_client.py
```

Uses:

```text
POST <OLLAMA_HOST>/api/generate
```

with the configured model.

Default:

```text
qwen2.5:3b
```

Supports normal and streaming generation.

## AWS Bedrock

Client:

```text
orchestrator-service/clients/bedrock_client.py
```

Uses the AWS Bedrock Runtime client.

Supported operations:

```text
InvokeModel
InvokeModelWithResponseStream
```

The current default model is:

```text
anthropic.claude-3-haiku-20240307-v1:0
```

## Provider Selection

`DEFAULT_PROVIDER` controls the preferred provider.

Example:

```text
DEFAULT_PROVIDER=ollama
```

results in:

```text
ModelProvider.OLLAMA
```

when Ollama is available.

Likewise:

```text
DEFAULT_PROVIDER=bedrock
```

selects Bedrock when the Bedrock client is enabled.

The routing policy falls back to its normal routing logic if the preferred provider is unavailable.

## Important Level 7 Detail

The frontend currently lets the user select:

```text
Ollama
AWS Bedrock
```

and stores that selection in browser local storage.

The backend runtime provider selection is controlled by the backend environment variable:

```text
DEFAULT_PROVIDER
```

The current source does not contain a frontend-to-orchestrator API that directly applies the browser's saved provider selection to the backend environment.

Therefore:

> **Frontend provider selection and backend provider selection are currently separate configuration mechanisms.**

This is important when modifying the system.

## Security

Provider credentials/configuration belong to the server-side runtime.

Do not put AWS credentials, API keys or other provider secrets into frontend local storage or committed source files.

## Future Extraction

If provider implementations are eventually moved into this directory, preserve the existing `BaseModel`/provider boundary so the orchestration layer remains independent of provider-specific APIs.
