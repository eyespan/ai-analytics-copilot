# API Gateway

## Purpose

`apps/api-gateway` is a small FastAPI HTTP gateway in front of the `orchestrator-service`.

Its current implementation is deliberately thin. It does not implement model routing, RAG, planning, tools, guardrails, evaluation logic, or trace generation itself. It forwards selected HTTP operations to the orchestrator.

## Source

```text
apps/api-gateway/
├── main.py
├── Dockerfile
├── requirements.txt
└── README.md
```

### `main.py`

Creates:

```python
app = FastAPI(title="API Gateway")
```

and reads:

```text
ORCHESTRATOR_URL
```

with default:

```text
http://orchestrator-service
```

## Endpoints

### `GET /health`

Returns:

```json
{"status":"ok"}
```

This is a local application health endpoint.

### `GET /`

Returns:

```json
{"message":"API Gateway Running"}
```

### `POST /ask-stream`

The gateway sends the request body to:

```text
${ORCHESTRATOR_URL}/ask-stream
```

using `requests.post(..., stream=True)`.

The response is returned as a FastAPI `StreamingResponse` with:

```text
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

The gateway therefore preserves the orchestrator's SSE stream.

> **Current implementation note:** there is no `/ask` route in `apps/api-gateway/main.py`. The non-streaming `/ask` endpoint is implemented directly by `orchestrator-service`.

### `POST /evaluate`

Forwards the JSON body to:

```text
${ORCHESTRATOR_URL}/evaluate
```

and returns the JSON response.

### `GET /evaluations`

Forwards:

```text
GET ${ORCHESTRATOR_URL}/evaluations
```

and passes the optional `limit` query parameter.

Default:

```text
limit=100
```

### `GET /traces`

Forwards:

```text
GET ${ORCHESTRATOR_URL}/traces
```

and passes the optional `limit`.

Default:

```text
limit=50
```

## Request Flow

```text
Client
  |
  v
API Gateway
  |
  +--> /ask-stream ------> Orchestrator /ask-stream
  |
  +--> /evaluate --------> Orchestrator /evaluate
  |
  +--> /evaluations -----> Orchestrator /evaluations
  |
  +--> /traces ----------> Orchestrator /traces
```

## Error Handling

For downstream requests, the gateway checks `response.ok`.

If the orchestrator returns an error status, the gateway raises an HTTP exception using the downstream status code and a gateway-level error message.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `ORCHESTRATOR_URL` | `http://orchestrator-service` | Internal orchestrator URL |

## Runtime Dependencies

The application uses:

- FastAPI
- `requests`
- FastAPI `StreamingResponse`

See `requirements.txt` for the exact dependency set.

## Container

The service has its own `Dockerfile`.

The gateway is intended to run as a container and communicate with the orchestrator through the Kubernetes service name/configured URL.

## Design Boundary

The gateway should remain a transport/API boundary.

It should not become responsible for:

- model selection
- provider fallback
- prompt construction
- RAG retrieval
- agent planning
- tool execution
- guardrails
- evaluation scoring
- trace persistence

Those responsibilities belong to downstream components.

## Level 7 Context

Level 7 moves the platform toward Kubernetes/AWS deployment while keeping the AI execution logic in the orchestrator. The gateway therefore remains a thin service boundary rather than becoming another orchestration layer.

## Testing

Inside the Kubernetes namespace:

```bash
kubectl get pods -n ai-analytics
kubectl get svc -n ai-analytics
```

Then test:

```bash
curl http://<gateway>/health
```

For streaming, send a JSON request to:

```text
POST /ask-stream
```

and inspect the SSE events returned from the orchestrator.
