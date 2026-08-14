# LLM Service

## Purpose
The LLM layer provides a provider-independent model execution abstraction.

```text
Orchestrator -> Model Router -> Model abstraction
                              +--> Ollama
                              +--> Bedrock
                              +--> OpenAI
```

## Model Interface
Provider wrappers expose the common operations:
```text
generate(prompt)
stream(prompt)
```

The orchestration layer should not depend on provider-specific response objects.

## Current Wrappers
- `OllamaModel`
- `BedrockModel`
- `OpenAIModel`

Model names are represented as:
```text
ollama:<model>
bedrock:<model-id>
openai:<model>
```

## Bedrock
The Bedrock wrapper delegates to `clients.bedrock_client.BedrockClient`, which uses the Bedrock Runtime API for normal and streaming generation.

## Ollama
The Ollama wrapper delegates to the Ollama client. The current default is `qwen2.5:3b`.

## Configuration
```text
DEFAULT_PROVIDER
OLLAMA_HOST
OLLAMA_MODEL
BEDROCK_ENABLED
BEDROCK_MODEL_ID
BEDROCK_TIMEOUT
OPENAI_MODEL
AWS_REGION
```

## Errors
Provider client construction and successful invocation are different states. For example, a Bedrock client can exist while an AWS SCP prevents model invocation.

## Design Principle
Provider-specific implementation belongs behind the model abstraction; orchestration, tools, guardrails, retrieval and evaluation remain provider-independent.
