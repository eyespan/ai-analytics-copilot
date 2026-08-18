# Infrastructure

This directory documents the AWS infrastructure and deployment process for the AI Analytics Copilot.

## Canonical Level 7 deployment sequence

```text
Bootstrap AWS OIDC
        ↓
Terraform Plan
        ↓
Terraform Apply
        ↓
Build ML Base Image
        ↓
Docker Image Builder
        ↓
Bootstrap Kubernetes Platform
        ↓
Deploy Dev
```

**Do not run these stages in parallel.**

## 1. Configure GitHub repository secrets

Repository:

https://github.com/eyespan/ai-analytics-copilot

Go to **Settings → Secrets and variables → Actions → Repository secrets** and create:

```text
AWS_ACCOUNT_ID
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

These provide the initial AWS access required by the bootstrap process.

## 2. Bootstrap AWS OIDC

Run **Bootstrap AWS OIDC**.

The purpose is to establish the IAM role used by GitHub Actions/Terraform for AWS deployments.

```text
Initial GitHub/AWS access
        ↓
Bootstrap AWS OIDC
        ↓
AWS IAM deployment role
        ↓
Terraform / GitHub Actions
```

## 3. Terraform Plan

Run **Terraform Plan**.

Review the proposed AWS infrastructure changes before applying them.

A successful plan does not mean the infrastructure has been deployed.

## 4. Terraform Apply

Run **Terraform Apply** and wait for successful completion.

This provisions the AWS resources required by later stages, including the EKS cluster, ECR repositories, networking, IAM and supporting infrastructure defined by Terraform.

Do not start image builds or Kubernetes deployment before this workflow succeeds.

## 5. Build ML Base Image

After Terraform has created ECR, run **Build ML Base Image**.

This builds the ML base image and pushes it to ECR.

```text
Terraform Apply
      ↓
ECR available
      ↓
Build ML Base Image
```

## 6. Docker Image Builder

Run **Docker Image Builder**.

The current image set is:

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

These images are pushed to ECR for consumption by Kubernetes.

## 7. Bootstrap Kubernetes Platform

Run **Bootstrap Kubernetes Platform**.

This prepares the EKS/Kubernetes platform and its supporting components before application workloads are deployed.

The deployment principle is:

```text
AWS infrastructure
        ↓
EKS cluster
        ↓
Kubernetes platform
        ↓
Application workloads
```

## 8. Deploy Dev

After Kubernetes platform bootstrap succeeds, run **Deploy Dev**.

This deploys the Level 7 application stack into the prepared EKS environment.

## Operational dependency model

```text
GitHub secrets
      ↓
Bootstrap AWS OIDC
      ↓
Terraform Plan
      ↓
Terraform Apply
      ├── VPC / networking
      ├── EKS
      ├── ECR
      ├── IAM
      └── supporting AWS resources
      ↓
Build ML Base Image
      ↓
Docker Image Builder
      ├── api-gateway
      ├── embedding-service
      ├── indexer-service
      ├── rag-service
      ├── orchestrator-service
      ├── frontend
      ├── clickhouse-seed
      └── embedding-ingest
      ↓
Bootstrap Kubernetes Platform
      ↓
Deploy Dev
      ↓
Level 7 application platform
```

## Failure handling

If a workflow fails:

1. Stop at the failed stage.
2. Inspect the GitHub Actions logs.
3. Fix the underlying issue.
4. Rerun the failed workflow.
5. Confirm successful completion.
6. Continue to the next stage.

For example, if Terraform Apply fails, do not proceed to Docker image building. If Kubernetes platform bootstrap fails, do not run Deploy Dev.

## Level 7 principle

> **Infrastructure first → platform second → application workloads third.**

This separation makes the deployment reproducible and makes failures easier to isolate.
