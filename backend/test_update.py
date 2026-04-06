import os
from dotenv import load_dotenv
from supabase import create_client, ClientOptions
import requests

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

email = "test991199@example.com"
password = "password123"

client = create_client(url, key)
resp = client.auth.sign_up({"email": email, "password": password})
token = resp.session.access_token

print("BEFORE:", client.auth.get_user(token).user.user_metadata)

try:
    # Method 1: Localized client
    user_client = create_client(url, key, options=ClientOptions(headers={"Authorization": f"Bearer {token}"}))
    update_resp = user_client.auth.update_user({"data": {"full_name": "Test Name Localized Client"}})
    print("UPDATED VIA SDK:", update_resp.user.user_metadata)

    print("GET USER AFTER SDK:", client.auth.get_user(token).user.user_metadata)
    
except Exception as e:
    print("Failed SDK method:", e)

# Clean up
client.auth.admin.delete_user(resp.user.id)
