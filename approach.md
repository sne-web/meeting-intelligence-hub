# 📄 Approach Document – Recall.

---

## 🧩 1. Problem Understanding  
Modern meetings generate long, unstructured transcripts that are difficult to navigate. Extracting key decisions, identifying action items, and assigning responsibilities manually is time-consuming and often leads to missed follow-ups and lost information.

---

## ⚙️ 2. Solution Overview  
Recall. is an AI-powered workspace that transforms raw meeting transcripts into structured insights and searchable knowledge. It automatically extracts summaries, decisions, and action items, and enables users to query past meetings through a conversational AI interface.

---

## 🏗️ 3. System Architecture  

```
User uploads transcript (React frontend)
        ↓
FastAPI backend processes request
        ↓
LLM (Groq / Anthropic) analyzes transcript
        ↓
Extract structured insights (summary, decisions, actions)
        ↓
Store in Supabase (PostgreSQL)
        ↓
Generate embeddings (HuggingFace - all-MiniLM-L6-v2)
        ↓
Store vectors in ChromaDB
        ↓
RAG chatbot enables semantic search across meetings
```

The system is designed as a decoupled pipeline to ensure scalability and efficient data processing.

---

## 🤖 4. AI Pipeline  
The AI pipeline uses structured prompting to enforce consistent outputs in JSON format. The model extracts:

- **Action Items** → Who, What, By When  
- **Decisions** → Key outcomes agreed upon  
- **Sentiment** → Overall tone of the meeting  

This ensures reliable and structured outputs instead of generic summaries.

---

## 🔍 5. RAG Chatbot  
To enable intelligent querying of past meetings, a Retrieval-Augmented Generation (RAG) system is implemented:

1. User submits a query  
2. Query is converted into embeddings  
3. Top-K relevant chunks are retrieved from ChromaDB  
4. Context is passed to the LLM  
5. The system generates a precise answer with supporting context  

---

## 🗄️ 6. Database Design  
Supabase (PostgreSQL) is used for structured data storage:

- **users** → Managed via Supabase Auth  
- **meetings** → Stores transcripts and metadata  
- **analysis** → Stores structured AI outputs (JSON)  

Relational integrity is maintained using cascading deletes to ensure consistency.

---

## 🔐 7. Authentication  
Authentication is handled using Supabase Auth (JWT-based).  
Row-Level Security (RLS) policies ensure users can only access and query their own meeting data.

---

## 🚀 8. Deployment  

- **Frontend:** Vercel (React UI with CDN delivery)  
- **Backend:** Render (FastAPI + Uvicorn)  
- **Database:** Supabase (PostgreSQL)  

This separation enables independent scaling and better performance.

---

## ⚡ 9. Challenges  

- **Handling Long Transcripts:** Implemented chunking using LangChain’s RecursiveCharacterTextSplitter to manage LLM context limits.  
- **API Latency:** Designed asynchronous processing and loading states to maintain smooth user experience.  
- **Data Synchronization:** Ensured consistency between Supabase (relational data) and ChromaDB (vector data), including cleanup on deletion.  

---

## 🔮 10. Future Scope  

- **Audio Input:** Integrate speech-to-text (e.g., Whisper) for direct audio processing  
- **Real-time Analysis:** Live meeting insights via streaming or webhook integration  
- **Collaboration:** Introduce shared workspaces for team-based access and querying  

---
