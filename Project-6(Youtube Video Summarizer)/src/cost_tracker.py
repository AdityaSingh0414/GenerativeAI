"""
cost_tracker.py
---------------
Reads usage_metadata off each response and aggregates it manually in
the main thread (safe regardless of ThreadPoolExecutor usage, unlike
LangChain's context-var-based get_openai_callback()).
"""

from dataclasses import dataclass
from typing import List, Optional


PRICING_PER_MILLION_TOKENS = {
    "gpt-4o-mini":  {"input": 0.15,  "output": 0.60},
    "gpt-4o":       {"input": 2.50,  "output": 10.00},
    "gpt-4.1-mini": {"input": 0.40,  "output": 1.60},
    "gpt-4.1":      {"input": 2.00,  "output": 8.00},
}
_DEFAULT_PRICE = {"input": 0.50, "output": 1.50}


@dataclass
class UsageReport:
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost_usd: float = 0.0
    successful_requests: int = 0

    def __str__(self) -> str:
        return (
            f"{self.total_tokens:,} tokens "
            f"({self.prompt_tokens:,} prompt / {self.completion_tokens:,} completion), "
            f"${self.total_cost_usd:.4f} est., {self.successful_requests} request(s)"
        )

    def add(self, other: "UsageReport") -> "UsageReport":
        return UsageReport(
            total_tokens=self.total_tokens + other.total_tokens,
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_cost_usd=self.total_cost_usd + other.total_cost_usd,
            successful_requests=self.successful_requests + other.successful_requests,
        )


def usage_from_message(message, model_name: str) -> UsageReport:
    usage: Optional[dict] = getattr(message, "usage_metadata", None)
    if not usage:
        return UsageReport()

    prompt_tokens = usage.get("input_tokens", 0)
    completion_tokens = usage.get("output_tokens", 0)
    total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

    price = PRICING_PER_MILLION_TOKENS.get(model_name, _DEFAULT_PRICE)
    cost = (prompt_tokens / 1_000_000) * price["input"] + (
        completion_tokens / 1_000_000
    ) * price["output"]

    return UsageReport(
        total_tokens=total_tokens,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_cost_usd=cost,
        successful_requests=1,
    )


def combine(reports: List["UsageReport"]) -> UsageReport:
    total = UsageReport()
    for r in reports:
        total = total.add(r)
    return total