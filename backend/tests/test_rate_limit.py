from app.core.rate_limit import RateLimitExceeded, check_rate_limit


def test_rate_limit_allows_requests_within_budget() -> None:
    check_rate_limit(key="test-user", max_requests=2, window_seconds=60)
    check_rate_limit(key="test-user", max_requests=2, window_seconds=60)


def test_rate_limit_blocks_excess_requests() -> None:
    key = "test-user-blocked"
    check_rate_limit(key=key, max_requests=1, window_seconds=60)

    try:
        check_rate_limit(key=key, max_requests=1, window_seconds=60)
    except RateLimitExceeded:
        return

    raise AssertionError("Expected RateLimitExceeded")
