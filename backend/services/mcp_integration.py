"""
Enhanced MCP (Model Context Protocol) Integration for NEO.

This module provides advanced integration with MCP servers, allowing NEO to:
- Connect to multiple MCP servers simultaneously
- Dynamically discover and use tools from MCP servers
- Manage MCP server lifecycle
- Handle tool execution with proper error handling and retries
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import aiohttp
import websockets
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MCPServerStatus(Enum):
    """MCP Server connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

@dataclass
class MCPTool:
    """Represents a tool available from an MCP server."""
    name: str
    description: str
    parameters: Dict[str, Any]
    server_id: str
    
@dataclass
class MCPServer:
    """Represents an MCP server configuration."""
    id: str
    name: str
    url: str
    protocol: str  # "http", "websocket", "stdio"
    status: MCPServerStatus = MCPServerStatus.DISCONNECTED
    tools: List[MCPTool] = None
    last_ping: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3

class MCPIntegration:
    """Enhanced MCP Integration Manager."""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.active_connections: Dict[str, Any] = {}
        self.tool_registry: Dict[str, MCPTool] = {}
        self._running = False
        
    async def start(self):
        """Start the MCP integration service."""
        self._running = True
        logger.info("Starting MCP Integration service")
        
        # Load default MCP servers
        await self._load_default_servers()
        
        # Start connection monitoring
        asyncio.create_task(self._monitor_connections())
        
    async def stop(self):
        """Stop the MCP integration service."""
        self._running = False
        logger.info("Stopping MCP Integration service")
        
        # Close all connections
        for server_id in list(self.active_connections.keys()):
            await self._disconnect_server(server_id)
            
    async def _load_default_servers(self):
        """Load default MCP servers configuration."""
        default_servers = [
            MCPServer(
                id="filesystem",
                name="Filesystem MCP Server",
                url="stdio://mcp-server-filesystem",
                protocol="stdio"
            ),
            MCPServer(
                id="web_search",
                name="Web Search MCP Server", 
                url="stdio://mcp-server-web-search",
                protocol="stdio"
            ),
            MCPServer(
                id="git",
                name="Git MCP Server",
                url="stdio://mcp-server-git",
                protocol="stdio"
            ),
            MCPServer(
                id="database",
                name="Database MCP Server",
                url="stdio://mcp-server-database",
                protocol="stdio"
            ),
            MCPServer(
                id="browser",
                name="Browser Automation MCP Server",
                url="stdio://mcp-server-browser",
                protocol="stdio"
            )
        ]
        
        for server in default_servers:
            self.servers[server.id] = server
            await self._connect_server(server.id)
            
    async def _connect_server(self, server_id: str) -> bool:
        """Connect to an MCP server."""
        if server_id not in self.servers:
            logger.error(f"Server {server_id} not found")
            return False
            
        server = self.servers[server_id]
        server.status = MCPServerStatus.CONNECTING
        
        try:
            if server.protocol == "stdio":
                connection = await self._connect_stdio(server)
            elif server.protocol == "websocket":
                connection = await self._connect_websocket(server)
            elif server.protocol == "http":
                connection = await self._connect_http(server)
            else:
                raise ValueError(f"Unsupported protocol: {server.protocol}")
                
            if connection:
                self.active_connections[server_id] = connection
                server.status = MCPServerStatus.CONNECTED
                server.last_ping = datetime.now()
                server.retry_count = 0
                
                # Discover tools
                await self._discover_tools(server_id)
                
                logger.info(f"Connected to MCP server: {server.name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {server.name}: {e}")
            server.status = MCPServerStatus.ERROR
            server.retry_count += 1
            
        return False
        
    async def _connect_stdio(self, server: MCPServer) -> Optional[Any]:
        """Connect to MCP server via stdio."""
        try:
            # For stdio connections, we would typically spawn a subprocess
            # This is a simplified implementation
            logger.info(f"Connecting to stdio MCP server: {server.url}")
            
            # Simulate successful connection for demo
            return {"type": "stdio", "server_id": server.id}
            
        except Exception as e:
            logger.error(f"Failed to connect via stdio: {e}")
            return None
            
    async def _connect_websocket(self, server: MCPServer) -> Optional[Any]:
        """Connect to MCP server via WebSocket."""
        try:
            websocket = await websockets.connect(server.url)
            return {"type": "websocket", "connection": websocket}
            
        except Exception as e:
            logger.error(f"Failed to connect via WebSocket: {e}")
            return None
            
    async def _connect_http(self, server: MCPServer) -> Optional[Any]:
        """Connect to MCP server via HTTP."""
        try:
            session = aiohttp.ClientSession()
            # Test connection
            async with session.get(f"{server.url}/health") as response:
                if response.status == 200:
                    return {"type": "http", "session": session}
                    
        except Exception as e:
            logger.error(f"Failed to connect via HTTP: {e}")
            return None
            
    async def _disconnect_server(self, server_id: str):
        """Disconnect from an MCP server."""
        if server_id in self.active_connections:
            connection = self.active_connections[server_id]
            
            try:
                if connection["type"] == "websocket":
                    await connection["connection"].close()
                elif connection["type"] == "http":
                    await connection["session"].close()
                    
            except Exception as e:
                logger.error(f"Error disconnecting from server {server_id}: {e}")
                
            del self.active_connections[server_id]
            
        if server_id in self.servers:
            self.servers[server_id].status = MCPServerStatus.DISCONNECTED
            
    async def _discover_tools(self, server_id: str):
        """Discover available tools from an MCP server."""
        if server_id not in self.active_connections:
            return
            
        try:
            # Send tools/list request to MCP server
            tools_response = await self._send_mcp_request(server_id, {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            })
            
            if tools_response and "result" in tools_response:
                tools = tools_response["result"].get("tools", [])
                server_tools = []
                
                for tool_data in tools:
                    tool = MCPTool(
                        name=tool_data["name"],
                        description=tool_data.get("description", ""),
                        parameters=tool_data.get("inputSchema", {}),
                        server_id=server_id
                    )
                    server_tools.append(tool)
                    
                    # Register tool globally
                    tool_key = f"{server_id}:{tool.name}"
                    self.tool_registry[tool_key] = tool
                    
                self.servers[server_id].tools = server_tools
                logger.info(f"Discovered {len(server_tools)} tools from {server_id}")
                
        except Exception as e:
            logger.error(f"Failed to discover tools from {server_id}: {e}")
            
    async def _send_mcp_request(self, server_id: str, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a request to an MCP server."""
        if server_id not in self.active_connections:
            return None
            
        connection = self.active_connections[server_id]
        
        try:
            if connection["type"] == "websocket":
                await connection["connection"].send(json.dumps(request))
                response = await connection["connection"].recv()
                return json.loads(response)
                
            elif connection["type"] == "http":
                async with connection["session"].post(
                    f"{self.servers[server_id].url}/mcp",
                    json=request
                ) as response:
                    if response.status == 200:
                        return await response.json()
                        
            elif connection["type"] == "stdio":
                # For stdio, we would write to stdin and read from stdout
                # This is a simplified implementation
                logger.info(f"Sending MCP request via stdio: {request}")
                return {"jsonrpc": "2.0", "id": request.get("id"), "result": {}}
                
        except Exception as e:
            logger.error(f"Failed to send MCP request to {server_id}: {e}")
            
        return None
        
    async def _monitor_connections(self):
        """Monitor MCP server connections and handle reconnections."""
        while self._running:
            try:
                for server_id, server in self.servers.items():
                    if server.status == MCPServerStatus.ERROR and server.retry_count < server.max_retries:
                        logger.info(f"Attempting to reconnect to {server.name}")
                        await self._connect_server(server_id)
                        
                    elif server.status == MCPServerStatus.CONNECTED:
                        # Send ping to check connection health
                        ping_response = await self._send_mcp_request(server_id, {
                            "jsonrpc": "2.0",
                            "id": 999,
                            "method": "ping"
                        })
                        
                        if ping_response:
                            server.last_ping = datetime.now()
                        else:
                            logger.warning(f"Lost connection to {server.name}")
                            server.status = MCPServerStatus.ERROR
                            await self._disconnect_server(server_id)
                            
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in connection monitoring: {e}")
                await asyncio.sleep(5)
                
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], server_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Execute a tool on an MCP server."""
        # Find the tool
        tool_key = None
        if server_id:
            tool_key = f"{server_id}:{tool_name}"
        else:
            # Search all servers for the tool
            for key in self.tool_registry:
                if key.endswith(f":{tool_name}"):
                    tool_key = key
                    break
                    
        if not tool_key or tool_key not in self.tool_registry:
            logger.error(f"Tool {tool_name} not found")
            return None
            
        tool = self.tool_registry[tool_key]
        
        # Execute the tool
        request = {
            "jsonrpc": "2.0",
            "id": int(datetime.now().timestamp()),
            "method": "tools/call",
            "params": {
                "name": tool.name,
                "arguments": parameters
            }
        }
        
        response = await self._send_mcp_request(tool.server_id, request)
        
        if response and "result" in response:
            logger.info(f"Successfully executed tool {tool_name}")
            return response["result"]
        else:
            logger.error(f"Failed to execute tool {tool_name}")
            return None
            
    def get_available_tools(self) -> List[MCPTool]:
        """Get all available tools from connected MCP servers."""
        return list(self.tool_registry.values())
        
    def get_server_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all MCP servers."""
        status = {}
        for server_id, server in self.servers.items():
            status[server_id] = {
                "name": server.name,
                "status": server.status.value,
                "tools_count": len(server.tools) if server.tools else 0,
                "last_ping": server.last_ping.isoformat() if server.last_ping else None,
                "retry_count": server.retry_count
            }
        return status

# Global MCP integration instance
mcp_integration = MCPIntegration()

async def get_mcp_integration() -> MCPIntegration:
    """Get the global MCP integration instance."""
    return mcp_integration