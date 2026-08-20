import json
import pandas as pd
from typing import Dict, Any, List


def validate_semantic_correctness(
    original_df: pd.DataFrame,
    optimized_df: pd.DataFrame,
    baseline_prompts: List[str],
    optimized_prompts: List[str]
) -> Dict[str, Any]:
    """
    Validates that optimization preserves dataset completeness, row integrity,
    cell value immutability, and analytical task semantics.
    """
    # 1. Row count check
    same_row_count = len(original_df) == len(optimized_df)

    # 2. Row index set equality check
    orig_indices = set(original_df.index)
    opt_indices = set(optimized_df.index)
    same_row_set = orig_indices == opt_indices

    # 3. Cell value integrity check
    cell_values_intact = False
    if same_row_set:
        # Re-sort optimized dataframe by original index to compare cell by cell
        reconstructed = optimized_df.loc[list(original_df.index)]
        cell_values_intact = original_df.equals(reconstructed)

    # 4. Prompt instruction immutability check
    instruction_intact = (len(baseline_prompts) == len(optimized_prompts)) and (len(baseline_prompts) > 0)
    if instruction_intact:
        orig_header = baseline_prompts[0].split("[Record]")[0]
        opt_header = optimized_prompts[0].split("[Record]")[0]
        instruction_intact = orig_header == opt_header

    all_passed = (
        same_row_count and same_row_set and cell_values_intact and instruction_intact
    )

    report = {
        "status": "PASSED" if all_passed else "FAILED",
        "checks": {
            "row_count_preserved": same_row_count,
            "row_set_preserved": same_row_set,
            "cell_values_intact": cell_values_intact,
            "instruction_header_preserved": instruction_intact,
        },
        "original_rows": len(original_df),
        "optimized_rows": len(optimized_df),
    }

    return report
