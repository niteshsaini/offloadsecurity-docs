---
title: "Deployment & Configuration"
sidebar_position: 2
---

The OffloadSecurity CSPM platform utilizes a multi-service architecture designed for high availability, security, and scalability. It supports containerized deployment via **Docker Compose** for rapid orchestration and **Bare-Metal** installation for enterprise environments requiring direct control over system resources.

## Docker Compose Architecture

The platform is orchestrated using a production-hardened `docker-compose.yml` that manages the core service categories. This architecture ensures process isolation and provides a standardized environment for security scanning tools.

### Service Grid & Data Flow

The following diagram illustrates the interaction between the core services, including the Docker-in-Docker (DinD) pattern used for security scanning.

**Diagram: Containerized Service Architecture**
```mermaid
graph TD
    subgraph "Public_Internet" [Public_Internet]
        User["Browser_Client"]
    end

    subgraph "Frontend_Container" [cspm-frontend]
        Nginx["Nginx_Server"]
        ReactApp["React_SPA"]
    end

    subgraph "Backend_Services" [Backend_Services]
        API["cspm-backend_FastAPI"]
        Worker["celery-worker"]
    end

    subgraph "Scanning_Layer" [Scanning_Layer]
        Prowler["Prowler_Container"]
        Trivy["Trivy_Container"]
        ZAP["ZAP_Container"]
    end

    subgraph "Persistence_Layer" [Persistence_Layer]
        MongoDB[("cspm-mongo_v7")]
        Redis[("cspm-redis_v7")]
    end

    User -->|HTTPS| Nginx
    Nginx -->|Proxy_API| API
    API -->|Async_Tasks| Redis
    Redis -->|Dispatch| Worker
    Worker -->|Docker_Socket| Prowler
    Worker -->|Docker_Socket| Trivy
    API -->|CRUD| MongoDB
    Worker -->|Write_Results| MongoDB
```

### Docker-in-Docker (DinD) Scanning Pattern
The platform executes security tools like **Prowler**, **Trivy**, and **ZAP** as sibling containers. The `backend` and `celery-worker` containers mount the host's `/var/run/docker.sock` and use the `PROWLER_HOST_OUTPUT_DIR` environment variable to resolve absolute host paths for volume mounting findings back into the system. The `backend` container includes the Docker CLI as a static binary to facilitate these interactions.

The backend image also pre-installs several scanning binaries directly for performance and to avoid root-privilege issues with the Docker socket during code scans. These include `opengrep` (SAST), `gitleaks` (secrets), `osv-scanner` (SCA), `syft` (SBOM), and `grype` (vulnerabilities).

## Environment Configuration

Configuration is managed via a central `.env` file. The setup wizard automates the generation of these secrets, including Fernet keys and HMAC secrets.

| Variable | Purpose |
| :--- | :--- |
| `SECRET_KEY` | JWT token signing and session encryption |
| `CLOUD_ENCRYPTION_KEY` | Fernet key for encrypting Cloud Credentials in MongoDB |
| `MONGO_URL` | Primary connection string for the 14+ databases |
| `PROWLER_HOST_OUTPUT_DIR` | Absolute host path for sibling container volume mounts |
| `WEBHOOK_SECRET` | HMAC-SHA256 secret for outbound webhook signing |
| `DOCKER_GID` | Host Docker group ID to permit socket access |

## Build Validation & Integrity

To prevent "broken" deployments, the platform includes a strict build validation phase and runtime monitoring.

### Build-Time Validation
The backend image uses a multi-stage build where the `builder` stage prepares dependencies. A critical validation step involves verifying that all required Python packages are correctly resolved before the final image is produced. If private packages fail, the build continues, but critical public packages must succeed.

### Runtime Integrity Monitoring
The system ensures that critical dependencies are healthy at runtime via health check endpoints. The backend container performs a health check against the `/api/health` route, while the frontend checks its own availability. MongoDB and Redis also have integrated health checks to ensure the `backend` and `celery-worker` only start when infrastructure is ready.

**Diagram: Deployment Integrity Flow**
```mermaid
sequenceDiagram
    participant D as "Backend Image Build"
    participant B as "builder stage"
    participant S as "FastAPI Server"
    participant H as "HealthCheck_Mechanism"

    D->>B: RUN pip install requirements-filtered.txt
    Note over B: Dependency Resolution
    B-->>D: Copy .local to /opt/python-packages
    
    D->>S: CMD ["python", "-m", "uvicorn", "server:app"]
    Note over S: Server initializes FastAPI
    
    H->>S: GET /api/health
    S-->>H: 200 OK (service_healthy)
```

## Nginx & SSL Configuration

The platform uses Nginx as a reverse proxy to handle SSL termination, rate limiting, and large file uploads.

### Request Timeouts
The Nginx configuration is synchronized with the backend `TimeoutMiddleware` to handle heavy security scans.
*   **Standard Path**: 30s timeout.
*   **Slow Paths**: 600s timeout for cloud validation and assessments.
*   **Upload Heavy Paths**: 900s timeout for code-scan ZIPs up to 500MB.
*   **Nginx Sync**: Nginx `proxy_read_timeout` and `proxy_send_timeout` are set to `900s` to match these backend requirements.

### ACME Challenge & Certbot
The `certbot` container handles Let's Encrypt certificates. Nginx is configured to serve the `.well-known/acme-challenge/` directory to facilitate the HTTP-01 challenge.

### Caching Strategy
To prevent stale frontend code after redeployment, the `index.html` entry point is explicitly configured with `no-cache` headers. Static assets under `/static/` use immutable long-term caching.

## Bare-Metal Deployment

For non-Docker environments, the platform provides idempotent installation scripts supporting Ubuntu 24 and Debian 12.

### Supervisor Management
The platform uses **Supervisor** for process management in bare-metal setups, enabling blue/green deployment strategies.
*   **Blue Instance**: Backend on port 8001, Frontend on 3000.
*   **Green Instance**: Backend on port 8002, Frontend on 3001.

### Idempotent Installation
The bare-metal installation scripts automate the installation of:
1.  **Python 3.12**: Installed via deadsnakes PPA on Ubuntu or built from source on Debian.
2.  **Node.js 20 & Yarn**: Configured via NodeSource and official Yarn repositories.
3.  **MongoDB 7.0 & Redis 7**: Configured with automatic service enablement and status verification.

**Diagram: Bare-Metal Process Management**
```mermaid
graph LR
    subgraph "Supervisor_Controller" [supervisord]
        Backend_Process["FastAPI_Uvicorn"]
        Frontend_Process["React_Static_Server"]
    end

    subgraph "Local_Infrastructure" [Local_Infrastructure]
        Mongo_Svc["mongod.service"]
        Redis_Svc["redis-server.service"]
        Nginx_Svc["nginx.service"]
    end

    Nginx_Svc -->|Proxy| Backend_Process
    Nginx_Svc -->|Proxy| Frontend_Process
    Backend_Process --> Mongo_Svc
    Backend_Process --> Redis_Svc
```

---