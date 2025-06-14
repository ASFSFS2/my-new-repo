#!/usr/bin/env python3
"""
Comprehensive verification script for Neo AI setup
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add backend to path for imports
sys.path.append('backend')

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}{Colors.ENDC}")

def check_mark(condition, message):
    if condition:
        print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}❌ {message}{Colors.ENDC}")
        return False

def warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")

def verify_environment_files():
    """Verify .env files are properly configured"""
    print_header("Environment Configuration")
    
    success = True
    
    # Backend .env
    backend_env = Path("backend/.env")
    if backend_env.exists():
        with open(backend_env) as f:
            content = f.read()
            
        success &= check_mark(
            "SUPABASE_URL=https://qytdfvyzywvbhcykwfox.supabase.co" in content,
            "Backend Supabase URL configured"
        )
        success &= check_mark(
            "OPENROUTER_API_KEY=sk-or-v1-" in content,
            "OpenRouter API key configured"
        )
        success &= check_mark(
            "MODEL_TO_USE=deepseek/deepseek-chat:free" in content,
            "Default model set to DeepSeek"
        )
        success &= check_mark(
            "ENV_MODE=local" in content,
            "Environment mode set to local"
        )
    else:
        success = False
        check_mark(False, "Backend .env file exists")
    
    # Frontend .env
    frontend_env = Path("frontend/.env")
    if frontend_env.exists():
        with open(frontend_env) as f:
            content = f.read()
            
        success &= check_mark(
            "qytdfvyzywvbhcykwfox.supabase.co" in content,
            "Frontend Supabase URL configured"
        )
        success &= check_mark(
            'NEXT_PUBLIC_ENV_MODE="LOCAL"' in content,
            "Frontend environment mode set"
        )
    else:
        success = False
        check_mark(False, "Frontend .env file exists")
    
    return success

def verify_model_configuration():
    """Verify model configuration is correct"""
    print_header("Model Configuration")
    
    success = True
    
    try:
        from backend.utils.constants import MODEL_ACCESS_TIERS, MODEL_NAME_ALIASES
        
        # Check all tiers have only DeepSeek
        all_models = set()
        for tier, models in MODEL_ACCESS_TIERS.items():
            all_models.update(models)
            success &= check_mark(
                models == ["deepseek/deepseek-chat:free"],
                f"Tier {tier} has only DeepSeek model"
            )
        
        success &= check_mark(
            all_models == {"deepseek/deepseek-chat:free"},
            "Only DeepSeek model available across all tiers"
        )
        
        # Check aliases
        success &= check_mark(
            "deepseek" in MODEL_NAME_ALIASES,
            "DeepSeek alias configured"
        )
        success &= check_mark(
            MODEL_NAME_ALIASES["deepseek"] == "deepseek/deepseek-chat:free",
            "DeepSeek alias points to correct model"
        )
        
    except ImportError as e:
        success = False
        check_mark(False, f"Could not import model configuration: {e}")
    
    return success

def verify_branding():
    """Verify all Neo references have been changed to Neo"""
    print_header("Branding Update")
    
    success = True
    
    # Check site configuration
    site_config = Path("frontend/src/lib/site.ts")
    if site_config.exists():
        with open(site_config) as f:
            content = f.read()
        
        success &= check_mark(
            "name: 'Neo AI'" in content,
            "Site name changed to Neo AI"
        )
        success &= check_mark(
            "url: 'https://neo.ai/'" in content,
            "Site URL updated to neo.ai"
        )
    else:
        success = False
        check_mark(False, "Site configuration file exists")
    
    # Check package.json files
    frontend_package = Path("frontend/package.json")
    if frontend_package.exists():
        with open(frontend_package) as f:
            content = json.load(f)
        
        success &= check_mark(
            content.get("name") == "neo",
            "Frontend package name changed to neo"
        )
    
    backend_pyproject = Path("backend/pyproject.toml")
    if backend_pyproject.exists():
        with open(backend_pyproject) as f:
            content = f.read()
        
        success &= check_mark(
            'name = "neo"' in content,
            "Backend package name changed to neo"
        )
    
    # Check README
    readme = Path("README.md")
    if readme.exists():
        with open(readme) as f:
            content = f.read()
        
        success &= check_mark(
            "# Neo - Open Source Generalist AI Agent" in content,
            "README title updated to Neo"
        )
    
    return success

def verify_dependencies():
    """Check if required dependencies are available"""
    print_header("Dependencies")
    
    success = True
    
    # Check Docker
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        success &= check_mark(result.returncode == 0, "Docker is installed")
    except FileNotFoundError:
        success = False
        check_mark(False, "Docker is installed")
    
    # Check Docker Compose
    try:
        result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
        success &= check_mark(result.returncode == 0, "Docker Compose is available")
    except FileNotFoundError:
        success = False
        check_mark(False, "Docker Compose is available")
    
    # Check Python version
    python_version = sys.version_info
    success &= check_mark(
        python_version >= (3, 11),
        f"Python version {python_version.major}.{python_version.minor} >= 3.11"
    )
    
    return success

def verify_file_structure():
    """Verify important files exist"""
    print_header("File Structure")
    
    success = True
    
    important_files = [
        "backend/api.py",
        "backend/utils/config.py",
        "backend/utils/constants.py",
        "frontend/package.json",
        "frontend/src/app/layout.tsx",
        "docker-compose.yaml",
        "setup.py",
        "start.py"
    ]
    
    for file_path in important_files:
        success &= check_mark(
            Path(file_path).exists(),
            f"{file_path} exists"
        )
    
    return success

def main():
    print(f"""
{Colors.BLUE}{Colors.BOLD}
   ███╗   ██╗███████╗ ██████╗ 
   ████╗  ██║██╔════╝██╔═══██╗
   ██╔██╗ ██║█████╗  ██║   ██║
   ██║╚██╗██║██╔══╝  ██║   ██║
   ██║ ╚████║███████╗╚██████╔╝
   ╚═╝  ╚═══╝╚══════╝ ╚═════╝ 
                              
   Setup Verification
{Colors.ENDC}""")
    
    all_checks = [
        verify_file_structure(),
        verify_environment_files(),
        verify_model_configuration(),
        verify_branding(),
        verify_dependencies()
    ]
    
    print_header("Summary")
    
    if all(all_checks):
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 All checks passed! Neo AI is ready to launch!{Colors.ENDC}")
        print(f"\n{Colors.BLUE}Next steps:{Colors.ENDC}")
        print("1. Run: python setup.py")
        print("2. Run: python start.py")
        print("3. Open: http://localhost:3000")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Some checks failed. Please review the issues above.{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())