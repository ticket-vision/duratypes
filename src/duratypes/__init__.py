"""
duratypes - Typed duration utilities for Python and Pydantic.
Supports strings like '30s', '5m', '1h' and normalizes them to integer seconds.
"""

__version__ = "0.1.0"
__author__ = "Dillon Barendt"
__email__ = "dillon.barendt@ticket-vision.com"

from .core import (
    Duration,
    DurationAdapter,
    Hours,
    Minutes,
    Seconds,
    format_duration,
    parse_duration,
)

__all__ = [
    "Duration",
    "DurationAdapter",
    "Hours",
    "Minutes",
    "Seconds",
    "format_duration",
    "parse_duration",
]
