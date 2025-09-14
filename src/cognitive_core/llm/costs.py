def compute_cost_from_usage(model: str, usage: dict, pricing_map: dict | None = None) -> float:
    """Compute a USD cost estimate from provider usage dict.
    pricing_map is a mapping model -> {'prompt_per_token': x, 'completion_per_token': y} in USD.
    If pricing_map is None, a conservative default is used (very small amounts) to avoid surprises.
    Returns float USD.
    """
    if not usage or not isinstance(usage, dict):
        return 0.0
    defaults = {"prompt_per_token": 0.000001, "completion_per_token": 0.000001}
    pricing = (pricing_map or {}).get(model, defaults)
    prompt_tokens = usage.get("prompt_tokens", 0) or 0
    completion_tokens = usage.get("completion_tokens", 0) or 0
    cost = prompt_tokens * pricing.get(
        "prompt_per_token", defaults["prompt_per_token"]
    ) + completion_tokens * pricing.get("completion_per_token", defaults["completion_per_token"])
    return float(cost)


def token_count_from_usage(usage: dict | None) -> int:
    """Return the total number of tokens from a provider usage dict."""
    if not usage or not isinstance(usage, dict):
        return 0
    prompt_tokens = usage.get("prompt_tokens", 0) or 0
    completion_tokens = usage.get("completion_tokens", 0) or 0
    return int(prompt_tokens + completion_tokens)
