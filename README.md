<div align="center">

# ⚡ RepoBlueprint

**Turn Any GitHub Repo Into An AI-Ready Master Blueprint**

[![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Tailwind CSS v4](https://img.shields.io/badge/Tailwind_v4-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)
[![Gemini AI](https://img.shields.io/badge/Powered_by-Gemini_AI-1A73E8?style=for-the-badge&logo=google)](https://ai.google.dev/)

*Designed with an unapologetic Neo-Brutalism aesthetic.*

</div>

---

## 🎯 What is it?

**RepoBlueprint** is an intelligent reproducibility engine. It takes any public GitHub repository, aggressively clones and filters its architecture in real-time, and feeds the entire raw context into a high-capacity LLM (**Gemini 3.1 Flash-Lite / 1.5 Pro**). 

The result? A **Master Blueprint Prompt**—a hyper-detailed, structured markdown document containing the tech stack, component breakdown, data flow, and file architecture, designed to be pasted directly into an AI agent (like Cursor, Windsurf, or Bolt.new) to instantly recreate the exact project from scratch.

---

## 🧠 How the System Works

The architecture is split into a blisteringly fast React frontend and a heavy-lifting Python backend that communicates via **Server-Sent Events (SSE)**.

### 🌊 The Data Flow Pipeline

1. **User Input (`Frontend`)**: The user pastes a GitHub URL into the Neo-Brutalist dashboard and hits "Analyze".
2. **SSE Handshake (`Next.js API`)**: The Next.js `/api/analyze` proxy route establishes a persistent streaming connection with the FastAPI backend.
3. **Ghost Cloning (`Backend — github_grabber.py`)**: The backend talks to the GitHub API, pulling down the repository's recursive tree. It ruthlessly drops heavy/unnecessary files (`node_modules`, images, `.lock` files) to preserve token limits.
4. **Context Construction (`Backend — context_manager.py`)**: The remaining raw code is prioritized—config files first, entry points second, core logic third. It's stitched into a massive context block optimized for Gemini's 2-Million token window.
5. **Real-time Terminal (`Frontend`)**: While the backend processes, it fires Server-Sent Events down the pipe. The React frontend translates these into a rich, retro terminal experience.
6. **AI Synthesis (`Backend — gemini_blueprint.py`)**: The assembled codebase is dispatched to Gemini with extreme, expert-level system instructions. 
7. **Master Blueprint Delivery (`Frontend`)**: The final generated Markdown drops into the UI, fully rendered with syntax highlighting, ready for one-click copying.

---

## 🏗️ Directory Structure

```text
repoblueprint/
├── frontend/                  # NEXT.JS 14 APP ROUTER
│   ├── src/app/
│   │   ├── api/analyze/       # SSE Proxy Route
│   │   ├── globals.css        # Neo-Brutalism Design Tokens (Tailwind v4)
│   │   └── page.tsx           # Dashboard & SSE State Machine
│   ├── src/components/
│   │   ├── ui/                # Custom Brutalist Primitives (NeoButton, NeoCard)
│   │   ├── AnalysisConsole.tsx# Typing hacker-terminal display
│   │   └── PromptOutput.tsx   # Markdown Renderer
│   ├── package.json           
│   └── tailwind.config.ts     
│
└── backend/                   # FASTAPI PYTHON SERVER
    ├── services/
    │   ├── github_grabber.py  # Tree fetching & strict token-saving filters
    │   ├── context_manager.py # Token budgeting & file priority sorting
    │   └── gemini_blueprint.py# Prompt Engineering & Gemini REST call
    ├── main.py                # SSE Streaming Endpoint
    ├── requirements.txt       
    └── .env                   # Configuration Files
```

---

## 🎨 The Neo-Brutalism Aesthetic

The UI abandons corporate minimalism in favor of **Neo-Brutalism**.
- **High Contrast:** Harsh blacks (`#0F172A`) against stark cream/yellow (`#FEF2E1`).
- **Thick Borders:** Every interactive element is boxed in unapologetic heavy weights (`border-2`).
- **Rigid Shadows:** Hover states don't "glow"—they physically translate into deep, hard offset drop-shadows.
- **Monospace Tooling:** Inputs and logs strictly adhere to monospaced hacker fonts for absolute clarity.

---

## 🚀 Getting Started

### 1. Start the Backend (FastAPI)
You will need a Gemini API Key from [Google AI Studio](https://aistudio.google.com/apikey).

```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

# Create environment file
touch .env
# Add the following to .env:
# GEMINI_API_KEY=your_key_here
# GITHUB_TOKEN=your_optional_github_token_for_rate_limits

# Start the server
python main.py # or `uvicorn main:app --reload`
```
*(Backend runs on `http://localhost:8000`)*

### 2. Start the Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
*(Frontend runs on `http://localhost:3000`)*

---

### 💡 Tech Stack Deep Dive
*   **Frontend**: Next.js 14, React 18, Tailwind CSS v4, Lucide React, React Markdown, Class Variance Authority.
*   **Backend**: Python 3.10+, FastAPI, Uvicorn, HTTPX (async).
*   **AI Engine**: `google-generativeai` package running `gemini-3.1-flash-lite-preview` (can be upgraded to `gemini-1.5-pro` for deeper analysis on massive repositories).
