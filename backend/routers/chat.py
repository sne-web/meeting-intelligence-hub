from fastapi import APIRouter, HTTPException, Depends
from routers.auth import get_current_user, security
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from services.rag_engine import query_transcripts, index_transcript
import os
from supabase import create_client, ClientOptions

router = APIRouter(prefix="/api/chat", tags=["chat"])

def get_user_client(token: str):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key, options=ClientOptions(headers={"Authorization": f"Bearer {token}"}))

class ChatRequest(BaseModel):
    question: str
    meeting_id: str = None  # Optional

@router.post("/ask")
async def ask_question(request: ChatRequest, user = Depends(get_current_user)):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    result = query_transcripts(
        question=request.question,
        meeting_id=request.meeting_id,
        user_id=str(user.id)
    )
    
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "question": request.question
    }

@router.post("/index/{meeting_id}")
async def index_meeting(meeting_id: str, user = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    supabase = get_user_client(credentials.credentials)
    
    res = supabase.table("meetings").select("transcript_text").eq("id", meeting_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    transcript_text = res.data[0].get("transcript_text", "")
    
    chunks_count = index_transcript(meeting_id, transcript_text)
    
    return {"indexed": True, "chunks": chunks_count}