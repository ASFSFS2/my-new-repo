#!/usr/bin/env python3
"""
Simple HTTP proxy for Neo AI global access
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import urllib.error
import json

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def do_PUT(self):
        self.proxy_request()
    
    def do_DELETE(self):
        self.proxy_request()
    
    def proxy_request(self):
        try:
            # Health check
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {
                    "status": "ok",
                    "proxy": "running",
                    "frontend": "http://localhost:3000",
                    "backend": "http://localhost:8000"
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Determine target URL
            if self.path.startswith('/api'):
                target_url = f"http://localhost:8000{self.path}"
            else:
                target_url = f"http://localhost:3000{self.path}"
            
            print(f"Proxying {self.command} {self.path} -> {target_url}")
            
            # Prepare request
            headers = {}
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection']:
                    headers[header] = value
            
            # Get request body for POST/PUT
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Make request
            req = urllib.request.Request(target_url, data=body, headers=headers, method=self.command)
            
            with urllib.request.urlopen(req) as response:
                # Send response status
                self.send_response(response.getcode())
                
                # Send response headers
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                
                # Send response body
                self.wfile.write(response.read())
                
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Proxy Error: {e.reason}".encode())
            
        except Exception as e:
            print(f"Proxy error: {e}")
            self.send_response(502)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Proxy Error: {str(e)}".encode())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 9000), ProxyHandler)
    print("🚀 Starting Simple Neo AI Proxy on port 9000...")
    print("🌍 Global access enabled!")
    server.serve_forever()