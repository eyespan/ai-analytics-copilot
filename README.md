# AI Analytics Copilot

> **Engineering Portfolio Project**
>
> AI Analytics Copilot is an independently designed and developed cloud-native AI platform demonstrating production-oriented AWS, Kubernetes, MLOps, LLM orchestration, RAG, evaluation, observability, and infrastructure engineering.

> A production-oriented, cloud-native AI analytics platform built progressively from data ingestion and retrieval through RAG, agentic orchestration, production controls, and AWS deployment.

**Repository:** https://github.com/eyespan/ai-analytics-copilot

---

## Project Objective

The **AI Analytics Copilot** is a progressive engineering project that demonstrates how an AI-powered analytics platform can evolve from a local prototype into a production-oriented, cloud-native system.

The project is intentionally developed through a sequence of architectural levels. Each level introduces a clearly defined capability while preserving and extending the work completed previously.

The overall journey is:

```text
Data & Embeddings
        ↓
Keyword Retrieval
        ↓
Hybrid RAG
        ↓
Advanced Retrieval & Ranking
        ↓
Memory, Agents & Orchestration
        ↓
Production Intelligence & Control
        ↓
Cloud-Native AWS Platform
```

The result is a platform combining:

- Data ingestion and indexing
- Embeddings and semantic search
- BM25 and hybrid retrieval
- Reranking
- Retrieval-augmented generation
- LLM model routing
- Agent planning and execution
- Tool use
- Memory and workflow state
- Guardrails
- Structured outputs
- Evaluation and trace replay
- Deterministic execution traces
- Kubernetes deployment
- Terraform infrastructure as code
- GitHub Actions CI/CD
- Amazon EKS and Amazon ECR
- AWS Bedrock and local Ollama model support
- Prometheus and Grafana observability
- Production-oriented operational controls

---

# Project Roadmap

The repository is organised around seven architectural levels.

| Level | Focus | Primary Objective |
|---|---|---|
| Level 1 | Embedding & Data Ingestion | Establish the data and embedding foundation |
| Level 2 | BM25 Retrieval | Introduce keyword-based retrieval |
| Level 3 | Hybrid RAG | Combine semantic and keyword retrieval |
| Level 4 | Advanced RAG + Ranking Intelligence | Improve retrieval quality and ranking |
| Level 5 | Memory, Agents & Orchestration | Introduce agents, tools, memory and orchestration |
| Level 6 | Production Intelligence & Control | Add guardrails, evaluation, tracing and controlled execution |
| **Level 7** | **Cloud-Native AWS Platform** | Move the platform to production-oriented AWS/EKS infrastructure |

## Level Design Documentation

Each level has its own detailed design document.

- [`DESIGN_LEVEL1.md`](DESIGN_LEVEL1.md)
- [`DESIGN_LEVEL2.md`](DESIGN_LEVEL2.md)
- [`DESIGN_LEVEL3.md`](DESIGN_LEVEL3.md)
- [`DESIGN_LEVEL4.md`](DESIGN_LEVEL4.md)
- [`DESIGN_LEVEL5.md`](DESIGN_LEVEL5.md)
- [`DESIGN_LEVEL6.md`](DESIGN_LEVEL6.md)
- [`DESIGN_LEVEL7.md`](DESIGN_LEVEL7.md)

The design documents explain the architectural objectives, implementation decisions, components, constraints, and success criteria for each stage.

---

# Level 7 — Cloud-Native AWS Platform

Level 7 does not introduce a new AI capability. Instead, it transforms the production-oriented platform developed through Levels 1–6 into a cloud-native AWS deployment.

The Level 7 objectives are:

- Cloud-native deployment
- Infrastructure as Code
- Kubernetes orchestration
- Automated CI/CD
- Enterprise-oriented operations

Amazon EKS becomes the primary production runtime while Docker Compose remains the local development environment.

The Level 7 architecture incorporates:

```text
Developer
   │
   ▼
GitHub
   │
   ▼
GitHub Actions
   │
   ├── Terraform
   │
   ├── Docker Builds
   │
   └── Helm
   │
   ▼
AWS
 ├── EKS
 ├── ECR
 ├── Bedrock
 ├── OpenSearch
 ├── CloudWatch
 └── supporting infrastructure
```

Level 7 also retains Ollama as a useful local/development model provider while allowing AWS Bedrock to be selected through the model-routing layer where the AWS environment permits Bedrock access.

See [`DESIGN_LEVEL7.md`](DESIGN_LEVEL7.md) for the complete architecture.

---

# Architecture

At a high level, the platform is composed of:

```text
                         ┌──────────────────┐
                         │     Frontend     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   API Gateway    │
                         └────────┬─────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │    Orchestrator Service  │
                    │                          │
                    │ Planning / Agents        │
                    │ Tool Execution            │
                    │ Guardrails                 │
                    │ Evaluation                 │
                    │ Trace Management           │
                    │ Model Routing              │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
        ┌───────────┐      ┌────────────┐     ┌─────────────┐
        │   RAG     │      │ LLM Router │     │   Tools     │
        │  Service  │      │            │     │             │
        └─────┬─────┘      └─────┬──────┘     └─────────────┘
              │                  │
              ▼                  ▼
        ┌───────────┐       ┌──────────────┐
        │ OpenSearch│       │ Ollama       │
        │           │       │ AWS Bedrock  │
        └───────────┘       └──────────────┘

              Data / Evaluation / Observability
                         │
          ┌──────────────┼───────────────┐
          ▼              ▼               ▼
     ClickHouse      Prometheus       Grafana
```

The exact implementation is documented in the component READMEs and Level design documents.

---

# Documentation Map

The repository contains documentation at both the architectural and component level.

## Core Architecture

| Area | Documentation |
|---|---|
| Project overview | [`README.md`](README.md) |
| Level 1 | [`DESIGN_LEVEL1.md`](DESIGN_LEVEL1.md) |
| Level 2 | [`DESIGN_LEVEL2.md`](DESIGN_LEVEL2.md) |
| Level 3 | [`DESIGN_LEVEL3.md`](DESIGN_LEVEL3.md) |
| Level 4 | [`DESIGN_LEVEL4.md`](DESIGN_LEVEL4.md) |
| Level 5 | [`DESIGN_LEVEL5.md`](DESIGN_LEVEL5.md) |
| Level 6 | [`DESIGN_LEVEL6.md`](DESIGN_LEVEL6.md) |
| Level 7 | [`DESIGN_LEVEL7.md`](DESIGN_LEVEL7.md) |

## Application Components

| Component | Documentation |
|---|---|
| API Gateway | [`apps/api-gateway/README.md`](apps/api-gateway/README.md) |
| Orchestrator | [`orchestrator-service/README.md`](orchestrator-service/README.md) |
| LLM Service | [`llm-service/README.md`](llm-service/README.md) |
| Providers | [`providers/README.md`](providers/README.md) |
| RAG Service | [`apps/rag-service/README.md`](apps/rag-service/README.md) |
| Indexer Service | [`apps/indexer-service/README.md`](apps/indexer-service/README.md) |
| Embedding Service | [`apps/embedding-service/README.md`](apps/embedding-service/README.md) |
| Frontend | [`apps/frontend/README.md`](apps/frontend/README.md) |

## Infrastructure and Operations

| Area | Documentation |
|---|---|
| Infrastructure | [`infra/README.md`](infra/README.md) |
| GitHub Actions / CI/CD | [`.github/workflows/README.md`](.github/workflows/README.md) |
| Terraform | [`infra/`](infra/) |
| Kubernetes / Helm | [`helm/`](helm/) |
| Monitoring | See infrastructure and monitoring documentation |
| EKS / EKS add-ons | See [`infra/README.md`](infra/README.md) |

---

# Deploy the Project

The project can be deployed to AWS using the repository's GitHub Actions workflows.

The deployment process is deliberately staged because the later workflows depend on infrastructure and container images created by earlier workflows.

The overall deployment sequence is:

```text
GitHub Repository Secrets
          │
          ▼
Bootstrap AWS OIDC
          │
          ▼
Terraform Plan
          │
          ▼
Terraform Apply
          │
          ▼
EKS + ECR
          │
          ▼
Build ML Base Image
          │
          ▼
Docker Image Builder
          │
          ▼
Bootstrap Kubernetes Platform
          │
          ▼
Deploy Dev
```

## Prerequisites

You need:

- An AWS account with the permissions required by the project's Terraform and deployment configuration
- A fork or clone of the repository
- A GitHub repository with Actions enabled
- AWS credentials suitable for bootstrapping the initial OIDC configuration

## 1. Configure GitHub Repository Secrets

In the GitHub repository:

**Settings → Secrets and variables → Actions → Repository secrets**

Create:

```text
AWS_ACCOUNT_ID
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

These are used by the initial GitHub Actions bootstrap process.

> Do not commit AWS credentials to the repository.

## 2. Bootstrap AWS OIDC

Run the:

**Bootstrap AWS OIDC** workflow.

This establishes the IAM role used by Terraform and subsequent GitHub Actions workflows to authenticate to AWS.

After this workflow completes successfully, the deployment pipeline can use the configured AWS IAM role rather than relying on long-lived credentials for normal deployment operations.

## 3. Run Terraform Plan

Run:

**Terraform Plan**

Review the proposed infrastructure changes.

Do not proceed to Terraform Apply until the plan completes successfully and the proposed changes are understood.

## 4. Run Terraform Apply

Run:

**Terraform Apply**

Wait for the workflow to complete successfully.

This provisions the AWS infrastructure required by the platform, including the EKS cluster and ECR repositories.

The later container and Kubernetes workflows depend on this infrastructure existing.

## 5. Build the ML Base Image

Once Terraform Apply has completed successfully, run:

**Build ML Base Image**

This creates the ML base image and publishes it to Amazon ECR.

The image provides the common machine-learning runtime used by the relevant services.

## 6. Build Application Container Images

Run:

**Docker Image Builder**

The workflow builds the project's application and supporting images, including:

```text
api-gateway
embedding-service
indexer-service
rag-service
orchestrator-service
frontend
clickhouse-seed
embedding-ingest
```

The resulting images are uploaded to Amazon ECR.

## 7. Bootstrap the Kubernetes Platform

After the required infrastructure and images are available, run:

**Bootstrap Kubernetes Platform**

This prepares the EKS cluster and installs/configures the Kubernetes platform components required by the application deployment.

This stage includes the platform-level Kubernetes and AWS integrations required by the workloads.

## 8. Deploy Dev

Finally run:

**Deploy Dev**

This deploys the application workloads into the EKS environment.

At this point the deployment flow is:

```text
AWS Infrastructure
       ↓
EKS / ECR
       ↓
Container Images
       ↓
Kubernetes Platform
       ↓
AI Analytics Copilot
```

## 9. Access the Frontend

Once the **Deploy Dev** workflow has completed successfully, the application can be accessed through the AWS Application Load Balancer (ALB) created for the Kubernetes Ingress.

### 9.1 Get the ALB URL

Run:

```bash
kubectl get ingress -n ai-analytics
```

You should see output similar to:

```bash
NAME        CLASS   HOSTS   ADDRESS
frontend    nginx   *       k8s-frontend-xxxxxxxx.eu-west-1.elb.amazonaws.com
```

The value in the ADDRESS column is the ALB endpoint.

You can also query the frontend ingress directly:

```bash
kubectl get ingress frontend -n ai-analytics
```

### 9.2 Open the Frontend

Copy the ADDRESS value and open it in a web browser:

```bash
http://<ALB-ADDRESS>
```

For example:

```bash
http://k8s-frontend-xxxxxxxx.eu-west-1.elb.amazonaws.com
```

The AI Analytics Copilot frontend should then be displayed.

### 9.3 Verify the Frontend Deployment

Before accessing the application, verify that the frontend pods are running:
```bash
kubectl get pods -n ai-analytics
```

Verify the frontend service:
```bash
kubectl get svc -n ai-analytics
```

Verify the ingress:
```bash
kubectl get ingress -n ai-analytics
```

For additional troubleshooting information:
```bash
kubectl describe ingress frontend -n ai-analytics
```

### 9.4 If the ALB Address Is Pending

The AWS load balancer may take several minutes to be provisioned after the ingress is created.

Monitor the ingress until an address appears:
```bash
kubectl get ingress -n ai-analytics -w
```
Wait until the ADDRESS column contains the AWS load balancer hostname.

###    9.5 Application Request Path

The deployed frontend request path is:
```text
Internet
    │
    ▼
AWS Application Load Balancer
    │
    ▼
Kubernetes Ingress
    │
    ▼
Frontend Service
    │
    ▼
Frontend Pod
```

The frontend then communicates with the application API through the configured API Gateway.

> Note: ```kubectl port-forward ``` is useful for local troubleshooting, but the ALB Ingress URL is the normal way to access the deployed application in the AWS/EKS environment.


### Detailed deployment documentation

For the full operational procedure, workflow dependencies, troubleshooting guidance and infrastructure details, see:

- [`infra/README.md`](infra/README.md)
- [`.github/workflows/README.md`](.github/workflows/README.md)

---

# Local Development

Docker Compose remains the local development environment.

This allows the platform to be developed and tested without requiring the complete AWS/EKS deployment.

The local environment is particularly useful for:

- Application development
- RAG testing
- Model-routing development
- Agent and tool testing
- Evaluation development
- Trace testing
- Local Ollama execution

The AWS/EKS environment is the cloud deployment target.

---

# Model Providers

The platform uses a model-routing abstraction so that the orchestration layer is not tightly coupled to a single LLM provider.

Current provider choices include:

```text
Ollama
AWS Bedrock
OpenAI
```

The Level 7 deployment configuration supports selecting the provider/model through the platform settings and routing configuration.

## Ollama

Ollama provides a local model runtime and is particularly useful for development and testing.

Example model:

```text
qwen2.5:3b
```

## AWS Bedrock

AWS Bedrock provides the cloud-hosted model path.

The current configuration includes support for Anthropic Claude models through Bedrock.

Example:

```text
anthropic.claude-3-haiku-20240307-v1:0
```

Bedrock availability is dependent on the AWS account, region, IAM permissions and applicable AWS organizational policies.

The model-routing layer can therefore support Bedrock even when a particular development AWS account does not permit Bedrock invocation.

---

# Evaluation and Observability

Production-oriented controls introduced in Level 6 remain part of the platform as it moves into Level 7.

The system includes:

- Execution traces
- Tool execution traces
- Model-routing traces
- Retrieval traces
- Evaluation results
- Evaluation replay
- Deterministic trace comparison
- Guardrail validation
- Structured output validation
- Prometheus metrics
- Grafana dashboards
- CloudWatch integration

The objective is that cloud deployment does not remove the control and evaluation discipline established in Level 6.

---

# Infrastructure

Level 7 uses Infrastructure as Code and Kubernetes.

The AWS infrastructure includes the platform required for:

- Amazon VPC
- Public and private networking
- IAM
- Amazon EKS
- Amazon ECR
- Load balancing
- DNS
- TLS certificates
- Persistent storage
- CloudWatch
- Kubernetes platform components

Terraform provides the infrastructure provisioning layer.

Helm provides Kubernetes application deployment.

GitHub Actions provides the workflow orchestration.

See [`infra/README.md`](infra/README.md) for the detailed infrastructure documentation.

---

# CI/CD

The repository uses GitHub Actions for infrastructure and application delivery.

The deployment process is intentionally separated into stages:

```text
AWS Bootstrap
     ↓
Infrastructure
     ↓
Container Images
     ↓
Kubernetes Platform
     ↓
Application Deployment
```

This separation makes infrastructure failures, image build failures and Kubernetes deployment failures easier to identify and recover from.

See [`.github/workflows/README.md`](.github/workflows/README.md) for the workflow documentation.

---

# Forking the Project

The repository is designed so that each architectural level can be studied independently.

To create your own version:

1. Fork the repository.
2. Clone your fork locally.
3. Select the level you want to study or extend.
4. Read the corresponding `DESIGN_LEVEL*.md` document.
5. Review the component README files relevant to that level.
6. Use Docker Compose for local development where appropriate.
7. Progress through the levels incrementally.
8. For Level 7 AWS deployment, configure your own AWS account and GitHub Actions secrets.

A fork does not need to reproduce the entire platform immediately.

A useful learning path is:

```text
Level 1
  ↓
Level 2
  ↓
Level 3
  ↓
Level 4
  ↓
Level 5
  ↓
Level 6
  ↓
Level 7
```

Each level provides a foundation for the next.

---

# Recommended Way to Explore the Repository

If you are new to the project, the recommended order is:

### 1. Read this README

Understand the overall objective and progression.

### 2. Read the Level Design Documents

Start with the level that interests you and work forward through the architecture.

### 3. Read the Component Documentation

Once the architecture is understood, inspect the component-level READMEs.

### 4. Run the Local Platform

Use Docker Compose to understand the application without requiring AWS.

### 5. Explore Level 6

Level 6 introduces the production intelligence and control layer:

- Agent orchestration
- Guardrails
- Structured outputs
- Evaluation
- Trace replay
- Deterministic execution
- Model routing

### 6. Explore Level 7

Level 7 moves the platform into AWS/EKS and introduces:

- Terraform
- EKS
- ECR
- Helm
- GitHub Actions
- Kubernetes platform components
- Cloud-native observability
- AWS model-provider integration

---

# Architectural Philosophy

The project deliberately separates concerns.

```text
Application Logic
       │
       ▼
Orchestration
       │
       ▼
Model Routing
       │
       ├── Ollama
       ├── AWS Bedrock
       └── Other Providers

Retrieval
       │
       ├── ClickHouse
       └── OpenSearch

Infrastructure
       │
       ├── Terraform
       ├── Kubernetes
       └── Helm

Delivery
       │
       └── GitHub Actions

Observability
       │
       ├── Traces
       ├── Prometheus
       ├── Grafana
       └── CloudWatch
```

This separation allows individual components to evolve without requiring the entire platform to be redesigned.

---

# Current Level 7 Outcome

The Level 7 target is a cloud-native enterprise-oriented AI platform built around:

- Amazon EKS
- Amazon ECR
- Terraform
- GitHub Actions
- Helm
- AWS Bedrock
- OpenSearch
- ClickHouse
- CloudWatch
- Prometheus
- Grafana
- Kubernetes
- Production-oriented security and operational controls

The architectural intent is to preserve the AI capabilities developed in Levels 1–6 while providing the infrastructure, deployment automation and operational foundation required for running the platform in AWS.

Docker Compose remains the local developer environment, while Amazon EKS becomes the production deployment platform.

---

# Contributing

Contributions are welcome.

When making changes:

1. Understand which architectural level the change belongs to.
2. Review the relevant design document.
3. Review the component README.
4. Keep existing contracts and interfaces stable where possible.
5. Add or update tests.
6. Update documentation when behaviour or architecture changes.
7. Keep infrastructure changes isolated and reviewable.
8. Do not commit credentials, secrets or environment-specific sensitive data.

For architectural changes, update the relevant `DESIGN_LEVEL*.md` document so that the implementation and documented architecture remain aligned.

---

# Project Status

The project has progressed through seven architectural levels:

```text
Level 1  ── Embedding & Data Ingestion
Level 2  ── BM25 Retrieval
Level 3  ── Hybrid RAG
Level 4  ── Advanced RAG + Ranking Intelligence
Level 5  ── Memory, Agents & Orchestration
Level 6  ── Production Intelligence & Control
Level 7  ── Cloud-Native AWS Platform
```

Level 7 represents the transition from a production-oriented AI application into a cloud-native AWS platform.

---

# Repository

**GitHub:** https://github.com/eyespan/ai-analytics-copilot

The repository contains the implementation, architectural design documents, component documentation, infrastructure code, Kubernetes/Helm configuration and GitHub Actions deployment workflows.



## Credits & Attribution

**AI Analytics Copilot** is an independent engineering project designed, developed, and maintained by **Yohannes Measho**

The project demonstrates the design and implementation of a production-oriented AI/ML platform covering:

- AWS cloud infrastructure and infrastructure-as-code
- Amazon EKS and Kubernetes
- Terraform and Helm
- GitHub Actions CI/CD
- LLM model routing and provider abstraction
- AWS Bedrock and local Ollama inference
- Retrieval-Augmented Generation (RAG)
- Embeddings and vector search
- OpenSearch and ClickHouse
- Agentic orchestration
- Tool execution and guardrails
- Structured outputs
- Evaluation and replay
- Distributed tracing and observability
- Prometheus and Grafana
- Production deployment patterns

The architecture and implementation have been developed progressively through the project's **Level 1 → Level 7** engineering roadmap. Each level documents the architectural decisions, implementation changes, testing, and progression toward a production-oriented AI platform.

### Author

**Yohannes Measho**

Cloud / AI / ML Platform Engineer

GitHub: [https://github.com/eyespan](https://github.com/eyespan)

Project: [https://github.com/eyespan/ai-analytics-copilot](https://github.com/eyespan/ai-analytics-copilot)

---

## Open Source & Third-Party Technologies

This project makes use of a number of open-source technologies and third-party services, including but not limited to:

- Kubernetes
- Amazon EKS
- Terraform
- Helm
- Docker
- GitHub Actions
- Prometheus
- Grafana
- OpenSearch
- ClickHouse
- FastAPI
- Next.js
- Ollama
- Sentence Transformers
- boto3
- AWS SDKs

Each third-party project remains subject to its own licence and terms of use.

Where applicable, the project documentation identifies the technologies and services used within the relevant component or infrastructure documentation.

---

## AWS Services

The project is designed to run on Amazon Web Services and uses AWS services including, where enabled:

- Amazon EKS
- Amazon ECR
- AWS IAM
- AWS VPC
- AWS Load Balancer Controller
- AWS Certificate Manager (ACM)
- Amazon Bedrock

AWS services are subject to the applicable **AWS Customer Agreement**, service terms, pricing, quotas, and regional availability.

Amazon Bedrock is implemented as a supported LLM provider. Access to individual foundation models depends on AWS account configuration, model availability, permissions, and applicable AWS policies.

---

## Project Status

This repository represents an **engineering portfolio and reference implementation** rather than a commercial product.

The platform has been intentionally developed through incremental architectural levels to demonstrate how an AI system can evolve from an initial prototype into a more controlled, observable, evaluated, and production-oriented platform.

The Level 7 implementation represents the current architectural baseline.

The project should not be interpreted as a guarantee that every component is production-ready for every workload. Production deployments should be independently assessed for security, reliability, scalability, cost, compliance, data protection, and operational requirements.

---

## Licence

Copyright © 2026 Eyespan Limited

Unless otherwise stated, the original source code and documentation in this repository are made available under the **MIT License**.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the conditions of the MIT License.

The software is provided **"as is"**, without warranty of any kind, express or implied.

See the [`LICENSE`](LICENSE) file for the complete licence text.

### Third-Party Licences

The MIT License applies only to original project material covered by this repository's licence.

Third-party libraries, frameworks, models, datasets, images, documentation, and services remain subject to their respective licences and terms.

Users of this project are responsible for reviewing and complying with those licences and terms.

---

## Disclaimer

This project is provided for educational, demonstration, research, and engineering portfolio purposes.

No guarantee is made regarding:

- production suitability
- security or compliance
- availability
- performance
- scalability
- AWS costs
- third-party service availability
- model behaviour
- accuracy of generated responses

Always review and adapt the implementation to the requirements of your own environment before deploying it to production.

---

## Why This Project Exists

AI Analytics Copilot was created to demonstrate the engineering challenges involved in moving beyond a simple LLM application toward a **controlled AI platform**.

The project focuses not only on getting an LLM to generate an answer, but on the surrounding engineering disciplines required to operate AI systems responsibly:

**Infrastructure → Deployment → Routing → Retrieval → Agents → Guardrails → Evaluation → Observability → Production Control**

The repository therefore serves as both a working reference implementation and a record of the engineering decisions made throughout the Level 1–Level 7 progression.
