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
