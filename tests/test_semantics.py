import pytest
import pandas as pd
from src.semantic_validator import validate_semantic_correctness
from src.baseline import evaluate_baseline
from src.ggr import optimize_ggr_inspired


def test_semantic_validation_passes():
    df = pd.DataFrame({
        "product_id": ["P100", "P100", "P101", "P101"],
        "category": ["Phone", "Phone", "Phone", "Phone"],
        "brand": ["Apple", "Apple", "Samsung", "Samsung"],
        "rating": [5, 4, 5, 3],
        "review_text": ["Good", "Better", "Great", "Okay"]
    })

    base_res = evaluate_baseline(df)
    ggr_res = optimize_ggr_inspired(df)
    opt_df = df.loc[ggr_res["row_order"]]

    report = validate_semantic_correctness(
        df, opt_df, base_res["prompts"], ggr_res["prompts"]
    )
    assert report["status"] == "PASSED"
    assert report["checks"]["row_count_preserved"] is True
    assert report["checks"]["row_set_preserved"] is True
    assert report["checks"]["cell_values_intact"] is True
    assert report["checks"]["instruction_header_preserved"] is True
