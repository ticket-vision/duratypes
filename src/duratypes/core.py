import re
from typing_extensions import Annotated
from pydantic import BeforeValidator, TypeAdapter

__all__ = [
    "Duration", "Seconds", "Minutes", "Hours",
    "parse_duration", "format_duration", "DurationAdapter",
]

_COMPOUND_RE = re.compile(
    r"(?P<value>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>s(?:ec(?:ond)?s?)?|m(?:in(?:ute)?s?)?|h(?:our)?s?)",
    re.IGNORECASE
)
_ISO_RE = re.compile(
    r"^(?P<sign>[+-])?P(?:\d+Y)?(?:\d+M)?(?:\d+D)?"
    r"(?:T"
    r"(?:(?P<h>\d+(?:\.\d+)?)H)?"
    r"(?:(?P<m>\d+(?:\.\d+)?)M)?"
    r"(?:(?P<s>\d+(?:\.\d+)?)S)?)?$",
    re.IGNORECASE
)
_LEADING_SIGN = re.compile(r"^(?P<sign>[+-])\s*(?P<rest>.*)$")

def parse_duration(v: str | int | float) -> int:
    sign = 1
    if isinstance(v, (int, float)):
        return int(v)

    raw = str(v).strip()
    m_sign = _LEADING_SIGN.match(raw)
    if m_sign:
        raw = m_sign.group("rest")
        sign = -1 if m_sign.group("sign") == "-" else 1

    m_iso = _ISO_RE.fullmatch(raw)
    if m_iso:
        if m_iso.group("sign"):
            sign = -1 if m_iso.group("sign") == "-" else +1
        h = float(m_iso.group("h") or 0)
        m = float(m_iso.group("m") or 0)
        s = float(m_iso.group("s") or 0)
        return sign * int(h * 3600 + m * 60 + s)

    total = 0.0
    found = False
    for m in _COMPOUND_RE.finditer(raw.lower()):
        found = True
        val = float(m.group("value"))
        unit = m.group("unit").lower().strip()
        if unit.startswith("h"):
            total += val * 3600
        elif unit.startswith("m"):
            total += val * 60
        else:
            total += val

    if found:
        return sign * int(total)

    raise ValueError(f"Invalid duration format: {v!r}")

def format_duration(seconds: int) -> str:
    sign_str = "-" if seconds < 0 else ""
    seconds = abs(seconds)
    parts = []
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if s or not parts:
        parts.append(f"{s}s")
    return sign_str + "".join(parts)

# Pydantic annotated types
Seconds = Annotated[int, BeforeValidator(parse_duration)]
Minutes = Seconds
Hours = Seconds
Duration = Seconds

# Singleton adapter for maximum reuse
DurationAdapter: TypeAdapter[Duration] = TypeAdapter(Duration)