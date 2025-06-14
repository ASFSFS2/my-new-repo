"""
Local Docker-based sandbox as an alternative to Daytona
Provides code execution, browser automation, and file operations
"""

import docker
import asyncio
import json
import time
import uuid
from typing import Dict, Any, Optional
from utils.logger import logger
from utils.config import config

class LocalSandbox:
    """Local Docker-based sandbox for code execution and browser automation"""
    
    def __init__(self):
        self.client = None
        self.containers: Dict[str, Any] = {}
        self.image_name = "neo-sandbox:latest"
        self._initialize_docker()
    
    def _initialize_docker(self):
        """Initialize Docker client"""
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if local sandbox is available"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def build_sandbox_image(self) -> bool:
        """Build the sandbox Docker image"""
        if not self.client:
            logger.error("Docker client not available")
            return False
        
        try:
            logger.info("Building local sandbox image...")
            dockerfile_path = "/workspace/neo/backend/sandbox/docker"
            
            # Build the image
            image, logs = self.client.images.build(
                path=dockerfile_path,
                tag=self.image_name,
                rm=True,
                forcerm=True
            )
            
            logger.info(f"Successfully built sandbox image: {self.image_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build sandbox image: {e}")
            return False
    
    def create_sandbox(self, sandbox_id: Optional[str] = None) -> str:
        """Create a new sandbox container"""
        if not self.client:
            raise Exception("Docker client not available")
        
        if not sandbox_id:
            sandbox_id = f"neo-sandbox-{uuid.uuid4().hex[:8]}"
        
        try:
            # Check if image exists, build if not
            try:
                self.client.images.get(self.image_name)
            except docker.errors.ImageNotFound:
                logger.info("Sandbox image not found, building...")
                if not self.build_sandbox_image():
                    raise Exception("Failed to build sandbox image")
            
            # Create container
            container = self.client.containers.run(
                self.image_name,
                name=sandbox_id,
                detach=True,
                ports={
                    '6080/tcp': None,  # noVNC
                    '5901/tcp': None,  # VNC
                    '9222/tcp': None,  # Chrome debugging
                    '8003/tcp': None,  # API server
                    '8080/tcp': None   # HTTP server
                },
                environment={
                    'ANONYMIZED_TELEMETRY': 'false',
                    'CHROME_PERSISTENT_SESSION': 'true',
                    'RESOLUTION': '1024x768x24',
                    'VNC_PASSWORD': 'neopassword',
                    'DISPLAY': ':99'
                },
                volumes={
                    '/tmp/.X11-unix': {'bind': '/tmp/.X11-unix', 'mode': 'rw'}
                },
                shm_size='2g',
                cap_add=['SYS_ADMIN'],
                security_opt=['seccomp=unconfined'],
                tmpfs={'/tmp': ''},
                remove=False
            )
            
            self.containers[sandbox_id] = container
            
            # Wait for container to be ready
            self._wait_for_container_ready(container)
            
            logger.info(f"Created local sandbox: {sandbox_id}")
            return sandbox_id
            
        except Exception as e:
            logger.error(f"Failed to create sandbox: {e}")
            raise
    
    def _wait_for_container_ready(self, container, timeout: int = 60):
        """Wait for container to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                container.reload()
                if container.status == 'running':
                    # Check if services are ready
                    result = container.exec_run("nc -z localhost 5901")
                    if result.exit_code == 0:
                        logger.info("Container is ready")
                        return
            except:
                pass
            time.sleep(2)
        
        raise Exception("Container failed to become ready within timeout")
    
    def execute_code(self, sandbox_id: str, code: str, language: str = "python") -> Dict[str, Any]:
        """Execute code in the sandbox"""
        if sandbox_id not in self.containers:
            raise Exception(f"Sandbox {sandbox_id} not found")
        
        container = self.containers[sandbox_id]
        
        try:
            if language.lower() == "python":
                # Create a temporary Python file
                file_content = f"""
import sys
import traceback
import json

try:
{chr(10).join('    ' + line for line in code.split(chr(10)))}
except Exception as e:
    print(f"Error: {{e}}")
    traceback.print_exc()
"""
                
                # Write code to file
                container.exec_run(f"echo '{file_content}' > /tmp/code.py")
                
                # Execute the code
                result = container.exec_run("python /tmp/code.py", workdir="/tmp")
                
            elif language.lower() in ["javascript", "js", "node"]:
                # Execute JavaScript with Node.js
                container.exec_run(f"echo '{code}' > /tmp/code.js")
                result = container.exec_run("node /tmp/code.js", workdir="/tmp")
                
            elif language.lower() == "bash":
                # Execute bash commands
                result = container.exec_run(f"bash -c '{code}'", workdir="/tmp")
                
            else:
                raise Exception(f"Unsupported language: {language}")
            
            return {
                "success": result.exit_code == 0,
                "output": result.output.decode('utf-8'),
                "exit_code": result.exit_code
            }
            
        except Exception as e:
            logger.error(f"Failed to execute code: {e}")
            return {
                "success": False,
                "output": f"Execution error: {e}",
                "exit_code": -1
            }
    
    def take_screenshot(self, sandbox_id: str, url: Optional[str] = None) -> Dict[str, Any]:
        """Take a screenshot using the browser in sandbox"""
        if sandbox_id not in self.containers:
            raise Exception(f"Sandbox {sandbox_id} not found")
        
        container = self.containers[sandbox_id]
        
        try:
            # Python script for taking screenshot
            screenshot_code = f"""
from playwright.sync_api import sync_playwright
import base64

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    {"page.goto('" + url + "')" if url else "page.goto('about:blank')"}
    
    screenshot = page.screenshot()
    browser.close()
    
    # Encode to base64
    import base64
    screenshot_b64 = base64.b64encode(screenshot).decode()
    print(f"SCREENSHOT_DATA:{{screenshot_b64}}")
"""
            
            # Execute screenshot code
            container.exec_run(f"echo '{screenshot_code}' > /tmp/screenshot.py")
            result = container.exec_run("python /tmp/screenshot.py", workdir="/tmp")
            
            if result.exit_code == 0:
                output = result.output.decode('utf-8')
                if "SCREENSHOT_DATA:" in output:
                    screenshot_data = output.split("SCREENSHOT_DATA:")[1].strip()
                    return {
                        "success": True,
                        "screenshot": screenshot_data,
                        "format": "base64_png"
                    }
            
            return {
                "success": False,
                "error": result.output.decode('utf-8')
            }
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_container_info(self, sandbox_id: str) -> Dict[str, Any]:
        """Get information about the sandbox container"""
        if sandbox_id not in self.containers:
            raise Exception(f"Sandbox {sandbox_id} not found")
        
        container = self.containers[sandbox_id]
        container.reload()
        
        # Get port mappings
        ports = {}
        if container.ports:
            for container_port, host_bindings in container.ports.items():
                if host_bindings:
                    ports[container_port] = host_bindings[0]['HostPort']
        
        return {
            "id": sandbox_id,
            "status": container.status,
            "ports": ports,
            "novnc_url": f"http://localhost:{ports.get('6080/tcp', 'N/A')}",
            "vnc_port": ports.get('5901/tcp', 'N/A'),
            "api_port": ports.get('8003/tcp', 'N/A')
        }
    
    def delete_sandbox(self, sandbox_id: str) -> bool:
        """Delete a sandbox container"""
        if sandbox_id not in self.containers:
            logger.warning(f"Sandbox {sandbox_id} not found")
            return False
        
        try:
            container = self.containers[sandbox_id]
            container.stop()
            container.remove()
            del self.containers[sandbox_id]
            
            logger.info(f"Deleted sandbox: {sandbox_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete sandbox {sandbox_id}: {e}")
            return False
    
    def list_sandboxes(self) -> Dict[str, Dict[str, Any]]:
        """List all active sandboxes"""
        result = {}
        for sandbox_id, container in self.containers.items():
            try:
                result[sandbox_id] = self.get_container_info(sandbox_id)
            except:
                pass
        return result
    
    def cleanup_all(self):
        """Clean up all sandbox containers"""
        for sandbox_id in list(self.containers.keys()):
            self.delete_sandbox(sandbox_id)


# Global instance
local_sandbox = LocalSandbox()


# Async wrapper functions to match Daytona interface
async def get_or_start_local_sandbox(sandbox_id: str = None):
    """Get or create a local sandbox"""
    if not local_sandbox.is_available():
        raise Exception("Docker is not available for local sandbox")
    
    if not sandbox_id:
        sandbox_id = local_sandbox.create_sandbox()
    elif sandbox_id not in local_sandbox.containers:
        sandbox_id = local_sandbox.create_sandbox(sandbox_id)
    
    return {
        "id": sandbox_id,
        "info": local_sandbox.get_container_info(sandbox_id)
    }


def create_local_sandbox(password: str = "neopassword", project_id: str = None):
    """Create a new local sandbox"""
    if not local_sandbox.is_available():
        raise Exception("Docker is not available for local sandbox")
    
    sandbox_id = project_id or f"neo-{uuid.uuid4().hex[:8]}"
    sandbox_id = local_sandbox.create_sandbox(sandbox_id)
    
    return {
        "id": sandbox_id,
        "info": local_sandbox.get_container_info(sandbox_id)
    }


async def delete_local_sandbox(sandbox_id: str):
    """Delete a local sandbox"""
    return local_sandbox.delete_sandbox(sandbox_id)