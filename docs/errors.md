# Error Handling

duratypes provides comprehensive error handling with a clear exception hierarchy and helpful error messages. This guide covers all the ways duratypes can fail and how to handle these situations gracefully.

## Exception Hierarchy

duratypes uses a custom exception hierarchy that inherits from Python's built-in exceptions:

```python
from duratypes.core import (
    DurationError,        # Base exception
    InvalidFormatError,   # Invalid format strings
    InvalidTypeError,     # Wrong input types
    InvalidValueError,    # Invalid values (None, NaN, etc.)
)
```

### Exception Tree

```
ValueError
└── DurationError (base for all duration errors)
    ├── InvalidFormatError (format parsing errors)
    ├── InvalidValueError (invalid values like None, NaN)
    └── InvalidTypeError (wrong input types)
        └── TypeError (also inherits from TypeError)
```

## Common Error Scenarios

### 1. Invalid Format Errors

**InvalidFormatError** is raised when a string cannot be parsed as a duration:

```python
from duratypes import parse_duration
from duratypes.core import InvalidFormatError

# Invalid format examples
try:
    parse_duration("invalid")
except InvalidFormatError as e:
    print(f"Format error: {e}")
    # Format error: Invalid duration format: 'invalid'. Supported formats: ...

try:
    parse_duration("30")  # Missing unit
except InvalidFormatError as e:
    print(f"Missing unit: {e}")
    # Missing unit: Invalid duration format: '30'. Supported formats: ...

try:
    parse_duration("1x")  # Invalid unit
except InvalidFormatError as e:
    print(f"Invalid unit: {e}")
    # Invalid unit: Invalid duration format: '1x'. Supported formats: ...
```

### 2. Invalid Type Errors

**InvalidTypeError** is raised for unsupported input types:

```python
from duratypes.core import InvalidTypeError

# Wrong type examples
try:
    parse_duration(None)
except InvalidTypeError as e:
    print(f"Type error: {e}")
    # Type error: Duration must be str, int, or float, got NoneType

try:
    parse_duration([1, 2, 3])
except InvalidTypeError as e:
    print(f"List error: {e}")
    # List error: Duration must be str, int, or float, got list
```

### 3. Invalid Value Errors

**InvalidValueError** is raised for invalid values:

```python
from duratypes.core import InvalidValueError
import math

# Invalid value examples
try:
    parse_duration("")  # Empty string
except InvalidValueError as e:
    print(f"Empty string: {e}")
    # Empty string: Duration string cannot be empty

try:
    parse_duration(float('nan'))  # NaN value
except InvalidValueError as e:
    print(f"NaN error: {e}")
    # NaN error: Invalid numeric duration: nan

try:
    parse_duration(None)
except InvalidValueError as e:
    print(f"None error: {e}")
    # None error: Duration cannot be None
```

### 4. Format Function Errors

**format_duration()** has its own validation:

```python
from duratypes import format_duration
from duratypes.core import InvalidTypeError

try:
    format_duration("not_an_int")
except InvalidTypeError as e:
    print(f"Format type error: {e}")
    # Format type error: Seconds must be an integer, got str

try:
    format_duration(30.5)  # Float instead of int
except InvalidTypeError as e:
    print(f"Float error: {e}")
    # Float error: Seconds must be an integer, got float
```

## Pydantic Integration Errors

When using duratypes with Pydantic models, you'll get **ValidationError** from Pydantic:

```python
from pydantic import BaseModel, ValidationError
from duratypes import Duration

class Task(BaseModel):
    name: str
    duration: Duration

# Pydantic validation errors
try:
    Task(name="Test", duration="invalid_format")
except ValidationError as e:
    print("Pydantic validation failed:")
    for error in e.errors():
        print(f"  {error['loc']}: {error['msg']}")
    # Pydantic validation failed:
    #   ('duration',): Invalid duration format: 'invalid_format'. Supported formats: ...

try:
    Task(name="Test", duration=None)
except ValidationError as e:
    print("None value error:")
    for error in e.errors():
        print(f"  {error['loc']}: {error['msg']}")
    # None value error:
    #   ('duration',): Duration cannot be None
```

## Error Handling Best Practices

### 1. Catch Specific Exceptions

Always catch the most specific exception first:

```python
from duratypes import parse_duration
from duratypes.core import InvalidFormatError, InvalidTypeError, InvalidValueError

def safe_parse_duration(value):
    try:
        return parse_duration(value)
    except InvalidFormatError:
        # Handle format errors (bad strings)
        return None
    except InvalidTypeError:
        # Handle type errors (wrong types)
        raise TypeError(f"Expected str, int, or float, got {type(value)}")
    except InvalidValueError:
        # Handle value errors (None, NaN, empty strings)
        return 0  # Default value
```

### 2. Use Base Exception for General Handling

Use **DurationError** to catch all duration-related errors:

```python
from duratypes.core import DurationError

def parse_with_fallback(value, default=0):
    try:
        return parse_duration(value)
    except DurationError as e:
        print(f"Duration parsing failed: {e}")
        return default
```

### 3. Validate Input Before Parsing

Pre-validate input to avoid exceptions:

```python
def validate_and_parse(value):
    # Type validation
    if not isinstance(value, (str, int, float)):
        raise TypeError(f"Expected str, int, or float, got {type(value)}")
    
    # Value validation
    if value is None:
        raise ValueError("Duration cannot be None")
    
    if isinstance(value, str) and not value.strip():
        raise ValueError("Duration string cannot be empty")
    
    if isinstance(value, float) and math.isnan(value):
        raise ValueError("Duration cannot be NaN")
    
    return parse_duration(value)
```

### 4. Graceful Degradation in Applications

Handle errors gracefully in applications:

```python
from duratypes import parse_duration
from duratypes.core import DurationError

def process_user_input(duration_str):
    try:
        seconds = parse_duration(duration_str)
        return {"success": True, "seconds": seconds}
    except DurationError as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Try formats like '30s', '5m', '1h30m', or 'PT1H30M'"
        }

# Usage
result = process_user_input("1h30m")
if result["success"]:
    print(f"Parsed: {result['seconds']} seconds")
else:
    print(f"Error: {result['error']}")
    print(f"Suggestion: {result['suggestion']}")
```

## Debugging Tips

### 1. Enable Logging

duratypes uses Python's logging module for debugging:

```python
import logging
from duratypes import parse_duration

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('duratypes.core')

# This will show debug information
result = parse_duration("1h30m")
```

### 2. Inspect Error Details

Exception objects contain useful information:

```python
from duratypes.core import InvalidFormatError

try:
    parse_duration("invalid")
except InvalidFormatError as e:
    print(f"Exception type: {type(e)}")
    print(f"Exception message: {e}")
    print(f"Exception args: {e.args}")
```

### 3. Test Edge Cases

Always test edge cases in your application:

```python
test_cases = [
    "",           # Empty string
    None,         # None value
    "invalid",    # Invalid format
    "30",         # Missing unit
    float('inf'), # Infinity
    float('nan'), # NaN
    [],           # Wrong type
]

for case in test_cases:
    try:
        result = parse_duration(case)
        print(f"✓ {case!r} -> {result}")
    except Exception as e:
        print(f"✗ {case!r} -> {type(e).__name__}: {e}")
```

## Error Messages

duratypes provides clear, actionable error messages:

- **Format errors**: Include the invalid input and list supported formats
- **Type errors**: Show expected types and actual type received
- **Value errors**: Explain what values are invalid and why

Example error messages:

```
Invalid duration format: 'invalid'. Supported formats: compound ('30s', '5m', '1h30m'), ISO 8601 ('PT30S', 'PT5M', 'PT1H30M'), or numeric (30, 30.5)

Duration must be str, int, or float, got NoneType

Duration string cannot be empty

Invalid numeric duration: nan
```

## Integration with Error Tracking

For production applications, integrate with error tracking services:

```python
import sentry_sdk
from duratypes.core import DurationError

def parse_with_tracking(value):
    try:
        return parse_duration(value)
    except DurationError as e:
        # Log to error tracking service
        sentry_sdk.capture_exception(e)
        # Re-raise or handle gracefully
        raise
```

This comprehensive error handling ensures your application can gracefully handle all duration parsing scenarios while providing clear feedback to users and developers.
