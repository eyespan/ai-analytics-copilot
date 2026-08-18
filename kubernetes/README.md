# Kubernetes Infrastructure

## Purpose

The `kubernetes/` directory is retained as part of the repository's Kubernetes infrastructure layout.

The current Level 7 deployment path, however, is primarily driven by:

```text
Terraform
+
Helm
+
GitHub Actions
```

rather than a populated Kustomize-style Kubernetes manifest tree.

## Current directory layout

```text
kubernetes/
├── base/
└── overlays/
    ├── dev/
    ├── stage/
    └── prod/
```

The supplied source snapshot does not contain populated Kubernetes YAML manifests in these directories.

## Active deployment path

The current cluster is bootstrapped using:

```text
.github/workflows/bootstrap-cluster.yml
```

and workloads are deployed using:

```text
helm/
```

The reusable Helm deployment workflow is:

```text
.github/workflows/helm-deploy.yml
```

## Why this directory remains

The directory provides a natural location for future raw Kubernetes manifests or Kustomize overlays.

At present, documenting it as an active deployment mechanism would be inaccurate.

## Source-of-truth model

For the current Level 7 implementation:

```text
AWS infrastructure
        ↓
Terraform

Kubernetes platform
        ↓
Helm + bootstrap-cluster.yml

Application workloads
        ↓
Helm values + application chart

One-off initialization
        ↓
kubectl-apply.yml + Helm Jobs
```

This README intentionally records the current state rather than describing planned Kubernetes overlays as though they were already active.
