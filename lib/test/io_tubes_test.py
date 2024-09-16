import pytest

from lib.io_tubes import *

def test_parse_time_limit():
    test_cases = [
        ("1", 1), ("1s", 1), ("1m", 60), ("1h", 3600), ("1d", 86400),
        ("1w", 604800), ("1y", 31536000), ("1.5", 1.5), ("1.5s", 1.5),
        ("1.5m", 90), ("1.5h", 5400), ("1.5d", 129600), ("1.5w", 907200)
    ]
    for input_str, expected in test_cases:
        assert parse_time_limit(input_str) == expected

def test_parse_time_limit_value_error():
    invalid_cases = ["invalid", "10x", "1.5x", "1.5.5s"]
    for input_str in invalid_cases:
        with pytest.raises(ValueError):
            parse_time_limit(input_str)