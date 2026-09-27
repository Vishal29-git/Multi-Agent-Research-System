# 🔬 Multi-Agent AI Research System

A production-style full-stack web application for automated AI research. Given a user query (e.g. *"How could AGI emerge in the future?"*), multiple specialized AI agents collaborate using **LangGraph**, **LangChain**, **FastAPI**, **React**, and **Ollama** to decompose topics, search web sources, index snippets in a **FAISS RAG Store**, verify empirical claims, synthesize analytical trends, and write a structured 13-section research report.

**100% Free & Local** — Runs completely free of cost using local LLM inference (Ollama) and local embeddings without requiring paid OpenAI, Claude, or Gemini APIs.

---

## 🏗️ Architecture & Multi-Agent Workflow

```
                             ┌─────────────────────────┐
                             │   React + Vite Frontend │
                             └────────────┬────────────┘
                                          │ REST API / SSE Stream
                                          ▼
                             ┌─────────────────────────┐
                             │     FastAPI Backend     │
                             └────────────┬────────────┘
                                          │ Orchestrates
                                          ▼
                             ┌─────────────────────────┐
                             │   LangGraph Workflow    │
                             └────────────┬────────────┘
                                          │
      ┌──────────────────┬────────────────┼────────────────┬──────────────────┐
      ▼                  ▼                ▼                ▼                  ▼
┌────────────┐    ┌─────────────┐   ┌────────────┐   ┌───────────┐      ┌────────────┐
│  Planner   │───►│ Researcher  │──►│Fact Checker│──►│  Analyst  │ ───► │   Critic   │
└────────────┘    └──────┬──────┘   └────────────┘   └───────────┘      └─────┬──────┘
                         │ RAG / Search                                       │ Loop?
                         ▼                                                    ▼
                   ┌───────────┐                                        ┌────────────┐
                   │ FAISS/DDG │                                        │   Writer   │
                   └───────────┘                                        └────────────┘
```

### Specialized Agents:
1. **Agent 1 — Research Planner**: Decomposes user queries into structured sub-topics & research tasks.
2. **Agent 2 — Research Agents**: Executes web searches, indices content into FAISS vector space, and extracts empirical findings and candidate claims.
3. **Agent 3 — Fact Checker**: Cross-references claims against source evidence, flags unsupported claims, and assigns confidence ratings (`high`, `medium`, `low`).
4. **Agent 4 — Analyst**: Synthesizes verified claims into domain patterns, relationships, structural trends, and tensions between evidence and speculation.
5. **Agent 5 — Critic**: Audits completeness and peer-review quality score (1-10). Loops back for additional research iterations if insufficient (capped by `MAX_ITERATIONS`).
6. **Agent 6 — Report Writer**: Compiles a comprehensive 13-section Markdown research report complete with source links and citations.

---

## 🛠️ Tech Stack

### Frontend
- **React.js** + **Vite**
- **Lucide React** icons
- **Axios** (REST API & SSE streaming)
- **React-Markdown** + **Remark-GFM** (GitHub-flavored document rendering)
- Clean, responsive glassmorphic dark CSS UI

### Backend
- **Python 3.10+** & **FastAPI**
- **LangGraph** (Multi-agent cyclic graph orchestration)
- **LangChain** (RAG retrieval & tool integration)
- **Ollama** (Local LLM inference, configurable via `OLLAMA_BASE_URL` & `OLLAMA_MODEL`)
- **FAISS** + **SentenceTransformers** (Local RAG vector embeddings)
- **DuckDuckGo Search** (Free web search tool with fallback resilient search provider)
- **SQLAlchemy** (PostgreSQL database with out-of-the-box SQLite fallback)

---

## 🚀 Quickstart Guide (Windows & Cross-Platform)

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`
- **Ollama** (Optional for local LLM inference, downloadable from [ollama.com](https://ollama.com))

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default `.env` settings:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
DATABASE_URL=sqlite:///./research.db
MAX_ITERATIONS=3
CRITIC_MIN_SCORE=7
HOST=0.0.0.0
PORT=8000
```

### 3. Setup Ollama Model (Free Local LLM)
Start Ollama and pull your model of choice:
```bash
ollama serve
ollama pull qwen2.5:3b
```
*(Note: If Ollama is starting up or not installed, the application includes a smart local fallback engine so research workflows complete without crashing!)*

---

## 🏃 Run Backend & Frontend

### Step A: Start FastAPI Backend
Open a terminal in the project root directory:

```bash
# Create and activate virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Start FastAPI server
python -m backend.main
```
The backend API will run at `http://localhost:8000`. API docs available at `http://localhost:8000/docs`.

### Step B: Start React Frontend
Open a second terminal window:

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```
The web dashboard will open at **`http://localhost:5173`**.

---

## 🐳 Docker Deployment (Optional)

Run PostgreSQL and backend with Docker Compose:

```bash
docker-compose up --build
```

---

## 📂 Project Directory Structure

```text
ai-research-system/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx          # Top navigation header
│   │   │   ├── Sidebar.jsx         # Research session history
│   │   │   ├── ResearchForm.jsx    # Prompt input & suggestion pills
│   │   │   ├── AgentStatusView.jsx # Live agent progress cards & stats
│   │   │   ├── ReportViewer.jsx    # Document tabbed Markdown renderer
│   │   │   └── SourcesTab.jsx      # Evidence & source links table
│   │   ├── services/
│   │   │   └── api.js              # Axios & SSE API client
│   │   ├── App.jsx                 # React root component
│   │   ├── main.jsx
│   │   └── index.css               # Modern glassmorphism dark styles
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── agents/
│   │   ├── base.py                 # Ollama LLM wrapper + smart fallback
│   │   ├── planner.py              # Agent 1 - Research Planner
│   │   ├── researcher.py           # Agent 2 - Research Agents
│   │   ├── fact_checker.py         # Agent 3 - Fact Checker
│   │   ├── analyst.py              # Agent 4 - Analyst
│   │   ├── critic.py               # Agent 5 - Peer Review Critic
│   │   └── writer.py               # Agent 6 - Report Writer
│   │
│   ├── orchestration/
│   │   └── graph.py                # LangGraph state workflow graph
│   │
│   ├── tools/
│   │   ├── search.py               # DuckDuckGo & abstract SearchTool
│   │   └── retrieval.py            # FAISS RAG vectorstore index
│   │
│   ├── models/
│   │   └── research.py             # SQLAlchemy DB schemas
│   ├── schemas/
│   │   └── research.py             # Pydantic API response models
│   ├── database/
│   │   └── session.py              # DB connection & SQLite fallback
│   ├── api/
│   │   └── routes.py               # FastAPI endpoints & SSE stream
│   ├── config.py                   # Pydantic Settings
│   └── main.py                     # FastAPI server entrypoint
│
├── .env.example
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## 📡 API Endpoints

- `POST /api/research` — Create a new research session & initiate background execution.
- `GET /api/research` — Retrieve list of previous research sessions (History).
- `GET /api/research/{id}` — Fetch session details, verified claims, sources, and full Markdown report.
- `GET /api/research/{id}/status` — Polling status endpoint with progress % and individual agent states.
- `GET /api/research/{id}/sources` — Fetch list of retrieved sources & relevance scores.
- `GET /api/research/{id}/stream` — Real-time Server-Sent Events (SSE) agent state update stream.

![System Demo](frontend\dist\assets\MultiAgent.gif)