# 💡 Luminosity  
### AI-Powered Multi-Agent Brainstorming Platform for Technical Solutions

**Luminosity** is an intelligent brainstorming platform that simulates a complete software development team. Three specialized AI agents collaborate to transform vague ideas into production-ready technical plans — complete with architecture diagrams, security reviews, and actionable user stories.

Built during the **3Pillar Hackathon**, Luminosity leverages **LangGraph**, **OpenRouter LLMs**, **FastAPI**, **Next.js**, and **MongoDB Atlas** to deliver enterprise-grade technical solutions in minutes.

---

## ✨ Core Features

### 🤖 **Three Specialized AI Agents**

Luminosity simulates a real software development team with three distinct personas powered by **LangGraph**:

#### 1️⃣ **The Architect (Idea Agent)**
- **Role:** Principal Solution Architect
- **Responsibility:** Designs scalable, production-ready technical architectures
- **Output:** 
  - Executive summaries
  - Tech stack selection with justifications
  - Data flow diagrams
  - Risk analysis
- **Enhanced with:**
  - 🌐 **Web Search Integration** (real-time competitor analysis)
  - 🧠 **RAG (Retrieval-Augmented Generation)** — learns from past successful ideas

#### 2️⃣ **The Reviewer (Critic Agent)**
- **Role:** Chief Information Security Officer (CISO) + Lead Architect
- **Responsibility:** Security & scalability review using OWASP Top 10 standards
- **Scoring System:**
  - **Security Score** (0-100): OWASP compliance, authentication, encryption
  - **Scalability Score** (0-100): Caching, CDN, horizontal scaling strategies
- **Special Mode:** 😈 **Devil's Advocate** — ultra-strict, sarcastic review mode
- **Feedback Loop:** Can reject proposals and request revisions

#### 3️⃣ **The Planner (Builder Agent)**
- **Role:** Technical Product Owner
- **Responsibility:** Converts approved architectures into implementation plans
- **Output:**
  - ✅ **User Stories** (Gherkin format with acceptance criteria)
  - 📋 **Technical Tasks** (actionable development tickets)
  - 📊 **Mermaid.js Diagrams** (system architecture flowcharts)

### 🔄 **Intelligent Feedback Loop**
- Critic can **reject** solutions and send them back to the Architect for revision
- Configurable revision limits (prevent infinite loops)
- Automatic approval after max revisions reached

### 🎨 **Visualizer Agent**
- Generates **DALL-E 3 architecture diagrams** (when OpenAI API is configured)
- Produces image prompts for technical illustrations

### 💾 **Persistent Knowledge Base**
- **MongoDB Atlas** stores all sessions, messages, and idea chunks
- **Vector Search** with embeddings for semantic similarity matching
- **Session Management:** Create, retrieve, update, and delete brainstorming sessions
- **User Statistics:** Track ideas generated, knowledge chunks, and session history

### 🔍 **Advanced Search Capabilities**
- **Vector Similarity Search** for finding related ideas across sessions
- **Context Retrieval** for continuing conversations with relevant history
- **Agent-specific filtering** (search by Idea/Critic/Builder responses)

---

## 🏗️ Tech Stack

### **Frontend**
- **Next.js 16** (App Router)
- **React 19** with Server Components
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Mermaid.js** for diagram rendering
- **React PDF** for session exports
- **React Markdown** for rich text display

### **Backend**
- **FastAPI** (async/await for high performance)
- **LangGraph** (multi-agent state orchestration)
- **LangChain** with OpenRouter integration
- **OpenRouter API** (GPT-4o / GPT-4o-mini)
- **Motor** (async MongoDB driver)
- **Sentence Transformers** for text embeddings
- **DuckDuckGo Search** / **Tavily** for web search
- **BeautifulSoup4** for web scraping

### **Database & Infrastructure**
- **MongoDB Atlas** (cloud-hosted)
- **Vector Embeddings** for semantic search
- Collections: `sessions`, `messages`, `idea_chunks`

### **AI & Machine Learning**
- **OpenRouter** (LLM provider)
- **GPT-4o** for high-quality responses
- **GPT-4o-mini** for cost-effective operations
- **DALL-E 3** for image generation (optional)

---

## 🧩 System Architecture

```mermaid
flowchart TD
    User["👤 User"] --> Frontend["🌐 Next.js Frontend<br/>(React 19 + TypeScript)"]
    
    Frontend --> API["⚡ FastAPI Backend<br/>(Async Python)"]
    
    API --> LangGraph["🔁 LangGraph<br/>Multi-Agent System"]
    API --> MongoDB["🗄️ MongoDB Atlas<br/>(Vector Search)"]
    
    LangGraph --> Architect["🏛️ Architect Agent<br/>(Solution Design)"]
    LangGraph --> Critic["⚖️ Critic Agent<br/>(Security Review)"]
    LangGraph --> Builder["🔨 Builder Agent<br/>(User Stories)"]
    LangGraph --> Visualizer["🎨 Visualizer Agent<br/>(DALL-E 3)"]
    
    Architect --> OpenRouter["🤖 OpenRouter API<br/>(GPT-4o)"]
    Critic --> OpenRouter
    Builder --> OpenRouter
    Visualizer --> OpenRouter
    
    Architect --> WebSearch["🌐 Web Search<br/>(DuckDuckGo/Tavily)"]
    Architect --> RAG["🧠 RAG System<br/>(Vector Embeddings)"]
    
    MongoDB --> VectorDB["📊 Collections:<br/>• sessions<br/>• messages<br/>• idea_chunks"]
```

---

## ⚙️ Setup & Installation

### **Prerequisites**
- **Python 3.12+**
- **Node.js 20+**
- **MongoDB Atlas account** (or local MongoDB)
- **OpenRouter API key** ([Get one here](https://openrouter.ai/))

### **1. Clone the Repository**
```bash
git clone https://github.com/Lexa2805/3Pillar_Hackathon.git
cd 3Pillar_Hackathon
```

### **2. Backend Setup (FastAPI)**

```bash
cd AI_backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

**Create `.env` file in `AI_backend/`:**
```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENAI_API_KEY=your-openrouter-api-key-here
OPENAI_BASE_URL=https://openrouter.ai/api/v1

# MongoDB Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB_NAME=luminosity_db

# Optional: Web Search (for enhanced idea generation)
TAVILY_API_KEY=your-tavily-api-key  # Optional
```

**Start the backend:**
```bash
uvicorn main:app --reload
```
➡️ Backend runs on **http://127.0.0.1:8000**  
📖 API Docs: **http://127.0.0.1:8000/docs**

### **3. Frontend Setup (Next.js)**

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
➡️ Frontend runs on **http://localhost:3000**

---

## 🚀 Usage Guide

### **Creating a Brainstorming Session**

1. **Navigate to the dashboard** at `http://localhost:3000/dashboard`
2. **Click "New Session"** and provide:
   - Session title
   - Description
   - Your email (for tracking)

### **Generating Ideas**

**Option 1: Full Brainstorm** (All 3 Agents)
```
POST /api/brainstorm
{
  "prompt": "Design a telemedicine platform for rural areas",
  "session_id": "your-session-id",
  "max_revisions": 2,
  "devils_advocate": false
}
```

**Response includes:**
- 🏛️ Architect's technical solution
- ⚖️ Critic's security review (with scores)
- 🔨 Builder's user stories + Mermaid diagram
- 🎨 Generated architecture image

**Option 2: Idea Agent Only**
```
POST /api/idea
{
  "prompt": "Blockchain solution for supply chain tracking",
  "session_id": "your-session-id"
}
```

**Option 3: Chat with Specific Agent**
```
POST /api/chat
{
  "prompt": "How would you handle user authentication?",
  "session_id": "your-session-id",
  "target_agent": "critic"
}
```

### **Searching Past Ideas**
```
POST /api/search/similar
{
  "query": "mobile app with offline sync",
  "limit": 5,
  "agent_filter": "idea"
}
```

---

## 📊 API Endpoints

### **Sessions**
- `POST /api/sessions` — Create new session
- `GET /api/sessions?user_email=user@example.com` — List all sessions
- `GET /api/sessions/{session_id}` — Get session with messages
- `DELETE /api/sessions/{session_id}` — Delete session

### **AI Agents**
- `POST /api/idea` — Run Idea Agent only
- `POST /api/brainstorm` — Run all agents with feedback loop
- `POST /api/chat` — Chat with specific agent

### **Search & Analytics**
- `POST /api/search/similar` — Vector similarity search
- `GET /api/search/context/{session_id}` — Get relevant context
- `GET /api/stats?user_email=user@example.com` — User statistics
- `GET /api/chunks/stats` — Embedding statistics

---

## 🎯 Real-World Use Cases

### **1. Hackathon Team Planning**
> "We need a project idea for a fintech hackathon with a sustainability focus"

**Output:**
- 3 vetted technical architectures
- Security compliance checklist (PCI-DSS, GDPR)
- 15 user stories ready for Jira
- Mermaid diagram for presentation

### **2. Startup MVP Planning**
> "Food delivery app for college campuses with group ordering"

**Output:**
- Tech stack: Next.js, Node.js, PostgreSQL, Redis
- Security review: Rate limiting, SQL injection prevention
- Scalability plan: Load balancer + CDN strategy
- Sprint 1 tasks breakdown

### **3. Enterprise Feature Scoping**
> "Add AI chatbot to our e-commerce platform"

**Output:**
- Integration architecture with existing systems
- OWASP security assessment
- Implementation roadmap (3 sprints)
- Cost estimation based on infrastructure

---

## 🧪 Example Workflow

```bash
# 1. User submits prompt
"Build a real-time collaborative whiteboard like Miro"

# 2. Architect Agent (with web search + RAG)
→ Researches WebRTC, WebSockets, Canvas API
→ Proposes: Next.js + Socket.io + Redis + PostgreSQL
→ Includes conflict resolution strategy (CRDT)

# 3. Critic Agent reviews (Security Score: 65/100 ❌)
→ REJECTED: "Missing authentication, no rate limiting, Canvas XSS risk"
→ Sends back to Architect for revision

# 4. Architect Agent (Revision #1)
→ Adds: Auth0, rate limiting (Redis), CSP headers
→ Resubmits

# 5. Critic Agent (Security Score: 88/100 ✅)
→ APPROVED: "Meets OWASP standards, scalable to 10k concurrent users"

# 6. Visualizer Agent
→ Generates DALL-E 3 architecture diagram

# 7. Builder Agent
→ Creates 12 user stories (Gherkin format)
→ Lists 25 technical tasks
→ Generates Mermaid.js system flowchart
```

---

## 🔧 Configuration Options

### **Feedback Loop Settings**
```python
# In API request
{
  "max_revisions": 3,  # Max times Critic can reject
  "devils_advocate": true  # Enable strict review mode
}
```

### **Web Search (Optional)**
Enable real-time competitor/tech research:
```env
TAVILY_API_KEY=your-key  # Advanced search
# Or uses DuckDuckGo (no key required)
```

### **RAG System**
Automatically learns from past sessions using vector embeddings.  
No configuration needed — works out of the box!

---

## 📈 Future Enhancements

- 🔐 **OAuth Authentication** (Google, GitHub)
- 💬 **Real-time Collaboration** (WebSocket multi-user sessions)
- 📊 **Analytics Dashboard** (idea success rate, agent performance)
- 🌍 **Deployment Templates** (Docker, Kubernetes, Vercel)
- 🤝 **Team Features** (shared workspaces, comments)
- 📄 **Export Formats** (PDF, Markdown, Confluence)
- 🎨 **Custom Agent Personalities** (user-defined system prompts)

---

## 🙏 Acknowledgments

Built during the **3Pillar Global Hackathon 2025** by Team Luminosity.

**Technologies:**
- [LangGraph](https://github.com/langchain-ai/langgraph) — Multi-agent orchestration
- [OpenRouter](https://openrouter.ai/) — Unified LLM API
- [FastAPI](https://fastapi.tiangolo.com/) — Modern Python web framework
- [Next.js](https://nextjs.org/) — React framework
- [MongoDB Atlas](https://www.mongodb.com/atlas) — Cloud database

---

## 📝 License

MIT License — feel free to use this for your hackathons and projects!

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## 📧 Contact

For questions or collaboration:
- **GitHub:** [@Lexa2805](https://github.com/Lexa2805), [@AbelC27](https://github.com/AbelC27)
- **Project Repository:** [3Pillar_Hackathon](https://github.com/Lexa2805/3Pillar_Hackathon)

---

**Luminosity** — *Illuminate Your Ideas, Architect Your Future* ✨