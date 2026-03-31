import os
from fastapi import APIRouter, HTTPException, status
from supabase import create_client, Client
from models.schemas import UserCreate, UserLogin, Token

router = APIRouter(prefix="/api/auth", tags=["auth"])

def get_supabase() -> Client:
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise HTTPException(
            status_code=500, 
            detail="Supabase credentials not found in .env files. Please set SUPABASE_URL and SUPABASE_KEY."
        )
    return create_client(url, key)

@router.post("/register", response_model=Token)
def register(user: UserCreate):
    supabase = get_supabase()
    try:
        response = supabase.auth.sign_up({"email": user.email, "password": user.password})
        
        # If email confirmations are enabled in Supabase by default, session will be null
        if response.session:
            return {"access_token": response.session.access_token, "token_type": "bearer"}
            
        # Fallback if email confirm is turned on
        raise HTTPException(
            status_code=400, 
            detail="Registration successful! Please check your email to confirm your account."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login(user: UserLogin):
    supabase = get_supabase()
    try:
        response = supabase.auth.sign_in_with_password({"email": user.email, "password": user.password})
        if not response.session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        return {"access_token": response.session.access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
