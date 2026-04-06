import os
from dotenv import load_dotenv
import requests

load_dotenv()
url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "Authorization": f"Bearer {service_key}",
    "apikey": service_key,
    "Content-Type": "application/json"
}

# 1. List users
r = requests.get(f"{url}/auth/v1/admin/users", headers=headers)
if r.status_code >= 400:
    print("List users failed:", r.status_code, r.text)
    exit(1)

users = r.json().get("users", [])
if not users:
    print("No users found.")
    exit(0)

# 2. Try to delete the first user
target_user = users[0]
print(f"Targeting: {target_user['email']} (ID: {target_user['id']})")

r_del = requests.delete(f"{url}/auth/v1/admin/users/{target_user['id']}", headers=headers)

if r_del.status_code >= 400:
    print("DELETE FAILED!")
    print("STATUS:", r_del.status_code)
    print("BODY:", r_del.text)
else:
    print("DELETE SUCCEEDED!")
