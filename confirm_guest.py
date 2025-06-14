#!/usr/bin/env python3
import requests

SUPABASE_URL = "https://rglnzrvwkdpwhbhrzvdo.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJnbG56cnZ3a2Rwd2hiaHJ6dmRvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTgxNDgyNCwiZXhwIjoyMDY1MzkwODI0fQ.NUQ1l5nbGWCKkLupBL8c_qaTHsa1LzEqlXYzf2-KxZI"

# Get user by email
url = f"{SUPABASE_URL}/auth/v1/admin/users"
headers = {
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "apikey": SERVICE_ROLE_KEY
}

response = requests.get(url, headers=headers)
users = response.json()

guest_user = None
for user in users.get('users', []):
    if user['email'] == 'guest@neo-demo.com':
        guest_user = user
        break

if guest_user:
    user_id = guest_user['id']
    print(f"Found guest user: {user_id}")
    
    # Update user to confirm email
    update_url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
    update_data = {
        "email_confirm": True
    }
    
    update_response = requests.put(update_url, json=update_data, headers=headers)
    print(f"Update response: {update_response.status_code}")
    print(f"Response: {update_response.text}")
else:
    print("Guest user not found")