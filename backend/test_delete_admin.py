import os
from dotenv import load_dotenv
from supabase import create_client
import sys

load_dotenv()
url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

admin_client = create_client(url, service_key)

# Get all users (just getting the first to find one that might fail)
try:
    auth_users = admin_client.auth.admin.list_users()
    if not auth_users.users:
        print("No users to delete!")
        sys.exit(0)
    
    target_user = auth_users.users[0]
    print(f"Trying to delete user: {target_user.email} ({target_user.id})")
    
    admin_client.auth.admin.delete_user(target_user.id)
    print("Deleted successfully!")
    
except Exception as e:
    import traceback
    traceback.print_exc()
    if hasattr(e, 'message'):
        print("Error message:", getattr(e, 'message'))
    print("Exception details:", dir(e))
    # If it's an API error, try to print its dict
    try:
        print("API Error mapping:", e.to_dict())
    except:
        pass
