# Observability Infrastructure

## Purpose

The `observability/` directory is reserved for the monitoring and observability configuration of the AI Analytics Copilot.

The Level 7 source tree contains the directory structure for:

```text
observability/
├── prometheus/
├── grafana/
│   ├── datasources/
│   └── dashboards/
└── loki/
```

At the current source snapshot these directories do not contain populated configuration files.

Therefore, the active monitoring deployment should be understood from the actual Kubernetes bootstrap workflow and Terraform EKS configuration rather than from assuming these directories contain the runtime configuration.

## Active monitoring components

### Prometheus / Grafana

The active Kubernetes bootstrap installs:

```text
kube-prometheus-stack
```

from:

```text
https://prometheus-community.github.io/helm-charts
```

It is deployed into:

```text
monitoring
```

with:

```text
prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

This allows Prometheus ServiceMonitor discovery beyond Helm-generated selector restrictions.

The kube-prometheus-stack chart provides the Prometheus/Grafana monitoring stack used by the cluster.

### Metrics Server

Metrics Server is installed into `kube-system`.

It provides Kubernetes resource metrics used by Kubernetes tooling and supports the cluster's operational visibility.

### CloudWatch

The EKS control plane is configured to emit:

```text
api
audit
authenticator
controllerManager
scheduler
```

logs.

These are sent to the CloudWatch log group:

```text
/aws/eks/<cluster-name>/cluster
```

The repository also defines a CloudWatch Agent IRSA role for workload telemetry.

## Observability architecture

The current platform therefore has two complementary layers:

```text
                    AWS
                     │
             ┌───────┴────────┐
             │   CloudWatch   │
             │ EKS control    │
             │ plane logs     │
             └────────────────┘

                     +

              Kubernetes
                     │
        ┌────────────┴────────────┐
        │                         │
   Metrics Server          kube-prometheus-stack
                                  │
                         ┌────────┴────────┐
                         │                 │
                    Prometheus          Grafana
```

## Application-level observability

The orchestrator independently records execution traces containing events such as:

- planning
- plan repair
- tool execution
- retrieval
- model routing
- final answer
- evaluation/replay information

This application trace layer complements infrastructure monitoring.

## Current repository status

The following are present as directories but are not populated in the supplied source snapshot:

```text
observability/prometheus/
observability/grafana/datasources/
observability/grafana/dashboards/
observability/loki/
```

Do not treat these directories as active Loki/Grafana dashboard configuration until files are added.

## Recommended future evolution

Once Level 7 is frozen, the natural observability expansion is to add version-controlled:

- Prometheus scrape configuration
- ServiceMonitors
- Grafana datasource configuration
- Grafana dashboards
- Loki deployment/configuration if log aggregation is required
- alerting rules
- application SLI/SLO dashboards

These can be introduced without changing the core Level 6/7 orchestration or evaluation model.


## Accessing Grafana and Monitoring the EKS Platform

Level 7 provides a platform observability layer using:

```text
Amazon EKS
     │
     ├── Prometheus
     │      └── Kubernetes / application metrics
     │
     ├── Grafana
     │      └── Dashboards and visualisation
     │
     └── CloudWatch
            └── AWS / EKS logs and metrics
```

This complements the Level 6 AI/application observability layer, which provides:

```text
Orchestrator
    │
    ├── /evaluate
    ├── /evaluations
    └── /traces
            │
            ▼
        ClickHouse
```

The Level 7 documentation explicitly separates these two observability layers: application/AI telemetry remains in the orchestrator and ClickHouse, while Prometheus, Grafana and CloudWatch provide Kubernetes/platform telemetry.

---

# 1. Verify the Observability Platform

After the **Bootstrap Kubernetes Platform** workflow has completed, first check the monitoring workloads.

```bash
kubectl get pods -A
```

Look for Prometheus and Grafana pods.

A more focused check is:

```bash
kubectl get pods -A | grep -Ei 'prometheus|grafana'
```

You should see the monitoring components in a healthy state, for example:

```text
prometheus-...
grafana-...
```

Check their services:

```bash
kubectl get svc -A | grep -Ei 'prometheus|grafana'
```

This is useful because the exact service names can depend on the Helm release and chart configuration.

---

# 2. Check the Monitoring Namespace

If the monitoring components have been deployed into the `monitoring` namespace, check:

```bash
kubectl get all -n monitoring
```

Also check:

```bash
kubectl get pods -n monitoring
```

and:

```bash
kubectl get svc -n monitoring
```

If the deployment uses another namespace, identify it with:

```bash
kubectl get pods -A | grep -Ei 'prometheus|grafana'
```

---

# 3. Check Grafana

First identify the Grafana service:

```bash
kubectl get svc -A | grep -i grafana
```

For example:

```text
monitoring   grafana   ClusterIP   172.20.x.x   <none>   80/TCP
```

The service name may differ depending on the Helm release.

You can inspect the service:

```bash
kubectl describe svc grafana -n monitoring
```

---

# 4. Access Grafana Using Port Forwarding

For the current Level 7 platform, the preferred method is local port forwarding rather than exposing Grafana directly to the Internet.

Run:

```bash
kubectl port-forward -n monitoring svc/grafana 3000:80
```

If the Grafana service exposes port `3000` instead, use:

```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

Then open:

```text
http://localhost:3000
```

Grafana's Kubernetes documentation also uses port `3000` as the standard local access path, while Prometheus Operator documents port-forwarding to the Grafana service as the normal quick-access method.

> Keep the terminal running while using Grafana. Press `Ctrl+C` to terminate the port-forward.

---

# 5. Obtain the Grafana Administrator Password

Do not assume the Grafana password.

First inspect the secrets:

```bash
kubectl get secrets -n monitoring
```

Look for the Grafana credentials secret.

For Helm-based Grafana deployments, the password can commonly be retrieved from the Kubernetes Secret using:

```bash
kubectl get secret <grafana-secret> \
  -n monitoring \
  -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

The exact secret name depends on the Helm release.

You can also inspect the Helm release:

```bash
helm list -n monitoring
```

and:

```bash
helm get notes <release-name> -n monitoring
```

The Helm chart notes normally provide the appropriate Grafana access and credential commands.

---

# 6. Log in to Grafana

Open:

```text
http://localhost:3000
```

Use the administrator credentials configured by the deployment.

Once logged in, verify that Prometheus is configured as a Grafana data source.

Navigate to:

```text
Connections
    ↓
Data sources
    ↓
Prometheus
```

The Prometheus data source should be available and healthy.

---

# 7. Check the Grafana Dashboards

The Level 7 observability platform is intended to provide visibility into:

```text
Kubernetes workloads
Pod health
CPU utilisation
Memory utilisation
API throughput
Request latency
Application performance
Infrastructure health
```

The Level 7 architecture identifies Grafana dashboards for:

- request latency
- retrieval latency
- model routing
- tool execution
- Kubernetes utilisation
- pod health
- evaluation scores
- API throughput

Depending on the installed kube-prometheus/Grafana configuration, the dashboard names may vary.

Start by looking under:

```text
Dashboards
```

and inspect the Kubernetes-related dashboards.

The kube-prometheus stack provides pre-configured Prometheus rules and Grafana dashboards as part of the monitoring stack.

---

# 8. Check Prometheus Directly

Grafana provides the visualisation layer, but Prometheus can be queried directly.

First identify the Prometheus service:

```bash
kubectl get svc -A | grep -i prometheus
```

Then port-forward the Prometheus service.

For example:

```bash
kubectl port-forward -n monitoring svc/prometheus-k8s 9090:9090
```

If the service has a different name, substitute the actual service name.

Open:

```text
http://localhost:9090
```

Prometheus Operator documents this port-forwarding approach for accessing the Prometheus UI.

---

# 9. Check Prometheus Targets

Inside Prometheus, navigate to:

```text
Status
    ↓
Targets
```

This is one of the most useful places to diagnose monitoring problems.

Targets should normally show a healthy state such as:

```text
UP
```

If a target is down, inspect:

```text
Endpoint
Last Scrape
Error
```

This can identify problems such as:

```text
Service unavailable
Pod unavailable
Incorrect ServiceMonitor
Network connectivity
Application metrics endpoint unavailable
```

Prometheus Operator also provides troubleshooting guidance for verifying whether `ServiceMonitor` resources have been discovered and incorporated into the Prometheus configuration.

---

# 10. Check Kubernetes Workloads

Grafana is useful for historical metrics, but `kubectl` remains the quickest way to establish the current Kubernetes state.

Check all workloads:

```bash
kubectl get pods -A
```

Check services:

```bash
kubectl get svc -A
```

Check deployments:

```bash
kubectl get deployments -A
```

Check StatefulSets:

```bash
kubectl get statefulsets -A
```

Check nodes:

```bash
kubectl get nodes
```

---

# 11. Check Application Namespace

The AI Analytics Copilot applications run in:

```text
ai-analytics
```

Check the application pods:

```bash
kubectl get pods -n ai-analytics
```

Check services:

```bash
kubectl get svc -n ai-analytics
```

Check deployments:

```bash
kubectl get deployments -n ai-analytics
```

Check the application ingress:

```bash
kubectl get ingress -n ai-analytics
```

A healthy application deployment should show the expected services and pods in a `Running`/`Ready` state.

---

# 12. Check Pod Health

For a specific pod:

```bash
kubectl describe pod <pod-name> -n ai-analytics
```

Check recent logs:

```bash
kubectl logs <pod-name> -n ai-analytics
```

For a deployment:

```bash
kubectl logs deployment/orchestrator-service -n ai-analytics
```

Follow logs live:

```bash
kubectl logs -f deployment/orchestrator-service -n ai-analytics
```

---

# 13. Check Orchestrator AI Observability

The Level 6 observability layer remains available after deployment to EKS.

Check evaluations:

```bash
wget -qO- http://orchestrator-service/evaluations
```

Check execution traces:

```bash
wget -qO- http://orchestrator-service/traces
```

Run an evaluation:

```bash
wget -qO- \
  --post-data='{"dataset":[{"id":"level7-observability-test","query":"what time is it","expected_tool":"get_time"}]}' \
  --header='Content-Type: application/json' \
  http://orchestrator-service/evaluate
```

The expected result is a successful evaluation with:

```text
passed: true
score: 1.0
deterministic: true
trace_match: true
```

The Level 7 architecture retains the Level 6 evaluation and execution-trace APIs, with evaluation and trace information persisted in ClickHouse.

---

# 14. Check Model Routing

Model-routing decisions are also part of the application observability layer.

Check the current backend provider configuration:

```bash
kubectl exec deployment/orchestrator-service -n ai-analytics -- \
  env | grep -E 'DEFAULT_PROVIDER|BEDROCK_ENABLED|BEDROCK_MODEL_ID|OLLAMA_MODEL'
```

Example:

```text
BEDROCK_ENABLED=true
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
DEFAULT_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:3b
```

Check the router:

```bash
kubectl exec -it deployment/orchestrator-service -n ai-analytics -- \
  python -c "
from router.model_router import ModelRouter

r = ModelRouter()

print('preferred_provider:', r.preferred_provider)

decision = r.route('what time is it')

print('DECISION:', decision.to_dict())

model = r.get_model(decision)

print('MODEL:', model.name)
"
```

The routing metadata includes:

```text
provider
complexity
reason
```

For example:

```json
{
  "provider": "ollama",
  "complexity": "low",
  "reason": "settings_provider"
}
```

AWS Bedrock is also supported by the Level 7 model-routing abstraction, although actual Bedrock invocation remains dependent on AWS account permissions and organizational policies.

---

# 15. Check ClickHouse Trace Persistence

ClickHouse remains the persistence layer for Level 6 evaluations and execution traces.

Check the stored records:

```bash
kubectl exec -it deployment/orchestrator-service -n ai-analytics -- \
  python -c "
from clickhouse_driver import Client

c = Client(
    host='clickhouse.data.svc.cluster.local',
    port=9000,
    database='ai_evaluation',
    user='admin',
    password='admin123'
)

print(
    'evaluation_runs_all:',
    c.execute(
        'SELECT count() FROM ai_evaluation.evaluation_runs_all'
    )
)

print(
    'execution_traces_all:',
    c.execute(
        'SELECT count() FROM ai_evaluation.execution_traces_all'
    )
)
"
```

This provides a simple check that the AI observability data is being persisted independently of the Prometheus/Grafana platform metrics.

---

# 16. Observability Troubleshooting Flow

When something appears unhealthy, use the following sequence.

```text
                    Problem
                       │
                       ▼
              kubectl get pods -A
                       │
                       ▼
                Is pod Running?
                 /          \
               No            Yes
               │              │
               ▼              ▼
        kubectl describe    Check Service
        kubectl logs             │
                                ▼
                         Check Prometheus
                         Targets
                                │
                                ▼
                         Check Grafana
                         dashboards
                                │
                                ▼
                       Check application
                       traces/evaluations
                                │
                                ▼
                         Check ClickHouse
                         persistence
```

Useful commands:

```bash
kubectl get pods -A
kubectl get svc -A
kubectl get deployments -A
kubectl get ingress -A
```

Then inspect the affected component:

```bash
kubectl describe pod <pod> -n <namespace>
kubectl logs <pod> -n <namespace>
```

---

# 17. Recommended Operational Checks

After each Level 7 deployment, the following checks provide a useful platform health baseline.

### Kubernetes

```bash
kubectl get nodes
kubectl get pods -A
kubectl get svc -A
```

### Application

```bash
kubectl get pods -n ai-analytics
kubectl get svc -n ai-analytics
kubectl get ingress -n ai-analytics
```

### Prometheus

```bash
kubectl get pods -A | grep -i prometheus
kubectl get svc -A | grep -i prometheus
```

### Grafana

```bash
kubectl get pods -A | grep -i grafana
kubectl get svc -A | grep -i grafana
```

### AI evaluation

```bash
wget -qO- http://orchestrator-service/evaluations
```

### AI traces

```bash
wget -qO- http://orchestrator-service/traces
```

### Provider routing

```bash
kubectl exec deployment/orchestrator-service -n ai-analytics -- \
  env | grep -E 'DEFAULT_PROVIDER|BEDROCK_ENABLED|BEDROCK_MODEL_ID|OLLAMA_MODEL'
```

---

# 18. Observability Architecture

The complete Level 7 observability model is:

```text
                    AI Analytics Copilot
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
       AI/Application                 Platform
       Observability                 Observability
              │                           │
              ▼                           ▼
       Orchestrator                  Kubernetes
              │                           │
       ┌──────┼──────┐              ┌─────┼─────┐
       ▼      ▼      ▼              ▼     ▼     ▼
    Traces  Eval   Routing      Prometheus Grafana CloudWatch
       │      │      │
       └──────┴──────┘
              │
              ▼
          ClickHouse
```

This separation is intentional.

**Prometheus/Grafana/CloudWatch** answer questions such as:

```text
Are the pods healthy?
How much CPU is being used?
How much memory is being used?
Are services available?
Are Kubernetes resources healthy?
Are metrics being collected?
```

**Orchestrator traces/evaluations/ClickHouse** answer questions such as:

```text
Which model provider was selected?
Why was that provider selected?
Which tools were executed?
What was the execution trace?
Did the evaluation pass?
Was replay deterministic?
What was the evaluation score?
```

Together these provide the Level 7 operational view of both the **AI system** and the **AWS/EKS platform**.