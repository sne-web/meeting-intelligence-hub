from fastapi import APIRouter, HTTPException, Depends
from routers.auth import get_current_user, security
from fastapi.security import HTTPAuthorizationCredentials
from services.extractor import extract_decisions_and_actions
from services.sentiment import analyse_sentiment
from services.rag_engine import index_transcript
import os
from supabase import create_client, ClientOptions

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

def get_user_client(token: str):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key, options=ClientOptions(headers={"Authorization": f"Bearer {token}"}))

@router.post("/analyse/{meeting_id}")
async def analyse_meeting(meeting_id: str, user = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    supabase = get_user_client(credentials.credentials)
    
    res = supabase.table("meetings").select("transcript_text, speakers").eq("id", meeting_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    m = res.data[0]
    transcript_text = m.get("transcript_text", "")
    speakers = m.get("speakers", [])
    
    if not transcript_text:
        raise HTTPException(status_code=400, detail="Transcript text is empty")
    
    extraction = extract_decisions_and_actions(transcript_text)
    sentiment = analyse_sentiment(transcript_text, speakers)
    
    try:
        index_transcript(meeting_id, transcript_text)
    except Exception as e:
        print(f"Warning: RAG indexing failed: {e}")
        
    analysis_results = {
        "decisions": extraction.get("decisions", []),
        "action_items": extraction.get("action_items", []),
        "sentiment": sentiment
    }
    
    supabase.table("meetings").update({
        "status": "processed",
        "analysis_results": analysis_results
    }).eq("id", meeting_id).execute()
    
    return {
        "meeting_id": meeting_id,
        "decisions": analysis_results["decisions"],
        "action_items": analysis_results["action_items"],
        "sentiment": analysis_results["sentiment"],
        "status": "processed"
    }

@router.get("/{meeting_id}")
def get_analysis(meeting_id: str, user = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    supabase = get_user_client(credentials.credentials)
    res = supabase.table("meetings").select("analysis_results, status").eq("id", meeting_id).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    m = res.data[0]
    analysis = m.get("analysis_results") or {}
    return {
        "meeting_id": meeting_id,
        "decisions": analysis.get("decisions", []),
        "action_items": analysis.get("action_items", []),
        "sentiment": analysis.get("sentiment"),
        "status": m.get("status", "uploaded")
    }