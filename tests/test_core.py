import pytest

from duratypes.core import parse_duration, format_duration, DurationAdapter


@pytest.mark.parametrize("input_val,expected_seconds", [
    ("60s", 60),
    ("60sec", 60),
    ("60 seconds", 60),
    ("1m", 60),
    ("1 minute", 60),
    ("2h", 7200),
    ("1h30m", 5400),
    ("90 sec", 90),
    ("PT90S", 90),
    ("PT1H30M", 5400),
    ("-60s", -60),
    ("-1min", -60),
    ("-1h30m", -5400),
    ("+PT90S", 90),
    ("PT-90S", -90),
    (45, 45),
    (1.5, 1),
])
def test_parse_and_adapter(input_val, expected_seconds):
    assert parse_duration(input_val) == expected_seconds
    result = DurationAdapter.validate_python(input_val)
    assert result == expected_seconds


@pytest.mark.parametrize("seconds,expected_str", [
    (60, "1m"),
    (90, "1m30s"),
    (5400, "1h30m"),
    (0, "0s"),
    (-90, "-1m30s"),
])
def test_format_duration(seconds, expected_str):
    assert format_duration(seconds) == expected_str


def test_invalid_input():
    with pytest.raises(ValueError):
        parse_duration("abc")
    with pytest.raises(ValueError):
        DurationAdapter.validate_python("5x")


def test_iso_edge_cases():
    assert parse_duration("P1DT2H") == 0  # unsupported day by default
    # but compound still works:
    assert parse_duration("1h 15m") == 4500


def test_rejects_empty_string():
    with pytest.raises(ValueError):
        parse_duration("")
    with pytest.raises(ValueError):
        DurationAdapter.validate_python("")
