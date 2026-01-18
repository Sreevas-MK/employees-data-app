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


# AWS Application Load Balancer (ALB) & Domain Setup

This guide explains how to set up an AWS Application Load Balancer (ALB) and configure a domain/subdomain via Route 53 for the Flask MySQL Redis application running on EC2 instances.

---

## Folder Structure

```
aws-alb/
├── README.md
└── images/
```

---

## Step 1: Create Target Group

1. Navigate to **EC2 → Target Groups → Create target group**.

2. Select:

   * Target group name
   * Protocol
   * IP address type
   * VPC
     ![Target Group](images/target-group-1.png)

3. Configure health checks:

   * Path: `/status`
     ![Health Check](images/target-group-2.png)

4. Add tags as required.
   ![Tags](images/target-group-3.png)

5. Select targets (EC2/container instances) and map to Flask container ports **3001** and **3002**:
   ![Target Mapping 1](images/target-group-4.png)
   ![Target Mapping 2](images/target-group-5.png)
   ![Target Mapping 3](images/target-group-6.png)

6. Click **Next** and **Create Target Group**.

---

## Step 2: Create Application Load Balancer (ALB)

1. Navigate to **EC2 → Load Balancers → Create Load Balancer → Application Load Balancer**.

2. Provide:

   * Name
   * VPC
   * Subnets and Availability Zones (select at least 2, e.g., `ap-south-1a` and `ap-south-1b`)
     ![Load Balancer Step 1](images/Load-balancer-1.png)
     ![Load Balancer Step 2](images/Load-balancer-2.png)

3. Configure listeners:

   * HTTPS listener
     ![HTTPS Listener](images/Load-balancer-3.png)
   * Select the target group created earlier
   * Choose ACM certificate for SSL
     ![ACM Certificate](images/Load-balancer-4.png)

4. Configure HTTP listener to redirect traffic to HTTPS
   ![HTTP Redirect](images/Load-balancer-5.png)

5. Review and click **Create Load Balancer**.

---

## Step 3: Add Route 53 Record

1. Open **Route 53 → Hosted zones → Select domain/subdomain**.

2. Create a new record:

   * Type: **A (Alias)**
   * Alias Target: select the ALB created in Step 2
     ![Route 53 Record](images/Route-53.png)

3. Save the record. The domain/subdomain now points to the ALB.

---

## Step 4: Verify Application

1. Open the browser and navigate to your domain/subdomain.
2. You should see the Flask MySQL Redis application running.

![Application Screenshot 1](images/Application-image-1.png)
![Application Screenshot 2](images/Application-image-2.png)

---

## Notes

* Ensure that EC2 instances running Flask containers are registered with the target group.
* Health checks `/status` ensure ALB routes traffic only to healthy instances.
* Route 53 alias allows users to access the site via a custom domain.
* Manual deployment ensures proper testing before automating with tools like Terraform or Ansible.

---

# Nginx Load Balancer Setup

This guide explains how to configure Nginx as a load balancer for the Flask MySQL Redis application.

---

## Folder Structure

```
nginx-container/
└── nginx.conf
```

---

## nginx.conf

```nginx
events {}

http {
    upstream flaskapp {
        server flaskapp-container1:3000;
        server flaskapp-container2:3000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://flaskapp;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

* `upstream flaskapp` defines the backend Flask containers.
* Nginx will forward requests to `flaskapp-container1` and `flaskapp-container2` on port 3000.
* Proxy headers preserve client information.

---

## Run Nginx Container

```bash
docker run -d --name nginx-lb \
  --network flaskapp-network \
  -p 8080:80 \
  -v $PWD/nginx.conf:/etc/nginx/nginx.conf:ro \
  nginx:alpine
```

* `--network flaskapp-network` ensures Nginx can reach the Flask containers.
* `-p 8080:80` exposes Nginx on host port 8080.
* `-v $PWD/nginx.conf:/etc/nginx/nginx.conf:ro` mounts the configuration file as read-only.

---

## Access the Application

* Open a browser and navigate to `http://<host-ip>:8080/`.
* Requests will be distributed between the two Flask containers automatically.

---

## Notes

* Ensure both Flask containers (`flaskapp-container1` and `flaskapp-container2`) are running before starting Nginx.
* Nginx acts as a simple reverse proxy and load balancer.
* For production, consider enabling SSL and monitoring container health.

---
