from typing import List, Dict, Any, Tuple


def tokenize_proxy(text: str) -> List[str]:
    """
    Deterministic whitespace tokenization proxy for prefix matching.
    Labels: Token approximation / cache-reuse proxy.
    """
    return text.strip().split()


def longest_common_prefix(tokens_a: List[str], tokens_b: List[str]) -> List[str]:
    """
    Computes the longest common token prefix between two token sequences.
    """
    min_len = min(len(tokens_a), len(tokens_b))
    lcp = []
    for i in range(min_len):
        if tokens_a[i] == tokens_b[i]:
            lcp.append(tokens_a[i])
        else:
            break
    return lcp


def compute_prefix_metrics(prompts: List[str]) -> Dict[str, Any]:
    """
    Computes Prefix Hit Count (PHC), total reused tokens, cache reuse ratio,
    and average prefix length across a sequence of LLM request prompts.
    """
    if not prompts:
        return {
            "total_prompts": 0,
            "total_input_tokens": 0,
            "reused_prefix_tokens": 0,
            "prefix_hit_count": 0,
            "cache_reuse_ratio": 0.0,
            "avg_prefix_token_length": 0.0,
        }

    tokenized_prompts = [tokenize_proxy(p) for p in prompts]
    total_input_tokens = sum(len(t) for t in tokenized_prompts)
    
    reused_tokens = 0
    phc = 0
    
    for i in range(1, len(tokenized_prompts)):
        lcp = longest_common_prefix(tokenized_prompts[i - 1], tokenized_prompts[i])
        match_len = len(lcp)
        if match_len > 0:
            reused_tokens += match_len
            phc += 1

    reuse_ratio = (
        round(reused_tokens / total_input_tokens, 4)
        if total_input_tokens > 0
        else 0.0
    )
    avg_prefix_len = (
        round(reused_tokens / (len(prompts) - 1), 2)
        if len(prompts) > 1
        else 0.0
    )

    return {
        "total_prompts": len(prompts),
        "total_input_tokens": total_input_tokens,
        "reused_prefix_tokens": reused_tokens,
        "prefix_hit_count": phc,
        "cache_reuse_ratio": reuse_ratio,
        "avg_prefix_token_length": avg_prefix_len,
    }
