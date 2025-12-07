# Manual Deployment Guide

This guide explains how to manually deploy the Flask MySQL Redis application using the Docker image from Docker Hub.

---

## Table of Contents

1. [Create Docker Network](#create-docker-network)
2. [MySQL Setup](#mysql-setup)
3. [Redis Setup](#redis-setup)
4. [Run Flask Containers](#run-flask-containers)
5. [Load Balancing](#load-balancing)
6. [Notes](#notes)

---

## Create Docker Network

```bash
docker network create flaskapp-network
```

This network allows containers to communicate with each other.

---

## MySQL Setup

1. Pull MySQL image:

```bash
docker image pull mysql:latest
```

2. Create volume for persistent storage:

```bash
docker volume create mysql-volume
```

3. Run MySQL container:

```bash
docker run --name mysql-container -d --network flaskapp-network \
  -e MYSQL_ROOT_PASSWORD="A9mQ2#vT7&kH6@" \
  -v mysql-volume:/var/lib/mysql mysql:latest
```

4. Access MySQL and create database, table, and user:

```bash
docker exec -it mysql-container mysql -u root -p
```

```sql
CREATE DATABASE company;
USE company;

CREATE TABLE employees(
    id INT(5),
    name VARCHAR(255),
    age INT(3),
    email VARCHAR(255)
);

INSERT INTO employees (id,name,age,email) VALUES
(100,"Alex",25,"alex@gmail.com"),
(101,"Ben",28,"ben@gmail.com"),
(102,"Christy",26,"christy@gmail.com"),
(103,"Emily",30,"emily@gmail.com");

CREATE USER 'appadmin'@'%' IDENTIFIED BY 'T8#cReP9hV6*uQ';
GRANT ALL PRIVILEGES ON company.* TO 'appadmin'@'%';
FLUSH PRIVILEGES;
```

---

## Redis Setup

```bash
docker run -d --name redis-container --network flaskapp-network -p 6379:6379 redis:alpine
```

Redis is used for caching and session stickiness.

---

## Run Flask Containers

### Pull Docker Image from Docker Hub

```bash
docker image pull sreevasmk1993/flask-mysql-redis-app:latest
```

### Run Containers

```bash
docker run -d --name flaskapp-container1 --network flaskapp-network \
  -e DATABASE_HOST="mysql-container" -e DATABASE_PORT=3306 \
  -e DATABASE_USER="appadmin" -e DATABASE_PASSWORD="T8#cReP9hV6*uQ" \
  -e DATABASE_NAME="company" -e DATABASE_TABLE="employees" \
  -e FLASK_PORT=3000 -e REDIS_HOST="redis-container" -e REDIS_PORT=6379 \
  -p 3001:3000 sreevasmk1993/flask-mysql-redis-app:latest

docker run -d --name flaskapp-container2 --network flaskapp-network \
  -e DATABASE_HOST="mysql-container" -e DATABASE_PORT=3306 \
  -e DATABASE_USER="appadmin" -e DATABASE_PASSWORD="T8#cReP9hV6*uQ" \
  -e DATABASE_NAME="company" -e DATABASE_TABLE="employees" \
  -e FLASK_PORT=3000 -e REDIS_HOST="redis-container" -e REDIS_PORT=6379 \
  -p 3002:3000 sreevasmk1993/flask-mysql-redis-app:latest
```

---

## Load Balancing

### Option 1: Nginx Container

1. Use the `nginx.conf` in `nginx-container/`.
2. Configure upstream servers for ports 3001 and 3002.
3. Expose Nginx on port 80.
4. Requests are balanced between Flask containers.

```bash
docker run -d --name nginx-lb \
  --network flaskapp-network \
  -p 8080:80 \
  -v $PWD/nginx.conf:/etc/nginx/nginx.conf:ro \
  nginx:alpine
```

### Option 2: AWS Application Load Balancer (ALB)

1. Create Target Group pointing to Flask container ports.
2. Attach EC2 instances or container instances running Flask.
3. Configure health check as `/status`.
4. Attach Target Group to ALB.

---

## Notes

* Make sure environment variables for MySQL, Redis, and Flask are correctly set.
* Health check endpoint helps Nginx or ALB monitor container health.
* Docker Hub image ensures consistent deployment without rebuilding locally.
* Manual deployment validates everything before automating with Ansible or Terraform.

