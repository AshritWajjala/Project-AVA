# Project AVA 🌌
**Advanced Virtual Assistant: Your Privacy-First Life OS**

Project AVA is a personal AI companion designed to bridge the gap between high-level reasoning and daily habit tracking. Built to run locally on an **RTX 5080**, AVA serves as a unified intelligence layer for fitness, journaling, and research, ensuring your data never leaves your machine.

---

## 🚀 Vision
AVA isn't just a chatbot; she is a **Life OS**. She transitions from a technical assistant to a personal health coach and researcher by integrating multiple data streams into a single, persistent state. 

### Core Pillars:
* **Privacy-First:** Powered by local LLMs (Ollama) to keep personal journals and health data private.
* **Unified Context:** One brain for everything—your PC specs, your weight goals, and your academic research.
* **Persistent Memory:** AVA remembers who you are across every session using advanced graph state persistence.

---

## ✨ Features
* 🧠 **Unified Reasoning Agent**: A single LangGraph-powered interface for all tasks.
* ⚖️ **Fitness & Diet Tracker**: Structured SQLite-based tracking for weight loss (Goal: 112.4kg → 85kg).
* 📖 **Semantic Journaling**: MongoDB-powered journaling with vector search for finding past reflections.
* 📚 **Research Hub**: RAG-based document intelligence (PDFs, ArXiv, Web) using Qdrant and Pinecone.
* ⚡ **High-Performance Backend**: Optimized for RTX 5080 with dual-model orchestration (Gemma 3 / DeepSeek).

---

## 🛠️ Tech Stack
* **Orchestration:** [LangGraph](https://www.langchain.com/langgraph) (State management & Memory)
* **LLM Engine:** [Ollama](https://ollama.com/) (Local) & [Groq](https://groq.com/) (Speed Fallback)
* **Databases:**
    * **Qdrant**: Long-term semantic memory (Vector)
    * **SQLite**: Structured fitness and diet logs (Relational)
    * **MongoDB**: Flexible daily journaling (Document)
* **API Layer:** FastAPI
* **Frontend:** Streamlit (Coming Soon)

---

## 📂 Project Structure
```text
AVA/
├── app/
│   ├── main.py          # Unified LangGraph assembly
│   ├── core/            # App Configuration & Pydantic settings
│   ├── database/        # Multi-DB Connection Factory
│   └── tools/           # Specialist utilities (Fitness, Web Search)
├── data/                # Local SQLite & Checkpoint storage
├── .env                 # Secret management (API Keys)
└── docker-compose.yml   # Infrastructure orchestration