# GitHub Actions Workflows

This directory contains GitHub Actions workflows used to automate the secure CI/CD process for the application and its Kubernetes deployments.

The pipeline performs security scanning, builds Docker images, pushes them to Docker Hub, and updates Helm repositories to trigger GitOps-based deployments via ArgoCD.

---

## image_updater.yaml

This workflow builds, scans, and pushes a Docker image whenever application source code changes and automatically updates Helm repositories with the new image tag.

---

## Purpose

The workflow automates the following process:

1. Detect application source code changes.
2. Perform secret scanning using GitLeaks.
3. Build → Scan → Push Docker image securely.
4. Perform vulnerability scanning using Trivy.
5. Update Helm repositories with the new image tag.
6. Trigger automated Kubernetes deployments through ArgoCD GitOps sync.

This ensures that only secure, scanned images are deployed to Kubernetes environments.

---

## Trigger Conditions

The workflow runs only when:

* A push is made to the `main` branch.
* Files inside the `application/` directory are modified.

The workflow does NOT run when only `application/README.md` is changed to prevent unnecessary builds.

---

## High-Level Flow

1. Checkout application source code.
2. Run **GitLeaks** to detect exposed secrets.
3. Build Docker image using commit SHA.
4. Install and run **Trivy** vulnerability scanning.
5. Block pipeline if HIGH or CRITICAL vulnerabilities are detected.
6. Log in to Docker Hub securely using GitHub secrets.
7. Push Docker images with:

   * immutable SHA tag
   * latest tag
8. Clone Helm repositories for:

   * Production EKS cluster
   * Development cluster
9. Update image tag in Helm `values.yaml`.
10. Commit and push updated Helm configuration to trigger GitOps deployment.

---

## Security Controls Implemented

### Secret Detection – GitLeaks

Scans the repository for:

* Hardcoded credentials
* Tokens
* API keys
* Sensitive configuration leaks

Pipeline fails immediately if secrets are detected.

### Container Vulnerability Scanning – Trivy

Scans Docker images for:

* Known CVEs
* OS package vulnerabilities
* Python dependency vulnerabilities

Pipeline fails if HIGH or CRITICAL vulnerabilities are found.

---

## Docker Image Tagging Strategy

Each build generates:

* `<git-sha>` – Immutable versioned image
* `latest` – Convenience reference

Using SHA-based tagging ensures:

* Immutable deployments
* Easy rollback
* Traceable releases

---

## Required GitHub Secrets

The following secrets must be configured:

| Secret          | Purpose                                |
| --------------- | -------------------------------------- |
| DOCKER_USERNAME | Docker Hub username                    |
| DOCKER_PASSWORD | Docker Hub access token                |
| EKS_HELM_TOKEN  | GitHub token for production Helm repo  |
| DEV_HELM_TOKEN  | GitHub token for development Helm repo |

---

## GitOps Deployment Model

This workflow does NOT deploy directly to Kubernetes.

Instead:

1. Image is built and pushed.
2. Helm values repository is updated.
3. ArgoCD detects Git changes.
4. ArgoCD synchronizes Kubernetes manifests automatically.

This provides:

* Declarative deployment
* Auditability
* Controlled rollouts
* Infrastructure and application separation

---

## Notes

* Workflow runs only for application changes.
* Documentation changes do not trigger builds.
* Security scans execute before image push.
* Non-YAML files inside `.github/workflows/` are ignored by GitHub Actions.

---
