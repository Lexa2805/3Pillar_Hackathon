# 🚀 TeamSpark AI  
### Multi-Agent AI Brainstorming Platform for Hackathons & Creative Teams

TeamSpark AI is a collaborative **multi-agent brainstorming tool** where AI agents take on different roles — **Idea Generator**, **Critic**, and **Builder** — to help teams generate, evaluate, and refine ideas quickly and efficiently.

Built during the **3Pillar Hackathon**, TeamSpark AI gives you an interactive space to spark creativity using **FastAPI**, **LangGraph**, **OpenRouter LLMs**, **Next.js**, and **MongoDB Atlas**.

---

## ✨ Features

- 🔥 **Multi-Agent Collaboration**  
  Powered by *LangGraph*, three AI agents work together:
  - The Idea Agent = "The Solution Architect"
In the corporate world, this is the person who bridges the gap between the client's vague wish and a concrete technical plan.

Real-Life Title: Solution Architect or Principal Engineer.

What they do all day: They listen to a client say, "I want an Uber for dog walking," and they draw the whiteboard diagrams. They decide "We need AWS, React Native, and a Microservices architecture." They don't write every line of code, but they define how it will be built.

Their Personality: Visionary, confident, technical, "Big Picture" thinker.

Hackathon Prompt (System Message):

"You are a Senior Solution Architect at a top tech consultancy. Your goal is to design innovative, scalable technical solutions for client problems. You rely on past case studies to ensure success. You are creative but practical." 
  - The Critic Agent = "The Review Board" (Security & Tech Lead)
In real life, you never just "ship" what the Architect draws. It goes through a Review Process. This agent represents the "grumpy" experts who keep the company from getting sued or hacked.

Real-Life Title: Security Architect + Lead Developer (Combined).

What they do all day: They look at the Architect's diagram and say, "This is dangerous. You didn't encrypt the user data. Also, this database will crash if 1 million people use it." They find the flaws before the code is written.

Their Personality: Skeptical, detail-oriented, risk-averse, strict, "Safety First."

Hackathon Prompt (System Message):

"You are a Strict Technical Review Board member. You are an expert in Cybersecurity (OWASP Top 10) and Scalability. Your job is NOT to be nice; it is to find flaws. You critique every proposal for security risks, performance bottlenecks, and missing requirements (like HIPAA or GDPR)."
  -The Builder Agent = "The Product Owner / Delivery Manager"
Once the plan is approved, someone has to organize the work for the developers. This agent doesn't write code; it writes the Plan.

Real-Life Title: Technical Product Owner (PO) or Delivery Manager.

What they do all day: They take the technical plan and break it down into "Tickets" (Jira tasks). They write "User Stories" (e.g., "As a user, I want to log in..."). They make sure the developers know exactly what to do on Monday morning.

Their Personality: Organized, structured, efficient, clear, "Get it done."

Hackathon Prompt (System Message):

"You are an efficient Technical Product Owner. Your job is to take a technical architecture and break it down into actionable work. You generate clean, formatted User Stories (in Gherkin syntax) and a list of Technical Tasks for the development team." 

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