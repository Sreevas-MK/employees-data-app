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

