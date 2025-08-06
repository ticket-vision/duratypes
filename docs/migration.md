# Migration Guide

This guide helps you migrate from other duration parsing libraries to duratypes. We cover the most common libraries and provide side-by-side examples to make the transition smooth.

## Why Migrate to duratypes?

- **Pydantic v2 Integration**: Native support for Pydantic models
- **Type Safety**: Comprehensive type hints and validation
- **Performance**: Optimized parsing with minimal overhead
- **Consistency**: Predictable behavior across all input formats
- **Zero Dependencies**: Only requires Pydantic (no heavy dependencies)

## From pytimeparse

[pytimeparse](https://github.com/wroberts/pytimeparse) is a popular duration parsing library.

### Basic Migration

**Before (pytimeparse):**
```python
from pytimeparse import parse

# Returns seconds as int or None
seconds = parse('1h 30m')  # 5400
seconds = parse('invalid')  # None
```

**After (duratypes):**
```python
from duratypes import parse_duration

# Returns seconds as int, raises exception on error
seconds = parse_duration('1h30m')  # 5400
# parse_duration('invalid')  # Raises InvalidFormatError
```

### Error Handling Migration

**Before (pytimeparse):**
```python
from pytimeparse import parse

def safe_parse(duration_str, default=0):
    result = parse(duration_str)
    return result if result is not None else default
```

**After (duratypes):**
```python
from duratypes import parse_duration
from duratypes.core import DurationError

def safe_parse(duration_str, default=0):
    try:
        return parse_duration(duration_str)
    except DurationError:
        return default
```

### Format Differences

| Input | pytimeparse | duratypes | Notes |
|-------|-------------|-----------|-------|
| `"1h 30m"` | ✅ 5400 | ✅ 5400 | Spaces handled |
| `"1:30:00"` | ✅ 5400 | ❌ Error | Time format not supported |
| `"90m"` | ✅ 5400 | ✅ 5400 | Both support |
| `"1.5h"` | ✅ 5400 | ✅ 5400 | Fractional hours |
| `"PT1H30M"` | ❌ None | ✅ 5400 | ISO 8601 support |

### Migration Checklist

- [ ] Replace `from pytimeparse import parse` with `from duratypes import parse_duration`
- [ ] Update error handling from `None` checks to exception handling
- [ ] Test time format inputs (`"1:30:00"`) - not supported in duratypes
- [ ] Consider using Pydantic integration for model validation

## From dateutil

[dateutil](https://dateutil.readthedocs.io/) provides comprehensive date/time parsing.

### Basic Migration

**Before (dateutil):**
```python
from dateutil.parser import parse
from datetime import datetime

# Parse relative time (complex)
base = datetime.now()
result = parse("1 hour 30 minutes", default=base)
duration = (result - base).total_seconds()  # 5400.0
```

**After (duratypes):**
```python
from duratypes import parse_duration

# Direct duration parsing (simple)
duration = parse_duration("1h30m")  # 5400
```

### ISO 8601 Duration Migration

**Before (dateutil):**
```python
# dateutil doesn't directly support ISO 8601 durations
# You'd need additional libraries like isodate
```

**After (duratypes):**
```python
from duratypes import parse_duration

duration = parse_duration("PT1H30M")  # 5400
```

### Migration Benefits

- **Simpler API**: Direct duration parsing without datetime objects
- **Better Performance**: No datetime object creation overhead
- **ISO 8601 Support**: Built-in support for standard duration format
- **Type Safety**: Clear integer return type

## From pendulum

[Pendulum](https://pendulum.eustace.io/) is a modern datetime library.

### Basic Migration

**Before (pendulum):**
```python
import pendulum

# Create duration object
duration = pendulum.duration(hours=1, minutes=30)
seconds = duration.total_seconds()  # 5400.0

# Parse from string (limited support)
# pendulum doesn't have built-in duration string parsing
```

**After (duratypes):**
```python
from duratypes import parse_duration

# Direct string parsing
seconds = parse_duration("1h30m")  # 5400
```

### Duration Object Migration

**Before (pendulum):**
```python
import pendulum

duration = pendulum.duration(hours=2, minutes=30, seconds=45)
total_seconds = duration.total_seconds()  # 9045.0

# Format back to string
formatted = str(duration)  # "2 hours 30 minutes 45 seconds"
```

**After (duratypes):**
```python
from duratypes import parse_duration, format_duration

# Parse and format
seconds = parse_duration("2h30m45s")  # 9045
formatted = format_duration(seconds)   # "2h30m45s"
```

## From Custom Parsers

If you have custom duration parsing code, here's how to migrate:

### Simple Regex Parser Migration

**Before (custom):**
```python
import re

def parse_simple_duration(duration_str):
    pattern = r'(\d+)([hms])'
    matches = re.findall(pattern, duration_str.lower())
    
    total = 0
    for value, unit in matches:
        value = int(value)
        if unit == 'h':
            total += value * 3600
        elif unit == 'm':
            total += value * 60
        elif unit == 's':
            total += value
    
    return total
```

**After (duratypes):**
```python
from duratypes import parse_duration

# Much simpler!
def parse_simple_duration(duration_str):
    return parse_duration(duration_str)
```

### Complex Parser Migration

**Before (custom):**
```python
def parse_complex_duration(duration_str):
    # Handle multiple formats
    if ':' in duration_str:
        # Handle HH:MM:SS format
        parts = duration_str.split(':')
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif 'PT' in duration_str.upper():
        # Handle ISO 8601 (partial implementation)
        # ... complex regex parsing ...
        pass
    else:
        # Handle compound format
        # ... more complex parsing ...
        pass
```

**After (duratypes):**
```python
from duratypes import parse_duration

def parse_complex_duration(duration_str):
    # duratypes handles multiple formats automatically
    return parse_duration(duration_str)
```

## Pydantic Integration Migration

### From Manual Validation

**Before (manual Pydantic validators):**
```python
from pydantic import BaseModel, validator
from pytimeparse import parse

class Task(BaseModel):
    name: str
    duration_str: str
    
    @validator('duration_str')
    def validate_duration(cls, v):
        result = parse(v)
        if result is None:
            raise ValueError('Invalid duration format')
        return v
    
    @property
    def duration_seconds(self):
        return parse(self.duration_str)
```

**After (duratypes):**
```python
from pydantic import BaseModel
from duratypes import Duration

class Task(BaseModel):
    name: str
    duration: Duration  # Automatic validation and conversion
    
    # No custom validators needed!
    # duration is already in seconds as an integer
```

## Performance Migration

### Caching Migration

**Before (with caching):**
```python
from functools import lru_cache
from pytimeparse import parse

@lru_cache(maxsize=128)
def cached_parse(duration_str):
    return parse(duration_str)
```

**After (duratypes with caching):**
```python
from functools import lru_cache
from duratypes import parse_duration

@lru_cache(maxsize=128)
def cached_parse(duration_str):
    return parse_duration(duration_str)
```

## Testing Migration

### Test Updates

**Before:**
```python
def test_duration_parsing():
    assert parse('1h 30m') == 5400
    assert parse('invalid') is None
```

**After:**
```python
from duratypes.core import InvalidFormatError

def test_duration_parsing():
    assert parse_duration('1h30m') == 5400
    
    with pytest.raises(InvalidFormatError):
        parse_duration('invalid')
```

## Common Migration Issues

### 1. Time Format Support

**Issue**: `"1:30:00"` format not supported in duratypes

**Solution**: Convert to compound format
```python
def convert_time_format(time_str):
    """Convert HH:MM:SS to compound format"""
    if ':' in time_str:
        parts = time_str.split(':')
        hours, minutes, seconds = map(int, parts)
        return f"{hours}h{minutes}m{seconds}s"
    return time_str

# Usage
duration_str = convert_time_format("1:30:00")  # "1h30m0s"
seconds = parse_duration(duration_str)
```

### 2. None Return Values

**Issue**: Libraries returning `None` vs exceptions

**Solution**: Wrap in try-catch or use validation
```python
def safe_migrate(old_parse_func, new_parse_func, duration_str):
    try:
        return new_parse_func(duration_str)
    except Exception:
        # Fallback to old behavior
        return old_parse_func(duration_str)
```

### 3. Float vs Integer Seconds

**Issue**: Some libraries return float seconds

**Solution**: duratypes returns integers (truncated)
```python
# If you need float precision, handle before parsing
def parse_with_precision(duration_str):
    if isinstance(duration_str, (int, float)):
        return float(duration_str)  # Keep precision
    return float(parse_duration(duration_str))  # Convert to float
```

## Migration Checklist

### Pre-Migration
- [ ] Identify all duration parsing code in your project
- [ ] Document current input formats used
- [ ] List any custom validation logic
- [ ] Note performance requirements

### During Migration
- [ ] Update imports to use duratypes
- [ ] Replace parsing calls with `parse_duration()`
- [ ] Update error handling to use exceptions
- [ ] Convert Pydantic models to use `Duration` type
- [ ] Update tests to expect exceptions instead of `None`

### Post-Migration
- [ ] Run comprehensive tests
- [ ] Benchmark performance improvements
- [ ] Update documentation
- [ ] Train team on new API

## Getting Help

If you encounter issues during migration:

1. **Check the [FAQ](faq.md)** for common questions
2. **Review [Error Handling](errors.md)** for exception patterns
3. **Open an issue** on [GitHub](https://github.com/dillon-barendt/duratypes/issues) with:
   - Your current library and version
   - Example input/output that's not working
   - Expected behavior vs actual behavior

We're here to help make your migration smooth and successful!
