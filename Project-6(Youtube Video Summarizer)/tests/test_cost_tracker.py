from types import SimpleNamespace

from src.cost_tracker import usage_from_message, combine, UsageReport


def test_usage_from_message_computes_cost():
    message = SimpleNamespace(
        usage_metadata={"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500}
    )
    usage = usage_from_message(message, "gpt-4o-mini")

    assert usage.total_tokens == 1500
    expected_cost = (1000 / 1_000_000) * 0.15 + (500 / 1_000_000) * 0.60
    assert abs(usage.total_cost_usd - expected_cost) < 1e-9


def test_usage_from_message_missing_metadata_returns_zero():
    message = SimpleNamespace(usage_metadata=None)
    usage = usage_from_message(message, "gpt-4o-mini")
    assert usage.total_tokens == 0


def test_combine_sums_reports():
    a = UsageReport(total_tokens=100, prompt_tokens=80, completion_tokens=20,
                     total_cost_usd=0.01, successful_requests=1)
    b = UsageReport(total_tokens=200, prompt_tokens=150, completion_tokens=50,
                     total_cost_usd=0.02, successful_requests=1)
    total = combine([a, b])
    assert total.total_tokens == 300
    assert abs(total.total_cost_usd - 0.03) < 1e-9