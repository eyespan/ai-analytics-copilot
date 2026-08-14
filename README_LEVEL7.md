# AI Analytics Copilot – Level 7

## Cloud-Native AWS Platform

Level 7 moves the AI Analytics Copilot from a primarily application-focused platform into a **cloud-native AWS deployment platform**.

The key principle is:

> **Level 6 controls the AI system. Level 7 operationalises that AI system on AWS and Kubernetes.**

Level 7 does not replace the Level 6 agent, guardrail, structured-output, evaluation, model-routing or tracing architecture. It provides the infrastructure and delivery platform around it.

---

## 1. What Level 7 Adds

Level 7 introduces:

- Amazon EKS
- Terraform infrastructure modules
- Amazon ECR
- Kubernetes/Helm deployment
- reusable GitHub Actions workflows
- platform bootstrap automation
- Prometheus
- Grafana
- CloudWatch integration
- IAM and IRSA
- GitHub OIDC foundations
- AWS Load Balancer Controller
- External DNS
- cert-manager
- EBS/EFS CSI integration
- repository-wide validation
- frontend Settings persistence
- explicit Ollama/AWS Bedrock provider selection
- AWS Bedrock model-routing integration

The existing Level 6 evaluation and trace APIs remain available.

---

## 2. Architecture

```text
                          GitHub
                            │
                            ▼
                     GitHub Actions
                      │    │    │
               Validate  Build  Terraform
                      │    │    │
                      │    ▼    ▼
                      │   ECR   AWS
                      │          │
                      │          ▼
                      └───────► EKS
                                 │
         ┌───────────────────────┼────────────────────────┐
         │                       │                        │
         ▼                       ▼                        ▼
    API Gateway            Orchestrator                Frontend
                                 │
                      ┌──────────┼───────────┐
                      ▼          ▼           ▼
                     RAG      Evaluation    Tracing
                      │
            ┌─────────┼──────────┐
            ▼         ▼          ▼
        ClickHouse OpenSearch  Model Router
                                  │
                         ┌────────┴────────┐
                         ▼                 ▼
                      Ollama          AWS Bedrock

                      EKS Observability
                           │
                ┌──────────┼──────────┐
                ▼          ▼          ▼
            Prometheus  Grafana   CloudWatch
```

AWS Bedrock is an external AWS managed service. It is not deployed as a Kubernetes workload.

---

## 3. Repository Structure

Important Level 7 areas include:

```text
.github/workflows/
├── bootstrap.yml
├── bootstrap-cluster.yml
├── build-docker-images.yml
├── build-ml-base.yml
├── deploy-dev.yml
├── docker-build.yml
├── helm-deploy.yml
├── kubectl-apply.yml
├── terraform-apply.yml
├── terraform-plan.yml
└── validate.yml

terraform/
├── environments/
│   └── dev/
└── modules/
    ├── cloudwatch/
    ├── ecr/
    ├── eks/
    ├── iam/
    ├── iam-irsa/
    ├── kubernetes/
    ├── networking/
    └── vpc/

helm/
├── charts/
├── jobs/
└── values/

apps/
├── api-gateway/
├── embedding-service/
├── frontend/
├── indexer-service/
├── rag-service/
└── ...

orchestrator-service/
└── Level 6 AI control/evaluation/routing layer
```

---

## 4. Terraform

The development environment composes reusable Terraform modules for:

```text
VPC
ECR
IAM
EKS
IAM / IRSA
Kubernetes namespaces
CloudWatch
Kubernetes add-ons
```

Terraform state is configured through the development environment backend.

The Level 7 repository also contains bootstrap automation for creating the GitHub OIDC provider, GitHub Actions IAM role and Terraform state bucket prerequisites.

---

## 5. Kubernetes

Amazon EKS is the runtime platform.

Application workloads include:

```text
API Gateway
Orchestrator
RAG Service
Embedding Service
Indexer Service
Frontend
```

Supporting workloads include:

```text
ClickHouse
OpenSearch
Ollama
Ingress NGINX
AWS Load Balancer Controller
Prometheus
Grafana
```

Kubernetes jobs initialise services where required.

---

## 6. Helm

The reusable application chart supports common deployment configuration such as:

- image repository
- image tag
- environment configuration
- service
- ingress
- persistent storage
- service accounts

The reusable GitHub Actions Helm workflow supports:

```text
helm repo configuration
values files
image tags
additional values
namespace creation
rollout verification
```

---

## 7. Container Images

Application images are stored in Amazon ECR.

The reusable Docker build workflow supports individual services or the complete application set.

Example:

```text
<account>.dkr.ecr.us-east-1.amazonaws.com/orchestrator-service:v1.0.0
```

Deployment workflows accept an image tag so the deployed version is explicit.

---

## 8. CI/CD

### Repository validation

The validation workflow checks:

```text
Terraform formatting
Terraform validation
Helm lint
Kubernetes manifests
Dockerfiles
isort
Black
flake8
Unit tests
```

### Image build

```text
Checkout
   ↓
AWS authentication
   ↓
ECR login
   ↓
Docker build
   ↓
Docker push
```

The current Docker workflow does not include a container vulnerability scanner.

### Development deployment

The development deployment workflow deploys the application services and applies the required initialization/ingestion jobs.

---

## 9. Platform Bootstrap

The Level 7 bootstrap workflow establishes the AWS/Kubernetes platform in dependency order.

The cluster bootstrap includes components such as:

```text
AWS Load Balancer Controller
Ingress NGINX
Metrics Server
Prometheus
ClickHouse
ClickHouse initialisation
ClickHouse seed
OpenSearch
OpenSearch initialisation
Ollama
Ollama model initialisation
```

The workflow uses reusable Helm and kubectl workflows.

---

## 10. LLM Providers

The existing model-routing layer supports multiple providers.

### Provider choices

```text
Ollama
AWS Bedrock
```

The provider abstraction is:

```text
ModelRouter
    │
    ├── OllamaModel
    │      └── OllamaClient
    │
    └── BedrockModel
           └── BedrockClient
```

The orchestrator does not need a separate orchestration implementation for each provider. The existing model abstraction allows the Level 6 application layer to select an executable model.

### Ollama

The current EKS environment uses:

```text
OLLAMA_MODEL=qwen2.5:3b
```

Ollama is the operational inference provider in the current cluster.

### AWS Bedrock

Bedrock is configured using:

```text
BEDROCK_ENABLED=true
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

The Bedrock integration supports:

- non-streaming invocation
- streaming invocation
- model selection through the existing router
- routing metadata/observability

Example backend configuration:

```text
DEFAULT_PROVIDER=bedrock
BEDROCK_ENABLED=true
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

Ollama configuration:

```text
DEFAULT_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:3b
```

### Current AWS account limitation

The Bedrock client and model adapter are implemented and can be selected by the router.

However, the current AWS account has an AWS Organizations SCP that denies:

```text
bedrock:InvokeModel
bedrock:InvokeModelWithResponseStream
```

Consequently, actual Bedrock inference is currently blocked in this EKS account.

This means:

> **Bedrock integration is implemented, but Ollama remains the active inference provider in the current AWS environment until the account-level SCP permits Bedrock invocation.**

This is an AWS account permission limitation rather than an application integration gap.

---

## 11. Frontend Settings

Level 7 adds a frontend Settings page.

The settings model covers:

```text
Model
Agent
Guardrails
Evaluation
```

The Model section provides:

```text
LLM Provider
    ├── Ollama
    └── AWS Bedrock

LLM Model

Enable fallback
```

The Save Changes action persists settings in browser storage:

```text
localStorage
    key = ai-analytics-settings
```

The page restores saved settings when reopened.

### Current limitation

Settings are browser-local.

They are not yet:

- backend-managed
- user-account-specific
- shared between browsers
- dynamically propagated into the orchestrator
- stored in ClickHouse

Actual backend model-provider selection is controlled by runtime configuration such as:

```text
DEFAULT_PROVIDER
BEDROCK_ENABLED
BEDROCK_MODEL_ID
OLLAMA_MODEL
```

Therefore, the frontend Settings feature should currently be understood as **persistent UI configuration**, not as a central configuration service.

---

## 12. Observability

Level 7 has two observability layers.

### AI/application observability

The Level 6 orchestrator continues to expose:

```text
GET /evaluations
GET /traces
POST /evaluate
```

Evaluation runs and execution traces are stored in ClickHouse.

Routing decisions include:

```text
provider
complexity
reason
```

Example:

```json
{
  "provider": "ollama",
  "complexity": "low",
  "reason": "settings_provider"
}
```

### Platform observability

The Level 7 platform adds:

```text
Prometheus
Grafana
CloudWatch
CloudWatch Logs
```

This separates AI execution telemetry from Kubernetes/platform telemetry.

---

## 13. Evaluation and Trace Persistence

Level 7 retains the Level 6 evaluation model.

An evaluation produces:

```text
evaluation_id
dataset_id
query
passed
score
score breakdown
diff
replay comparison
trace
```

Execution traces contain:

```text
trace_id
query
steps
latency
created_at
```

The current ClickHouse architecture remains the application data store for evaluation and execution-trace persistence.

A successful Level 7 validation run can be checked with:

```bash
wget -qO- \
  --post-data='{"dataset":[{"id":"level7-final","query":"what time is it","expected_tool":"get_time"}]}' \
  --header='Content-Type: application/json' \
  http://orchestrator-service/evaluate
```

The expected result is a passing evaluation with deterministic replay and a matching execution trace.

---

## 14. Security

Level 7 adds AWS/Kubernetes identity foundations:

```text
IAM
IRSA
EKS OIDC
GitHub OIDC
AWS Load Balancer Controller role
Bedrock role
CloudWatch role
External DNS role
EBS CSI role
EFS CSI role
```

### Credential note

GitHub OIDC is implemented and used by the Terraform plan workflow.

Some bootstrap/deployment workflows still use AWS access-key secrets, so the platform is not yet uniformly OIDC-only.

---

## 15. Data Services

The current Level 7 deployment retains:

```text
ClickHouse
OpenSearch
```

inside Kubernetes.

This is important:

> The current implementation does **not** replace ClickHouse with a managed AWS database and does **not** use Amazon OpenSearch Service.

The application architecture therefore remains consistent with the established Level 6 data model.

---

## 16. Level 6 Preservation

Level 7 does not replace the Level 6 AI control layer.

The existing execution architecture remains:

```text
Planner
    ↓
Repair
    ↓
Guardrails
    ↓
Tool Execution
    ↓
Structured Output Validation
    ↓
Final Answer
```

Evaluation remains available through:

```text
POST /evaluate
GET  /evaluations
```

Tracing remains available through:

```text
GET /traces
```

The model router records the selected provider.

The Level 7 provider-selection work therefore changes the model-provider configuration without redesigning:

- orchestration
- planner/repair workflow
- guardrails
- tools
- retrieval
- evaluation
- trace persistence

---

## 17. Current Production-Hardening Boundaries

Level 7 provides the platform foundation, but the following should not be considered completed merely from the current implementation:

- HPA
- Cluster Autoscaler
- PodDisruptionBudgets
- NetworkPolicies
- canary deployments
- blue/green deployments
- multi-region failover
- full disaster-recovery automation
- full OIDC-only GitHub authentication
- centrally persisted application settings
- container vulnerability scanning in the current Docker workflow

These are appropriate future hardening stages rather than completed Level 7 functionality.

---

## 18. Level Progression

```text
Level 1
Embedding & Data Ingestion
        │
        ▼
Level 2
BM25 Retrieval
        │
        ▼
Level 3
Hybrid RAG
        │
        ▼
Level 4
Advanced RAG + Ranking
        │
        ▼
Level 5
Memory + Agents + Orchestration
        │
        ▼
Level 6
Production Intelligence & Control
        │
        ▼
Level 7
Cloud-Native AWS Platform
```

---

## 19. Level 7 Definition of Done

The current Level 7 implementation establishes:

- [x] Terraform AWS platform
- [x] Amazon EKS
- [x] Amazon ECR
- [x] Kubernetes/Helm deployment
- [x] GitHub Actions automation
- [x] ClickHouse deployment
- [x] OpenSearch deployment
- [x] Prometheus
- [x] Grafana
- [x] CloudWatch integration
- [x] IAM/IRSA
- [x] GitHub OIDC foundation
- [x] repository validation
- [x] Level 6 evaluations
- [x] Level 6 execution traces
- [x] Settings persistence
- [x] Ollama provider routing
- [x] AWS Bedrock provider integration
- [x] Bedrock streaming integration
- [x] Ollama/Bedrock provider selection in Settings

The Level 7 platform is therefore best described as a **cloud-native AWS foundation for the existing AI Analytics Copilot**, with multi-provider LLM integration, rather than a claim that every enterprise production-hardening capability has already been implemented.

---

## 20. Quick Validation

### Check the EKS workloads

```bash
kubectl get pods -A
```

### Check application services

```bash
kubectl get svc -A
```

### Check orchestrator routes

```bash
kubectl exec -it deployment/orchestrator-service -n ai-analytics -- python -c "
from main import app
for r in app.routes:
    print(r.path, r.methods)
"
```

Expected Level 6/7 routes include:

```text
/health
/ask
/ask-stream
/evaluate
/evaluations
/traces
```

### Check backend provider configuration

```bash
kubectl exec deployment/orchestrator-service -n ai-analytics -- \
  env | grep -E 'DEFAULT_PROVIDER|BEDROCK_ENABLED|BEDROCK_MODEL_ID|OLLAMA_MODEL'
```

### Check model router

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

### Check evaluations

```bash
wget -qO- http://orchestrator-service/evaluations
```

### Check traces

```bash
wget -qO- http://orchestrator-service/traces
```

### Check ClickHouse persistence

```bash
kubectl exec -it deployment/orchestrator-service -n ai-analytics -- python -c "
from clickhouse_driver import Client

c = Client(
    host='clickhouse.data.svc.cluster.local',
    port=9000,
    database='ai_evaluation',
    user='admin',
    password='admin123'
)

print('evaluation_runs_all:',
      c.execute('SELECT count() FROM ai_evaluation.evaluation_runs_all'))

print('execution_traces_all:',
      c.execute('SELECT count() FROM ai_evaluation.execution_traces_all'))
"
```

---

## 21. Level 7 Freeze

Level 7 is considered **frozen** at this point.

The frozen scope includes:

- AWS/EKS platform foundation
- Terraform infrastructure
- ECR
- Kubernetes and Helm deployment
- GitHub Actions automation
- ClickHouse/OpenSearch Kubernetes deployment
- Prometheus/Grafana/CloudWatch observability
- IAM/IRSA and GitHub OIDC foundations
- Level 6 evaluation and trace preservation
- frontend Settings persistence
- Ollama provider support
- AWS Bedrock provider support
- provider-aware model routing

Future improvements such as HPA, Cluster Autoscaler, central settings management, stronger deployment strategies, full OIDC-only workflows, and disaster recovery should be treated as **future hardening or a subsequent level**, rather than silently added to the frozen Level 7 scope.

---

## 22. Final Architecture Statement

Level 7 is the infrastructure and operations layer around the existing AI system:

```text
Level 6
AI Intelligence + Control
        +
Level 7
AWS + Kubernetes + CI/CD + Observability + LLM Provider Integration
        =
Cloud-Native AI Analytics Copilot
```

The result is a reproducible AWS/EKS platform that preserves the Level 6 AI control layer while adding the infrastructure, deployment automation, identity, observability, provider selection and operational foundations required for continued production hardening.

---

# End of Level 7 README
