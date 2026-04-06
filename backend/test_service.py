import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("Key available:", bool(service_key))
print("Key prefix:", service_key[:10] if service_key else "None")

try:
    admin_client = create_client(url, service_key)
    
    # Try to create a dummy user
    print("Creating dummy user via admin...")
    resp = admin_client.auth.admin.create_user({
        "email": "dummy_test_delete_12345@example.com",
        "password": "password123",
        "email_confirm": True
    })
    
    user_id = resp.user.id
    print("Created successfully:", user_id)
    
    # Try to delete it
    print("Deleting user via admin...")
    admin_client.auth.admin.delete_user(user_id)
    print("Deleted successfully!")
    
except Exception as e:
    print("Exception occurred:", type(e), str(e))
