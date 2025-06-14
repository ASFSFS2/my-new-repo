#!/usr/bin/env python3
"""
Test script to verify Neo configuration
"""

import os
import sys
sys.path.append('backend')

def test_env_files():
    """Test that .env files exist and contain required values"""
    print("🔍 Testing environment files...")
    
    # Check backend .env
    backend_env = "backend/.env"
    if os.path.exists(backend_env):
        print(f"✅ {backend_env} exists")
        with open(backend_env, 'r') as f:
            content = f.read()
            if "SUPABASE_URL=https://qytdfvyzywvbhcykwfox.supabase.co" in content:
                print("✅ Supabase URL configured")
            if "OPENROUTER_API_KEY=sk-or-v1-" in content:
                print("✅ OpenRouter API key configured")
            if "MODEL_TO_USE=deepseek/deepseek-chat:free" in content:
                print("✅ Default model set to DeepSeek")
    else:
        print(f"❌ {backend_env} not found")
    
    # Check frontend .env
    frontend_env = "frontend/.env"
    if os.path.exists(frontend_env):
        print(f"✅ {frontend_env} exists")
        with open(frontend_env, 'r') as f:
            content = f.read()
            if "qytdfvyzywvbhcykwfox.supabase.co" in content:
                print("✅ Frontend Supabase URL configured")
    else:
        print(f"❌ {frontend_env} not found")

def test_model_config():
    """Test model configuration"""
    print("\n🤖 Testing model configuration...")
    
    try:
        from backend.utils.constants import MODEL_ACCESS_TIERS, MODEL_NAME_ALIASES
        
        # Check that only DeepSeek is available
        all_models = set()
        for tier_models in MODEL_ACCESS_TIERS.values():
            all_models.update(tier_models)
        
        if all_models == {"deepseek/deepseek-chat:free"}:
            print("✅ Only DeepSeek model available in all tiers")
        else:
            print(f"❌ Unexpected models found: {all_models}")
        
        # Check aliases
        if "deepseek" in MODEL_NAME_ALIASES:
            print("✅ DeepSeek alias configured")
        
    except ImportError as e:
        print(f"❌ Could not import model configuration: {e}")

def test_site_config():
    """Test site configuration"""
    print("\n🌐 Testing site configuration...")
    
    try:
        sys.path.append('frontend/src')
        # We can't directly import the TypeScript file, so we'll check the files
        
        site_config_file = "frontend/src/lib/site.ts"
        if os.path.exists(site_config_file):
            with open(site_config_file, 'r') as f:
                content = f.read()
                if "name: 'Neo AI'" in content:
                    print("✅ Site name changed to Neo AI")
                if "url: 'https://neo.ai/'" in content:
                    print("✅ Site URL updated")
        
        # Check package.json
        package_json = "frontend/package.json"
        if os.path.exists(package_json):
            with open(package_json, 'r') as f:
                content = f.read()
                if '"name": "neo"' in content:
                    print("✅ Frontend package name changed to neo")
        
        # Check backend pyproject.toml
        pyproject = "backend/pyproject.toml"
        if os.path.exists(pyproject):
            with open(pyproject, 'r') as f:
                content = f.read()
                if 'name = "neo"' in content:
                    print("✅ Backend package name changed to neo")
                    
    except Exception as e:
        print(f"❌ Error checking site config: {e}")

def main():
    print("🚀 Neo AI Configuration Test")
    print("=" * 40)
    
    test_env_files()
    test_model_config()
    test_site_config()
    
    print("\n" + "=" * 40)
    print("✨ Configuration test completed!")
    print("\nNext steps:")
    print("1. Run 'python setup.py' to complete setup")
    print("2. Run 'python start.py' to start the application")

if __name__ == "__main__":
    main()