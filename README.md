# 🤝 Personalized Networking Assistant

An advanced, AI-powered Full-Stack Networking Assistant designed to analyze collegiate and professional events, extract insights via Wikipedia verification, and dynamically generate hyper-personalized conversation starters and icebreakers.

Built using a distributed architecture: a robust **FastAPI Backend** hosted on Hugging Face Spaces (with persistent storage) and an interactive **Streamlit Frontend** for the user interface.
---

## 🚀 Key Features

* **Smart Event Classification:** Utilizes a fine-tuned `DistilBERT` zero-shot classification pipeline to analyze event descriptions and categorize them dynamically.
* **AI Icebreaker Generation:** Powered by `SmolLM2-360M-Instruct` & `GPT-2` text generation pipelines to draft contextual, tailored talking points based on user roles and event contexts.
* **Automated Wikipedia Fact-Checking:** Synchronizes with the Wikipedia API to cross-verify event themes, historically accurate contexts, and domains.
* **Persistent Analytics & Logs:** Integrated with Hugging Face's modern **Storage Buckets** mapped to `/data` to maintain evaluation history, feedback logs, and telemetry data across server restarts.
* **Dual-Cloud Architecture:** Decentralized hosting with the Frontend on Streamlit Cloud and the GPU/CPU-heavy AI inference layer on Hugging Face Spaces.

---

## 🏗️ Architecture Overview

The project is split into two independent repositories/folders for clean separation of concerns:

1.  **Frontend (`/frontend`):** A lightweight, state-managed Streamlit application handling user inputs, configuration secrets, and rendering markdown-rich networking cards.
2.  **Backend (`/app`):** An asynchronous FastAPI application that handles model initialization, heavy NLP pipelines, data logging, and custom routing configurations.

```text
┌─────────────────┐       HTTP Requests       ┌─────────────────┐
│                 ├──────────────────────────>│                 │
│Streamlit UI     │                           │ FastAPI Backend │
│(Streamlit Cloud)│<──────────────────────────┤   (HF Spaces)   │
└─────────────────┘        JSON Responses     └────────┬────────┘
                                                       │
                                        ┌──────────────┴──────────────┐
                                        ▼                             ▼
                            ┌───────────────────────┐     ┌───────────────────────┐
                            │   HF Transformers     │     │ Persistent Storage    │
                            │ (SmolLM2 / DistilBERT)│     │   (/data Volumes)     │
                            └───────────────────────┘     └───────────────────────┘

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit, Python 3.13, HTTPX
* **Backend API:** FastAPI, Uvicorn, Pydantic v2
* **AI/NLP Models:** Hugging Face Transformers (`SmolLM2-360M-Instruct`, `distilbert-base-uncased-mnli`, `gpt2`)
* **Environment Management:** `uv` (Ultra-fast Python package installer & resolver)
* **Deployment:** Docker, Hugging Face Spaces, Streamlit Cloud

---

## 📂 Project Directory Structure

```text
Personalized-Networking-Assistant/
├── app/                        # FastAPI Backend Code
│   ├── models/                 # Pydantic Schemas & DTOs
│   │   └── schemas.py          # UserProfile, EventContext validation
│   ├── routes/                 # API Endpoint Router controllers
│   │   └── conversation.py     # Inference & Telemetry routes
│   ├── services/               # Core business logic & Core ML Pipelines
│   │   ├── event_analyzer.py   # DistilBERT Classification Pipeline
│   │   └── topic_generator.py  # SmolLM/GPT-2 Tokenization & Generation
│   ├── config.py               # Application configurations & LRU Caching
│   └── main.py                 # ASGI entrypoint initialization
├── frontend/                   # Streamlit Frontend Code
│   ├── .streamlit/
│   │   └── secrets.toml        # Local Secrets Configuration
│   └── streamlit_app.py        # Streamlit UI Components
├── .gitattributes              # Git LFS Trackers & Line Endings Config
├── Dockerfile                  # Multi-stage production Python 3.13 Image
├── README.md                   # Project Documentation
└── requirements.txt            # Production dependencies
```


## Local Setup & Installation

Make sure you have Python 3.13 and the `uv` package manager installed.

### 1. Clone the repository

```bash
git clone https://github.com/shivangdadhich/personalized-networking-assistant.git
cd personalized-networking-assistant
```

### 2. Set up the backend environment

You can install dependencies from either `pyproject.toml` or the flat requirements file.

```bash
uv venv
```

On Windows:

```powershell
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
uv pip install -r requirment.txt
```

If you prefer to use the project manifest instead:

```bash
uv sync
```

### 3. Configure local frontend secrets

Create this file:

`frontend/.streamlit/secrets.toml`

```toml
BACKEND_API_URL = "http://localhost:8000/conversation"
```

If you are pointing the frontend to a deployed backend, replace that URL with your public endpoint.

### 4. Run the backend locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs:

- http://localhost:8000/docs
- http://localhost:8000/redoc

### 5. Run the frontend locally

```bash
cd frontend
streamlit run streamlit_app.py
```

## API Endpoints

The backend router is mounted at `/conversation`.

- `POST /conversation/generate-conversation`
- `POST /conversation/fact-check`
- `POST /conversation/feedback`
- `GET /conversation/history`
- `GET /conversation/feedback`

## Cloud Deployment Configuration

### Hugging Face Spaces Docker image

Use a Python 3.13 Docker base image that matches the local runtime:

```dockerfile
FROM python:3.13-slim

WORKDIR /code

COPY pyproject.toml /code/pyproject.toml
COPY requirment.txt /code/requirment.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /code/requirment.txt

COPY . .

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

### Hugging Face Space metadata

Add the following at the top of the Space README if you deploy with a Docker Space:

```yaml
---
title: Personalized Networking Assistant
emoji: 🤝
sdk: docker
app_port: 7860
---
```

## Persistent Evaluation & Telemetry

The backend stores conversation and feedback logs in the `storage/` directory during local development.

Stored artifacts:

- `storage/conversation_history.json`
- `storage/feedback.json`

If you deploy to Hugging Face Spaces with persistent storage, mirror these files under the mounted persistent path so data survives restarts.

## Notes

- The backend code currently serves the API from `/conversation`, not the root path.
- The frontend defaults to `http://127.0.0.1:8000/conversation` if no secret is provided, but the recommended local backend port in this project is `7860`.
- The repository currently includes `requirment.txt` as the dependency file name.