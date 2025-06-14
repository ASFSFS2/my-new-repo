#!/usr/bin/env python3
"""
Create test user for Neo AI
"""

import requests
import json
import uuid

# Supabase config
SUPABASE_URL = "https://rglnzrvwkdpwhbhrzvdo.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJnbG56cnZ3a2Rwd2hiaHJ6dmRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk4MTQ4MjQsImV4cCI6MjA2NTM5MDgyNH0.quAzFvK7NP71zeTQVCLAb8P8NNewI8O2gHjBlKNm2C8"

# Test user credentials
TEST_EMAIL = "test@neo.ai"
TEST_PASSWORD = "NeoAI2025!"

def create_test_user():
    """Create test user via Supabase Auth"""
    
    # Sign up endpoint
    signup_url = f"{SUPABASE_URL}/auth/v1/signup"
    
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "data": {
            "name": "Test User",
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=test"
        }
    }
    
    try:
        print("🔧 Создаю тестового пользователя...")
        response = requests.post(signup_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            user_id = data.get('user', {}).get('id')
            
            print("✅ Тестовый пользователь создан успешно!")
            print(f"📧 Email: {TEST_EMAIL}")
            print(f"🔑 Password: {TEST_PASSWORD}")
            print(f"🆔 User ID: {user_id}")
            print("")
            print("🌍 Войти можно по ссылке:")
            print("https://hugely-great-marmot.ngrok-free.app/auth")
            
            return True
            
        elif response.status_code == 422:
            # User already exists
            print("ℹ️ Пользователь уже существует!")
            print(f"📧 Email: {TEST_EMAIL}")
            print(f"🔑 Password: {TEST_PASSWORD}")
            print("")
            print("🌍 Войти можно по ссылке:")
            print("https://hugely-great-marmot.ngrok-free.app/auth")
            
            return True
            
        else:
            print(f"❌ Ошибка создания пользователя: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    create_test_user()