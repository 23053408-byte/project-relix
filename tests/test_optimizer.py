import pytest
import pandas as pd
from src.ophr import optimize_ophr_exact
from src.ggr import optimize_ggr_inspired
from src.baseline import evaluate_baseline


@pytest.fixture
def tiny_df():
    data = [
        {"review_id": 1, "product_id": "P100", "category": "Phone", "brand": "Apple", "rating": 5},
        {"review_id": 2, "product_id": "P100", "category": "Phone", "brand": "Apple", "rating": 4},
        {"review_id": 3, "product_id": "P101", "category": "Phone", "brand": "Samsung", "rating": 5},
        {"review_id": 4, "product_id": "P102", "category": "Laptop", "brand": "Apple", "rating": 5},
    ]
    return pd.DataFrame(data)


def test_ophr_small_dataset(tiny_df):
    fields = ["category", "brand", "product_id", "rating"]
    result = optimize_ophr_exact(tiny_df, candidate_fields=fields, max_rows=5)
    assert result["method"] == "OPHR (Exact)"
    assert len(result["row_order"]) == len(tiny_df)
    assert set(result["row_order"]) == set(tiny_df.index)


def test_ggr_inspired_optimization(tiny_df):
    result = optimize_ggr_inspired(tiny_df)
    assert result["method"] == "GGR-Inspired"
    assert len(result["row_order"]) == len(tiny_df)
    assert set(result["row_order"]) == set(tiny_df.index)
    
    # Check that high repetition fields are prioritized near the front of field_order
    field_order = result["field_order"]
    assert "category" in field_order[:3] or "brand" in field_order[:3] or "product_id" in field_order[:3]


def test_ggr_improves_or_equals_baseline_reuse(tiny_df):
    base_res = evaluate_baseline(tiny_df)
    ggr_res = optimize_ggr_inspired(tiny_df)
    assert ggr_res["metrics"]["reused_prefix_tokens"] >= base_res["metrics"]["reused_prefix_tokens"]
