# 🚀 TeamSpark AI  
### Multi-Agent AI Brainstorming Platform for Hackathons & Creative Teams

TeamSpark AI is a collaborative **multi-agent brainstorming tool** where AI agents take on different roles — **Idea Generator**, **Critic**, and **Builder** — to help teams generate, evaluate, and refine ideas quickly and efficiently.

Built during the **3Pillar Hackathon**, TeamSpark AI gives you an interactive space to spark creativity using **FastAPI**, **LangGraph**, **OpenRouter LLMs**, **Next.js**, and **MongoDB Atlas**.

---

## ✨ Features

- 🔥 **Multi-Agent Collaboration**  
  Powered by *LangGraph*, three AI agents work together:
  - **Idea Agent** – Generates creative ideas  
  - **Critic Agent** – Points out risks, weaknesses  
  - **Builder Agent** – Improves and proposes solutions  

- 🎯 **Real-time brainstorming sessions**
- 💾 **Persistent sessions & messages** stored in MongoDB Atlas
- 🌐 **Next.js frontend** for a clean, fast UI
- ⚡ **FastAPI backend** for agent orchestration & API handling
- 🤖 **OpenRouter (GPT-4o / GPT-4o-mini)** for high-quality AI responses
- 📡 **Cloud database** → work simultaneously with your team
- 🧠 **Session history** so you never lose an idea

---

## 🧩 Project Architecture

```mermaid
flowchart TD

    User["👤 User"] --> NextJS["🌐 Next.js Frontend"]

    NextJS --> FastAPI["⚡ FastAPI Backend"]

    FastAPI --> LangGraph["🔁 LangGraph Multi-Agent System"]
    LangGraph --> OpenRouter["🤖 OpenRouter (GPT-4o / GPT-4o-mini)"]

    FastAPI --> MongoDB["🗄️ MongoDB Atlas\n(hackathon_db)"]

    subgraph MongoDB Collections
        S["📁 sessions"]
        M["📁 messages"]
    end

    MongoDB --> FastAPI
🏗️ Tech Stack
Frontend

Next.js 14

React

Axios / fetch

Deployed on Vercel (optional)

Backend

FastAPI

LangGraph (multi-agent orchestration)

OpenRouter (GPT-4o / GPT-4o-mini)

Python 3.12

Async architecture (async / await)

Database

MongoDB Atlas  

▶️ How to Run Locally
Backend (FastAPI)
cd AI_backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload


The backend runs on
➡️ http://127.0.0.1:8000

Frontend (Next.js)
cd AI_frontend
npm install
npm run dev


The frontend runs on
➡️ http://localhost:3000

🤖 Multi-Agent Flow (Example)

User writes:

"Give me startup ideas for education."

Agents respond:

🧠 Idea Agent → Generates 3–5 ideas

⚠️ Critic Agent → Evaluates risks

🔧 Builder Agent → Improves ideas and fixes weaknesses

All responses are stored in:

sessions

messages

📝 To-Do / Future Improvements

🔐 Add user authentication

💬 Add WebSocket live chat

🎨 Add better UI/UX

🌍 Deploy on Azure/Vercel

📊 Analytics: agent performance, idea quality scoring

🔁 Export sessions as PDF/Markdown