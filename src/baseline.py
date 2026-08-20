import pandas as pd
from typing import Dict, Any, List, Optional
from src.prompt_generator import generate_prompts
from src.prefix_metrics import compute_prefix_metrics
from src.cost_model import calculate_cost_and_latency


def evaluate_baseline(
    df: pd.DataFrame,
    field_order: Optional[List[str]] = None,
    task_type: str = "sentiment",
    est_output_tokens_per_prompt: int = 15
) -> Dict[str, Any]:
    """
    Evaluates baseline performance: original row ordering with default field order.
    """
    if field_order is None:
        field_order = list(df.columns)

    prompts = generate_prompts(df, field_order=field_order, task_type=task_type)
    prefix_stats = compute_prefix_metrics(prompts)
    
    total_output_tokens = len(df) * est_output_tokens_per_prompt

    cost_latency = calculate_cost_and_latency(
        total_input_tokens=prefix_stats["total_input_tokens"],
        reused_input_tokens=prefix_stats["reused_prefix_tokens"],
        total_output_tokens=total_output_tokens,
        num_prompts=len(prompts)
    )

    result = {
        "method": "Baseline",
        "row_order": list(df.index),
        "field_order": field_order,
        "prompts": prompts,
        "metrics": {**prefix_stats, **cost_latency}
    }
    return result
