# Operations

## Local
```mermaid
flowchart LR
    Dev[Developer] -->|make setup| Env[Virtualenv]
    Env -->|make api| App[FastAPI Server]
```
Steps:
1. Install dependencies and start the API:
   ```bash
   make setup
   make api
   ```
2. Open the docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## Docker
```mermaid
flowchart LR
    Dev[Developer] -->|docker compose up -d --build| Container[API Container]
```
Steps:
1. Build and run services:
   ```bash
   docker compose up -d --build
   ```
2. Follow logs:
   ```bash
   docker compose logs -f api
   ```
