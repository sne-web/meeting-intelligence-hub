from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import transcripts

load_dotenv()

app = FastAPI(
    title="Recall. API",
    description="Backend API for the Recall meeting intelligence platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers — this tells FastAPI about all the transcript routes
app.include_router(transcripts.router)

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api")
def read_root():
    return {"message": "Welcome to Recall. API", "status": "running"}