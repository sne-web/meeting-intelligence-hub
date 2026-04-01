# 🎙️ Recall. — Meeting Intelligence Hub

**Recall.** is an AI-powered meeting intelligence workspace that transforms raw meeting transcripts into structured, actionable insights. It extracts key decisions, tracks action items, analyzes sentiment, and enables natural language querying through a built-in chatbot.

---

## 🚀 Features

- **AI-Powered Extraction**  
  Automatically identifies decisions, action items (WHO, WHAT, BY WHEN), and sentiment from transcripts.

- **RAG-Based Chatbot**  
  Ask questions across your meeting data using a chatbot powered by LangChain and ChromaDB.

- **Multi-Transcript Support**  
  Upload and analyze multiple meeting transcripts.

- **Data Visualization**  
  View insights through a clean dashboard with structured tables.

- **Export Functionality**  
  Download results as CSV or PDF.

- **Modern UI**  
  Dark-themed interface built with React and Tailwind CSS.

---

## 🛠️ Tech Stack

**Frontend**
- React (Vite)
- Tailwind CSS

**Backend**
- FastAPI (Python)
- Uvicorn

**AI & Data**
- Groq API — LLM processing (action items, decisions, sentiment)
- HuggingFace (all-MiniLM-L6-v2) — embeddings
- LangChain — RAG pipeline
- ChromaDB — vector database

**Utilities**
- pandas — CSV export  
- reportlab — PDF generation  

---

## 📦 Prerequisites

Make sure you have installed
- Node.js (v16+)
- Python (3.10+)
- pip

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/sne-web/meeting-intelligence-hub
cd recall
```


### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Activate environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# Create .env file and add:
# GROQ_API_KEY=your_api_key_here

uvicorn main:app --reload
```

Backend runs on: http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:5173

---

## ▶️ How to Use

1. Open the application in your browser  
2. Create a workspace  
3. Upload a `.txt` or a `.vtt` meeting transcript  
4. Click "Analyse with AI"  
5. View extracted:
   - Action Items  
   - Decisions  
   - Sentiment  
6. Use the chatbot to query meetings  
7. Export results as CSV or PDF

---

## 🧠 How It Works

1. Transcript is uploaded  
2. Backend processes it using Groq LLM  
3. Extracts structured insights  
4. Generates embeddings using HuggingFace model  
5. Stores embeddings in ChromaDB  
6. Chatbot retrieves and answers using RAG

---

## 📄 License

This project is for educational and hackathon purposes.

---
