#!/usr/bin/env python3
"""
Script to disable email confirmation in Supabase
"""
import os
import requests
from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = "https://rglnzrvwkdpwhbhrzvdo.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJnbG56cnZ3a2Rwd2hiaHJ6dmRvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTgxNDgyNCwiZXhwIjoyMDY1MzkwODI0fQ.NUQ1l5nbGWCKkLupBL8c_qaTHsa1LzEqlXYzf2-KxZI"

def disable_email_confirmation():
    """Disable email confirmation in Supabase"""
    
    # Create admin client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    # Try to update auth settings via REST API
    auth_config_url = f"{SUPABASE_URL}/auth/v1/settings"
    
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "apikey": SUPABASE_SERVICE_ROLE_KEY
    }
    
    # Configuration to disable email confirmation
    config = {
        "DISABLE_SIGNUP": False,
        "SITE_URL": "https://work-1-ycmuzsgbjujyabkc.prod-runtime.all-hands.dev",
        "MAILER_AUTOCONFIRM": True,
        "ENABLE_SIGNUP": True
    }
    
    try:
        response = requests.put(auth_config_url, json=config, headers=headers)
        print(f"Auth config update response: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Email confirmation disabled successfully!")
        else:
            print(f"❌ Failed to update auth config: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error updating auth config: {e}")
    
    # Alternative: Create a confirmed user directly
    try:
        print("\n🔄 Creating pre-confirmed guest user...")
        
        # Create user with email_confirmed_at set
        result = supabase.auth.admin.create_user({
            "email": "guest@neo-demo.com",
            "password": "GuestPassword123!",
            "email_confirm": True,
            "user_metadata": {
                "role": "guest",
                "created_by": "system"
            }
        })
        
        print(f"✅ Guest user created: {result}")
        
    except Exception as e:
        print(f"ℹ️  Guest user might already exist: {e}")

if __name__ == "__main__":
    disable_email_confirmation()