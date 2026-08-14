# Orchestrator Service

## Purpose
The Orchestrator Service is the central AI execution and control component.

```text
Request
  |
  v
Orchestrator
  +--> Retrieval
  +--> Model Routing
  +--> Planning
  +--> Plan Repair
  +--> Tool Execution
  +--> Guardrails
  +--> Final Answer
  +--> Tracing / Evaluation
```

## Model Routing
The router separates provider selection from orchestration. The project represents providers with `ModelProvider` values including `OLLAMA`, `BEDROCK` and `OPENAI`.

Routing decisions contain:
- `provider`
- `complexity`
- `reason`

The preferred provider is configured through `DEFAULT_PROVIDER`.

## Providers
Ollama:
```text
OLLAMA_HOST
OLLAMA_MODEL
```

AWS Bedrock:
```text
AWS_REGION
BEDROCK_ENABLED
BEDROCK_MODEL_ID
BEDROCK_TIMEOUT
```

OpenAI:
```text
OPENAI_MODEL
```

Bedrock uses the AWS Bedrock Runtime API. Successful client creation does not guarantee invocation permission; AWS IAM/SCP policy can still deny `bedrock:InvokeModel` or `bedrock:InvokeModelWithResponseStream`.

## Complexity
The current routing policy uses deterministic heuristics based on query length, reasoning terms and multiple intents to classify LOW/MEDIUM/HIGH complexity.

## Agent Execution
The controlled workflow includes:
```text
Planner -> Execution Plan -> Validation/Repair -> Tool Execution -> Final Answer
```

The architecture is designed to prevent uncontrolled loops.

## Guardrails
The Level 6 control layer includes concepts for prompt validation, plan validation, tool permissions, tool input/output validation and structured output validation.

## Tracing
Execution traces record events such as:
```text
retrieval
model_router
planner_agent
repair_agent
tool_execution
final_answer
```

Latency and success information are captured where implemented.

## Evaluation
The service supports evaluation and replay. Observed evaluation results include alignment, coverage, ordering, penalties, diffs, deterministic replay and trace matching.

## Endpoints
The deployed service has been exercised through:
```text
POST /ask
POST /ask-stream
POST /evaluate
GET  /traces
GET  /evaluations
```

Streaming emits event categories such as `metadata`, `trace`, `token` and `done`.

## Kubernetes
The service runs as `deployment/orchestrator-service` in namespace `ai-analytics`.

## Basic Test
```bash
kubectl exec deployment/orchestrator-service -n ai-analytics --   python -c "
from router.model_router import ModelRouter
r = ModelRouter()
d = r.route('what time is it')
print(d.to_dict())
"
```

## Level 6 / Level 7
Level 7 adds provider/configuration choice while preserving the Level 6 planner, guardrails, tools, evaluation and tracing architecture.

## Design Principle
The orchestrator owns control, not a particular LLM provider.
