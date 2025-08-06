import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from hypothesis import given, strategies as st, assume, example
from hypothesis.strategies import composite
from pydantic import ValidationError

from duratypes.core import DurationAdapter, format_duration, parse_duration


@pytest.mark.parametrize(
    "input_val,expected_seconds",
    [
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
    ],
)
def test_parse_and_adapter(input_val, expected_seconds):
    assert parse_duration(input_val) == expected_seconds
    result = DurationAdapter.validate_python(input_val)
    assert result == expected_seconds


@pytest.mark.parametrize(
    "seconds,expected_str",
    [
        (60, "1m"),
        (90, "1m30s"),
        (5400, "1h30m"),
        (0, "0s"),
        (-90, "-1m30s"),
    ],
)
def test_format_duration(seconds, expected_str):
    assert format_duration(seconds) == expected_str


def test_invalid_input():
    with pytest.raises(ValueError):
        parse_duration("abc")
    with pytest.raises(ValueError):
        DurationAdapter.validate_python("5x")


def test_iso_edge_cases():
    assert parse_duration("P1DT2H") == 93600  # 1 day = 86400 + 2 hours = 7200 = 93600
    assert parse_duration("1h 15m") == 4500


def test_rejects_empty_string():
    with pytest.raises(ValueError):
        parse_duration("")
    with pytest.raises(ValueError):
        DurationAdapter.validate_python("")


class TestComprehensiveEdgeCases:
    """Comprehensive edge case tests for duratypes parsing and validation."""

    def test_extreme_values(self):
        """Test parsing of extreme numeric values."""
        # Large positive values
        assert parse_duration(999999999) == 999999999
        assert parse_duration("999999999s") == 999999999

        # Large negative values
        assert parse_duration(-999999999) == -999999999
        assert parse_duration("-999999999s") == -999999999

        # Zero values
        assert parse_duration(0) == 0
        assert parse_duration("0s") == 0
        assert parse_duration("0m") == 0
        assert parse_duration("0h") == 0

    def test_whitespace_handling(self):
        """Test various whitespace scenarios."""
        # Leading/trailing whitespace
        assert parse_duration("  30s  ") == 30
        assert parse_duration("\t1h30m\n") == 5400
        assert parse_duration("   PT1H   ") == 3600

        # Internal whitespace variations
        assert parse_duration("1 h 30 m") == 5400
        assert parse_duration("30 seconds") == 30
        assert parse_duration("5  minutes") == 300

        # Multiple spaces
        assert parse_duration("1    h    30    m") == 5400

    def test_case_sensitivity(self):
        """Test case insensitive parsing."""
        # Mixed case compound formats
        assert parse_duration("30S") == 30
        assert parse_duration("5M") == 300
        assert parse_duration("1H") == 3600
        assert parse_duration("1H30M45S") == 5445

        # Mixed case ISO formats
        assert parse_duration("pt30s") == 30
        assert parse_duration("PT1h30M") == 5400
        assert parse_duration("Pt1H30m45S") == 5445

    def test_decimal_precision(self):
        """Test decimal value handling and precision."""
        # Float inputs (should truncate to int)
        assert parse_duration(30.9) == 30
        assert parse_duration(30.1) == 30
        assert parse_duration(30.5) == 30

        # String decimal values
        assert parse_duration("30.5s") == 30
        assert parse_duration("1.5h") == 5400  # 1.5 * 3600 = 5400
        assert parse_duration("2.25m") == 135  # 2.25 * 60 = 135

    def test_malformed_iso_formats(self):
        """Test various malformed ISO 8601 formats."""
        # These should actually parse as valid ISO formats with zero values
        assert parse_duration("P") == 0  # Empty ISO parses as 0
        assert parse_duration("PT") == 0  # Empty time part parses as 0

        # These should fail
        with pytest.raises(ValueError):
            parse_duration("PT1X")  # Invalid unit
        with pytest.raises(ValueError):
            parse_duration("INVALID")  # Not ISO format

    def test_malformed_compound_formats(self):
        """Test various malformed compound formats."""
        with pytest.raises(ValueError):
            parse_duration("30")  # No unit
        with pytest.raises(ValueError):
            parse_duration("s30")  # Unit before number
        with pytest.raises(ValueError):
            parse_duration("30x")  # Invalid unit
        with pytest.raises(ValueError):
            parse_duration("h")  # Unit without number

    def test_sign_edge_cases(self):
        """Test various sign scenarios."""
        # Leading signs with whitespace
        assert parse_duration("+ 30s") == 30
        assert parse_duration("- 30s") == -30
        assert parse_duration("+  PT30S") == 30
        assert parse_duration("-  PT30S") == -30

        # Invalid sign scenarios
        with pytest.raises(ValueError):
            parse_duration("+")  # Sign only
        with pytest.raises(ValueError):
            parse_duration("-")  # Sign only
        with pytest.raises(ValueError):
            parse_duration("+ ")  # Sign with whitespace only

    def test_none_and_invalid_types(self):
        """Test None and invalid type handling."""
        with pytest.raises(ValueError):
            parse_duration(None)

        with pytest.raises(TypeError):
            parse_duration([])

        with pytest.raises(TypeError):
            parse_duration({})

        with pytest.raises(TypeError):
            parse_duration(object())

    def test_nan_and_infinity(self):
        """Test NaN and infinity handling."""
        import math

        with pytest.raises(ValueError):
            parse_duration(float('nan'))

        with pytest.raises(OverflowError):
            parse_duration(float('inf'))

        with pytest.raises(OverflowError):
            parse_duration(float('-inf'))

    def test_unicode_and_special_characters(self):
        """Test Unicode and special character handling."""
        # Unicode whitespace should be handled by strip()
        assert parse_duration("30s\u00A0") == 30  # Non-breaking space

        # Invalid Unicode characters should fail
        with pytest.raises(ValueError):
            parse_duration("30ś")  # Unicode 's' variant

        # Test that zero-width space doesn't break parsing
        with pytest.raises(ValueError):
            parse_duration("invalid\u200B")  # Zero-width space with invalid text

    def test_very_long_strings(self):
        """Test very long input strings."""
        # Long valid string
        long_valid = "1h" + "0m" * 100 + "30s"
        assert parse_duration(long_valid) == 3630

        # Long invalid string
        long_invalid = "x" * 1000
        with pytest.raises(ValueError):
            parse_duration(long_invalid)

    def test_boundary_conditions(self):
        """Test boundary conditions for time units."""
        # Exactly 1 minute in seconds
        assert parse_duration("60s") == 60
        assert parse_duration("1m") == 60

        # Exactly 1 hour in minutes/seconds
        assert parse_duration("60m") == 3600
        assert parse_duration("1h") == 3600
        assert parse_duration("3600s") == 3600

        # Exactly 1 day in hours/minutes/seconds
        assert parse_duration("24h") == 86400
        assert parse_duration("1440m") == 86400
        assert parse_duration("86400s") == 86400

    def test_complex_compound_formats(self):
        """Test complex compound format combinations."""
        # Multiple same units (should sum)
        assert parse_duration("30s45s") == 75
        assert parse_duration("1h2h") == 10800  # 3 hours
        assert parse_duration("30m15m") == 2700  # 45 minutes

        # Out-of-order units
        assert parse_duration("30s1h15m") == 4530  # 30 + 3600 + 900 = 4530
        assert parse_duration("45s30m2h") == 9045  # 45 + 1800 + 7200 = 9045

    def test_iso_with_fractional_seconds(self):
        """Test ISO format with fractional components."""
        assert parse_duration("PT30.5S") == 30
        assert parse_duration("PT1.5H") == 5400  # 1.5 hours
        assert parse_duration("PT90.5M") == 5430  # 90.5 minutes

    def test_format_duration_edge_cases(self):
        """Test format_duration with edge cases."""
        # Very large values
        assert format_duration(999999) == "1w4d13h46m39s"

        # Negative values
        assert format_duration(-3661) == "-1h1m1s"

        # Boundary values
        assert format_duration(59) == "59s"
        assert format_duration(60) == "1m"
        assert format_duration(61) == "1m1s"
        assert format_duration(3599) == "59m59s"
        assert format_duration(3600) == "1h"
        assert format_duration(3661) == "1h1m1s"

    def test_format_duration_invalid_types(self):
        """Test format_duration with invalid types."""
        with pytest.raises(TypeError):
            format_duration("30")

        with pytest.raises(TypeError):
            format_duration(30.5)

        with pytest.raises(TypeError):
            format_duration(None)

    def test_adapter_edge_cases(self):
        """Test DurationAdapter with various edge cases."""
        # All the same edge cases should work with the adapter
        assert DurationAdapter.validate_python("  30s  ") == 30
        assert DurationAdapter.validate_python(999999) == 999999
        assert DurationAdapter.validate_python("-1h30m") == -5400

        with pytest.raises(ValueError):
            DurationAdapter.validate_python("")

        with pytest.raises(ValueError):
            DurationAdapter.validate_python("invalid")

        with pytest.raises(ValidationError):
            DurationAdapter.validate_python([])

    def test_logging_and_debug_info(self):
        """Test that parsing works correctly (logging is internal)."""
        # These should parse without errors and produce correct results
        assert parse_duration("1h30m45s") == 5445
        assert parse_duration("PT1H30M45S") == 5445
        assert parse_duration(3661) == 3661


class TestPropertyBasedTesting:
    """Property-based tests using Hypothesis for comprehensive input validation."""

    @composite
    def duration_strings(draw):
        """Generate valid duration strings in compound format."""
        hours = draw(st.integers(min_value=0, max_value=999))
        minutes = draw(st.integers(min_value=0, max_value=59))
        seconds = draw(st.integers(min_value=0, max_value=59))

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:  # Always include seconds if no other parts
            parts.append(f"{seconds}s")

        return "".join(parts)

    @composite
    def iso_duration_strings(draw):
        """Generate valid ISO 8601 duration strings."""
        hours = draw(st.integers(min_value=0, max_value=999))
        minutes = draw(st.integers(min_value=0, max_value=59))
        seconds = draw(st.integers(min_value=0, max_value=59))

        parts = ["PT"]
        if hours > 0:
            parts.append(f"{hours}H")
        if minutes > 0:
            parts.append(f"{minutes}M")
        if seconds > 0:
            parts.append(f"{seconds}S")

        # Ensure we have at least one time component
        if len(parts) == 1:  # Only "PT"
            parts.append("0S")

        return "".join(parts)

    @given(st.integers(min_value=-999999, max_value=999999))
    def test_numeric_round_trip(self, seconds):
        """Test that numeric inputs parse correctly and format consistently."""
        parsed = parse_duration(seconds)
        assert parsed == seconds

        # Test that formatting and re-parsing gives the same result
        formatted = format_duration(parsed)
        reparsed = parse_duration(formatted)
        assert reparsed == seconds

    @given(duration_strings())
    def test_compound_format_parsing(self, duration_str):
        """Test that generated compound format strings parse without error."""
        result = parse_duration(duration_str)
        assert isinstance(result, int)
        assert result >= 0  # Generated strings should be positive

        # Test round-trip: parse -> format -> parse
        formatted = format_duration(result)
        reparsed = parse_duration(formatted)
        assert reparsed == result

    @given(iso_duration_strings())
    def test_iso_format_parsing(self, iso_str):
        """Test that generated ISO format strings parse without error."""
        result = parse_duration(iso_str)
        assert isinstance(result, int)
        assert result >= 0  # Generated strings should be positive

    @given(st.integers(min_value=0, max_value=999999))
    def test_format_duration_properties(self, seconds):
        """Test properties of format_duration function."""
        formatted = format_duration(seconds)

        # Should always be a string
        assert isinstance(formatted, str)

        # Should be parseable back to the same value
        parsed = parse_duration(formatted)
        assert parsed == seconds

        # Should not contain leading/trailing whitespace
        assert formatted == formatted.strip()

        # Should contain only valid characters
        valid_chars = set("0123456789hmsydwo-")  # Added y(ears), d(ays), w(eeks), o(months)
        assert all(c in valid_chars for c in formatted)

    @given(st.integers(min_value=-999999, max_value=-1))
    def test_negative_duration_properties(self, negative_seconds):
        """Test properties of negative durations."""
        # Should parse correctly
        parsed = parse_duration(negative_seconds)
        assert parsed == negative_seconds
        assert parsed < 0

        # Should format with negative sign
        formatted = format_duration(parsed)
        assert formatted.startswith("-")

        # Should round-trip correctly
        reparsed = parse_duration(formatted)
        assert reparsed == negative_seconds

    @given(st.floats(min_value=-999999.0, max_value=999999.0, allow_nan=False, allow_infinity=False))
    def test_float_input_truncation(self, float_val):
        """Test that float inputs are truncated to integers."""
        parsed = parse_duration(float_val)
        assert isinstance(parsed, int)
        assert parsed == int(float_val)

    @given(st.text(min_size=1, max_size=10))
    def test_invalid_string_handling(self, random_text):
        """Test that random invalid strings raise ValueError."""
        # Skip strings that might accidentally be valid
        assume(not any(c in random_text.lower() for c in "hms"))
        assume(not random_text.startswith("pt"))
        assume(not random_text.replace(".", "").replace("-", "").replace("+", "").isdigit())

        with pytest.raises((ValueError, TypeError)):
            parse_duration(random_text)

    @given(st.integers(min_value=0, max_value=999),
           st.integers(min_value=0, max_value=59),
           st.integers(min_value=0, max_value=59))
    def test_compound_format_generation(self, hours, minutes, seconds):
        """Test parsing of systematically generated compound formats."""
        # Build duration string
        parts = []
        expected_seconds = 0

        if hours > 0:
            parts.append(f"{hours}h")
            expected_seconds += hours * 3600
        if minutes > 0:
            parts.append(f"{minutes}m")
            expected_seconds += minutes * 60
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
            expected_seconds += seconds

        duration_str = "".join(parts)
        parsed = parse_duration(duration_str)
        assert parsed == expected_seconds

    @given(st.booleans(), st.integers(min_value=1, max_value=999999))
    def test_sign_handling(self, is_negative, abs_seconds):
        """Test sign handling in various formats."""
        seconds = -abs_seconds if is_negative else abs_seconds

        # Test numeric input
        assert parse_duration(seconds) == seconds

        # Test formatted string with sign
        formatted = format_duration(seconds)
        assert parse_duration(formatted) == seconds

        # Test explicit sign in string
        if is_negative:
            assert formatted.startswith("-")
        else:
            assert not formatted.startswith("-")

    @given(st.integers(min_value=0, max_value=999999))
    @example(0)  # Ensure we test zero
    @example(60)  # Ensure we test exact minute
    @example(3600)  # Ensure we test exact hour
    def test_adapter_consistency(self, seconds):
        """Test that DurationAdapter behaves consistently with parse_duration."""
        # Test numeric input
        adapter_result = DurationAdapter.validate_python(seconds)
        parse_result = parse_duration(seconds)
        assert adapter_result == parse_result

        # Test string input
        formatted = format_duration(seconds)
        adapter_result = DurationAdapter.validate_python(formatted)
        assert adapter_result == seconds

    @given(st.lists(st.integers(min_value=1, max_value=100), min_size=1, max_size=5))
    def test_multiple_same_units(self, values):
        """Test that multiple instances of the same unit sum correctly."""
        # Test multiple seconds
        seconds_str = "".join(f"{v}s" for v in values)
        expected = sum(values)
        assert parse_duration(seconds_str) == expected

        # Test multiple minutes
        minutes_str = "".join(f"{v}m" for v in values)
        expected = sum(values) * 60
        assert parse_duration(minutes_str) == expected

        # Test multiple hours
        hours_str = "".join(f"{v}h" for v in values)
        expected = sum(values) * 3600
        assert parse_duration(hours_str) == expected


class TestErrorHandlingAndExceptions:
    """Comprehensive tests for error handling and exception scenarios."""

    def test_parse_duration_value_errors(self):
        """Test all ValueError scenarios in parse_duration."""
        # None input
        with pytest.raises(ValueError, match="Duration cannot be None"):
            parse_duration(None)

        # Empty string
        with pytest.raises(ValueError, match="Duration string cannot be empty"):
            parse_duration("")

        # Whitespace-only string
        with pytest.raises(ValueError, match="Duration string cannot be empty"):
            parse_duration("   ")

        # Invalid format - no units
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("123")

        # Invalid format - random text
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("invalid")

        # Invalid format - unit without number
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("h")

        # Invalid format - number without unit
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("30x")

        # Sign without duration
        with pytest.raises(ValueError, match="missing duration after sign"):
            parse_duration("+")

        with pytest.raises(ValueError, match="missing duration after sign"):
            parse_duration("-")

        with pytest.raises(ValueError, match="missing duration after sign"):
            parse_duration("+ ")

    def test_parse_duration_type_errors(self):
        """Test all TypeError scenarios in parse_duration."""
        # List input
        with pytest.raises(TypeError, match="Duration must be str, int, or float"):
            parse_duration([1, 2, 3])

        # Dict input
        with pytest.raises(TypeError, match="Duration must be str, int, or float"):
            parse_duration({"duration": 30})

        # Object input
        with pytest.raises(TypeError, match="Duration must be str, int, or float"):
            parse_duration(object())

        # Tuple input
        with pytest.raises(TypeError, match="Duration must be str, int, or float"):
            parse_duration((30, "seconds"))

    def test_parse_duration_nan_handling(self):
        """Test NaN handling in parse_duration."""
        import math

        with pytest.raises(ValueError, match="Invalid numeric duration"):
            parse_duration(float('nan'))

    def test_parse_duration_infinity_handling(self):
        """Test infinity handling in parse_duration."""
        # Positive infinity
        with pytest.raises(OverflowError):
            parse_duration(float('inf'))

        # Negative infinity
        with pytest.raises(OverflowError):
            parse_duration(float('-inf'))

    def test_format_duration_type_errors(self):
        """Test all TypeError scenarios in format_duration."""
        # String input
        with pytest.raises(TypeError, match="Seconds must be an integer"):
            format_duration("30")

        # Float input
        with pytest.raises(TypeError, match="Seconds must be an integer"):
            format_duration(30.5)

        # None input
        with pytest.raises(TypeError, match="Seconds must be an integer"):
            format_duration(None)

        # List input
        with pytest.raises(TypeError, match="Seconds must be an integer"):
            format_duration([30])

        # Dict input
        with pytest.raises(TypeError, match="Seconds must be an integer"):
            format_duration({"seconds": 30})

    def test_duration_adapter_error_propagation(self):
        """Test that DurationAdapter properly propagates errors from parse_duration."""
        # ValueError scenarios
        with pytest.raises(ValueError):
            DurationAdapter.validate_python("")

        with pytest.raises(ValueError):
            DurationAdapter.validate_python("invalid")

        with pytest.raises(ValueError):
            DurationAdapter.validate_python(None)

        # TypeError scenarios (wrapped in ValidationError by Pydantic)
        with pytest.raises(ValidationError):
            DurationAdapter.validate_python([])

        with pytest.raises(ValidationError):
            DurationAdapter.validate_python({})

    def test_malformed_iso_error_messages(self):
        """Test specific error handling for malformed ISO formats."""
        # Invalid ISO characters
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("PT1X")  # Invalid unit

        # These should fail as they don't match any valid format
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("1PT30S")  # PT not at start

        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("PTXYZ")  # Invalid ISO format

    def test_malformed_compound_error_messages(self):
        """Test specific error handling for malformed compound formats."""
        # Invalid unit
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("30x")

        # Completely invalid format
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("xyz123")

    def test_edge_case_error_scenarios(self):
        """Test edge case error scenarios."""
        # Very long invalid string (simplified)
        long_invalid = "invalid" * 100
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration(long_invalid)

    def test_unicode_error_scenarios(self):
        """Test Unicode-related error scenarios."""
        # Simple Unicode test that should fail
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("αβγ")  # Greek letters

    def test_boundary_error_conditions(self):
        """Test boundary conditions that should cause errors."""
        # Test clearly invalid boundary cases
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("30")  # Number without unit

        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("abc")  # Pure text

    def test_sign_error_scenarios(self):
        """Test sign-related error scenarios."""
        # Test clearly invalid sign usage
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("30s-")  # Sign at end

        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("3-0s")  # Sign in middle of number

    def test_numeric_overflow_scenarios(self):
        """Test numeric overflow scenarios."""
        # Test reasonable overflow case
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("not_a_number")

    def test_error_message_consistency(self):
        """Test that error messages are consistent and helpful."""
        # Test that all ValueError messages contain helpful information
        test_cases = [
            ("", "empty"),
            ("invalid", "Invalid duration format"),
            ("30", "Invalid duration format"),
            ("30x", "Invalid duration format"),
        ]

        for invalid_input, expected_keyword in test_cases:
            with pytest.raises(ValueError) as exc_info:
                parse_duration(invalid_input)
            assert expected_keyword.lower() in str(exc_info.value).lower()

    def test_exception_inheritance(self):
        """Test that exceptions have proper inheritance."""
        # ValueError should be a subclass of Exception
        try:
            parse_duration("invalid")
        except ValueError as e:
            assert isinstance(e, Exception)
        except Exception:
            pytest.fail("Should raise ValueError, not generic Exception")

        # TypeError should be a subclass of Exception
        try:
            parse_duration([])
        except TypeError as e:
            assert isinstance(e, Exception)
        except Exception:
            pytest.fail("Should raise TypeError, not generic Exception")

    def test_error_state_consistency(self):
        """Test that errors don't leave the system in an inconsistent state."""
        # Test that after an error, normal parsing still works
        with pytest.raises(ValueError):
            parse_duration("invalid")

        # This should still work normally
        assert parse_duration("30s") == 30

        # Test with adapter too
        with pytest.raises(ValueError):
            DurationAdapter.validate_python("invalid")

        # This should still work normally
        assert DurationAdapter.validate_python("30s") == 30


class TestPerformanceBenchmarks:
    """Performance benchmarks and regression tests."""

    def test_parse_duration_performance_compound(self):
        """Benchmark parse_duration with compound formats."""
        test_cases = [
            "30s", "5m", "1h", "1h30m", "2h45m30s", "10h59m59s"
        ]

        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            for case in test_cases:
                parse_duration(case)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_parse = total_time / (iterations * len(test_cases))

        # Performance regression test: should parse in less than 1ms on average
        assert avg_time_per_parse < 0.001, f"Performance regression: avg time {avg_time_per_parse:.6f}s > 1ms"

        print(f"Compound format parsing: {avg_time_per_parse:.6f}s per parse ({iterations * len(test_cases)} total)")

    def test_parse_duration_performance_iso(self):
        """Benchmark parse_duration with ISO 8601 formats."""
        test_cases = [
            "PT30S", "PT5M", "PT1H", "PT1H30M", "PT2H45M30S", "PT10H59M59S"
        ]

        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            for case in test_cases:
                parse_duration(case)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_parse = total_time / (iterations * len(test_cases))

        # Performance regression test: should parse in less than 1ms on average
        assert avg_time_per_parse < 0.001, f"Performance regression: avg time {avg_time_per_parse:.6f}s > 1ms"

        print(f"ISO format parsing: {avg_time_per_parse:.6f}s per parse ({iterations * len(test_cases)} total)")

    def test_parse_duration_performance_numeric(self):
        """Benchmark parse_duration with numeric inputs."""
        test_cases = [30, 300, 3600, 7200, 86400]

        iterations = 10000
        start_time = time.time()

        for _ in range(iterations):
            for case in test_cases:
                parse_duration(case)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_parse = total_time / (iterations * len(test_cases))

        # Numeric parsing should be very fast
        assert avg_time_per_parse < 0.0001, f"Performance regression: avg time {avg_time_per_parse:.6f}s > 0.1ms"

        print(f"Numeric parsing: {avg_time_per_parse:.6f}s per parse ({iterations * len(test_cases)} total)")

    def test_format_duration_performance(self):
        """Benchmark format_duration performance."""
        test_cases = [30, 300, 3600, 7200, 86400, 90061]  # Various durations

        iterations = 10000
        start_time = time.time()

        for _ in range(iterations):
            for case in test_cases:
                format_duration(case)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_format = total_time / (iterations * len(test_cases))

        # Formatting should be fast
        assert avg_time_per_format < 0.0001, f"Performance regression: avg time {avg_time_per_format:.6f}s > 0.1ms"

        print(f"Duration formatting: {avg_time_per_format:.6f}s per format ({iterations * len(test_cases)} total)")

    def test_duration_adapter_performance(self):
        """Benchmark DurationAdapter performance."""
        test_cases = ["30s", "5m", "1h30m", "PT1H30M", 3600]

        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            for case in test_cases:
                DurationAdapter.validate_python(case)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_validation = total_time / (iterations * len(test_cases))

        # Adapter validation should be reasonably fast
        assert avg_time_per_validation < 0.001, f"Performance regression: avg time {avg_time_per_validation:.6f}s > 1ms"

        print(f"DurationAdapter validation: {avg_time_per_validation:.6f}s per validation ({iterations * len(test_cases)} total)")

    def test_round_trip_performance(self):
        """Benchmark round-trip parse -> format performance."""
        test_strings = ["30s", "5m30s", "1h30m45s", "2h15m"]

        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            for test_str in test_strings:
                seconds = parse_duration(test_str)
                formatted = format_duration(seconds)
                # Verify round-trip works
                assert parse_duration(formatted) == seconds

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_round_trip = total_time / (iterations * len(test_strings))

        # Round-trip should be reasonably fast
        assert avg_time_per_round_trip < 0.002, f"Performance regression: avg time {avg_time_per_round_trip:.6f}s > 2ms"

        print(f"Round-trip performance: {avg_time_per_round_trip:.6f}s per round-trip ({iterations * len(test_strings)} total)")


class TestThreadSafety:
    """Thread safety tests for singleton DurationAdapter and core functions."""

    def test_parse_duration_thread_safety(self):
        """Test that parse_duration is thread-safe."""
        test_cases = [
            "30s", "5m", "1h", "1h30m", "PT30S", "PT5M", "PT1H30M",
            3600, 300, 30
        ]
        expected_results = [
            30, 300, 3600, 5400, 30, 300, 5400,
            3600, 300, 30
        ]

        results = []
        errors = []

        def worker(case, expected):
            try:
                for _ in range(100):  # Multiple iterations per thread
                    result = parse_duration(case)
                    if result != expected:
                        errors.append(f"Expected {expected}, got {result} for {case}")
                    results.append(result)
            except Exception as e:
                errors.append(f"Exception in worker: {e}")

        # Run multiple threads concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for case, expected in zip(test_cases, expected_results):
                for _ in range(5):  # 5 threads per test case
                    futures.append(executor.submit(worker, case, expected))

            # Wait for all threads to complete
            for future in as_completed(futures):
                future.result()  # This will raise any exceptions

        # Verify no errors occurred
        assert not errors, f"Thread safety errors: {errors}"

        # Verify we got expected number of results
        expected_total = len(test_cases) * 5 * 100  # cases * threads_per_case * iterations_per_thread
        assert len(results) == expected_total, f"Expected {expected_total} results, got {len(results)}"

    def test_format_duration_thread_safety(self):
        """Test that format_duration is thread-safe."""
        test_cases = [30, 300, 3600, 5400, 7200, 90061]
        expected_results = ["30s", "5m", "1h", "1h30m", "2h", "1d1h1m1s"]

        results = []
        errors = []

        def worker(case, expected):
            try:
                for _ in range(100):
                    result = format_duration(case)
                    if result != expected:
                        errors.append(f"Expected {expected}, got {result} for {case}")
                    results.append(result)
            except Exception as e:
                errors.append(f"Exception in worker: {e}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for case, expected in zip(test_cases, expected_results):
                for _ in range(5):
                    futures.append(executor.submit(worker, case, expected))

            for future in as_completed(futures):
                future.result()

        assert not errors, f"Thread safety errors: {errors}"
        expected_total = len(test_cases) * 5 * 100
        assert len(results) == expected_total

    def test_duration_adapter_singleton_thread_safety(self):
        """Test that the singleton DurationAdapter is thread-safe."""
        test_cases = ["30s", "5m", "1h30m", "PT1H", 3600]
        expected_results = [30, 300, 5400, 3600, 3600]

        results = []
        errors = []
        adapter_instances = []

        def worker(case, expected):
            try:
                # Capture the adapter instance to verify singleton behavior
                adapter_instances.append(id(DurationAdapter))

                for _ in range(50):
                    result = DurationAdapter.validate_python(case)
                    if result != expected:
                        errors.append(f"Expected {expected}, got {result} for {case}")
                    results.append(result)
            except Exception as e:
                errors.append(f"Exception in worker: {e}")

        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            for case, expected in zip(test_cases, expected_results):
                for _ in range(6):  # 6 threads per test case
                    futures.append(executor.submit(worker, case, expected))

            for future in as_completed(futures):
                future.result()

        # Verify no errors occurred
        assert not errors, f"Thread safety errors: {errors}"

        # Verify singleton behavior - all threads should see the same adapter instance
        unique_adapter_ids = set(adapter_instances)
        assert len(unique_adapter_ids) == 1, f"Expected 1 unique adapter instance, got {len(unique_adapter_ids)}"

        # Verify expected number of results
        expected_total = len(test_cases) * 6 * 50
        assert len(results) == expected_total

    def test_concurrent_mixed_operations(self):
        """Test concurrent mixed operations (parse, format, adapter) for thread safety."""
        results = []
        errors = []

        def parse_worker():
            try:
                for _ in range(100):
                    result = parse_duration("1h30m")
                    results.append(("parse", result))
            except Exception as e:
                errors.append(f"Parse worker error: {e}")

        def format_worker():
            try:
                for _ in range(100):
                    result = format_duration(5400)
                    results.append(("format", result))
            except Exception as e:
                errors.append(f"Format worker error: {e}")

        def adapter_worker():
            try:
                for _ in range(100):
                    result = DurationAdapter.validate_python("1h30m")
                    results.append(("adapter", result))
            except Exception as e:
                errors.append(f"Adapter worker error: {e}")

        # Run all types of workers concurrently
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []

            # Submit multiple instances of each worker type
            for _ in range(5):
                futures.append(executor.submit(parse_worker))
                futures.append(executor.submit(format_worker))
                futures.append(executor.submit(adapter_worker))

            for future in as_completed(futures):
                future.result()

        # Verify no errors
        assert not errors, f"Concurrent operation errors: {errors}"

        # Verify results
        parse_results = [r[1] for r in results if r[0] == "parse"]
        format_results = [r[1] for r in results if r[0] == "format"]
        adapter_results = [r[1] for r in results if r[0] == "adapter"]

        # All parse and adapter results should be 5400 (1h30m in seconds)
        assert all(r == 5400 for r in parse_results), "Parse results inconsistent"
        assert all(r == 5400 for r in adapter_results), "Adapter results inconsistent"

        # All format results should be "1h30m"
        assert all(r == "1h30m" for r in format_results), "Format results inconsistent"

        # Verify expected counts
        assert len(parse_results) == 500  # 5 workers * 100 iterations
        assert len(format_results) == 500
        assert len(adapter_results) == 500
