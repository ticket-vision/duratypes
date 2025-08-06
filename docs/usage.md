# Usage Guide

Comprehensive guide to using duratypes in your Python applications.

## Core Functions

### parse_duration()

The main parsing function that converts various duration formats to seconds.

```python
from duratypes import parse_duration

# Compound formats
result = parse_duration("1h30m45s")  # 5445 seconds
result = parse_duration("90 minutes") # 5400 seconds
result = parse_duration("2.5h")       # 9000 seconds

# ISO 8601 formats
result = parse_duration("PT1H30M45S") # 5445 seconds
result = parse_duration("PT90M")      # 5400 seconds
result = parse_duration("P1DT2H")     # 93600 seconds

# Numeric formats
result = parse_duration(3600)         # 3600 seconds
result = parse_duration(30.5)         # 30 seconds (truncated)
```

### format_duration()

Converts seconds back to human-readable duration strings.

```python
from duratypes import format_duration

# Basic formatting
formatted = format_duration(3661)    # "1h1m1s"
formatted = format_duration(300)     # "5m"
formatted = format_duration(45)      # "45s"

# Edge cases
formatted = format_duration(0)       # "0s"
formatted = format_duration(-300)    # "-5m"
```

## Advanced Usage

### Handling Negative Durations

```python
from duratypes import parse_duration, format_duration

# Negative compound formats
result = parse_duration("-1h30m")     # -5400 seconds
result = parse_duration("-PT1H30M")   # -5400 seconds

# Formatting negative durations
formatted = format_duration(-3661)   # "-1h1m1s"
```

### Case Insensitivity

All string parsing is case-insensitive:

```python
from duratypes import parse_duration

# All equivalent
result = parse_duration("1H30M")      # 5400 seconds
result = parse_duration("1h30m")      # 5400 seconds
result = parse_duration("1Hour30Min") # 5400 seconds
```

### Whitespace Handling

Whitespace is automatically handled:

```python
from duratypes import parse_duration

# All equivalent
result = parse_duration("1h30m")      # 5400 seconds
result = parse_duration("1h 30m")     # 5400 seconds
result = parse_duration(" 1h 30m ")   # 5400 seconds
```

## Unit Support

### Supported Time Units

| Unit | Aliases | Example |
|------|---------|---------|
| Seconds | `s`, `sec`, `second`, `seconds` | `"30s"`, `"30 seconds"` |
| Minutes | `m`, `min`, `minute`, `minutes` | `"5m"`, `"5 minutes"` |
| Hours | `h`, `hour`, `hours` | `"2h"`, `"2 hours"` |

### Fractional Units

Fractional values are supported in compound formats:

```python
from duratypes import parse_duration

result = parse_duration("1.5h")       # 5400 seconds (1.5 hours)
result = parse_duration("2.5m")       # 150 seconds (2.5 minutes)
result = parse_duration("30.5s")      # 30 seconds (truncated)
```

## Complex Examples

### Multi-unit Combinations

```python
from duratypes import parse_duration

# Complex compound formats
result = parse_duration("2h30m45s")   # 9045 seconds
result = parse_duration("1h 30 minutes 45 seconds") # 5445 seconds
result = parse_duration("90m30s")     # 5430 seconds

# ISO 8601 combinations
result = parse_duration("PT2H30M45S") # 9045 seconds
result = parse_duration("P1DT2H30M")  # 95400 seconds (1 day + 2h30m)
```

### Real-world Examples

```python
from duratypes import parse_duration, format_duration

# Configuration timeouts
api_timeout = parse_duration("30s")        # 30 seconds
cache_ttl = parse_duration("1h")           # 3600 seconds
session_timeout = parse_duration("24h")    # 86400 seconds

# Processing durations
video_length = parse_duration("1h23m45s")  # 5025 seconds
download_time = parse_duration("2m30s")    # 150 seconds

# Format for display
print(f"Video length: {format_duration(video_length)}")  # "1h23m45s"
print(f"Download time: {format_duration(download_time)}") # "2m30s"
```

## Performance Considerations

### Direct Adapter Usage

duratypes provides a pre-configured `DurationAdapter` for optimal performance:

```python
from duratypes import DurationAdapter

# Direct validation using the pre-configured adapter
result = DurationAdapter.validate_python("1h30m")  # 5400
```

### Caching

For applications that parse the same duration strings repeatedly, consider caching:

```python
from functools import lru_cache
from duratypes import parse_duration

@lru_cache(maxsize=128)
def cached_parse_duration(duration_str):
    return parse_duration(duration_str)

# Subsequent calls with same input are cached
result1 = cached_parse_duration("1h30m")  # Parsed
result2 = cached_parse_duration("1h30m")  # From cache
```

## Best Practices

### Input Validation

Always handle potential parsing errors:

```python
from duratypes import parse_duration, InvalidFormatError, InvalidTypeError

def safe_parse_duration(value, default=0):
    try:
        return parse_duration(value)
    except (InvalidFormatError, InvalidTypeError) as e:
        print(f"Invalid duration '{value}': {e}")
        return default

# Usage
timeout = safe_parse_duration("5m", default=300)
```

### Type Hints

Use proper type hints for better code clarity:

```python
from typing import Union
from duratypes import parse_duration

def process_timeout(timeout: Union[str, int, float]) -> int:
    """Process timeout value and return seconds."""
    return parse_duration(timeout)
```

### Configuration Files

duratypes works well with configuration files:

```python
import json
from duratypes import parse_duration

# config.json
config_data = {
    "api_timeout": "30s",
    "retry_delay": "5s",
    "max_duration": "1h"
}

# Parse configuration
config = {
    key: parse_duration(value) 
    for key, value in config_data.items()
}
```

## Common Patterns

### Timeout Decorators

```python
import time
from functools import wraps
from duratypes import parse_duration

def timeout(duration):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            timeout_seconds = parse_duration(duration)
            # Implementation would use threading.Timer or similar
            return func(*args, **kwargs)
        return wrapper
    return decorator

@timeout("30s")
def api_call():
    # Function implementation
    pass
```

### Duration Arithmetic

```python
from duratypes import parse_duration, format_duration

# Calculate total duration
task1_duration = parse_duration("1h30m")
task2_duration = parse_duration("45m")
total_duration = task1_duration + task2_duration

print(f"Total time: {format_duration(total_duration)}")  # "2h15m"
```

## Next Steps

- Learn about [Pydantic Integration](pydantic.md)
- Understand [Error Handling](errors.md)
- Check [Performance Tips](performance.md)
- Review the [API Reference](api/core.md)
