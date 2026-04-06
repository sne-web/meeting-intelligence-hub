import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
client = create_client(url, key)

try:
    res = client.table("users").select("*").limit(1).execute()
    print("Found 'users' table:", res.data)
except Exception as e:
    print("No 'users' table accessible via REST:", e)
    
try:
    res = client.table("profiles").select("*").limit(1).execute()
    print("Found 'profiles' table:", res.data)
except Exception as e:
    print("No 'profiles' table accessible via REST:", e)

