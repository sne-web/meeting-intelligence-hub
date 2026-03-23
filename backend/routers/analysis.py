from fastapi import APIRouter, HTTPException
from services.extractor import extract_decisions_and_actions
from services.sentiment import analyse_sentiment
import json
import os

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

STORAGE_DIR = "storage"
MEETINGS_FILE = os.path.join(STORAGE_DIR, "meetings_store.json")

def load_meetings():
    if not os.path.exists(MEETINGS_FILE):
        return []
    with open(MEETINGS_FILE, "r") as f:
        return json.load(f)

def save_meetings(meetings):
    with open(MEETINGS_FILE, "w") as f:
        json.dump(meetings, f, indent=2)

@router.post("/analyse/{meeting_id}")
async def analyse_meeting(meeting_id: str):
    """
    Triggers full AI analysis of a meeting — extraction + sentiment.
    React will call this when the user clicks 'Analyse' on a meeting.
    """
    meetings = load_meetings()
    
    # Find the meeting by ID
    meeting = next((m for m in meetings if m["id"] == meeting_id), None)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Read the transcript file from disk
    try:
        with open(meeting["file_path"], "r", encoding="utf-8") as f:
            transcript_text = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transcript file not found")
    
    # Run extraction — sends transcript to Claude
    extraction = extract_decisions_and_actions(transcript_text)
    
    # Run sentiment analysis — sends transcript to Claude
    sentiment = analyse_sentiment(transcript_text, meeting.get("speakers", []))
    
    # Update the meeting record with results
    for m in meetings:
        if m["id"] == meeting_id:
            m["decisions"] = extraction.get("decisions", [])
            m["action_items"] = extraction.get("action_items", [])
            m["sentiment"] = sentiment
            m["status"] = "processed"
            break
    
    save_meetings(meetings)
    
    return {
        "meeting_id": meeting_id,
        "decisions": extraction.get("decisions", []),
        "action_items": extraction.get("action_items", []),
        "sentiment": sentiment,
        "status": "processed"
    }


@router.get("/{meeting_id}")
def get_analysis(meeting_id: str):
    """Returns previously computed analysis for a meeting."""
    meetings = load_meetings()
    meeting = next((m for m in meetings if m["id"] == meeting_id), None)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {
        "meeting_id": meeting_id,
        "decisions": meeting.get("decisions", []),
        "action_items": meeting.get("action_items", []),
        "sentiment": meeting.get("sentiment"),
        "status": meeting.get("status", "uploaded")
    }