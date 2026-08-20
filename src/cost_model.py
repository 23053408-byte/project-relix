from typing import Dict, Any


def calculate_cost_and_latency(
    total_input_tokens: int,
    reused_input_tokens: int,
    total_output_tokens: int,
    num_prompts: int,
    input_price_per_million: float = 2.50,
    cached_input_discount: float = 0.50,  # 50% cost discount on cached input tokens
    output_price_per_million: float = 10.00,
    prefill_throughput_tps: float = 2500.0,  # uncached tokens processed per second
    decode_throughput_tps: float = 120.0,   # output tokens generated per second
    fixed_overhead_per_request: float = 0.02 # fixed network/scheduling overhead per request (sec)
) -> Dict[str, Any]:
    """
    Computes estimated LLM API inference cost and simulated latency,
    accounting for KV-cache prefix hits and reduced prefill overhead.
    """
    uncached_input_tokens = total_input_tokens - reused_input_tokens
    
    # Cost estimation
    cached_price_per_million = input_price_per_million * (1.0 - cached_input_discount)
    
    uncached_input_cost = (uncached_input_tokens / 1_000_000.0) * input_price_per_million
    cached_input_cost = (reused_input_tokens / 1_000_000.0) * cached_price_per_million
    output_cost = (total_output_tokens / 1_000_000.0) * output_price_per_million
    
    total_cost = round(uncached_input_cost + cached_input_cost + output_cost, 6)

    # Latency simulation
    prefill_latency = uncached_input_tokens / max(prefill_throughput_tps, 1.0)
    decode_latency = total_output_tokens / max(decode_throughput_tps, 1.0)
    overhead_latency = num_prompts * fixed_overhead_per_request
    
    total_latency_sec = round(prefill_latency + decode_latency + overhead_latency, 4)

    return {
        "uncached_input_tokens": uncached_input_tokens,
        "reused_input_tokens": reused_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_cost_usd": total_cost,
        "estimated_latency_sec": total_latency_sec,
        "prefill_latency_sec": round(prefill_latency, 4),
        "decode_latency_sec": round(decode_latency, 4),
    }
