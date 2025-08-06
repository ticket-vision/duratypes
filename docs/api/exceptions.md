# Exceptions API Reference

This page documents the custom exception classes provided by duratypes for error handling.

## Exception Hierarchy

duratypes provides a comprehensive exception hierarchy for different types of errors:

```
DurationError (ValueError)
├── InvalidFormatError
├── InvalidTypeError (also inherits from TypeError)
└── InvalidValueError
```

## Base Exception

### DurationError

```python
from duratypes import DurationError
```

Base exception class for all duration-related errors.

**Inheritance**: `ValueError`

**Description**: Base class for all duration parsing and validation errors. All other duration exceptions inherit from this class.

**Usage**:
```python
from duratypes import parse_duration, DurationError

try:
    result = parse_duration("invalid")
except DurationError as e:
    print(f"Duration error: {e}")
```

## Specific Exceptions

### InvalidFormatError

```python
from duratypes import InvalidFormatError
```

Raised when a duration string has an invalid or unrecognized format.

**Inheritance**: `DurationError` → `ValueError`

**Common Causes**:
- Malformed duration strings
- Unrecognized unit abbreviations
- Invalid ISO 8601 format
- Plain numeric strings without units

**Examples**:
```python
from duratypes import parse_duration, InvalidFormatError

# These will raise InvalidFormatError
try:
    parse_duration("invalid")        # Unrecognized format
except InvalidFormatError as e:
    print(f"Invalid format: {e}")

try:
    parse_duration("30")             # Plain number without unit
except InvalidFormatError as e:
    print(f"Invalid format: {e}")

try:
    parse_duration("1x")             # Invalid unit 'x'
except InvalidFormatError as e:
    print(f"Invalid format: {e}")
```

### InvalidTypeError

```python
from duratypes import InvalidTypeError
```

Raised when an unsupported input type is provided.

**Inheritance**: `DurationError` → `ValueError`, `TypeError`

**Common Causes**:
- Passing unsupported types (lists, dicts, objects, etc.)
- None values (when not expected)

**Examples**:
```python
from duratypes import parse_duration, InvalidTypeError

# These will raise InvalidTypeError
try:
    parse_duration([30])             # List not supported
except InvalidTypeError as e:
    print(f"Invalid type: {e}")

try:
    parse_duration({"seconds": 30})  # Dict not supported
except InvalidTypeError as e:
    print(f"Invalid type: {e}")

try:
    parse_duration(None)             # None not supported
except InvalidTypeError as e:
    print(f"Invalid type: {e}")
```

### InvalidValueError

```python
from duratypes import InvalidValueError
```

Raised when a duration value is invalid (e.g., infinite or NaN values).

**Inheritance**: `DurationError` → `ValueError`

**Common Causes**:
- Infinite float values
- NaN (Not a Number) float values
- Other mathematically invalid values

**Examples**:
```python
import math
from duratypes import parse_duration, InvalidValueError

# These will raise InvalidValueError
try:
    parse_duration(float('inf'))     # Infinite value
except InvalidValueError as e:
    print(f"Invalid value: {e}")

try:
    parse_duration(float('nan'))     # NaN value
except InvalidValueError as e:
    print(f"Invalid value: {e}")
```

## Error Handling Patterns

### Catch All Duration Errors

```python
from duratypes import parse_duration, DurationError

def safe_parse_duration(value, default=0):
    """Safely parse duration with fallback."""
    try:
        return parse_duration(value)
    except DurationError as e:
        print(f"Duration parsing failed: {e}")
        return default

# Usage
timeout = safe_parse_duration("5m", default=300)
```

### Catch Specific Errors

```python
from duratypes import (
    parse_duration, 
    InvalidFormatError, 
    InvalidTypeError, 
    InvalidValueError
)

def parse_with_specific_handling(value):
    """Parse duration with specific error handling."""
    try:
        return parse_duration(value)
    except InvalidFormatError:
        print("The duration format is not recognized")
        return None
    except InvalidTypeError:
        print("The input type is not supported")
        return None
    except InvalidValueError:
        print("The duration value is invalid")
        return None

# Usage
result = parse_with_specific_handling("invalid")
```

### Pydantic Integration Error Handling

```python
from duratypes import Duration
from pydantic import BaseModel, ValidationError

class Config(BaseModel):
    timeout: Duration

def create_config_safely(timeout_value):
    """Create config with error handling."""
    try:
        return Config(timeout=timeout_value)
    except ValidationError as e:
        print(f"Validation error: {e}")
        return None

# Usage
config = create_config_safely("invalid")  # Returns None
```

## Error Messages

duratypes provides descriptive error messages to help identify issues:

### InvalidFormatError Messages

```python
# Examples of error messages
"Invalid duration format: 'invalid'. Expected formats: '30s', '5m', '1h', 'PT30S', or numeric value."
"Plain numeric strings are not supported. Use '30s' instead of '30'."
"Invalid unit 'x' in duration '1x'. Supported units: s, m, h, sec, min, hour, seconds, minutes, hours."
```

### InvalidTypeError Messages

```python
# Examples of error messages
"Invalid input type <class 'list'>. Expected str, int, or float."
"Invalid input type <class 'NoneType'>. Expected str, int, or float."
```

### InvalidValueError Messages

```python
# Examples of error messages
"Invalid duration value: inf. Duration must be finite."
"Invalid duration value: nan. Duration must be a valid number."
```

## Best Practices

### Use Specific Exception Handling

```python
from duratypes import parse_duration, InvalidFormatError, InvalidTypeError

def robust_duration_parser(value):
    """Robust duration parser with specific error handling."""
    try:
        return parse_duration(value)
    except InvalidFormatError:
        # Handle format errors - maybe try alternative parsing
        return handle_format_error(value)
    except InvalidTypeError:
        # Handle type errors - maybe convert type first
        return handle_type_error(value)
```

### Provide User-Friendly Messages

```python
from duratypes import parse_duration, DurationError

def user_friendly_parse(value):
    """Parse duration with user-friendly error messages."""
    try:
        return parse_duration(value)
    except DurationError as e:
        # Convert technical error to user-friendly message
        user_message = f"Invalid duration '{value}'. Please use formats like '30s', '5m', or '1h'."
        raise ValueError(user_message) from e
```

### Logging Errors

```python
import logging
from duratypes import parse_duration, DurationError

logger = logging.getLogger(__name__)

def logged_parse_duration(value):
    """Parse duration with error logging."""
    try:
        return parse_duration(value)
    except DurationError as e:
        logger.error(f"Failed to parse duration '{value}': {e}")
        raise
```

### Validation in Configuration

```python
from duratypes import Duration, InvalidFormatError
from pydantic import BaseModel, field_validator

class ServerConfig(BaseModel):
    timeout: Duration
    
    @field_validator('timeout')
    @classmethod
    def validate_timeout_range(cls, v):
        if v < 1:
            raise ValueError('Timeout must be at least 1 second')
        if v > 86400:  # 24 hours
            raise ValueError('Timeout cannot exceed 24 hours')
        return v

# Usage with error handling
def create_server_config(timeout_value):
    try:
        return ServerConfig(timeout=timeout_value)
    except ValidationError as e:
        # Handle both duration parsing errors and custom validation errors
        print(f"Configuration error: {e}")
        return None
```

## Exception Attributes

All duratypes exceptions include standard exception attributes:

```python
from duratypes import parse_duration, InvalidFormatError

try:
    parse_duration("invalid")
except InvalidFormatError as e:
    print(f"Exception type: {type(e).__name__}")
    print(f"Exception message: {str(e)}")
    print(f"Exception args: {e.args}")
```

## Thread Safety

All exception classes are thread-safe and can be used safely in multi-threaded applications.

## See Also

- [Core Functions](core.md) - Main parsing and formatting functions
- [Types](types.md) - Pydantic annotated types
- [Error Handling Guide](../errors.md) - Comprehensive error handling guide
