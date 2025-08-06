# Types API Reference

This page documents the types and adapters provided by duratypes for Pydantic integration.

## Annotated Types

duratypes provides several annotated types for use with Pydantic models. All types are functionally equivalent and convert input to integer seconds internally.

### Duration

```python
from duratypes import Duration
```

Generic duration type that accepts various input formats and converts them to seconds.

**Type**: `Annotated[int, BeforeValidator(parse_duration)]`

**Usage**:
```python
from duratypes import Duration
from pydantic import BaseModel

class Config(BaseModel):
    timeout: Duration = "5m"  # Default: 300 seconds

config = Config(timeout="2h")  # 7200 seconds
```

**Supported Input Formats**:
- Compound: `"30s"`, `"5m"`, `"1h30m45s"`
- ISO 8601: `"PT30S"`, `"PT5M"`, `"PT1H30M45S"`
- Numeric: `30`, `30.5` (integers/floats)

### Seconds

```python
from duratypes import Seconds
```

Duration type specifically for seconds. Functionally identical to `Duration` but provides semantic clarity.

**Type**: `Annotated[int, BeforeValidator(parse_duration)]`

**Usage**:
```python
from duratypes import Seconds
from pydantic import BaseModel

class Config(BaseModel):
    retry_delay: Seconds = "30s"  # Default: 30 seconds

config = Config(retry_delay=45)  # 45 seconds
```

### Minutes

```python
from duratypes import Minutes
```

Duration type specifically for minutes. Functionally identical to `Duration` but provides semantic clarity.

**Type**: `Annotated[int, BeforeValidator(parse_duration)]`

**Usage**:
```python
from duratypes import Minutes
from pydantic import BaseModel

class Config(BaseModel):
    session_timeout: Minutes = "30m"  # Default: 1800 seconds

config = Config(session_timeout="1h")  # 3600 seconds
```

### Hours

```python
from duratypes import Hours
```

Duration type specifically for hours. Functionally identical to `Duration` but provides semantic clarity.

**Type**: `Annotated[int, BeforeValidator(parse_duration)]`

**Usage**:
```python
from duratypes import Hours
from pydantic import BaseModel

class Config(BaseModel):
    max_duration: Hours = "2h"  # Default: 7200 seconds

config = Config(max_duration="90m")  # 5400 seconds
```

## Type Equivalence

All duration types are aliases for the same underlying implementation:

```python
from duratypes import Duration, Seconds, Minutes, Hours
from pydantic import BaseModel

class Config(BaseModel):
    timeout1: Duration = "5m"    # 300 seconds
    timeout2: Seconds = "5m"     # 300 seconds  
    timeout3: Minutes = "5m"     # 300 seconds
    timeout4: Hours = "5m"       # 300 seconds

config = Config()
assert config.timeout1 == config.timeout2 == config.timeout3 == config.timeout4
```

The different type names are provided for semantic clarity in your models.

## DurationAdapter

```python
from duratypes import DurationAdapter
```

Pre-configured TypeAdapter for efficient duration validation and conversion.

### Usage

The `DurationAdapter` is a pre-configured `TypeAdapter[Duration]` instance that can be used directly:

```python
from duratypes import DurationAdapter

# Direct usage
result = DurationAdapter.validate_python("1h30m")  # 5400
result = DurationAdapter.validate_python(300)      # 300
result = DurationAdapter.validate_python("PT1H")   # 3600
```

### Methods

#### `validate_python(value: str | int | float) -> int`

Validates and converts a duration value to seconds.

**Parameters**:
- `value`: Duration input (string, integer, or float)

**Returns**: Duration in seconds as integer

**Raises**:
- `InvalidFormatError`: For malformed duration strings
- `InvalidTypeError`: For unsupported input types
- `InvalidValueError`: For invalid duration values

**Usage**:
```python
from duratypes import DurationAdapter

result = DurationAdapter.validate_python("1h30m")  # 5400
result = DurationAdapter.validate_python(300)      # 300
result = DurationAdapter.validate_python("PT1H")   # 3600
```

### Performance Benefits

The `DurationAdapter` is a module-level instance that provides:

- **Memory Efficiency**: Single TypeAdapter instance shared across the module
- **Performance**: Avoids repeated TypeAdapter creation overhead
- **Consistency**: All validations use the same adapter configuration

### Thread Safety

The DurationAdapter is thread-safe and can be used safely in multi-threaded applications.

## Performance Considerations

### Direct Validation

For applications that need to bypass Pydantic model validation overhead, you can use the adapter directly:

```python
from duratypes import DurationAdapter

# Direct validation (faster than Pydantic model validation)
durations = ["30s", "1m", "2h", "45m"]
seconds = [DurationAdapter.validate_python(d) for d in durations]
```

## Type Hints

All types are properly typed for use with type checkers:

```python
from typing import Union
from duratypes import Duration, Seconds, Minutes, Hours

def process_timeout(timeout: Duration) -> int:
    """Process timeout value."""
    return timeout  # Already converted to int

def create_config(
    request_timeout: Seconds,
    session_timeout: Minutes,
    max_duration: Hours
) -> dict[str, int]:
    """Create configuration dictionary."""
    return {
        "request_timeout": request_timeout,
        "session_timeout": session_timeout,
        "max_duration": max_duration
    }
```

## Examples

### Basic Usage

```python
from duratypes import Duration, Seconds, Minutes, Hours
from pydantic import BaseModel

class ServerConfig(BaseModel):
    request_timeout: Seconds = "30s"
    session_timeout: Minutes = "30m"
    max_duration: Hours = "24h"
    cache_ttl: Duration = "1h"

# Create with defaults
config = ServerConfig()

# Create with custom values
config = ServerConfig(
    request_timeout=45,
    session_timeout="1h",
    max_duration="12h",
    cache_ttl="30m"
)
```

### Advanced Usage

```python
from typing import Optional
from duratypes import Duration
from pydantic import BaseModel, Field

class AdvancedConfig(BaseModel):
    timeout: Duration = Field(
        default="30s",
        description="Request timeout",
        examples=["30s", "1m", "PT30S"]
    )
    optional_timeout: Optional[Duration] = None
    
# Usage
config = AdvancedConfig(
    timeout="45s",
    optional_timeout="2m"
)
```
