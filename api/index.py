import sys
from pathlib import Path

# Add project root directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relix | Cybernetic Relational Query Optimizer</title>
            <meta font-family="Outfit, sans-serif">
            <style>
                body {
                    background: #030712;
                    color: #e2e8f0;
                    font-family: system-ui, -apple-system, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                }
                .card {
                    background: rgba(15, 23, 42, 0.7);
                    border: 1px solid rgba(0, 242, 254, 0.3);
                    border-radius: 20px;
                    padding: 40px;
                    max-width: 600px;
                    text-align: center;
                    box-shadow: 0 20px 50px rgba(0, 242, 254, 0.15);
                    backdrop-filter: blur(20px);
                }
                h1 {
                    font-size: 2.8rem;
                    margin-bottom: 10px;
                    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #00ff87 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                p { font-size: 1.1rem; color: #94a3b8; line-height: 1.6; }
                .btn {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 14px 28px;
                    background: linear-gradient(135deg, #00f2fe 0%, #7f00ff 100%);
                    color: white;
                    text-decoration: none;
                    font-weight: bold;
                    border-radius: 12px;
                    box-shadow: 0 10px 25px rgba(0, 242, 254, 0.4);
                }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>⚡ Relix</h1>
                <p>Cybernetic Cost- & Latency-Aware Relational LLM Query Optimizer</p>
                <p><b>MLSys 2025 Paper Grounded</b></p>
                <p>Relix repository is connected to Vercel via GitHub <b>23053408-byte/project-relix</b>.</p>
                <a href="https://github.com/23053408-byte/project-relix" class="btn" target="_blank">View GitHub Repository</a>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))
        return
