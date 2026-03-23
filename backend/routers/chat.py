from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.rag_engine import query_transcripts, index_transcript
import json
import os

router = APIRouter(prefix="/api/chat", tags=["chat"])

STORAGE_DIR = "storage"
MEETINGS_FILE = os.path.join(STORAGE_DIR, "meetings_store.json")

def load_meetings():
    if not os.path.exists(MEETINGS_FILE):
        return []
    with open(MEETINGS_FILE, "r") as f:
        return json.load(f)

# Pydantic model — defines the shape of the request body React sends
class ChatRequest(BaseModel):
    question: str
    meeting_id: str = None  # Optional — if None, search all meetings

@router.post("/ask")
async def ask_question(request: ChatRequest):
    """
    Receives a question from React and returns an AI answer
    with citations from the transcript.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    result = query_transcripts(
        question=request.question,
        meeting_id=request.meeting_id
    )
    
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "question": request.question
    }

@router.post("/index/{meeting_id}")
async def index_meeting(meeting_id: str):
    """
    Indexes a meeting transcript into ChromaDB for RAG search.
    Called automatically when a meeting is analysed.
    """
    meetings = load_meetings()
    meeting = next((m for m in meetings if m["id"] == meeting_id), None)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    try:
        with open(meeting["file_path"], "r", encoding="utf-8") as f:
            transcript_text = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transcript file not found")
    
    chunks_count = index_transcript(meeting_id, transcript_text)
    
    return {"indexed": True, "chunks": chunks_count}