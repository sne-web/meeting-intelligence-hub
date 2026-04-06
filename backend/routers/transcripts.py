from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from routers.auth import get_current_user, security
from fastapi.security import HTTPAuthorizationCredentials
from typing import List
import os
import uuid
from datetime import datetime
from supabase import create_client, ClientOptions

router = APIRouter(prefix="/api/transcripts", tags=["transcripts"])

def get_user_client(token: str):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key, options=ClientOptions(headers={"Authorization": f"Bearer {token}"}))

@router.post("/upload")
async def upload_transcripts(
    files: List[UploadFile] = File(...), 
    user = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    allowed_extensions = {".txt", ".vtt"}
    uploaded = []
    
    supabase = get_user_client(credentials.credentials)

    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Only .txt and .vtt allowed")

        content = await file.read()
        text = content.decode("utf-8", errors="ignore")

        meeting_id = str(uuid.uuid4())
        word_count = len(text.split())
        
        speakers = []
        for line in text.split("\n"):
            if ":" in line:
                pot = line.split(":")[0].strip()
                if 0 < len(pot.split()) <= 4:
                    if pot not in speakers:
                        speakers.append(pot)

        data = {
            "id": meeting_id,
            "user_id": str(user.id),
            "filename": file.filename,
            "status": "uploaded",
            "word_count": word_count,
            "speakers": speakers,
            "transcript_text": text
        }
        
        res = supabase.table("meetings").insert(data).execute()
        
        uploaded.append({
            "id": meeting_id,
            "filename": file.filename,
            "word_count": word_count,
            "speakers": speakers,
            "upload_date": datetime.now().isoformat()
        })

    return {"uploaded": uploaded, "count": len(uploaded)}

@router.get("/")
def get_meetings(user = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    supabase = get_user_client(credentials.credentials)
    res = supabase.table("meetings").select("id, filename, upload_date, status, word_count, speakers, analysis_results").order("upload_date", desc=True).execute()
    
    meetings = []
    for m in res.data:
        analysis = m.get("analysis_results") or {}
        meetings.append({
            "id": m["id"],
            "filename": m["filename"],
            "upload_date": m["upload_date"],
            "word_count": m["word_count"],
            "speakers": m["speakers"],
            "status": m["status"],
            "action_items_count": len(analysis.get("action_items", [])),
            "decisions_count": len(analysis.get("decisions", []))
        })
    return {"meetings": meetings}

@router.get("/{meeting_id}")
def get_meeting(meeting_id: str, user = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    supabase = get_user_client(credentials.credentials)
    res = supabase.table("meetings").select("*").eq("id", meeting_id).execute()
    if not res.data:
        raise HTTPException(404, "Meeting not found")
        
    m = res.data[0]
    analysis = m.get("analysis_results") or {}
    return {
        "id": m["id"],
        "filename": m["filename"],
        "upload_date": m["upload_date"],
        "status": m["status"],
        "transcript_text": m.get("transcript_text", ""),
        "word_count": m.get("word_count", 0),
        "speakers": m.get("speakers", []),
        "decisions": analysis.get("decisions", []),
        "action_items": analysis.get("action_items", []),
        "sentiment": analysis.get("sentiment")
    }

@router.delete("/{meeting_id}")
def delete_meeting(meeting_id: str, user = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    supabase = get_user_client(credentials.credentials)
    res = supabase.table("meetings").delete().eq("id", meeting_id).execute()
    
    try:
        import chromadb
        client = chromadb.PersistentClient(path="storage/chroma_db")
        client.delete_collection(f"meeting_{meeting_id}")
    except: pass
    
    return {"deleted": True, "meeting_id": meeting_id}