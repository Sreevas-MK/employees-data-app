# GitHub Actions Workflows

This directory contains GitHub Actions workflows used to automate the CI/CD process for the application and its Kubernetes deployment.

The workflows are designed to build Docker images, push them to Docker Hub, and update the Helm repository so that deployments are automatically triggered through GitOps.

---

## image_updater.yaml

This workflow builds and pushes a Docker image whenever application source code changes and updates the Helm chart with the new image tag.

---

### Purpose

The main goal of this workflow is to automate the following steps:

1. Detect changes in the application source code.
2. Build a new Docker image using the updated code.
3. Push the image to Docker Hub with a unique tag.
4. Update the Helm chart to reference the new image tag.

This enables continuous deployment to Kubernetes through Helm and ArgoCD.

---

### Trigger Conditions

The workflow runs only when:

- A push is made to the `main` branch.
- Files inside the `application/` directory are modified.

The workflow does NOT run when only `application/README.md` is changed.  
This avoids unnecessary image rebuilds caused by documentation updates.

---

### High-Level Flow

1. GitHub Actions checks out the source code.
2. Docker Buildx is initialized.
3. The workflow logs in to Docker Hub using GitHub secrets.
4. A Docker image is built from the `application/` directory.
5. The image is pushed to Docker Hub with two tags:
   - `latest`
   - the current Git commit SHA
6. The Helm repository is cloned.
7. The image tag in `values.yaml` is updated to the new commit SHA.
8. The updated Helm values file is committed and pushed back to the Helm repository.

---

### Docker Image Tags

Each build produces two image tags:

- `latest` for convenience
- `<git-sha>` for immutable and traceable deployments

Using the Git SHA ensures reproducibility and easy rollback.

---

### Required Secrets

The following GitHub secrets must be configured for this workflow to function correctly:

- `DOCKER_USERNAME` – Docker Hub username
- `DOCKER_PASSWORD` – Docker Hub password or access token
- `ACCESS_TOKEN` – GitHub Personal Access Token with access to the Helm repository

---

### Why This Workflow Exists

This workflow separates application delivery from infrastructure code.

- Application code lives in this repository.
- Kubernetes manifests and Helm charts live in a separate repository.
- GitHub Actions acts as the bridge between application changes and cluster deployment.

This pattern closely follows real-world GitOps practices used in production environments.

---

### Notes

- Non-YAML files inside `.github/workflows/` are ignored by GitHub Actions.
- This README exists only for documentation and does not affect workflow execution.

