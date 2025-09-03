#!/usr/bin/env python3
"""
Local development server for score-handler Lambda
Run with: python run_local.py
"""

import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import Lambda function
from lambda_function import lambda_handler

class LocalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')
    
    def do_POST(self):
        self.handle_request('POST')
    
    def do_OPTIONS(self):
        self.handle_request('OPTIONS')
    
    def handle_request(self, method):
        try:
            # Parse URL
            parsed_url = urlparse(self.path)
            
            # Read body for POST requests
            body = None
            if method == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    body = self.rfile.read(content_length).decode('utf-8')
            
            # Create Lambda event
            event = {
                'httpMethod': method,
                'path': parsed_url.path,
                'body': body,
                'headers': dict(self.headers),
                'pathParameters': {},
                'queryStringParameters': dict(parse_qs(parsed_url.query)) if parsed_url.query else {}
            }
            
            # Extract path parameters for routes like /repayment-plan/{user_id}
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) >= 2 and path_parts[0] == 'repayment-plan':
                event['pathParameters'] = {'user_id': path_parts[1]}
            
            # Call Lambda handler
            response = lambda_handler(event, {})
            
            # Send response
            self.send_response(response['statusCode'])
            
            # Set headers
            for key, value in response.get('headers', {}).items():
                self.send_header(key, value)
            self.end_headers()
            
            # Send body
            self.wfile.write(response['body'].encode('utf-8'))
            
        except Exception as e:
            print(f"Error handling request: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({'error': str(e)})
            self.wfile.write(error_response.encode('utf-8'))

def main():
    # Set environment variables
    os.environ.setdefault('DATABASE_URL', 'postgresql://user:pass@localhost:5432/db')
    os.environ.setdefault('ENVIRONMENT', 'dev')
    
    port = 8080
    server = HTTPServer(('localhost', port), LocalHandler)
    
    print(f"🚀 Score Handler running locally at http://localhost:{port}")
    print("📋 Available endpoints:")
    print("  GET  /health")
    print("  POST /survey")
    print("  POST /repayment-plan")
    print("  GET  /repayment-plan/{user_id}")
    print("\n💡 Test with:")
    print(f"  curl http://localhost:{port}/health")
    print("\n⏹️  Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

if __name__ == '__main__':
    main()