import sys
from pathlib import Path

# Add project root directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
from src.profiler import profile_dataset
from src.baseline import evaluate_baseline
from src.ggr import optimize_ggr_inspired
from src.benchmark import generate_synthetic_dataset

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        # Run Relix sample dataset optimization for live serverless render
        df = generate_synthetic_dataset(20)
        profile = profile_dataset(df)
        base_res = evaluate_baseline(df, task_type="sentiment")
        ggr_res = optimize_ggr_inspired(df, task_type="sentiment")

        b_m = base_res["metrics"]
        g_m = ggr_res["metrics"]
        speedup = round(b_m["estimated_latency_sec"] / max(g_m["estimated_latency_sec"], 1e-6), 2)
        cost_red = round(((b_m["total_cost_usd"] - g_m["total_cost_usd"]) / max(b_m["total_cost_usd"], 1e-6)) * 100, 1)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relix | Cybernetic Relational Query Optimizer</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
            <style>
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                body {{
                    background: #030712;
                    background-image: radial-gradient(circle at 15% 15%, rgba(127, 0, 255, 0.15) 0%, transparent 40%),
                                      radial-gradient(circle at 85% 85%, rgba(0, 242, 254, 0.15) 0%, transparent 40%);
                    color: #e2e8f0;
                    font-family: 'Plus Jakarta Sans', sans-serif;
                    padding: 40px 20px;
                    min-height: 100vh;
                }}
                .container {{ max-width: 1100px; margin: 0 auto; }}
                .hero {{
                    text-align: center;
                    margin-bottom: 40px;
                }}
                h1 {{
                    font-family: 'Outfit', sans-serif;
                    font-size: 3.5rem;
                    font-weight: 800;
                    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #00ff87 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 10px;
                }}
                .subtitle {{ font-size: 1.2rem; color: #94a3b8; margin-bottom: 20px; }}
                .badge {{
                    display: inline-block;
                    padding: 6px 16px;
                    background: rgba(0, 242, 254, 0.1);
                    border: 1px solid rgba(0, 242, 254, 0.3);
                    border-radius: 50px;
                    color: #38bdf8;
                    font-size: 0.85rem;
                    font-weight: 600;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
                    gap: 16px;
                    margin-bottom: 30px;
                }}
                .card {{
                    background: rgba(15, 23, 42, 0.65);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 18px;
                    padding: 20px;
                    backdrop-filter: blur(20px);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                }}
                .card-label {{ font-family: 'Outfit', sans-serif; font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px; }}
                .card-val {{ font-family: 'Outfit', sans-serif; font-size: 2rem; font-weight: 800; color: #00f2fe; }}
                .card-delta {{ font-size: 0.85rem; color: #34d399; margin-top: 4px; }}
                .section-title {{ font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 700; color: #f8fafc; margin-bottom: 16px; margin-top: 30px; }}
                pre {{
                    background: rgba(15, 23, 42, 0.8);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 16px;
                    overflow-x: auto;
                    font-size: 0.9rem;
                    color: #38bdf8;
                }}
                .btn {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 14px 28px;
                    background: linear-gradient(135deg, #00f2fe 0%, #7f00ff 100%);
                    color: white;
                    text-decoration: none;
                    font-weight: bold;
                    border-radius: 12px;
                    box-shadow: 0 10px 25px rgba(0, 242, 254, 0.4);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="hero">
                    <h1>⚡ Relix</h1>
                    <div class="subtitle">Cybernetic Cost- & Latency-Aware Relational LLM Query Optimizer</div>
                    <span class="badge">✨ MLSys 2025 Paper Grounded Live Vercel Deployment</span>
                </div>

                <div class="section-title">💎 Live Measured Relix Optimization Gains</div>
                <div class="grid">
                    <div class="card">
                        <div class="card-label">Prefix Hits</div>
                        <div class="card-val">{g_m['prefix_hit_count']}</div>
                        <div class="card-delta">+{g_m['prefix_hit_count'] - b_m['prefix_hit_count']} over baseline</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Cache Reuse</div>
                        <div class="card-val">{g_m['cache_reuse_ratio']*100:.1f}%</div>
                        <div class="card-delta">+{(g_m['cache_reuse_ratio'] - b_m['cache_reuse_ratio'])*100:.1f}% ratio</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Reused Tokens</div>
                        <div class="card-val">{g_m['reused_prefix_tokens']:,}</div>
                        <div class="card-delta">Tokens saved</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Est. Latency</div>
                        <div class="card-val">{g_m['estimated_latency_sec']:.2f}s</div>
                        <div class="card-delta">Reduced prefill time</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Est. Cost</div>
                        <div class="card-val">${g_m['total_cost_usd']:.4f}</div>
                        <div class="card-delta">-{cost_red}% API cost</div>
                    </div>
                    <div class="card">
                        <div class="card-label">Speedup Factor</div>
                        <div class="card-val">{speedup}×</div>
                        <div class="card-delta">Inference Acceleration</div>
                    </div>
                </div>

                <div class="section-title">📝 Field Structure & Generated Prompt Optimization</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div class="card">
                        <div class="card-label">Baseline Field Order</div>
                        <pre>{", ".join(base_res["field_order"])}</pre>
                    </div>
                    <div class="card">
                        <div class="card-label">Relix Optimized Field Order</div>
                        <pre>{", ".join(ggr_res["field_order"])}</pre>
                    </div>
                </div>

                <div style="text-align: center; margin-top: 40px;">
                    <a href="https://github.com/23053408-byte/project-relix" class="btn" target="_blank">View GitHub Repository (23053408-byte/project-relix)</a>
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))
        return
