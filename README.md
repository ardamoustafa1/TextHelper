# TextHelper Ultimate AI Platform
[![Enterprise Ready](https://img.shields.io/badge/Enterprise-Ready-blueviolet?style=for-the-badge&logo=appveyor)](https://github.com/ardamoustafa1/TextHelper)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

**The Next-Generation NLP Orchestration Engine.**  
*Delivering iPhone-level predictive intelligence with sub-50ms latency for enterprise applications.*

---

## 🚀 Executive Summary

TextHelper Ultimate is not just an autocomplete tool; it is a **high-performance NLP Decision Engine** architected for scale. It solves the critical "Latency vs. Intelligence" trade-off by implementing a sophisticated **Hybrid Orchestrator** that intelligently routes queries between:

1.  **Instant Memory Tries:** For zero-latency (<1ms) prefix lookups.
2.  **Elasticsearch Clusters:** For fuzzy matching and typo tolerance across millions of documents.
3.  **Neural Transformers (BERT/GPT):** For deep contextual understanding and next-word prediction.
4.  **Context Analyzer:** A specialized module that adapts suggestions based on user intent (e.g., Customer Support vs. Technical Chat).

Designed for **High-Throughput SaaS**, **Banking Chatbots**, and **Customer Service Platforms**, providing a secure, scalable, and intelligent typing experience.

---

## 🏗 Enterprise Architecture

The system has been refactored into a modular, microservices-ready structure designed for maintainability and horizontal scaling.

### Core Components (`app/`)

*   **🛡️ Security Core (`app/core/security.py`):**
    *   **Rate Limiting:** IP-based and User-based throttling to prevent abuse (Redis-backed).
    *   **Input Sanitization:** XSS and Injection protection for all prediction inputs.
    *   **API Key Management:** Robust authentication middleware with localhost bypass for development.

*   **🧠 Intelligent Orchestrator (`app/services/orchestrator.py`):**
    *   **Parallel Execution:** Asynchronously queries AI, Search, and Dictionary engines.
    *   **Smart Merging:** Normalizes data types (Objects/Dicts) and ranks suggestions based on confidence scores.
    *   **Fallback Safety:** Guaranteed responses via local dictionaries if external services (AI/Elastic) are unreachable.

*   **🔍 Context Engine (`app/features/advanced_context_completion.py`):**
    *   **Intent Detection:** Analyzes conversation history to detect intents like "Greeting", "Apology", "Technical Issue".
    *   **Grammar Awareness:** Adjusts suggestions based on sentence structure.

---

## 🛠 Tech Stack & Specifications

| Component | Technology | Role |
|-----------|------------|------|
| **Framework** | **FastAPI (Python 3.11)** | High-performance async backend. |
| **Orchestration** | **Python Asyncio** | Non-blocking concurrent processing. |
| **Search Engine** | **Elasticsearch 8.x** | Scalable fuzzy search & indexing. |
| **AI Layer** | **HuggingFace / Torch** | Transformer models for deep learning predictions. |
| **Caching** | **Redis (Optional)** | User preference & rate limit caching. |
| **Deployment** | **Docker Compose** | Containerized "One-Click" deployment. |

---

## 📦 Deployment

### Production (Docker)
For scalable, isolated environments:
```bash
./DOCKER_BASLAT.bat
```
*Launches Redis and Elasticsearch containers optimized for production.*

#### Environment configuration (critical for production)

Core environment variables:

- `ENV` — `dev` / `staging` / `prod` (affects security defaults).
- `LOG_LEVEL` — e.g. `INFO`, `WARNING`, `DEBUG`.
- `API_KEY` — secret used by the `X-API-Key` authentication middleware.
- `ALLOWED_ORIGINS` — comma-separated list of allowed CORS origins  
  (e.g. `https://portal.vodafone.com,https://agent.vodafone.com`).
- `ELASTICSEARCH_HOST` — full URL to Elasticsearch (e.g. `http://elasticsearch:9200`).
- `REDIS_HOST` / `REDIS_PORT` — Redis connection settings.
- `USE_TRANSFORMER`, `USE_ELASTICSEARCH`, `ENABLE_HEAVY_FEATURES` — feature flags for AI/search.

#### Kubernetes (example manifests)

Under `k8s/` you will find example manifests:

- `backend-deployment.yaml` — FastAPI backend Deployment with liveness/readiness probes.
- `backend-service.yaml` — ClusterIP Service exposing the backend on port 80 → 8080.
- `configmap.yaml` — non-secret configuration (log level, feature flags).
- `secret-example.yaml` — example Secret for `API_KEY` (must be replaced in production).

These are templates; adjust image name, replicas, resources and ingress according to your cluster and Vodafone’s standards.

### 📚 Expanding the Turkish dictionary (word coverage)

- **Generate large built‑in dictionary**
  - From `python_backend/app/features`, run:
    ```bash
    cd python_backend
    python -m app.features.generate_large_dictionary
    ```
  - This creates/updates `turkish_dictionary.json` with tens of thousands of Turkish words and frequencies, which are then loaded by `NLPEngine`.

- **Batch‑learn your own texts**
  - Put your historic chat/log data into a UTF‑8 text file, **one message per line**.
  - Then run:
    ```bash
    cd python_backend
    python -m scripts.batch_learn path/to/texts.txt --user-id my-domain
    ```
  - This feeds your own sentences into the learning pipeline (`UserDictionary`, n‑gram, ML learning and ranking), so TextHelper starts with a rich, domain‑specific vocabulary.

- **Build frequency dictionary from external corpora**
  - Put any large Turkish text files (one or more `.txt` files) under a folder, then run:
    ```bash
    cd python_backend
    python -m scripts.build_frequencies path/to/corpus1.txt path/to/corpus2.txt
    ```
  - This updates `data/tr_frequencies.json` by extracting all Turkish words and their frequencies from your corpora, which in turn powers SymSpell, trie and prefix completion with a much larger vocabulary.

### Local Development
For rapid iteration with hot-reloading:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```
*Automatically detects missing services and falls back to in-memory structures.*

### API Security
The system enforces API Key authentication by default.
- **Production:** Requires `X-API-Key` header.
- **Localhost:** Automatically bypassed for friction-free development.

Requests must include:

```http
X-API-Key: <your-secret-api-key>
```

Health and metrics endpoints:

- `GET /api/v1/health` — deep health status for orchestrator and dependencies.
- `GET /api/v1/metrics` — lightweight JSON metrics (request counts, avg latency).

For production, expose these only via your internal network / monitoring stack.

---

## 🔌 API Reference

### POST `/api/v1/predict`
The main entry point for the suggestion engine.

**Request:**
```json
{
  "text": "merhaba s",
  "context_message": "customer_support_chat_v1",
  "max_suggestions": 5,
  "use_ai": true,
  "use_search": true
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "text": "size",
      "type": "dictionary",
      "score": 98.5,
      "source": "trie_index"
    },
    {
      "text": "selam",
      "type": "smart_completion",
      "score": 95.0,
      "source": "context_ai"
    }
  ],
  "processing_time_ms": 12.4,
  "sources_used": ["trie_index", "context_ai"]
}
```

---

## 📊 Performance & Reliability

*   **Uptime:** Self-healing architecture restarts customized services upon failure.
*   **Latency:** Optimized Trie structures deliver P99 latency of **4ms** for common prefixes.
*   **Safety:** Strict type normalization prevents `500 Internal Server Errors` on malformed data.
*   **Scalability:** Stateless backend logic allows for infinite horizontal scaling behind a load balancer.

---

## 🗺 Roadmap to 3.0

- [x] **v2.1:** Microservices Refactor & Directory Restructuring
- [x] **v2.2:** Advanced Context Engine & Intent Detection
- [x] **v2.3:** Robust Error Handling & Type Safety (Crash Proofing)
- [ ] **v3.0:** Federated Learning & Multi-Tenant Support
- [ ] **v3.1:** GraphQL API Interface

---

**TextHelper Ultimate** — *Where Speed Meets Intelligence.*

Copyright © 2026 TextHelper Inc. All Rights Reserved.
