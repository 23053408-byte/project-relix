import itertools
import pandas as pd
from typing import Dict, Any, List, Tuple
from src.prompt_generator import generate_prompts
from src.prefix_metrics import compute_prefix_metrics
from src.cost_model import calculate_cost_and_latency


def optimize_ophr_exact(
    df: pd.DataFrame,
    candidate_fields: List[str],
    task_type: str = "sentiment",
    max_rows: int = 7,
    max_fields: int = 4
) -> Dict[str, Any]:
    """
    OPHR — Optimal Prefix Hit Recursion (Exact Brute-Force Oracle).
    Solves the exact row and field ordering problem for small datasets.
    """
    num_rows = len(df)
    fields = candidate_fields[:max_fields]

    if num_rows > max_rows:
        raise ValueError(
            f"OPHR brute-force exact search is restricted to max_rows={max_rows} "
            f"(received dataset with {num_rows} rows). Search space n! * m! is non-scalable."
        )

    best_reused_tokens = -1
    best_row_order: List[int] = list(df.index)
    best_field_order: List[str] = fields
    best_prompts: List[str] = []
    best_metrics: Dict[str, Any] = {}

    row_indices = list(df.index)
    row_permutations = list(itertools.permutations(row_indices))
    field_permutations = list(itertools.permutations(fields))

    for r_perm in row_permutations:
        sub_df = df.loc[list(r_perm)]
        for f_perm in field_permutations:
            f_list = list(f_perm)
            prompts = generate_prompts(sub_df, field_order=f_list, task_type=task_type)
            stats = compute_prefix_metrics(prompts)
            reused = stats["reused_prefix_tokens"]

            if reused > best_reused_tokens:
                best_reused_tokens = reused
                best_row_order = list(r_perm)
                best_field_order = f_list
                best_prompts = prompts
                best_metrics = stats

    total_output_tokens = len(df) * 15
    cost_latency = calculate_cost_and_latency(
        total_input_tokens=best_metrics["total_input_tokens"],
        reused_input_tokens=best_metrics["reused_prefix_tokens"],
        total_output_tokens=total_output_tokens,
        num_prompts=len(best_prompts)
    )

    return {
        "method": "OPHR (Exact)",
        "row_order": best_row_order,
        "field_order": best_field_order,
        "prompts": best_prompts,
        "metrics": {**best_metrics, **cost_latency}
    }
