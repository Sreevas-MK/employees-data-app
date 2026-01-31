# Stage 1: Builder
FROM python:3.11.14-alpine AS builder

WORKDIR /install

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copy requirements
COPY ./code/requirements.txt .

# Upgrade ALL packages to fixed versions FIRST
RUN pip install --upgrade pip==25.3 wheel==0.46.2 setuptools jaraco.context==6.1.0

# Now install app packages (this ensures jaraco.context stays at 6.1.0)
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.11.14-alpine

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
