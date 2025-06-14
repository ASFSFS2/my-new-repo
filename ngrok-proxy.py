#!/usr/bin/env python3
"""
Ngrok proxy for Neo AI on port 80
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import urllib.error
import json
import socket

class NgrokProxyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def do_PUT(self):
        self.proxy_request()
    
    def do_DELETE(self):
        self.proxy_request()
    
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def check_service(self, host, port):
        """Check if service is running"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def proxy_request(self):
        try:
            # Health check
            if self.path == '/health' or self.path == '/api/health':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                
                frontend_status = "✅ Running" if self.check_service('localhost', 3000) else "❌ Down"
                backend_status = "✅ Running" if self.check_service('localhost', 8000) else "❌ Down"
                
                response = {
                    "status": "ok",
                    "proxy": "ngrok-ready",
                    "services": {
                        "frontend": frontend_status,
                        "backend": backend_status
                    },
                    "urls": {
                        "frontend": "http://localhost:3000",
                        "backend": "http://localhost:8000",
                        "ngrok": "https://hugely-great-marmot.ngrok-free.app"
                    }
                }
                self.wfile.write(json.dumps(response, indent=2).encode())
                return
            
            # Route to backend for API calls
            if self.path.startswith('/api'):
                if not self.check_service('localhost', 8000):
                    self.send_error(503, "Backend service unavailable")
                    return
                target_url = f"http://localhost:8000{self.path}"
            else:
                # Route to frontend for everything else
                if not self.check_service('localhost', 3000):
                    self.send_error(503, "Frontend service unavailable")
                    return
                target_url = f"http://localhost:3000{self.path}"
            
            print(f"🌍 {self.command} {self.path} -> {target_url}")
            
            # Prepare headers
            headers = {}
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection', 'content-length']:
                    headers[header] = value
            
            # Get request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Make request
            req = urllib.request.Request(target_url, data=body, headers=headers, method=self.command)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                # Send response status
                self.send_response(response.getcode())
                
                # Send response headers
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                
                # Add CORS headers
                self.send_cors_headers()
                self.end_headers()
                
                # Send response body
                self.wfile.write(response.read())
                
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP Error {e.code}: {e.reason}")
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            error_response = {
                "error": f"HTTP {e.code}",
                "message": e.reason,
                "path": self.path
            }
            self.wfile.write(json.dumps(error_response).encode())
            
        except Exception as e:
            print(f"❌ Proxy error: {e}")
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            error_response = {
                "error": "Proxy Error",
                "message": str(e),
                "path": self.path
            }
            self.wfile.write(json.dumps(error_response).encode())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 80), NgrokProxyHandler)
    print("🚀 Starting Neo AI Ngrok Proxy on port 80...")
    print("🌍 Ngrok URL: https://hugely-great-marmot.ngrok-free.app")
    print("📡 Frontend: http://localhost:3000")
    print("🔧 Backend: http://localhost:8000")
    print("✅ Ready for ngrok tunnel!")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Proxy stopped")
        server.shutdown()