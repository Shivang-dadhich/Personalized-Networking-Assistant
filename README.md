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



🚀 Getting Started
Prerequisites
Ensure you have the following installed locally:

Python 3.13+

uv package manager (recommended) or pip

Docker (Optional, for containerized local execution)

1. Backend Setup
Navigate to the root directory and install the necessary dependencies: 

# Install dependencies using uv
uv pip install -r requirements.txt

# Run the backend server locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

2. Frontend Setup
Navigate to the frontend directory and run the Streamlit application: