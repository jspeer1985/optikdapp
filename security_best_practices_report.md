# MongoDB Security Audit — Optik Platform Backend

## Executive Summary
- Reviewed the MongoDB-related deployment assets under `optik-platform/backend`, focusing on the Docker compose stack that pairs `optik-api` with the MongoDB services and admin tooling.
- Found two high-severity issues: the API container runs Uvicorn in reload mode via the same compose file that wires to MongoDB, and the optional Mongo Express UI exposes the database with default `admin/admin` credentials on an open host port.
- Both findings violate the FastAPI deployment guidance (secure production server configuration) and MongoDB hardening practices; recommendations are included below and documented in this report file.

## High Severity Findings

### Finding 01 — Dev server command exposes Mongo+FastAPI stack (FASTAPI-DEPLOY-001)
- **Rule ID:** FASTAPI-DEPLOY-001
- **Severity:** High
- **Location:** `optik-platform/backend/docker-compose.mongodb.yml:104`
- **Evidence:** The `optik-api` service command is `uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload`, which starts the FastAPI development server (auto-reload, single worker) from inside a Docker container that directly depends on MongoDB.
- **Impact:** If this compose file is used outside a strictly local environment, anyone who can reach port `8000` gains an automatically reloading debug server, detailed tracebacks, and no worker/process management. That state is susceptible to DoS, accidental data exposure, and unauthorized state modifications via the MongoDB backend.
- **Fix:** Run a production-grade ASGI command without `--reload` (e.g., `uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4`) or replace it with `gunicorn`/`uvicorn`+`gunicorn` so that the Mongo-connected API only serves through hardened workers.
- **Mitigation:** Restrict this compose stack to local development by gating the port (loopback or VPN) and avoid binding 8000 to the public interface when the stack is used in staging/production.
- **False Positive Notes:** This compose file is primarily a development helper, but the default `docker-compose -f docker-compose.mongodb.yml up -d` command (used by `setup-mongodb.sh`) launches the insecure server unless someone removes `--reload`; verify that production deployments do not depend on this file.

### Finding 02 — Mongo Express UI published with default admin/admin login (MONGO-EXPRESS-001)
- **Rule ID:** MONGO-EXPRESS-001
- **Severity:** High
- **Location:** `optik-platform/backend/docker-compose.mongodb.yml:35` and `:40`
- **Evidence:** The `mongo-express` service exposes port `8081:8081` and sets `ME_CONFIG_BASICAUTH_USERNAME: admin` + `ME_CONFIG_BASICAUTH_PASSWORD: admin` in the environment, so the MongoDB admin panel is reachable on the host using credentials that are publicly documented (and even highlighted by `setup-mongodb.sh`).
- **Impact:** Anyone who discovers port 8081 can log in, browse the `optik` database, and modify or drop collections that the Mongo backend relies on, potentially disrupting data persisted by the API.
- **Fix:** Do not run Mongo Express on publicly reachable interfaces; either remove the `ports` block, bind it only to localhost, or disable the service entirely in production. If the UI is necessary, load credentials from a secrets store and set a strong Basic Auth password instead of hardcoding `admin/admin`.
- **Mitigation:** Keep this service confined to the `dev` profile (run it only with `--profile dev`), and wrap it with an SSH tunnel or VPN if occasional access is required while the MongoDB backend is running.
- **False Positive Notes:** The service is tagged with the `dev` profile, but `setup-mongodb.sh` still advertises and logs the accessible UI, indicating that it is run locally with default auth; validate that no automated deployment exposes port 8081 with those defaults.
