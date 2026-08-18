# Frontend

## Purpose

`apps/frontend` is the Next.js/React user interface for AI Analytics Copilot.

It provides:

- the application shell
- chat UI
- streaming API proxying
- evaluation dashboard
- trace viewer
- Level 7 settings UI

## Technology

The supplied `package.json` uses:

```text
Next.js 16.2.12
React 19.2.4
React DOM 19.2.4
TypeScript 5
Tailwind CSS 4
```

Scripts:

```text
npm run dev
npm run build
npm run start
npm run lint
```

## Source Structure

Important routes include:

```text
app/
├── page.tsx
├── chat/page.tsx
├── evaluation/page.tsx
├── traces/page.tsx
├── settings/page.tsx
└── api/
    ├── ask-stream/route.ts
    ├── evaluate/route.ts
    ├── evaluations/route.ts
    └── traces/route.ts
```

## Application Shell

`app/layout.tsx` sets:

```text
title: AI Analytics Copilot
description: Production AI orchestration and intelligence platform
```

and wraps application content in:

```text
AppShell
```

## Chat

`app/chat/page.tsx` renders:

```text
ChatWindow
```

The frontend has a Next.js API route:

```text
POST /api/ask-stream
```

which forwards the request to:

```text
${ORCHESTRATOR_URL}/ask-stream
```

and preserves the response as:

```text
text/event-stream
```

## Evaluation

The frontend has:

```text
POST /api/evaluate
GET  /api/evaluations
```

The evaluation page loads:

```text
/api/evaluations
```

and renders:

```text
MetricGrid
EvaluationTable
EvaluationDetail
```

## Traces

The frontend has:

```text
GET /api/traces
```

which proxies to:

```text
${ORCHESTRATOR_URL}/traces
```

The traces page renders the returned trace list using:

```text
TraceViewer
```

## Settings

The settings page is a client component.

The settings type is:

```text
model
  provider
  model
  fallback

agent
  max_steps
  planner_enabled
  repair_enabled

guardrails
  prompt_injection
  tool_validation
  output_validation

evaluation
  auto_run
  store_traces
  retention_days
```

## Provider UI

The current provider selector contains:

```text
Ollama
AWS Bedrock
```

Selecting Ollama automatically sets:

```text
qwen2.5:3b
```

Selecting AWS Bedrock automatically sets:

```text
anthropic.claude-3-haiku-20240307-v1:0
```

The model selector exposes the corresponding model.

There is also an:

```text
Enable fallback
```

checkbox.

## Important Configuration Boundary

The current settings page saves the selected settings to browser local storage:

```text
ai-analytics-settings
```

The source currently does **not** send the settings object to a backend settings endpoint.

Therefore the current provider selector is a frontend configuration UI, while the actual backend `ModelRouter` uses environment configuration such as:

```text
DEFAULT_PROVIDER
BEDROCK_ENABLED
BEDROCK_MODEL_ID
OLLAMA_MODEL
```

This distinction is important:

```text
Browser Settings
      |
      v
localStorage
```

is currently separate from:

```text
Kubernetes Environment
      |
      v
ModelRouter
      |
      v
Actual provider
```

The frontend's `fallback` setting is therefore stored as UI configuration; it is not currently wired to a backend fallback API in the supplied source.

## Settings Persistence

The page uses:

```text
localStorage.getItem("ai-analytics-settings")
localStorage.setItem("ai-analytics-settings", ...)
```

Missing sections are merged with defaults.

The default settings include:

```text
provider: ollama
model: qwen2.5:3b
fallback: false
max_steps: 5
planner_enabled: true
repair_enabled: true
prompt_injection: true
tool_validation: true
output_validation: true
auto_run: true
store_traces: true
retention_days: 30
```

## API Boundary

The frontend does not directly call Ollama or Bedrock.

Its server-side Next.js API routes use:

```text
ORCHESTRATOR_URL
```

to reach the orchestrator.

This keeps provider credentials and model execution server-side.

## Deployment

The frontend has its own Dockerfile and Next.js build.

Useful Kubernetes checks:

```bash
kubectl get deployment -n ai-analytics
kubectl get svc -n ai-analytics
kubectl get ingress -n ai-analytics
```

## Level 7 Role

The frontend is the Level 7 production intelligence/configuration console.

It exposes provider choices and operational controls without moving the orchestration engine into the browser.

## Design Boundary

The frontend should not contain:

- planner logic
- tool execution
- provider credentials
- RAG algorithms
- evaluation scoring logic
- trace persistence
- Bedrock invocation

Those remain backend responsibilities.
