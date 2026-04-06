import os
import requests
from supabase import create_client

# parse .env
with open('.env') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            k, v = line.strip().split('=', 1)
            os.environ[k] = v.strip("'").strip('"')

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

email = "test456789@example.com"
password = "password123"

client = create_client(url, key)
resp = client.auth.sign_up({"email": email, "password": password})
token = resp.session.access_token

print("BEFORE:", client.auth.get_user(token).user.user_metadata)

r = requests.put(
    f"{url}/auth/v1/user",
    headers={
        "Authorization": f"Bearer {token}",
        "apikey": key,
        "Content-Type": "application/json"
    },
    json={"data": {"full_name": "Test User"}}
)
print("PUT STATUS:", r.status_code)
print("PUT BODY:", r.json())

print("AFTER:", client.auth.get_user(token).user.user_metadata)

# Clean up
try:
    client.auth.admin.delete_user(resp.user.id)
except Exception as e:
    print("Delete error:", e)
