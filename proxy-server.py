#!/usr/bin/env python3
"""
Simple reverse proxy server for Neo AI global access
"""

import asyncio
import aiohttp
from aiohttp import web, ClientSession
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Target servers
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

async def proxy_handler(request):
    """Handle proxy requests"""
    path = request.path_qs
    method = request.method
    headers = dict(request.headers)
    
    # Remove hop-by-hop headers
    hop_by_hop = ['connection', 'keep-alive', 'proxy-authenticate', 
                  'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade']
    for header in hop_by_hop:
        headers.pop(header, None)
    
    # Determine target URL
    if path.startswith('/api'):
        target_url = BACKEND_URL + path
        headers['Host'] = 'localhost:8000'
    else:
        target_url = FRONTEND_URL + path
        headers['Host'] = 'localhost:3000'
    
    try:
        async with ClientSession() as session:
            # Get request body if present
            data = None
            if method in ['POST', 'PUT', 'PATCH']:
                data = await request.read()
            
            # Make request to target server
            async with session.request(
                method=method,
                url=target_url,
                headers=headers,
                data=data,
                allow_redirects=False
            ) as resp:
                # Copy response headers
                response_headers = {}
                for key, value in resp.headers.items():
                    if key.lower() not in hop_by_hop:
                        response_headers[key] = value
                
                # Handle redirects
                if resp.status in [301, 302, 303, 307, 308]:
                    location = resp.headers.get('Location', '')
                    if location.startswith('http://localhost:3000'):
                        location = location.replace('http://localhost:3000', '')
                    elif location.startswith('http://localhost:8000'):
                        location = location.replace('http://localhost:8000', '/api')
                    response_headers['Location'] = location
                
                # Create response
                response = web.Response(
                    status=resp.status,
                    headers=response_headers
                )
                
                # Stream response body
                async for chunk in resp.content.iter_chunked(8192):
                    await response.write(chunk)
                
                return response
                
    except Exception as e:
        logger.error(f"Proxy error for {path}: {e}")
        return web.Response(
            status=502,
            text=f"Proxy Error: {str(e)}",
            content_type='text/plain'
        )

async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "ok",
        "proxy": "running",
        "frontend": FRONTEND_URL,
        "backend": BACKEND_URL
    })

def create_app():
    """Create the proxy application"""
    app = web.Application()
    
    # Add routes
    app.router.add_route('GET', '/health', health_check)
    app.router.add_route('*', '/{path:.*}', proxy_handler)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    print("🚀 Starting Neo AI Proxy Server...")
    print(f"📡 Frontend proxy: {FRONTEND_URL}")
    print(f"🔧 Backend proxy: {BACKEND_URL}")
    print("🌍 Global access enabled!")
    
    web.run_app(app, host='0.0.0.0', port=9000)