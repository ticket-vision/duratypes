import logging
import re
from typing import Annotated

from pydantic import BeforeValidator, TypeAdapter


# Custom exception hierarchy
class DurationError(ValueError):
    """Base exception for all duration-related errors."""
    pass


class InvalidFormatError(DurationError):
    """Raised when a duration string has an invalid format."""
    pass


class InvalidTypeError(DurationError, TypeError):
    """Raised when an invalid type is provided for duration parsing."""
    pass


class InvalidValueError(DurationError):
    """Raised when a duration value is invalid (e.g., None, NaN)."""
    pass


# Constants for time unit conversions
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400
SECONDS_PER_WEEK = 604800  # 7 * 24 * 60 * 60
SECONDS_PER_MONTH = 2592000  # 30 * 24 * 60 * 60 (approximate)
SECONDS_PER_YEAR = 31536000  # 365 * 24 * 60 * 60 (approximate)

# Logger for debugging
logger = logging.getLogger(__name__)

__all__ = [
    "Duration",
    "DurationAdapter",
    "DurationError",
    "Hours",
    "InvalidFormatError",
    "InvalidTypeError",
    "InvalidValueError",
    "Minutes",
    "Seconds",
    "format_duration",
    "parse_duration",
]

_COMPOUND_RE = re.compile(
    r"(?P<value>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>y(?:ear)?s?|mo(?:nth)?s?|w(?:eek)?s?|d(?:ay)?s?|h(?:our)?s?|m(?:in(?:ute)?s?)?|s(?:ec(?:ond)?s?)?)",
    re.IGNORECASE,
)
_ISO_RE = re.compile(
    r"^(?P<sign>[+-])?P(?:\d+Y)?(?:\d+M)?(?:(?P<d>\d+(?:\.\d+)?)D)?"
    r"(?:T"
    r"(?:(?P<h>[+-]?\d+(?:\.\d+)?)H)?"
    r"(?:(?P<m>[+-]?\d+(?:\.\d+)?)M)?"
    r"(?:(?P<s>[+-]?\d+(?:\.\d+)?)S)?)?$",
    re.IGNORECASE,
)
_LEADING_SIGN = re.compile(r"^(?P<sign>[+-])\s*(?P<rest>.*)$")


def _validate_input(v: str | int | float) -> None:
    """Validate input type and basic constraints."""
    if v is None:
        raise InvalidValueError("Duration cannot be None")


def _parse_numeric(v: int | float) -> int:
    """Parse numeric duration input."""
    if not isinstance(v, (int, float)) or v != v:  # Check for NaN
        raise InvalidValueError(f"Invalid numeric duration: {v!r}")
    logger.debug(f"Parsing numeric duration: {v}")
    return int(v)


def _extract_sign(raw: str, original: str | int | float) -> tuple[str, int]:
    """Extract leading sign from duration string."""
    sign = 1
    m_sign = _LEADING_SIGN.match(raw)
    if m_sign:
        raw = m_sign.group("rest").strip()
        sign = -1 if m_sign.group("sign") == "-" else 1
        if not raw:
            raise InvalidFormatError(
                f"Invalid duration format: missing duration after sign in {original!r}"
            )
    return raw, sign


def _parse_iso8601(raw: str, sign: int) -> int | None:
    """Parse ISO 8601 duration format."""
    m_iso = _ISO_RE.fullmatch(raw)
    if not m_iso:
        return None

    logger.debug(f"Matched ISO 8601 format: {raw}")
    if m_iso.group("sign"):
        sign = -1 if m_iso.group("sign") == "-" else +1

    # Parse individual components (can have their own signs)
    d = float(m_iso.group("d") or 0)
    h = float(m_iso.group("h") or 0)
    minutes = float(m_iso.group("m") or 0)
    s = float(m_iso.group("s") or 0)

    total_seconds = int(
        d * SECONDS_PER_DAY
        + h * SECONDS_PER_HOUR
        + minutes * SECONDS_PER_MINUTE
        + s
    )
    return sign * total_seconds


def _parse_compound(raw: str, sign: int) -> int | None:
    """Parse compound duration format (e.g., '1h30m45s')."""
    total = 0.0
    matches = list(_COMPOUND_RE.finditer(raw.lower()))

    if not matches:
        return None

    # Check that matches cover the entire string without gaps
    expected_pos = 0
    for match in matches:
        # Skip whitespace before the match
        while expected_pos < len(raw) and raw[expected_pos].isspace():
            expected_pos += 1

        # Check if match starts where we expect
        if match.start() != expected_pos:
            # There's a gap or unexpected characters
            return None

        val = float(match.group("value"))
        unit = match.group("unit").lower().strip()

        if unit.startswith("y"):
            total += val * SECONDS_PER_YEAR
        elif unit.startswith("mo"):
            total += val * SECONDS_PER_MONTH
        elif unit.startswith("w"):
            total += val * SECONDS_PER_WEEK
        elif unit.startswith("d"):
            total += val * SECONDS_PER_DAY
        elif unit.startswith("h"):
            total += val * SECONDS_PER_HOUR
        elif unit.startswith("m"):
            total += val * SECONDS_PER_MINUTE
        else:  # seconds
            total += val

        expected_pos = match.end()

        logger.debug(
            f"Parsed component: {val}{unit} -> {val * (SECONDS_PER_HOUR if unit.startswith('h') else SECONDS_PER_MINUTE if unit.startswith('m') else 1)} seconds"
        )

    # Check that we've consumed the entire string (ignoring trailing whitespace)
    while expected_pos < len(raw) and raw[expected_pos].isspace():
        expected_pos += 1

    if expected_pos != len(raw):
        # There are unconsumed characters
        return None

    return sign * int(total)


def parse_duration(v: str | int | float) -> int:
    """
    Parse a duration string, integer, or float into seconds.

    Args:
        v: Duration input in various formats:
            - String: "30s", "5m", "1h30m", "PT1H30M", etc.
            - Integer/Float: Direct seconds value

    Returns:
        Duration in seconds as an integer

    Raises:
        InvalidFormatError: If the input format is invalid or unsupported
        InvalidTypeError: If the input type is not supported
        InvalidValueError: If the input value is invalid (None, NaN, empty string)
    """
    _validate_input(v)

    # Handle numeric inputs
    if isinstance(v, (int, float)):
        return _parse_numeric(v)

    # Handle string inputs
    if not isinstance(v, str):
        raise InvalidTypeError(
            f"Duration must be str, int, or float, got {type(v).__name__}")

    raw = str(v).strip()
    if not raw:
        raise InvalidValueError("Duration string cannot be empty")

    logger.debug(f"Parsing duration string: {raw!r}")

    # Extract leading sign
    raw, sign = _extract_sign(raw, v)

    # Try ISO 8601 format first
    result = _parse_iso8601(raw, sign)
    if result is not None:
        return result

    # Try compound format
    result = _parse_compound(raw, sign)
    if result is not None:
        return result

    # If we get here, no format matched
    raise InvalidFormatError(
        f"Invalid duration format: {v!r}. "
        f"Supported formats: compound ('30s', '5m', '1h30m'), "
        f"ISO 8601 ('PT30S', 'PT5M', 'PT1H30M'), or numeric (30, 30.5)"
    )


def format_duration(seconds: int) -> str:
    """
    Format a duration in seconds into a human-readable string.

    Args:
        seconds: Duration in seconds (can be negative)

    Returns:
        Human-readable duration string (e.g., "1h30m45s", "30s", "-2h15m")

    Raises:
        InvalidTypeError: If seconds is not an integer
    """
    if not isinstance(seconds, int):
        raise InvalidTypeError(
            f"Seconds must be an integer, got {type(seconds).__name__}")

    logger.debug(f"Formatting duration: {seconds} seconds")

    sign_str = "-" if seconds < 0 else ""
    seconds = abs(seconds)
    parts = []

    # Break down into largest units first
    y, rem = divmod(seconds, SECONDS_PER_YEAR)
    mo, rem = divmod(rem, SECONDS_PER_MONTH)
    w, rem = divmod(rem, SECONDS_PER_WEEK)
    d, rem = divmod(rem, SECONDS_PER_DAY)
    h, rem = divmod(rem, SECONDS_PER_HOUR)
    m, s = divmod(rem, SECONDS_PER_MINUTE)

    if y:
        parts.append(f"{y}y")
    if mo:
        parts.append(f"{mo}mo")
    if w:
        parts.append(f"{w}w")
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if s or not parts:  # Always include seconds if it's the only component
        parts.append(f"{s}s")

    result = sign_str + "".join(parts)
    logger.debug(f"Formatted duration result: {result}")
    return result


# Pydantic annotated types
Seconds = Annotated[int, BeforeValidator(parse_duration)]
Minutes = Seconds
Hours = Seconds
Duration = Seconds

# Singleton adapter for maximum reuse
DurationAdapter: TypeAdapter[Duration] = TypeAdapter(Duration)
