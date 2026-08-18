# Terraform Infrastructure

## Purpose

The `terraform/` directory provisions the AWS infrastructure used by the AI Analytics Copilot Level 7 platform.

The current repository contains a **development Terraform environment** under:

```text
terraform/environments/dev/
```

Terraform is responsible for the AWS foundation and EKS platform rather than the application source code.

## Current infrastructure composition

The development environment composes these Terraform modules:

```text
terraform/environments/dev/main.tf
        │
        ├── modules/vpc
        ├── modules/ecr
        ├── modules/iam
        ├── modules/eks
        ├── modules/iam-irsa
        └── modules/kubernetes/namespaces
```

The infrastructure includes:

- VPC networking
- Public and private subnets
- NAT gateway configuration
- Amazon ECR repositories
- EKS cluster
- EKS managed node groups
- EKS managed add-ons
- EKS OIDC provider
- IRSA roles
- Kubernetes namespaces
- CloudWatch EKS control-plane logging
- Default encrypted `gp3` Kubernetes storage class

## Environment layout

```text
terraform/
├── environments/
│   ├── dev/
│   │   ├── backend.tf
│   │   ├── locals.tf
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   ├── providers.tf
│   │   ├── terraform.tfvars
│   │   └── variables.tf
│   ├── stage/
│   └── prod/
└── modules/
```

The current populated environment is `dev`. `stage` and `prod` directories exist but are not populated with equivalent Terraform configuration in the supplied source tree.

## Terraform providers

The dev environment configures:

- AWS provider
- Kubernetes provider
- Helm provider

The Kubernetes and Helm providers authenticate to EKS using:

```text
aws eks get-token
```

rather than embedding a static Kubernetes credential.

## State

The repository contains a Terraform backend configuration in:

```text
terraform/environments/dev/backend.tf
```

The repository's bootstrap workflow creates the development Terraform state S3 bucket and enables:

- S3 versioning
- server-side AES256 encryption
- public-access blocking

Terraform state files should not be committed to source control in a production repository. The supplied source tree currently contains development state artefacts, so these should be reviewed before the repository is treated as a clean production baseline.

## Typical local commands

From:

```bash
cd terraform/environments/dev
```

run:

```bash
terraform init
terraform fmt
terraform validate
terraform plan
```

Apply is normally performed through the GitHub Actions workflow.

## CI/CD

Terraform validation and deployment are integrated into GitHub Actions:

```text
terraform-plan.yml
terraform-apply.yml
terraform.yml
validate.yml
```

The current workflows use AWS credentials and, for Terraform plan, also contain an OIDC role-assumption path.

## Important implementation note

The Terraform code is deliberately modular. EKS-specific add-ons are defined in the EKS module, while workload-specific IAM/IRSA configuration is separated into `modules/iam-irsa`.

This separation allows the Level 7 platform to evolve without changing the application services themselves.
