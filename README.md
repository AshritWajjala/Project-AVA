# Project AVA 🌌
**Advanced Virtual Assistant: Your sidekick for a better day, every day.**

Project AVA is a personal assistant designed to clear the mental clutter. It’s a simple, smart ecosystem for tracking my PPL gains, getting my thoughts down, and making sense of my research without breaking a sweat.

---

## 🚀 Why AVA?
Life gets messy. AVA keeps it structured so I can focus on doing.

* **🏋️ Gym & Gains:** No-nonsense tracking for my PPL split and the road to 85kg.
* **✍️ Headspace:** A place to dump my thoughts and actually find them later.
* **📖 Deep Dives:** A private researcher for my PDFs and the web.
* **🤝 One Brain:** AVA knows my goals, my history, and my vibe.

## 📅 Version Updates & Development Journal

### **[Feb 20, 2026] - The Dynamic Form & AI Integration**
* **Multi-Exercise Logger:** Implemented a dynamic "Plus/Minus" form system in Streamlit to log entire PPL sessions at once.
* **State Management:** Solved the "Widget-State Lock" error using the **Callback Pattern** (`on_click`) to safely reset forms.
* **Contextual RAG Bridge:** Created `get_ai_context()` in `sqlite_db.py` to feed structured weight and workout history into the LLM.
* **AI "Brain" Client:** Set up the `google-genai` SDK with **Gemini 3 Flash** (2026 Stable Preview) to act as a contextual fitness coach.

### **[Feb 18-19, 2026] - Foundation & Backend**
* **Relational Schema:** Established SQLite tables for `fitness_logs` and `workout_logs`.
* **Core Logic:** Built the Pydantic-based configuration and logging system.
* **UI Prototype:** Initialized the Streamlit multi-tab interface for data entry and historical visualization.

---

## 🛠️ Tech Stack
* **Frontend:** [Streamlit](https://streamlit.io/)
* **Orchestration:** [LangGraph](https://www.langchain.com/langgraph) (In-progress)
* **LLM Engine:** [Gemini 3 Flash](https://aistudio.google.com/) (API-based Reasoning)
* **Databases:**
    * **SQLite**: Structured fitness and diet logs (Relational)
    * **Qdrant/MongoDB**: (Planned for Journaling & Vector Memory)
* **OS:** Pop!_OS (Linux)

---

## 📂 Project Structure
```text
BUDDY/
├── app/
│   ├── main.py          # Streamlit UI & Tab Logic
│   ├── core/            # Config, LLM Client, & Exceptions
│   ├── database/        # SQLite DB Operations
│   └── utils/           # Form reset & Helper functions
├── data/                # Local .db storage
└── .env                 # API Keys (Gemini)