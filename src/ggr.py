import pandas as pd
from typing import Dict, Any, List, Optional
from src.profiler import profile_dataset
from src.prompt_generator import generate_prompts
from src.prefix_metrics import compute_prefix_metrics
from src.cost_model import calculate_cost_and_latency


def optimize_ggr_inspired(
    df: pd.DataFrame,
    candidate_fields: Optional[List[str]] = None,
    task_type: str = "sentiment",
    est_output_tokens_per_prompt: int = 15
) -> Dict[str, Any]:
    """
    GGR-Inspired — Practical Greedy Group Recursion Optimizer.
    Reorders rows and fields based on statistical profiling, value repetition,
    and candidate functional dependencies to maximize shared prompt prefixes.
    """
    if df.empty:
        return {
            "method": "GGR-Inspired",
            "row_order": [],
            "field_order": candidate_fields or [],
            "prompts": [],
            "metrics": {}
        }

    profile = profile_dataset(df)
    unique_counts = profile["unique_counts"]
    cardinality_ratio = profile["cardinality_ratio"]
    fds = profile["candidate_dependencies"]

    fields = candidate_fields or list(df.columns)

    # 1. Score and order fields by prefix utility
    def field_utility_score(f: str) -> float:
        # Exclude ID and text fields from top prefix positions
        if "text" in f.lower() or "id" in f.lower() and cardinality_ratio.get(f, 1.0) > 0.9:
            return 999.0
        # Lower cardinality ratio = higher repetition = higher priority (lower score)
        return cardinality_ratio.get(f, 1.0)

    sorted_fields = sorted(fields, key=field_utility_score)

    # Adjust field order using functional dependencies (determinants precede dependents)
    for fd in fds:
        det, dep = fd.split(" -> ")
        if det in sorted_fields and dep in sorted_fields:
            idx_det = sorted_fields.index(det)
            idx_dep = sorted_fields.index(dep)
            if idx_det > idx_dep:
                sorted_fields.remove(dep)
                sorted_fields.insert(idx_det + 1, dep)

    # 2. Reorder rows by grouping along top high-repetition fields
    grouping_cols = [
        f for f in sorted_fields
        if cardinality_ratio.get(f, 1.0) < 0.8 and f in df.columns
    ]

    if grouping_cols:
        # Group by high-repetition fields, sorted by group size (descending)
        sorted_df = df.sort_values(by=grouping_cols, ascending=True)
    else:
        sorted_df = df.copy()

    best_row_order = list(sorted_df.index)
    best_field_order = sorted_fields

    prompts = generate_prompts(
        sorted_df, field_order=best_field_order, task_type=task_type
    )
    prefix_stats = compute_prefix_metrics(prompts)
    total_output_tokens = len(df) * est_output_tokens_per_prompt

    cost_latency = calculate_cost_and_latency(
        total_input_tokens=prefix_stats["total_input_tokens"],
        reused_input_tokens=prefix_stats["reused_prefix_tokens"],
        total_output_tokens=total_output_tokens,
        num_prompts=len(prompts)
    )

    return {
        "method": "GGR-Inspired",
        "row_order": best_row_order,
        "field_order": best_field_order,
        "prompts": prompts,
        "metrics": {**prefix_stats, **cost_latency}
    }
