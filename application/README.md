# Employees data app - Application Layer

This folder contains the Flask application along with Dockerfile and source code.
The app uses MySQL for persistent storage, Redis for caching and session stickiness, and is fully Dockerized.

---

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Dockerfile Explanation](#dockerfile-explanation)
4. [Build and Push Docker Image](#build-push-docker-image)
5. [Environment Variables](#environment-variables)

---

## Overview

* Flask web app to display employee data.
* Redis caching for session stickiness.
* Supports multiple instances for load balancing.
* Dockerized for easy deployment.

---

## Directory Structure

```
application/
├── Dockerfile
├── README.md
└── code/
    ├── app.py
    ├── requirements.txt
    ├── static/
    │   └── css/styles.css
    └── templates/index.html.tmpl
```

---

## Dockerfile Explanation

```dockerfile
# Stage 1: Builder
FROM python:3.11.14-alpine AS builder

# Upgrade Alpine OS packages to pull latest security patches
RUN apk update && apk upgrade --no-cache

WORKDIR /install

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copy requirements
COPY ./code/requirements.txt .

# Upgrade ALL packages to fixed versions FIRST
RUN pip install --upgrade pip==25.3 wheel==0.46.2 setuptools jaraco.context==6.1.0

# Install app packages (this ensures jaraco.context stays at 6.1.0)
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.11.14-alpine

# Upgrade Alpine OS packages to pull latest security patches
RUN apk update && apk upgrade --no-cache

WORKDIR /flaskapp

# Create a non-root user
RUN adduser -D flask-user

# Upgrade system packages in final image too
RUN pip install --upgrade pip==25.3 wheel==0.46.2 setuptools jaraco.context==6.1.0

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY ./code/ .

# Fix ownership
RUN chown -R flask-user:flask-user /flaskapp

USER flask-user
EXPOSE 3000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:3000", "app:app"]
```

### Stage 1: Builder Image

* Uses `python:3.11.14-alpine` as a lightweight base.
* Updates Alpine system packages to ensure latest security patches.
* Installs build dependencies:

  * gcc
  * musl-dev
  * libffi-dev
* Upgrades critical Python packaging tools:

  * pip
  * wheel
  * setuptools
  * jaraco.context (pinned to secure version)
* Installs application dependencies into a temporary directory (`/install`).
* This stage isolates compilation tools so they are not included in the final runtime image.

### Stage 2: Runtime Image

* Starts from a fresh minimal Alpine Python image.
* Applies OS security updates again to ensure the runtime layer is patched.
* Creates a dedicated non-root user (`flask-user`) for secure container execution.
* Copies only the prebuilt dependencies from the builder stage, reducing image size and attack surface.
* Copies application source code into `/flaskapp`.
* Fixes file ownership to ensure the non-root user can run the app.
* Exposes port `3000`.
* Runs the application using Gunicorn with 2 workers.

### Security & Optimization Features

* Multi-stage build reduces final image size.
* No compiler tools present in runtime image.
* Non-root container execution.
* Explicit dependency version pinning.
* OS-level patching in both build and runtime layers.
* Gunicorn production WSGI server instead of Flask dev server.

---

## Build and Push Docker Image

### Build Locally

```bash
docker image build -t flask-mysql-redis-app .
```

### Tag for Docker Hub

```bash
docker image tag flask-mysql-redis-app sreevasmk1993/employees-data-app:latest
```

### Push to Docker Hub

```bash
docker image push sreevasmk1993/employees-data-app:latest
```

> After this, the image is available on Docker Hub and can be pulled directly using:
>
> ```bash
> docker pull sreevasmk1993/employees-data-app:latest
> ```

---

## Environment Variables

| Variable          | Default        | Description      |
| ----------------- | -------------- | ---------------- |
| DATABASE_HOST     | -              | MySQL hostname   |
| DATABASE_USER     | -              | MySQL username   |
| DATABASE_PASSWORD | -              | MySQL password   |
| DATABASE_NAME     | company        | Database name    |
| DATABASE_TABLE    | employees      | Table name       |
| FLASK_PORT        | 3000           | Flask port       |
| FLASK_DEBUG       | True           | Debug mode       |
| REDIS_HOST        | redis          | Redis hostname   |
| REDIS_PORT        | 6379           | Redis port       |
| FLASK_SECRET_KEY  | supersecretkey | Flask secret key |

This Docker image is reusable across standalone Docker setups, Nginx or AWS ALB load balancing, and Kubernetes environments including Helm-based deployments.
