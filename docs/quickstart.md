# Quick Start

Get up and running with duratypes in minutes.

## Installation

```bash
pip install duratypes
```

## Basic Usage

### Direct Function Usage

```python
from duratypes import parse_duration, format_duration

# Parse different duration formats
seconds = parse_duration("1h30m")     # 5400
seconds = parse_duration("PT2H30M")   # 9000 (ISO 8601)
seconds = parse_duration(300)         # 300 (numeric)

# Format seconds back to human-readable
formatted = format_duration(5400)     # "1h30m"
formatted = format_duration(90)       # "1m30s"
```

### Pydantic Integration

```python
from duratypes import Duration, Seconds, Minutes, Hours
from pydantic import BaseModel

class TaskConfig(BaseModel):
    timeout: Duration = "5m"           # 300 seconds
    retry_delay: Seconds = "30s"       # 30 seconds
    max_duration: Hours = "2h"         # 7200 seconds

# Create instance with string values
config = TaskConfig(
    timeout="10m",
    retry_delay=45,
    max_duration="1.5h"
)

print(config.timeout)      # 600
print(config.retry_delay)  # 45
print(config.max_duration) # 5400
```

## Supported Formats

### Compound Format
Human-readable with units:
```python
parse_duration("30s")        # 30 seconds
parse_duration("5m")         # 300 seconds
parse_duration("2h")         # 7200 seconds
parse_duration("1h30m45s")   # 5445 seconds
```

### ISO 8601 Format
Standard duration format:
```python
parse_duration("PT30S")      # 30 seconds
parse_duration("PT5M")       # 300 seconds
parse_duration("PT1H30M")    # 5400 seconds
```

### Numeric Format
Direct integer/float values:
```python
parse_duration(30)     # 30 seconds
parse_duration(30.5)   # 30 seconds (truncated)
```

## Error Handling

```python
from duratypes import parse_duration, InvalidFormatError

try:
    result = parse_duration("invalid")
except InvalidFormatError as e:
    print(f"Invalid format: {e}")
```

## Next Steps

- Read the [Usage Guide](usage.md) for detailed examples
- Learn about [Pydantic Integration](pydantic.md)
- Check the [API Reference](api/core.md) for complete documentation
