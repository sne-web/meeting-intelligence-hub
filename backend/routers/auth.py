import os
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from models.schemas import UserCreate, UserLogin, Token, NameUpdate
import requests

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

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    supabase = get_supabase()
    try:
        response = supabase.auth.get_user(credentials.credentials)
        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return response.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

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

@router.get("/me")
def get_me(user = Depends(get_current_user)):
    return {
        "email": user.email,
        "full_name": user.user_metadata.get("full_name", "")
    }

@router.put("/me/name")
def update_name(name_update: NameUpdate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    resp = requests.put(
        f"{url}/auth/v1/user",
        headers={
            "Authorization": f"Bearer {token}",
            "apikey": key,
            "Content-Type": "application/json"
        },
        json={"data": {"full_name": name_update.full_name}}
    )
    if resp.status_code >= 400:
        raise HTTPException(status_code=400, detail="Failed to update name")
    return {"message": "success", "full_name": name_update.full_name}

@router.delete("/me")
def delete_account(user = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    import os
    from supabase import create_client, ClientOptions
    
    # 1. Clean ChromaDB since Postgres CASCADE won't reach local file stores
    try:
        token = credentials.credentials
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        supabase = create_client(url, key, options=ClientOptions(headers={"Authorization": f"Bearer {token}"}))
        
        res = supabase.table("meetings").select("id").eq("user_id", str(user.id)).execute()
        if res.data:
            import chromadb
            client = chromadb.PersistentClient(path="storage/chroma_db")
            for m in res.data:
                try: client.delete_collection(f"meeting_{m['id']}")
                except: pass
    except Exception as e:
        print("Chroma cleanup failed prior to deletion", e)
        
    # 2. Fully delete the user from Supabase auth.users database
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if service_key:
        try:
            admin_client = create_client(url, service_key)
            admin_client.auth.admin.delete_user(user.id)
            return {"message": "Account fully deleted from Supabase. You can now log out."}
        except Exception as e:
            print(f"Admin delete failed: {e}")
            raise HTTPException(status_code=500, detail=f"Supabase rejected the admin API call: {str(e)}")
    else:
        raise HTTPException(status_code=500, detail="Missing SUPABASE_SERVICE_ROLE_KEY in backend/.env")
