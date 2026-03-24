from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import json
import uuid
from datetime import datetime

# APIRouter is like a mini FastAPI app — it holds a group of related routes
# We'll register this router in main.py so FastAPI knows about it
router = APIRouter(prefix="/api/transcripts", tags=["transcripts"])

# Path to our JSON "database" file and uploads folder
STORAGE_DIR = "storage"
UPLOADS_DIR = os.path.join(STORAGE_DIR, "uploads")
MEETINGS_FILE = os.path.join(STORAGE_DIR, "meetings_store.json")

def load_meetings():
    """Read all meetings from our JSON store."""
    if not os.path.exists(MEETINGS_FILE):
        return []
    with open(MEETINGS_FILE, "r") as f:
        return json.load(f)

def save_meetings(meetings):
    """Write meetings list back to our JSON store."""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    with open(MEETINGS_FILE, "w") as f:
        json.dump(meetings, f, indent=2)

def count_words(text):
    """Count total words in a transcript."""
    return len(text.split())

def detect_speakers(text):
    """
    Try to find speaker names in the transcript.
    Most transcripts follow the pattern 'Speaker Name: dialogue'
    We look for lines matching that pattern and collect unique names.
    """
    speakers = set()
    lines = text.split("\n")
    for line in lines:
        # If a line has a colon, the part before it might be a speaker name
        if ":" in line:
            potential_speaker = line.split(":")[0].strip()
            # Speaker names are usually short (under 5 words) and not too long
            if len(potential_speaker) > 0 and len(potential_speaker.split()) <= 4:
                speakers.add(potential_speaker)
    return list(speakers)

@router.post("/upload")
async def upload_transcripts(files: List[UploadFile] = File(...)):
    """
    Receives one or more transcript files from React,
    saves them to disk, and stores metadata in our JSON store.
    """
    # Validate file types — only .txt and .vtt allowed
    allowed_extensions = {".txt", ".vtt"}
    uploaded = []

    for file in files:
        # Get the file extension e.g. ".txt"
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' is not supported. Only .txt and .vtt files are allowed."
            )

        # Read the file content
        content = await file.read()
        text = content.decode("utf-8", errors="ignore")

        # Generate a unique ID for this meeting
        meeting_id = str(uuid.uuid4())

        # Save the file to disk
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        file_path = os.path.join(UPLOADS_DIR, f"{meeting_id}{ext}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        # Build metadata about this meeting
        meeting = {
            "id": meeting_id,
            "filename": file.filename,
            "file_path": file_path,
            "extension": ext,
            "upload_date": datetime.now().isoformat(),
            "word_count": count_words(text),
            "speakers": detect_speakers(text),
            "status": "uploaded",  # Will change to "processed" after AI analysis
            "decisions": [],
            "action_items": [],
            "sentiment": None
        }

        # Add to our meetings list
        meetings = load_meetings()
        meetings.append(meeting)
        save_meetings(meetings)

        uploaded.append({
            "id": meeting_id,
            "filename": file.filename,
            "word_count": meeting["word_count"],
            "speakers": meeting["speakers"],
            "upload_date": meeting["upload_date"]
        })

    return {"uploaded": uploaded, "count": len(uploaded)}


@router.get("/")
def get_meetings():
    """Returns all uploaded meetings for the Dashboard."""
    meetings = load_meetings()
    # Return a summary of each meeting (not the full text)
    return {"meetings": [
        {
            "id": m["id"],
            "filename": m["filename"],
            "upload_date": m["upload_date"],
            "word_count": m["word_count"],
            "speakers": m["speakers"],
            "status": m["status"],
            "action_items_count": len(m.get("action_items", [])),
            "decisions_count": len(m.get("decisions", []))
        }
        for m in meetings
    ]}


@router.get("/{meeting_id}")
def get_meeting(meeting_id: str):
    """Returns full details of a single meeting."""
    meetings = load_meetings()
    meeting = next((m for m in meetings if m["id"] == meeting_id), None)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.delete("/{meeting_id}")
def delete_meeting(meeting_id: str):
    """
    Deletes a meeting — removes the file, JSON record, 
    and ChromaDB collection.
    """
    meetings = load_meetings()
    meeting = next((m for m in meetings if m["id"] == meeting_id), None)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Delete the transcript file from disk
    try:
        if os.path.exists(meeting["file_path"]):
            os.remove(meeting["file_path"])
    except Exception as e:
        print(f"Warning: could not delete file: {e}")
    
    # Delete from ChromaDB
    try:
        import chromadb
        client = chromadb.PersistentClient(path="storage/chroma_db")
        client.delete_collection(f"meeting_{meeting_id}")
    except Exception as e:
        print(f"Warning: could not delete ChromaDB collection: {e}")
    
    # Remove from JSON store
    meetings = [m for m in meetings if m["id"] != meeting_id]
    save_meetings(meetings)
    
    return {"deleted": True, "meeting_id": meeting_id}