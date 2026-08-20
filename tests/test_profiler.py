import pytest
import pandas as pd
from src.profiler import profile_dataset


def test_profile_dataset():
    df = pd.DataFrame({
        "product_id": ["P1", "P1", "P2", "P2"],
        "brand": ["Apple", "Apple", "Samsung", "Samsung"],
        "review_text": ["Good", "Great", "Nice", "Awesome"]
    })
    
    profile = profile_dataset(df)
    assert profile["rows"] == 4
    assert profile["columns"] == 3
    assert profile["unique_counts"]["brand"] == 2
    assert profile["cardinality_ratio"]["brand"] == 0.5
    assert "product_id -> brand" in profile["candidate_dependencies"]
