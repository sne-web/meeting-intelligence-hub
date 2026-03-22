from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

# Notice we added root_path="/api" — this tells FastAPI
# that all its routes are prefixed with /api
# So /health becomes /api/health, matching what React calls
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

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api")
def read_root():
    return {"message": "Welcome to Recall. API", "status": "running"}
