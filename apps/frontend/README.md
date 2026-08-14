# Frontend

## Purpose
The Frontend is the user-facing Next.js application.

```text
Browser -> Next.js Frontend -> API Gateway -> Orchestrator
```

## Responsibilities
- User interaction.
- Display AI responses.
- Display streaming output.
- Provide configuration UI.
- Send requests through the API boundary.
- Present application state.

The frontend does not implement AI orchestration.

## Settings
The settings model contains:
```text
model
agent
guardrails
evaluation
```

Model configuration includes:
```text
provider
model
fallback
```

Agent configuration includes:
```text
max_steps
planner_enabled
repair_enabled
```

Guardrail configuration includes:
```text
prompt_injection
tool_validation
output_validation
```

Evaluation configuration includes:
```text
auto_run
store_traces
retention_days
```

## Provider Selection
Level 7 exposes provider/model configuration including Ollama and AWS Bedrock. The frontend configures the backend; it does not directly invoke either provider.

```text
Frontend setting -> Backend configuration -> Model Router -> Provider
```

## Settings Persistence
The current settings page persists browser settings using local storage under:
```text
ai-analytics-settings
```

Stored settings are merged with defaults so missing fields can receive current defaults.

## Streaming
The backend streaming path exposes events such as:
```text
metadata
trace
token
done
```
The frontend can use these to present progressive execution/output.

## React
The settings page is client-side because it uses browser storage and interactive state. State changes should be driven by user actions rather than unnecessary synchronous state updates inside effects.

## Kubernetes
The frontend runs in namespace `ai-analytics` and is exposed through the project's Ingress/service architecture.

Useful checks:
```bash
kubectl get pods -n ai-analytics
kubectl get svc -n ai-analytics
kubectl get ingress -n ai-analytics
```

## Level 6 / Level 7
Level 7 adds provider/configuration controls without moving planner, guardrails, tools, evaluation or tracing into the browser.

## Design Principle
The frontend is a presentation and configuration layer; AI control remains server-side.
