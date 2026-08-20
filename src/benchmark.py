import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.profiler import profile_dataset
from src.baseline import evaluate_baseline
from src.ophr import optimize_ophr_exact
from src.ggr import optimize_ggr_inspired
from src.semantic_validator import validate_semantic_correctness



def generate_synthetic_dataset(num_rows: int, seed: int = 42) -> pd.DataFrame:
    """
    Generates a scaled synthetic relational dataset with realistic value repetition.
    """
    np.random.seed(seed)
    categories = ["Phone", "Laptop", "Headphones", "Smartwatch", "Tablet"]
    brands = ["Apple", "Samsung", "Sony", "Bose", "Dell", "Garmin"]
    
    # Create product_id -> (category, brand) mapping for functional dependencies
    num_products = max(5, num_rows // 20)
    products = [f"P{100 + i}" for i in range(num_products)]
    product_meta = {}
    for p in products:
        product_meta[p] = (
            np.random.choice(categories),
            np.random.choice(brands)
        )

    reviews_pool = [
        "Excellent performance and stunning build quality.",
        "Average battery life, but beautiful display.",
        "Disappointing quality, would not recommend.",
        "Top tier product with fast shipping and great support.",
        "Unbeatable value for the price point."
    ]

    data = []
    for i in range(1, num_rows + 1):
        pid = np.random.choice(products)
        cat, brand = product_meta[pid]
        rating = int(np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.1, 0.2, 0.3, 0.3]))
        review_text = np.random.choice(reviews_pool)
        data.append({
            "review_id": i,
            "product_id": pid,
            "category": cat,
            "brand": brand,
            "rating": rating,
            "review_text": review_text
        })
    return pd.DataFrame(data)


def run_benchmark_suite(
    sample_csv_path: str = "data/sample_reviews.csv",
    results_dir: str = "experiments/results"
) -> Dict[str, Any]:
    """
    Runs the full LLM-Opt benchmark suite and exports results.
    """
    os.makedirs(results_dir, exist_ok=True)

    # 1. Load primary sample dataset
    if os.path.exists(sample_csv_path):
        sample_df = pd.read_csv(sample_csv_path)
    else:
        sample_df = generate_synthetic_dataset(50)

    # Export dataset profile
    profile = profile_dataset(sample_df)
    with open(os.path.join(results_dir, "dataset_profile.json"), "w") as f:
        json.dump(profile, f, indent=2)

    # 2. Semantic correctness evaluation
    baseline_sample = evaluate_baseline(sample_df, task_type="sentiment")
    ggr_sample = optimize_ggr_inspired(sample_df, task_type="sentiment")
    opt_df = sample_df.loc[ggr_sample["row_order"]]

    correctness_report = validate_semantic_correctness(
        sample_df, opt_df, baseline_sample["prompts"], ggr_sample["prompts"]
    )
    with open(os.path.join(results_dir, "correctness_report.json"), "w") as f:
        json.dump(correctness_report, f, indent=2)

    # 3. Comprehensive benchmark across scale sizes and workloads
    scale_sizes = [100, 1000, 10000]
    workloads = ["sentiment", "entity_extraction", "attribute_extraction"]
    
    benchmark_records: List[Dict[str, Any]] = []

    for size in scale_sizes:
        df_scaled = generate_synthetic_dataset(size)
        
        for query_type in workloads:
            # Baseline
            base_res = evaluate_baseline(df_scaled, task_type=query_type)
            b_m = base_res["metrics"]
            
            benchmark_records.append({
                "Method": "Baseline",
                "Rows": size,
                "Query": query_type,
                "Prefix Hits": b_m["prefix_hit_count"],
                "Reused Tokens": b_m["reused_prefix_tokens"],
                "Total Tokens": b_m["total_input_tokens"],
                "Reuse Ratio": b_m["cache_reuse_ratio"],
                "Estimated Latency (s)": b_m["estimated_latency_sec"],
                "Estimated Cost ($)": b_m["total_cost_usd"],
                "Speedup": 1.00,
                "Cost Reduction (%)": 0.0,
            })

            # GGR-Inspired
            ggr_res = optimize_ggr_inspired(df_scaled, task_type=query_type)
            g_m = ggr_res["metrics"]
            
            speedup = round(b_m["estimated_latency_sec"] / max(g_m["estimated_latency_sec"], 1e-6), 2)
            cost_red = round(
                ((b_m["total_cost_usd"] - g_m["total_cost_usd"]) / max(b_m["total_cost_usd"], 1e-6)) * 100,
                2
            )

            benchmark_records.append({
                "Method": "GGR-Inspired",
                "Rows": size,
                "Query": query_type,
                "Prefix Hits": g_m["prefix_hit_count"],
                "Reused Tokens": g_m["reused_prefix_tokens"],
                "Total Tokens": g_m["total_input_tokens"],
                "Reuse Ratio": g_m["cache_reuse_ratio"],
                "Estimated Latency (s)": g_m["estimated_latency_sec"],
                "Estimated Cost ($)": g_m["total_cost_usd"],
                "Speedup": speedup,
                "Cost Reduction (%)": cost_red,
            })

            # OPHR (Small Data Oracle only for tiny sizes <= 7)
            if size <= 7:
                ophr_res = optimize_ophr_exact(df_scaled, candidate_fields=list(df_scaled.columns), task_type=query_type)
                o_m = ophr_res["metrics"]
                o_speedup = round(b_m["estimated_latency_sec"] / max(o_m["estimated_latency_sec"], 1e-6), 2)
                o_cost_red = round(
                    ((b_m["total_cost_usd"] - o_m["total_cost_usd"]) / max(b_m["total_cost_usd"], 1e-6)) * 100,
                    2
                )
                benchmark_records.append({
                    "Method": "OPHR (Exact)",
                    "Rows": size,
                    "Query": query_type,
                    "Prefix Hits": o_m["prefix_hit_count"],
                    "Reused Tokens": o_m["reused_prefix_tokens"],
                    "Total Tokens": o_m["total_input_tokens"],
                    "Reuse Ratio": o_m["cache_reuse_ratio"],
                    "Estimated Latency (s)": o_m["estimated_latency_sec"],
                    "Estimated Cost ($)": o_m["total_cost_usd"],
                    "Speedup": o_speedup,
                    "Cost Reduction (%)": o_cost_red,
                })

    # Save benchmark records to CSV & JSON
    df_results = pd.DataFrame(benchmark_records)
    df_results.to_csv(os.path.join(results_dir, "results.csv"), index=False)

    with open(os.path.join(results_dir, "results.json"), "w") as f:
        json.dump(benchmark_records, f, indent=2)

    return {
        "status": "COMPLETED",
        "total_experiments": len(benchmark_records),
        "results_path": os.path.join(results_dir, "results.csv"),
    }


if __name__ == "__main__":
    run_benchmark_suite()
