# Architecture

The engine follows the principles of Clean Architecture, separating domain logic from framework-specific concerns.

```mermaid
flowchart TD
    subgraph Domain
        D[Entities]
    end
    subgraph Application
        U[Use Cases]
    end
    subgraph Interfaces
        F[FastAPI]
        C[CLI]
        P[Plugins]
    end
    D --> U
    U --> F
    U --> C
    U --> P
```

## Layers
- **domain**: entities and invariants
- **app**: use cases and services (pure logic)
- **api**: FastAPI routers (health, math, sse)
- **plugins**: registry and examples
- **tests**: unit and end-to-end

## API Data Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant F as FastAPI
    participant U as Use Case
    participant D as Domain
    C->>F: HTTP Request
    F->>U: invoke use case
    U->>D: read/write
    D-->>U: result
    U-->>F: response
    F-->>C: HTTP Response
```

## Pipeline Data Flow

```mermaid
flowchart LR
    I[Input] --> P1[Stage 1]
    P1 --> P2[Stage 2]
    P2 --> P3[Stage 3]
    P3 --> R[Result]
```

## Plugin Interaction

```mermaid
flowchart TB
    Core -->|load| Registry
    Registry --> PluginA
    Registry --> PluginB
    PluginA -->|callback| Core
    PluginB -->|callback| Core
```

## Setup
1. Install dependencies:
   ```bash
   make setup
   ```
2. Run the API server:
   ```bash
   make api
   ```
