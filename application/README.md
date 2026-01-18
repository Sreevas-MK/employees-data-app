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
FROM python:3.11-alpine

# Create app directory and user
RUN mkdir /flaskapp
RUN adduser -h /flaskapp -s /bin/sh -D -H flask-user

WORKDIR /flaskapp
COPY ./code/ .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Set proper permissions
RUN chown -R flask-user:flask-user /flaskapp

EXPOSE 3000
USER flask-user

# Start the Flask app
CMD ["python3","app.py"]
```

* Creates a dedicated `flask-user` for security.
* Copies source code from `code/` folder.
* Installs Python dependencies.
* Exposes port 3000 inside the container.
* Runs Flask as a non-root user.

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

This image can now be used to run multiple Flask containers for load balancing with Nginx or AWS ALB.

