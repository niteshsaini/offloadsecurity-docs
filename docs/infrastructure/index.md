---
title: "Deployment & Operations"
sidebar_position: 1
---

This section covers how Offload Security is deployed and run — for teams that self-host the platform or run it alongside private infrastructure. For the on-premises scanning model (internal-network visibility, OpenVAS, Wazuh), see **[On-Premises & Private Infrastructure](../on-premises/index.md)**.

## Deployment model

The platform runs as a multi-service application, orchestrated with **Docker Compose** for a fast, standardized setup, or installed on **bare metal** for environments that require direct control over host resources. A hardened production configuration isolates the data and cache tiers (MongoDB, Redis) from the public-facing API and dashboard.

### Core services

| Service | Role | Technology |
| :--- | :--- | :--- |
| Data store | Primary store for platform and scan data | MongoDB |
| Cache & task broker | Background-task queue and session cache | Redis |
| Backend | Core API and scan orchestration | FastAPI |
| Frontend | Security dashboard and management UI | React / Nginx |
| TLS | Automated SSL/TLS certificate management | Let's Encrypt / ACME |

The backend image ships with the security tooling scans depend on (for example `nmap`, `syft`, `grype`, and `trivy`), so a standard deployment is ready to scan without assembling a separate toolchain. An interactive setup wizard handles secret generation, environment configuration, and host tuning, and TLS is activated automatically once certificates are issued.

For step-by-step instructions and configuration options, see **[Deployment & Configuration](./deployment.md)**.

## Related

- **[On-Premises & Private Infrastructure](../on-premises/index.md)** — deploy internal scanning and Wazuh/OpenVAS inside your network.
- **[Getting Started](../getting-started.md)** — sign in and take a first tour once the platform is running.
