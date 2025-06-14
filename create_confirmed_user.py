#!/usr/bin/env python3
"""
Create confirmed test user for Neo AI using service role key
"""

import requests
import json
import uuid
from datetime import datetime, timezone

# Supabase config
SUPABASE_URL = "https://rglnzrvwkdpwhbhrzvdo.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJnbG56cnZ3a2Rwd2hiaHJ6dmRvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTgxNDgyNCwiZXhwIjoyMDY1MzkwODI0fQ.NUQ1l5nbGWCKkLupBL8c_qaTHsa1LzEqlXYzf2-KxZI"

# Test user credentials
TEST_EMAIL = "test@neo.ai"
TEST_PASSWORD = "NeoAI2025!"

def create_confirmed_user():
    """Create confirmed test user via Supabase Admin API"""
    
    # Admin users endpoint
    admin_url = f"{SUPABASE_URL}/auth/v1/admin/users"
    
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }
    
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "email_confirm": True,  # Auto-confirm email
        "user_metadata": {
            "name": "Test User",
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=test"
        },
        "app_metadata": {},
        "confirm": True
    }
    
    try:
        print("🔧 Создаю подтвержденного тестового пользователя...")
        response = requests.post(admin_url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            data = response.json()
            user_id = data.get('id')
            
            print("✅ Подтвержденный тестовый пользователь создан успешно!")
            print(f"📧 Email: {TEST_EMAIL}")
            print(f"🔑 Password: {TEST_PASSWORD}")
            print(f"🆔 User ID: {user_id}")
            print(f"✅ Email confirmed: True")
            print("")
            print("🌍 Войти можно по ссылке:")
            print("https://hugely-great-marmot.ngrok-free.app/auth")
            
            return True
            
        else:
            print(f"❌ Ошибка создания пользователя: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try to delete existing user first
            if "already been registered" in response.text or response.status_code == 422:
                print("🔄 Пользователь уже существует, пытаюсь обновить...")
                return update_existing_user()
            
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def update_existing_user():
    """Update existing user to confirm email"""
    
    # First, get user by email
    get_url = f"{SUPABASE_URL}/auth/v1/admin/users"
    
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get users
        response = requests.get(get_url, headers=headers)
        if response.status_code == 200:
            users = response.json().get('users', [])
            test_user = None
            
            for user in users:
                if user.get('email') == TEST_EMAIL:
                    test_user = user
                    break
            
            if test_user:
                user_id = test_user['id']
                
                # Update user to confirm email
                update_url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
                
                update_payload = {
                    "email_confirm": True,
                    "user_metadata": {
                        "name": "Test User",
                        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=test"
                    }
                }
                
                update_response = requests.put(update_url, headers=headers, json=update_payload)
                
                if update_response.status_code == 200:
                    print("✅ Пользователь обновлен и подтвержден!")
                    print(f"📧 Email: {TEST_EMAIL}")
                    print(f"🔑 Password: {TEST_PASSWORD}")
                    print(f"🆔 User ID: {user_id}")
                    print(f"✅ Email confirmed: True")
                    print("")
                    print("🌍 Войти можно по ссылке:")
                    print("https://hugely-great-marmot.ngrok-free.app/auth")
                    return True
                else:
                    print(f"❌ Ошибка обновления пользователя: {update_response.status_code}")
                    print(f"Response: {update_response.text}")
                    return False
            else:
                print("❌ Пользователь не найден")
                return False
        else:
            print(f"❌ Ошибка получения пользователей: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка обновления: {e}")
        return False

if __name__ == "__main__":
    create_confirmed_user()