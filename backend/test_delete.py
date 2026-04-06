import os
from dotenv import load_dotenv
from supabase import create_client, ClientOptions

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

email = "delete_test_99@example.com"
password = "password123"

# Create standard admin client to manage user
client = create_client(url, key)
resp = client.auth.sign_up({"email": email, "password": password})
token = resp.session.access_token

# Connect user client to test RPC
user_client = create_client(url, key, options=ClientOptions(headers={"Authorization": f"Bearer {token}"}))
try:
    rpc_res = user_client.rpc("delete_current_user").execute()
    print("Delete success!")
except Exception as e:
    print("RPC ERROR:", e)

# Force verify deletion using the original client:
try:
    print("Verification post-delete:", client.auth.get_user(token).user.email)
    
    # If the email printed, it wasn't deleted. Let's force clean up
    client.auth.admin.delete_user(resp.user.id)
    print("Cleaned up failure.")
except Exception as e:
    print("Verify user failed - which means they might be successfully deleted!", e)
    
