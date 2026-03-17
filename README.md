# CMPE 273 — Microservice with Service Discovery

Demonstrates client-side service discovery: two instances of a microservice register with a central registry; a client discovers them and routes calls randomly across instances.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Service Registry                   │
│                    (port 5001)                       │
│  POST /register  │  GET /discover  │  POST /heartbeat│
└────────┬─────────────────┬─────────────────┬─────────┘
         │ register/hb     │ register/hb     │ discover
         ▼                 ▼                 ▼
┌────────────────┐  ┌────────────────┐  ┌──────────────┐
│ Hello Service  │  │ Hello Service  │  │    Client    │
│  Instance 1    │  │  Instance 2    │  │              │
│  (port 8001)   │  │  (port 8002)   │  │ picks random │
│  GET /hello    │  │  GET /hello    │  │  instance &  │
└────────────────┘  └────────────────┘  │  calls /hello│
                                        └──────────────┘
```

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the registry (Terminal 1)
```bash
python service_registry.py
```

### 3. Start service instance 1 (Terminal 2)
```bash
python hello_service.py --port 8001
```

### 4. Start service instance 2 (Terminal 3)
```bash
python hello_service.py --port 8002
```

### 5. Run the discovery client (Terminal 4)
```bash
python client.py
```

The client will discover both instances from the registry and make 5 calls, routing each one to a randomly selected instance.

## How It Works

1. **Registration** — each service instance calls `POST /register` on startup with its name and address.
2. **Heartbeat** — instances send `POST /heartbeat` every 10 seconds; the registry removes instances that stop sending after 30 seconds.
3. **Discovery** — the client calls `GET /discover/hello-service` to get the list of active instances.
4. **Random routing** — the client picks an instance with `random.choice` and calls its `/hello` endpoint directly.
5. **Deregistration** — on shutdown (Ctrl+C), instances call `POST /deregister` to remove themselves cleanly.

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register a service instance |
| GET | `/discover/<service>` | Get active instances |
| POST | `/heartbeat` | Update liveness |
| POST | `/deregister` | Remove an instance |
| GET | `/services` | List all services |
| GET | `/health` | Registry health check |

## Optional: Service Mesh

For production-grade discovery, the optional extension uses **Istio** or **Linkerd**:

```
App → Sidecar Proxy → Service Mesh
```

Benefits: traffic routing, mTLS security, observability (metrics/tracing).
