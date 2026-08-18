# Orchestrator Service

## Purpose

`orchestrator-service` is the central runtime control layer of AI Analytics Copilot.

It combines:

- RAG retrieval
- prompt construction
- model routing
- Ollama execution
- AWS Bedrock execution
- controlled agent execution
- planner and plan repair
- tool execution
- guardrails
- short-term conversation memory
- streaming
- evaluation and replay
- trace persistence

The service is implemented as a FastAPI application.

## Source Structure

```text
orchestrator-service/
├── main.py
├── agents/
│   ├── agent_executor.py
│   ├── guardrails.py
│   ├── plan_repair.py
│   ├── planner.py
│   ├── state.py
│   ├── tool_registry.py
│   ├── tools.py
│   └── trace.py
├── clients/
│   ├── bedrock_client.py
│   └── ollama_client.py
├── config/
│   ├── permissions.py
│   └── settings.py
├── core/
│   └── structured_output.py
├── evaluation/
│   ├── cli.py
│   ├── dataset_loader.py
│   ├── diff_engine.py
│   ├── evaluator.py
│   ├── runner.py
│   ├── store.py
│   ├── trace_replay.py
│   └── types.py
├── memory/
├── orchestrator/
├── prompts/
├── router/
├── schemas/
├── streaming/
└── workflows/
```

## Application Entry Point

`main.py` creates:

```python
app = FastAPI(
    title="Orchestrator Service",
    lifespan=lifespan,
)
```

The global pipeline is:

```python
pipeline = OrchestrationPipeline()
```

## HTTP API

### `GET /health`

```json
{"status":"ok"}
```

### `POST /ask`

Input:

```json
{
  "query": "what time is it",
  "session_id": "example"
}
```

The request is passed to:

```python
pipeline.run(
    query=payload["query"],
    session_id=payload.get("session_id", "default"),
    stream=False,
)
```

The response includes the answer, routing information, model used, trace information where applicable, session ID and latency.

### `POST /ask-stream`

Calls the same pipeline with:

```text
stream=True
```

and returns a `text/event-stream`.

### `POST /evaluate`

The service builds an evaluation agent using the currently selected model:

```python
pipeline.router.select_model(
    query="evaluation",
    context=""
)
```

It then creates an `EvaluationRunner` and executes the supplied dataset.

Expected request shape:

```json
{
  "dataset": [
    {
      "id": "example",
      "query": "what time is it",
      "expected_tool": "get_time"
    }
  ]
}
```

### `GET /evaluations`

Returns stored evaluation runs, including a summary of:

- total
- passed
- failed
- average score

and the individual results.

### `GET /traces`

Returns persisted execution traces from `EvaluationStore`.

## Orchestration Pipeline

The main pipeline is implemented in:

```text
orchestrator/pipeline.py
```

The request path is approximately:

```text
Request
  |
  v
Prompt Guardrail
  |
  v
Conversation Memory
  |
  v
RAG Retrieval
  |
  v
PromptManager
  |
  v
ModelRouter
  |
  +-------------------+
  |                   |
  v                   v
RAG response       Agent branch
                      |
                      v
                   Planner
                      |
                      v
                 Plan Repair
                      |
                      v
                 Tool Executor
                      |
                      v
                  Final Answer
```

## RAG Branch

For normal RAG requests, the pipeline:

1. retrieves from the RAG service
2. normalises the retrieval response
3. reranks the hybrid results
4. builds a prompt using `PromptManager`
5. selects an LLM using `ModelRouter`
6. calls `model.generate()`
7. stores conversation memory
8. returns routing and retrieval trace information

## Agent Branch

The pipeline selects the agent branch based on the prompt type.

It constructs:

```text
Planner
PlanRepairEngine
AgentExecutor
MultiAgentOrchestrator
```

The registered tools include:

```text
get_time
echo
search_docs
```

Typed schemas are registered for `get_time` and `search_docs`.

## Model Routing

`router/model_router.py` contains:

```text
BaseModel
├── BedrockModel
├── OllamaModel
└── OpenAIModel
```

The active executable providers in the current `ModelRouter` are:

- AWS Bedrock
- Ollama

The `OpenAIModel` wrapper exists in the source, but `ModelRouter.get_model()` currently only returns Bedrock or Ollama and raises `RuntimeError` for unsupported providers.

### Provider Configuration

```text
DEFAULT_PROVIDER
BEDROCK_ENABLED
BEDROCK_MODEL_ID
AWS_REGION
OLLAMA_HOST
OLLAMA_MODEL
PREFER_LOCAL_LLM
```

Current defaults:

```text
DEFAULT_PROVIDER=ollama
BEDROCK_ENABLED=false
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
AWS_REGION=us-east-1
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=qwen2.5:3b
PREFER_LOCAL_LLM=false
```

### Level 7 Provider Selection

`DEFAULT_PROVIDER` is parsed into `ModelProvider`.

If the configured provider is available, `RoutingPolicy.choose()` returns:

```text
reason=settings_provider
```

For example:

```text
DEFAULT_PROVIDER=ollama
    -> ModelProvider.OLLAMA
    -> ollama:qwen2.5:3b
```

or:

```text
DEFAULT_PROVIDER=bedrock
    -> ModelProvider.BEDROCK
    -> bedrock:anthropic.claude-3-haiku-20240307-v1:0
```

If the preferred provider is unavailable, the policy continues through the existing routing logic.

### Complexity Routing

The current complexity estimator is deterministic.

HIGH is selected when:

- the query is longer than 12 words
- or contains terms such as `why`, `how`, `compare`, `architecture`, `design`, `explain`
- or contains ` and ` / ` vs `

MEDIUM is selected for queries longer than six words.

Otherwise the query is LOW.

## AWS Bedrock

`clients/bedrock_client.py` creates:

```python
boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
)
```

It implements:

```text
generate()
stream_generate()
```

using:

```text
InvokeModel
InvokeModelWithResponseStream
```

The current Anthropic request format is:

```json
{
  "anthropic_version": "bedrock-2023-05-31",
  "max_tokens": 2048,
  "messages": [
    {
      "role": "user",
      "content": "<prompt>"
    }
  ]
}
```

A Bedrock client can be constructed even when AWS later rejects invocation. For example, an AWS Service Control Policy can deny `bedrock:InvokeModel` or `bedrock:InvokeModelWithResponseStream`.

## Ollama

`clients/ollama_client.py` calls:

```text
POST <OLLAMA_HOST>/api/generate
```

Non-streaming requests use `stream=false`.

Streaming requests use `stream=true` and parse newline-delimited JSON responses.

The default model is:

```text
qwen2.5:3b
```

## Guardrails

The pipeline invokes prompt validation before continuing.

Agent execution also has guardrail infrastructure for validating plans, tool permissions, inputs and outputs.

## Structured Output

The service contains:

```text
core/structured_output.py
schemas/
```

for structured validation and planner/tool schema definitions.

## Evaluation and Replay

Evaluation components include:

```text
evaluation/runner.py
evaluation/evaluator.py
evaluation/diff_engine.py
evaluation/trace_replay.py
evaluation/store.py
```

The deployed Level 7 tests have demonstrated deterministic replay and matching execution traces for the `get_time` evaluation.

## Tracing

The execution stack records events including:

```text
retrieval
routing
plan
plan_repaired
tool_execution
final_answer
```

Streaming additionally emits metadata and token events.

## Memory

The service contains short-term conversation memory and a conversation store under:

```text
memory/
```

The pipeline associates memory with the supplied `session_id`.

## Streaming

`streaming/sse.py` provides SSE event generation.

The normal streaming path emits metadata containing:

```text
provider
model
complexity
reason
```

and trace/token/done events.

## Kubernetes

The deployed service is addressed inside the cluster as:

```text
orchestrator-service
```

Typical inspection:

```bash
kubectl get deployment orchestrator-service -n ai-analytics
kubectl logs deployment/orchestrator-service -n ai-analytics
```

## Design Boundary

The orchestrator is the control plane for AI execution. Provider adapters should remain below the router; retrieval remains a separate service; the frontend should not contain orchestration logic.

## Level 7 Boundary

Level 7 adds cloud-native deployment and provider selection without redesigning the Level 6 planning, guardrail, evaluation, trace or tool architecture.
