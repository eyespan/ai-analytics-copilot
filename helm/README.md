# Helm Infrastructure and Application Deployment

## Purpose

The `helm/` directory contains the Helm packaging, values and Kubernetes Jobs used to deploy the Level 7 platform onto EKS.

The repository uses one reusable application chart for the internal AI services and external Helm repositories for platform/data components.

## Directory structure

```text
helm/
├── charts/
│   └── application/
├── values/
│   ├── applications/
│   ├── data/
│   ├── infrastructure/
│   └── llm/
└── jobs/
    ├── clickhouse-init/
    ├── clickhouse-seed/
    ├── embedding-ingest/
    ├── ollama-init/
    └── opensearch-init/
```

## Reusable application chart

The chart is:

```text
helm/charts/application
```

It templates:

- Deployment
- Service
- Ingress
- PVC
- ServiceAccount
- ConfigMap template

The same chart is parameterised for:

```text
api-gateway
orchestrator-service
rag-service
embedding-service
indexer-service
frontend
ollama
```

## Application values

Per-service values live under:

```text
helm/values/applications/
```

The values control:

- image repository
- image tag
- replica count
- container port
- service port
- environment variables
- resource requests/limits
- ingress configuration
- persistence

## Ingress

The application chart supports NGINX Ingress.

The frontend is exposed at `/`.

The API gateway is exposed at `/api` and uses NGINX rewrite configuration.

The NGINX controller itself is configured by:

```text
helm/values/infrastructure/ingress-nginx.yaml
```

The controller Service is a Kubernetes `LoadBalancer` with an AWS internet-facing NLB annotation.

## Data services

The bootstrap workflow installs:

- ClickHouse from the Bitnami Helm repository
- OpenSearch from the OpenSearch Helm repository

Their values are:

```text
helm/values/data/clickhouse.yaml
helm/values/data/opensearch.yaml
```

Both use the repository's `gp3` StorageClass.

## LLM runtime

The development Kubernetes platform also supports Ollama through:

```text
helm/values/llm/ollama.yaml
```

Ollama uses persistent storage for its model directory.

Production model routing can instead select AWS Bedrock through the orchestrator configuration; Bedrock is not installed through Helm.

## Initialisation Jobs

Helm deployments are complemented by Kubernetes Jobs:

### ClickHouse

```text
clickhouse-init
clickhouse-seed
```

### OpenSearch

```text
opensearch-init
```

### Embeddings

```text
embedding-ingest
```

### Ollama

```text
ollama-init
```

The reusable `kubectl-apply.yml` workflow deletes and reapplies Jobs when required and waits for Job completion.

## Deployment mechanism

`.github/workflows/helm-deploy.yml` provides the reusable deployment primitive.

It:

1. Checks out the repository.
2. Configures AWS credentials.
3. Updates the EKS kubeconfig.
4. Installs Helm.
5. Adds external Helm repositories when required.
6. Selects the local application chart otherwise.
7. Applies values and image tags.
8. Runs `helm upgrade --install`.
9. Optionally waits for readiness.

## Platform bootstrap

`.github/workflows/bootstrap-cluster.yml` establishes the platform in dependency order:

```text
AWS Load Balancer Controller
        ↓
NGINX Ingress
        ↓
Metrics Server
        ↓
Prometheus / kube-prometheus-stack
        ↓
ClickHouse
        ↓
ClickHouse init / seed
        ↓
OpenSearch
        ↓
OpenSearch init
        ↓
Ollama
        ↓
Ollama model load
```

Application deployment is performed separately.

## Important distinction

Terraform creates the AWS/EKS foundation and EKS-managed add-ons.

Helm creates the Kubernetes platform services and application workloads.

GitHub Actions orchestrates both.
