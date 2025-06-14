#!/usr/bin/env python3
"""
Test script for local Docker sandbox
Run this to test if local sandbox works without Daytona
"""

import sys
import os
sys.path.append('backend')

from backend.sandbox.local_sandbox import local_sandbox
import asyncio

async def test_local_sandbox():
    """Test local sandbox functionality"""
    
    print("🧪 Testing Local Docker Sandbox")
    print("=" * 50)
    
    # Check if Docker is available
    print("1. Checking Docker availability...")
    if not local_sandbox.is_available():
        print("❌ Docker is not available or not running")
        print("   Please install Docker and make sure it's running")
        return False
    print("✅ Docker is available")
    
    # Build sandbox image
    print("\n2. Building sandbox image...")
    if not local_sandbox.build_sandbox_image():
        print("❌ Failed to build sandbox image")
        return False
    print("✅ Sandbox image built successfully")
    
    # Create sandbox
    print("\n3. Creating sandbox container...")
    try:
        sandbox_id = local_sandbox.create_sandbox()
        print(f"✅ Sandbox created: {sandbox_id}")
    except Exception as e:
        print(f"❌ Failed to create sandbox: {e}")
        return False
    
    # Get container info
    print("\n4. Getting container information...")
    try:
        info = local_sandbox.get_container_info(sandbox_id)
        print(f"✅ Container status: {info['status']}")
        print(f"   noVNC URL: {info['novnc_url']}")
        print(f"   VNC Port: {info['vnc_port']}")
    except Exception as e:
        print(f"❌ Failed to get container info: {e}")
    
    # Test code execution
    print("\n5. Testing Python code execution...")
    try:
        result = local_sandbox.execute_code(
            sandbox_id, 
            "print('Hello from local sandbox!')\nprint(2 + 2)",
            "python"
        )
        if result['success']:
            print("✅ Python code executed successfully")
            print(f"   Output: {result['output'].strip()}")
        else:
            print(f"❌ Python execution failed: {result['output']}")
    except Exception as e:
        print(f"❌ Failed to execute Python code: {e}")
    
    # Test JavaScript execution
    print("\n6. Testing JavaScript code execution...")
    try:
        result = local_sandbox.execute_code(
            sandbox_id,
            "console.log('Hello from Node.js!'); console.log(2 + 2);",
            "javascript"
        )
        if result['success']:
            print("✅ JavaScript code executed successfully")
            print(f"   Output: {result['output'].strip()}")
        else:
            print(f"❌ JavaScript execution failed: {result['output']}")
    except Exception as e:
        print(f"❌ Failed to execute JavaScript code: {e}")
    
    # Test screenshot
    print("\n7. Testing screenshot functionality...")
    try:
        result = local_sandbox.take_screenshot(sandbox_id, "https://example.com")
        if result['success']:
            print("✅ Screenshot taken successfully")
            print(f"   Format: {result['format']}")
            print(f"   Data length: {len(result['screenshot'])} characters")
        else:
            print(f"❌ Screenshot failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Failed to take screenshot: {e}")
    
    # Cleanup
    print("\n8. Cleaning up...")
    try:
        local_sandbox.delete_sandbox(sandbox_id)
        print("✅ Sandbox cleaned up successfully")
    except Exception as e:
        print(f"❌ Failed to cleanup: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Local sandbox test completed!")
    print("\nTo use local sandbox instead of Daytona:")
    print("1. Set SANDBOX_MODE=local in backend/.env")
    print("2. Or remove DAYTONA_API_KEY to auto-fallback to local")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_local_sandbox())