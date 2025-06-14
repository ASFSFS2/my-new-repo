"""
Hybrid sandbox system that can use either Daytona (cloud) or Local Docker
Automatically falls back to local if Daytona is not available
"""

from utils.logger import logger
from utils.config import config
from typing import Dict, Any, Optional

# Import both sandbox implementations
try:
    from .sandbox import daytona, get_or_start_sandbox as daytona_get_sandbox
    from .sandbox import create_sandbox as daytona_create_sandbox
    from .sandbox import delete_sandbox as daytona_delete_sandbox
    DAYTONA_AVAILABLE = daytona is not None
except Exception as e:
    logger.warning(f"Daytona not available: {e}")
    DAYTONA_AVAILABLE = False

try:
    from .local_sandbox import local_sandbox
    from .local_sandbox import get_or_start_local_sandbox, create_local_sandbox, delete_local_sandbox
    LOCAL_AVAILABLE = local_sandbox.is_available()
except Exception as e:
    logger.warning(f"Local sandbox not available: {e}")
    LOCAL_AVAILABLE = False


class HybridSandboxManager:
    """Manages both Daytona and local sandbox options"""
    
    def __init__(self):
        self.preferred_mode = self._determine_preferred_mode()
        logger.info(f"Sandbox mode: {self.preferred_mode}")
    
    def _determine_preferred_mode(self) -> str:
        """Determine which sandbox mode to use"""
        # Check environment preference
        sandbox_mode = getattr(config, "SANDBOX_MODE", "auto").lower()
        
        if sandbox_mode == "local":
            if LOCAL_AVAILABLE:
                return "local"
            else:
                logger.warning("Local sandbox requested but not available, checking Daytona...")
                if DAYTONA_AVAILABLE:
                    return "daytona"
                else:
                    return "none"
        
        elif sandbox_mode == "daytona":
            if DAYTONA_AVAILABLE:
                return "daytona"
            else:
                logger.warning("Daytona requested but not available, checking local...")
                if LOCAL_AVAILABLE:
                    return "local"
                else:
                    return "none"
        
        else:  # auto mode
            if DAYTONA_AVAILABLE:
                return "daytona"
            elif LOCAL_AVAILABLE:
                return "local"
            else:
                return "none"
    
    def is_available(self) -> bool:
        """Check if any sandbox is available"""
        return self.preferred_mode != "none"
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all sandbox options"""
        return {
            "preferred_mode": self.preferred_mode,
            "daytona_available": DAYTONA_AVAILABLE,
            "local_available": LOCAL_AVAILABLE,
            "docker_available": LOCAL_AVAILABLE
        }
    
    async def get_or_start_sandbox(self, sandbox_id: str = None):
        """Get or start a sandbox using preferred mode"""
        if self.preferred_mode == "daytona":
            return await daytona_get_sandbox(sandbox_id)
        elif self.preferred_mode == "local":
            return await get_or_start_local_sandbox(sandbox_id)
        else:
            raise Exception("No sandbox provider available")
    
    def create_sandbox(self, password: str = "neopassword", project_id: str = None):
        """Create a sandbox using preferred mode"""
        if self.preferred_mode == "daytona":
            return daytona_create_sandbox(password, project_id)
        elif self.preferred_mode == "local":
            return create_local_sandbox(password, project_id)
        else:
            raise Exception("No sandbox provider available")
    
    async def delete_sandbox(self, sandbox_id: str):
        """Delete a sandbox using preferred mode"""
        if self.preferred_mode == "daytona":
            return await daytona_delete_sandbox(sandbox_id)
        elif self.preferred_mode == "local":
            return await delete_local_sandbox(sandbox_id)
        else:
            raise Exception("No sandbox provider available")
    
    def execute_code(self, sandbox_id: str, code: str, language: str = "python"):
        """Execute code in sandbox"""
        if self.preferred_mode == "local":
            return local_sandbox.execute_code(sandbox_id, code, language)
        else:
            # For Daytona, we'd need to implement code execution via their API
            raise Exception("Code execution not implemented for Daytona mode")
    
    def take_screenshot(self, sandbox_id: str, url: str = None):
        """Take screenshot in sandbox"""
        if self.preferred_mode == "local":
            return local_sandbox.take_screenshot(sandbox_id, url)
        else:
            # For Daytona, we'd need to implement screenshot via their API
            raise Exception("Screenshot not implemented for Daytona mode")


# Global hybrid manager instance
hybrid_sandbox = HybridSandboxManager()


# Wrapper functions that use the hybrid manager
async def get_or_start_sandbox(sandbox_id: str = None):
    """Get or start sandbox using hybrid manager"""
    return await hybrid_sandbox.get_or_start_sandbox(sandbox_id)


def create_sandbox(password: str = "neopassword", project_id: str = None):
    """Create sandbox using hybrid manager"""
    return hybrid_sandbox.create_sandbox(password, project_id)


async def delete_sandbox(sandbox_id: str):
    """Delete sandbox using hybrid manager"""
    return await hybrid_sandbox.delete_sandbox(sandbox_id)


def execute_code(sandbox_id: str, code: str, language: str = "python"):
    """Execute code in sandbox"""
    return hybrid_sandbox.execute_code(sandbox_id, code, language)


def take_screenshot(sandbox_id: str, url: str = None):
    """Take screenshot in sandbox"""
    return hybrid_sandbox.take_screenshot(sandbox_id, url)


def get_sandbox_status():
    """Get status of sandbox system"""
    return hybrid_sandbox.get_status()