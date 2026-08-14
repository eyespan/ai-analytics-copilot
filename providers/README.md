# Model Providers

## Purpose
The provider layer isolates external LLM APIs from routing and orchestration.

```text
Model Router
 +--> Ollama
 +--> AWS Bedrock
 +--> OpenAI
```

## Ollama
Local/testing provider.

Configuration:
```text
OLLAMA_HOST
OLLAMA_MODEL
```

Current default:
```text
http://ollama:11434
qwen2.5:3b
```

## AWS Bedrock
Managed AWS model provider.

Configuration:
```text
AWS_REGION
BEDROCK_ENABLED
BEDROCK_MODEL_ID
BEDROCK_TIMEOUT
```

Current default model:
```text
anthropic.claude-3-haiku-20240307-v1:0
```

The implementation uses Bedrock Runtime normal and streaming invocation.

An AWS organization may block Bedrock through IAM/SCP. Such a denial is an environment authorization issue, not evidence that the provider adapter is absent.

## OpenAI
The routing layer defines an OpenAI provider and model wrapper. The configured default model is `gpt-4o-mini`; actual execution requires the corresponding client/configuration.

## Routing vs Provider
Provider means where/how the model executes. Routing means which provider/model should handle a request. Keeping these separate allows provider implementations to evolve without rewriting the orchestration system.

## Fallback
Fallback must remain inside the routing/provider boundary and must never bypass normal guardrails, tracing or evaluation.

## Security
Credentials must not be committed. Use the deployment environment's secure identity/configuration mechanisms.

## Design Principle
Adding a provider should not require rewriting retrieval, agents, guardrails, evaluation or tracing.
