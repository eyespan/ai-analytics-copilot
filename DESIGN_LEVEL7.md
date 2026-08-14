# AI Analytics Copilot – Level 7
# Cloud-Native AWS Platform

---

## 1. Vision

Level 7 moves the AI Analytics Copilot from a production-oriented AI platform toward a **cloud-native AWS deployment platform**.

Level 7 does **not introduce a new AI capability layer**. The primary change is operational and infrastructural:

- AWS infrastructure is defined with Terraform.
- Amazon EKS becomes the Kubernetes runtime.
- GitHub Actions provides reusable build, validation, infrastructure, and deployment workflows.
- Helm manages Kubernetes application deployments.
- Amazon ECR stores application images.
- Prometheus, Grafana, and CloudWatch provide platform observability.
- ClickHouse and OpenSearch remain Kubernetes-hosted data services in the current implementation.
- Ollama remains available for the development/runtime path used by the current cluster.
- AWS Bedrock is supported through the existing Level 5/6 model-routing abstraction and is selectable as an LLM provider.

The Level 7 implementation therefore focuses on **cloud infrastructure, Kubernetes, automation, deployment repeatability, security integration, operational foundations, and provider selection**, while preserving the Level 6 AI orchestration, guardrails, tracing, and evaluation capabilities.

---

## 2. Scope

### Implemented Level 7 capabilities

| Area | Status | Implementation |
|---|---|---|
| Terraform AWS infrastructure | Implemented | VPC, EKS, ECR, IAM and supporting modules |
| Kubernetes platform | Implemented | EKS, namespaces, add-ons and Helm deployments |
| GitHub Actions | Implemented | Reusable build/deploy/apply/validation workflows |
| Amazon ECR | Implemented | Application image repositories and lifecycle configuration |
| Helm deployment | Implemented | Reusable application chart and deployment workflow |
| ClickHouse on Kubernetes | Implemented | Stateful deployment plus initialization/seed jobs |
| OpenSearch on Kubernetes | Implemented | Stateful deployment plus initialization job |
| Prometheus | Implemented | kube-prometheus-stack deployment |
| Grafana | Implemented | Included with kube-prometheus-stack |
| CloudWatch integration | Implemented | EKS/CloudWatch configuration and IRSA support |
| AWS Load Balancer Controller | Implemented | Helm deployment plus IRSA |
| External DNS | Implemented | Kubernetes add-on and IAM/IRSA support |
| cert-manager | Implemented | Kubernetes add-on configuration |
| EBS CSI | Implemented | EKS add-on/IRSA integration |
| EFS CSI | Implemented | IRSA/add-on configuration |
| GitHub OIDC | Implemented | IAM OIDC provider/role infrastructure |
| Repository validation | Implemented | Terraform, Helm, Kubernetes, Dockerfile, Python and unit-test validation |
| Frontend settings persistence | Implemented | Browser `localStorage` |
| LLM provider selection | Implemented | Frontend provider/model selection plus backend routing configuration |
| Ollama routing | Implemented | Existing model router/provider |
| AWS Bedrock routing | Implemented | Existing Bedrock client/model adapter and routing path |
| Level 6 evaluation/tracing | Preserved | Orchestrator evaluation and execution-trace APIs remain available |

### Not claimed as implemented

The design deliberately does **not** claim the following as completed Level 7 capabilities because they are not demonstrated by the current implementation:

- Container vulnerability scanning in the Docker build workflow
- Horizontal Pod Autoscaler resources
- Cluster Autoscaler
- Pod Disruption Budgets
- Kubernetes NetworkPolicy resources
- Canary deployments
- Blue/green deployments
- A completed disaster-recovery implementation
- Multi-region deployment
- A dedicated Kubernetes Evaluation Service
- A dedicated Kubernetes Reranking Service
- Amazon OpenSearch Service
- Amazon EFS resource provisioning
- AWS Certificate Manager resource provisioning
- Route 53 hosted-zone provisioning
- Backend/database-backed application settings
- Dynamic runtime application of browser-local settings to the orchestrator

These may be future hardening areas, but they are not represented as completed Level 7 features.

---

## 3. High-Level Architecture

```text
                         Developer
                             │
                             ▼
                          GitHub
                             │
                             ▼
                      GitHub Actions
                     /      |       \
              Validate    Build    Terraform
                          │           │
                          ▼           ▼
                         ECR        AWS Platform
                                      │
                                      ▼
                                     EKS
                                      │
              ┌───────────────────────┼────────────────────────┐
              │                       │                        │
              ▼                       ▼                        ▼
        API Gateway             Orchestrator               Frontend
                                      │
                         ┌────────────┼────────────┐
                         │            │            │
                         ▼            ▼            ▼
                        RAG       Evaluation     Tracing
                         │
               ┌─────────┼───────────┐
               ▼         ▼           ▼
          ClickHouse  OpenSearch   Model Router
                                      │
                              ┌───────┴────────┐
                              ▼                ▼
                           Ollama          AWS Bedrock
```

The model router remains part of the existing AI application layer. Level 7 does not replace the Level 6 orchestration architecture.

---

## 4. Architectural Principles

### Infrastructure as Code

Terraform defines the core AWS platform and reusable modules.

The Level 7 Terraform structure includes:

```text
terraform/
├── environments/
│   └── dev/
└── modules/
    ├── vpc/
    ├── eks/
    ├── ecr/
    ├── iam/
    ├── iam-irsa/
    ├── networking/
    ├── cloudwatch/
    └── kubernetes/
        ├── addons/
        └── namespaces/
```

Terraform therefore provides a repeatable and version-controlled foundation for the AWS platform.

### Kubernetes First

Application workloads are deployed into Amazon EKS rather than directly onto EC2 instances.

The current platform also deploys infrastructure/data workloads such as ClickHouse and OpenSearch into Kubernetes.

### Immutable Container Deployment

Application images are built and pushed to ECR with explicit image tags. Helm then deploys the selected image tag into Kubernetes.

### GitHub-Centred Automation

GitHub Actions contains reusable workflows for:

- Docker builds
- Helm deployments
- Kubernetes manifest application
- Terraform plan
- Terraform apply
- repository validation
- platform bootstrap

The current implementation is automation-oriented rather than a fully GitOps controller-based platform.

---

## 5. Amazon EKS Platform

Amazon EKS is the Kubernetes runtime for the Level 7 environment.

The platform includes application workloads such as:

```text
API Gateway
Orchestrator Service
RAG Service
Embedding Service
Indexer Service
Frontend
```

The current environment also deploys:

```text
Ollama
ClickHouse
OpenSearch
Prometheus
Grafana
Ingress NGINX
AWS Load Balancer Controller
```

EKS add-ons and supporting integrations include:

```text
VPC CNI
CoreDNS
kube-proxy
EBS CSI
EFS CSI integration
External DNS
cert-manager
CloudWatch integration
```

The current implementation supports rolling Kubernetes deployments and readiness verification through the reusable Helm deployment workflow.

AWS Bedrock is **not a Kubernetes workload**. It is an external AWS managed model service accessed by the orchestrator through the Bedrock runtime API.

---

## 6. Terraform Infrastructure

The development environment wires reusable modules for:

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

The EKS module includes cluster, node-group, OIDC and Kubernetes storage/add-on integration.

The IAM/IRSA modules provide AWS permissions for Kubernetes workloads such as:

- AWS Load Balancer Controller
- Bedrock access
- CloudWatch
- EBS CSI
- External DNS
- EFS CSI

### Bootstrap distinction

Not every AWS bootstrap operation is Terraform-managed.

The Level 7 repository also contains GitHub Actions bootstrap logic that can create/configure:

- the GitHub OIDC provider
- the GitHub Actions IAM role
- the Terraform state S3 bucket
- state bucket versioning/encryption/public-access blocking

Therefore:

> Terraform manages the core application/platform infrastructure, while bootstrap workflows establish prerequisites required for the Terraform and deployment pipeline.

---

## 7. GitHub Actions

The Level 7 repository introduces reusable workflows for:

```text
bootstrap.yml
bootstrap-cluster.yml
docker-build.yml
build-docker-images.yml
build-ml-base.yml
helm-deploy.yml
kubectl-apply.yml
terraform-plan.yml
terraform-apply.yml
validate.yml
deploy-dev.yml
```

### Validation pipeline

The repository validation workflow covers:

```text
Python setup
    ↓
Development dependencies
    ↓
Terraform format
    ↓
Terraform validation
    ↓
Helm lint
    ↓
Kubernetes manifest validation
    ↓
Dockerfile validation
    ↓
isort
    ↓
Black
    ↓
flake8
    ↓
Unit tests
```

### Image pipeline

The reusable Docker workflow:

```text
Select service
      ↓
Build image
      ↓
Tag image
      ↓
Push image to ECR
```

The current Docker build workflow does not include a container vulnerability scanner; therefore security scanning should not be represented as a completed pipeline stage.

---

## 8. Helm and Kubernetes Deployment

A reusable application Helm chart is used for Kubernetes application deployments.

The reusable Helm deployment workflow supports:

- configurable namespace
- chart/repository selection
- values files
- image repository/tag injection
- additional Helm values
- readiness verification
- deployment-specific rollout handling

The platform also uses Kubernetes manifests/jobs for initialization tasks such as:

- ClickHouse schema initialization
- ClickHouse seed data
- OpenSearch index initialization
- embedding ingestion
- Ollama model initialization

---

## 9. Container Registry

Amazon ECR is the private container registry.

The Level 7 Docker workflow builds application images and pushes them to:

```text
<account>.dkr.ecr.us-east-1.amazonaws.com/<service>:<tag>
```

The ECR Terraform module provides repositories and lifecycle configuration.

---

## 10. Data and Storage Architecture

The current Level 7 implementation retains Kubernetes-hosted data services:

```text
ClickHouse
OpenSearch
```

Persistent Kubernetes storage is supported through EKS storage integrations including EBS CSI and EFS CSI configuration.

The architecture does **not** currently provision an AWS EFS filesystem resource directly in the Level 7 Terraform implementation, so EFS should be treated as an integration capability rather than a fully provisioned managed storage service in this design.

ClickHouse remains the evaluation and execution-trace data store used by the application.

---

## 11. LLM Provider Architecture

Level 7 exposes the existing multi-provider model-routing capability through the application configuration and frontend Settings experience.

### Supported provider choices

```text
Ollama
AWS Bedrock
```

The provider abstraction remains:

```text
ModelRouter
    │
    ├── OllamaModel
    │      └── OllamaClient
    │
    └── BedrockModel
           └── BedrockClient
```

The existing routing policy continues to produce a `RoutingDecision` containing:

```json
{
  "provider": "ollama",
  "complexity": "low",
  "reason": "settings_provider"
}
```

or:

```json
{
  "provider": "bedrock",
  "complexity": "low",
  "reason": "settings_provider"
}
```

The selected executable model is then obtained through the existing `ModelRouter.get_model()` path.

### Ollama

The current Kubernetes environment uses:

```text
OLLAMA_MODEL=qwen2.5:3b
```

Ollama is the currently operational inference provider in the EKS environment.

### AWS Bedrock

The Bedrock integration uses:

```text
BEDROCK_ENABLED=true
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

The Bedrock client supports both:

- non-streaming model invocation
- streaming model invocation

The Bedrock path is integrated without changing the Level 6 orchestration, guardrails, evaluation, trace, retrieval, or agent execution architecture.

### Provider configuration

The backend routing configuration uses:

```text
DEFAULT_PROVIDER=ollama
BEDROCK_ENABLED=true
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
OLLAMA_MODEL=qwen2.5:3b
```

For example:

```text
DEFAULT_PROVIDER=ollama
```

causes the router to select Ollama when the configured provider is used.

A Bedrock deployment can instead use:

```text
DEFAULT_PROVIDER=bedrock
```

provided that Bedrock is enabled and the AWS account permits the required Bedrock API calls.

### Current AWS environment limitation

The current EKS AWS account has been tested with the Bedrock client and model adapter. The client can be constructed and the router can select:

```text
bedrock:anthropic.claude-3-haiku-20240307-v1:0
```

However, actual Bedrock inference in the current AWS account is blocked by an AWS Organizations service-control policy (`SCP`) denying:

```text
bedrock:InvokeModel
bedrock:InvokeModelWithResponseStream
```

Therefore:

> **Bedrock support is implemented and integrated, but Ollama remains the operational inference provider in the current EKS account until the account-level SCP permits Bedrock invocation.**

This is an environment permission limitation, not a missing application integration.

---

## 12. Security Architecture

Level 7 adds AWS/Kubernetes security foundations including:

- IAM
- IAM Roles for Service Accounts (IRSA)
- EKS OIDC integration
- Kubernetes service accounts
- AWS Load Balancer Controller IAM permissions
- Bedrock IAM permissions
- CloudWatch IAM permissions
- External DNS IAM permissions
- EBS/EFS CSI IAM permissions
- Kubernetes namespace isolation

The platform also introduces GitHub OIDC infrastructure.

### Credential caveat

The Level 7 workflows are not yet uniformly OIDC-only.

The Terraform plan workflow uses GitHub OIDC to assume the GitHub Actions IAM role, while several bootstrap/deployment workflows still use AWS access-key secrets.

Therefore:

> GitHub OIDC is implemented and used by the Terraform plan path, but complete removal of long-lived AWS access-key credentials from all workflows remains future hardening.

---

## 13. Observability

Level 6 execution tracing and evaluation are retained.

Level 7 adds platform-level observability using:

```text
Prometheus
Grafana
CloudWatch
CloudWatch Logs
```

The application layer continues to expose:

```text
/evaluations
/traces
/evaluate
```

The orchestrator persists evaluation and execution-trace information in ClickHouse.

This creates two complementary observability layers:

```text
Application / AI observability
    ├── evaluation runs
    ├── execution traces
    ├── tool execution
    ├── model routing
    └── agent workflow

Platform observability
    ├── Kubernetes metrics
    ├── Prometheus
    ├── Grafana
    └── CloudWatch
```

Model-routing decisions include the selected provider, query complexity, and routing reason.

---

## 14. Frontend Settings

Level 7 introduces a Settings page and typed settings model.

The settings model contains:

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

The Settings page supports:

```text
LLM Provider
    ├── Ollama
    └── AWS Bedrock

LLM Model

Enable fallback
```

The Settings → Save Changes action persists the configuration in browser `localStorage` under:

```text
ai-analytics-settings
```

The page reloads saved values and merges them with defaults.

### Important scope boundary

These settings are currently **frontend-local configuration**.

They are not yet:

- stored in ClickHouse
- stored in a backend configuration service
- shared across users/devices
- automatically propagated from browser `localStorage` into the orchestrator process

The backend model router continues to use its runtime configuration, including:

```text
DEFAULT_PROVIDER
BEDROCK_ENABLED
BEDROCK_MODEL_ID
OLLAMA_MODEL
```

Therefore the frontend provider selection is currently a persisted configuration/UI capability, while actual orchestrator provider selection is controlled by backend runtime configuration.

This distinction is intentional and prevents the Level 7 Settings feature from being incorrectly represented as a central configuration-management system.

---

## 15. Level 6 Preservation

Level 7 does not replace the Level 6 AI control layer.

The following remain intact:

```text
Planner
    ↓
Repair
    ↓
Guardrail validation
    ↓
Tool execution
    ↓
Structured output validation
    ↓
Final answer
```

Level 6 evaluation remains available through:

```text
POST /evaluate
GET  /evaluations
```

Execution tracing remains available through:

```text
GET /traces
```

The model-routing layer continues to record provider metadata.

The current evaluation test demonstrated:

```text
total: 1
passed: 1
failed: 0
score: 1.0
```

with deterministic replay and trace matching.

The successful Level 6 `get_time` planner/tool workflow therefore remains operational after the Level 7 provider-selection changes.

---

## 16. Autoscaling and Resilience

The Level 7 platform provides Kubernetes deployment foundations and EKS node groups, but the current implementation does not demonstrate completed HPA or Cluster Autoscaler resources.

| Capability | Status |
|---|---|
| EKS node groups | Implemented |
| Kubernetes deployment readiness checks | Implemented |
| Rolling deployment mechanism | Implemented |
| HPA | Not demonstrated |
| Cluster Autoscaler | Not demonstrated |
| PodDisruptionBudget | Not demonstrated |
| NetworkPolicy | Not demonstrated |
| Multi-region deployment | Not demonstrated |
| Disaster recovery automation | Not demonstrated |

These remain future production-hardening areas.

---

## 17. Production Operations

Implemented operational foundations include:

- Kubernetes readiness verification
- Helm-based deployment
- rollout status checking
- reusable deployment workflows
- initialization jobs
- EKS managed node groups
- Prometheus/Grafana monitoring
- CloudWatch integration
- load balancer controller integration
- external DNS integration
- cert-manager integration

The current implementation should not yet claim complete:

- disaster recovery
- multi-region failover
- canary deployment
- blue/green deployment
- automated rollback orchestration

without additional implementation.

---

## 18. Level 7 Success Criteria

The following represents the implementation state reflected by the Level 7 implementation and subsequent provider-selection work:

| Requirement | Status |
|---|---|
| Terraform provisions core AWS platform | ✅ |
| Amazon EKS hosts Kubernetes workloads | ✅ |
| Amazon ECR stores application images | ✅ |
| GitHub Actions automates builds/deployments | ✅ |
| Helm manages application deployments | ✅ |
| ClickHouse runs in Kubernetes | ✅ |
| OpenSearch runs in Kubernetes | ✅ |
| Prometheus deployed | ✅ |
| Grafana deployed | ✅ |
| CloudWatch integration present | ✅ |
| IAM/IRSA foundations present | ✅ |
| GitHub OIDC infrastructure present | ✅ |
| Repository validation workflow present | ✅ |
| Level 6 evaluations retained | ✅ |
| Level 6 execution traces retained | ✅ |
| Frontend settings persistence | ✅ |
| Ollama provider routing | ✅ |
| AWS Bedrock provider integration | ✅ |
| Bedrock streaming integration | ✅ |
| Frontend Ollama/Bedrock selection | ✅ |
| HPA | ⏳ |
| Cluster Autoscaler | ⏳ |
| Canary deployment | ⏳ |
| Blue/green deployment | ⏳ |
| Full OIDC-only GitHub authentication | ⏳ |
| Central backend settings persistence | ⏳ |
| Bedrock invocation in current AWS account | Blocked by SCP |

---

## 19. Architectural Shift

| Level | Primary Focus |
|---|---|
| Level 1 | Embedding & Data Ingestion |
| Level 2 | BM25 Retrieval |
| Level 3 | Hybrid RAG |
| Level 4 | Advanced RAG + Ranking Intelligence |
| Level 5 | Memory, Agents & Orchestration |
| Level 6 | Production Intelligence & Control |
| **Level 7** | **Cloud-Native AWS Platform** |

Level 7 therefore represents a shift from improving the AI system itself to making the existing AI system **deployable, repeatable, observable and operable on AWS/Kubernetes**, while exposing the existing multi-provider LLM routing capability through the platform.

---

## 20. Level 7 Freeze

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

## 21. Architectural Outcome

The Level 7 implementation establishes a cloud-native AI Analytics Copilot using:

```text
Amazon EKS
Terraform
GitHub Actions
Helm
Amazon ECR
ClickHouse
OpenSearch
Ollama
AWS Bedrock integration
Prometheus
Grafana
CloudWatch
IAM / IRSA
GitHub OIDC
Kubernetes
```

The Level 6 AI control layer remains intact.

The result is a platform that can be built, provisioned, deployed and operated through repeatable infrastructure and CI/CD workflows, while retaining the existing agent, guardrail, evaluation, model-routing and execution-tracing capabilities.

---

# End of Level 7 Design
