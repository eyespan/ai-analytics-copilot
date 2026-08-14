# API Gateway

## Purpose
The API Gateway is the client-facing HTTP boundary for AI Analytics Copilot. It keeps external API concerns separate from the internal AI orchestration, retrieval, routing, agent, evaluation and tracing layers.

```text
Client -> API Gateway -> Orchestrator -> AI control/runtime
```

## Responsibilities
- Accept and validate client requests.
- Forward requests to internal services.
- Return normal and streaming responses.
- Hide internal service topology.
- Provide a stable external API boundary.

The gateway should remain thin; planning, routing, tools, guardrails, retrieval and evaluation belong downstream.

## Request Flow
```text
HTTP Client
   |
   v
API Gateway
   |
   v
Orchestrator
   +--> Retrieval
   +--> Model Router
   +--> Agents / Tools
   +--> Guardrails
   +--> Evaluation
   +--> Tracing
   |
   v
Response
```

## Kubernetes
The gateway runs within the `ai-analytics` namespace and communicates with internal services using Kubernetes service discovery. Public exposure is provided through the project's Ingress/load-balancer architecture.

## Observability
Gateway requests should remain correlatable with downstream orchestration traces. Errors should distinguish invalid requests, downstream failures, timeouts and unexpected failures without exposing credentials or sensitive infrastructure details.

## Testing
Use the deployed gateway endpoint to test health and end-to-end `/ask` requests. The exact public URL depends on the active Ingress configuration.

## Level 6 / Level 7
Level 6/7 control logic remains downstream. Provider selection, planning, guardrails, tools, evaluation and tracing must not be moved into the gateway.

## Design Principle
Keep the gateway thin and stable; put AI control and execution in the orchestration layer.
