import pytest
from src.prefix_metrics import (
    longest_common_prefix,
    compute_prefix_metrics,
    tokenize_proxy
)


def test_longest_common_prefix():
    tokens_a = ["You", "are", "a", "sentiment", "classifier.", "Product:", "P100"]
    tokens_b = ["You", "are", "a", "sentiment", "classifier.", "Product:", "P101"]
    lcp = longest_common_prefix(tokens_a, tokens_b)
    assert lcp == ["You", "are", "a", "sentiment", "classifier.", "Product:"]


def test_compute_prefix_metrics():
    prompts = [
        "You are a sentiment analyzer. Category: Phone Brand: Apple",
        "You are a sentiment analyzer. Category: Phone Brand: Apple",
        "You are a sentiment analyzer. Category: Laptop Brand: Apple",
    ]
    stats = compute_prefix_metrics(prompts)
    assert stats["total_prompts"] == 3
    assert stats["prefix_hit_count"] == 2
    assert stats["reused_prefix_tokens"] > 0
    assert stats["cache_reuse_ratio"] > 0.0
