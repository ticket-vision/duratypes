# Pydantic Integration

duratypes provides seamless integration with Pydantic v2 through annotated types and custom validation.

## Overview

duratypes offers several annotated types that work directly with Pydantic models:

- `Duration` - Generic duration type (alias for all duration types)
- `Seconds` - Duration specifically in seconds
- `Minutes` - Duration specifically in minutes  
- `Hours` - Duration specifically in hours

All types are functionally equivalent and convert input to integer seconds internally.

## Basic Usage

### Simple Model Definition

```python
from duratypes import Duration, Seconds, Minutes, Hours
from pydantic import BaseModel

class TaskConfig(BaseModel):
    timeout: Duration = "5m"           # Default: 300 seconds
    retry_delay: Seconds = "30s"       # Default: 30 seconds
    max_duration: Hours = "2h"         # Default: 7200 seconds
    poll_interval: Minutes = "1m"      # Default: 60 seconds

# Create with defaults
config = TaskConfig()
print(config.timeout)      # 300
print(config.retry_delay)  # 30
print(config.max_duration) # 7200
print(config.poll_interval) # 60
```

### Model Instantiation

```python
from duratypes import Duration
from pydantic import BaseModel

class ServerConfig(BaseModel):
    request_timeout: Duration
    session_timeout: Duration
    cleanup_interval: Duration

# Multiple input formats supported
config = ServerConfig(
    request_timeout="30s",           # Compound format
    session_timeout="PT1H",          # ISO 8601 format
    cleanup_interval=3600            # Numeric format
)

print(config.request_timeout)   # 30
print(config.session_timeout)   # 3600
print(config.cleanup_interval)  # 3600
```

## Advanced Features

### Optional Fields

```python
from typing import Optional
from duratypes import Duration
from pydantic import BaseModel

class OptionalConfig(BaseModel):
    required_timeout: Duration
    optional_timeout: Optional[Duration] = None
    default_timeout: Duration = "1m"

# Valid instantiations
config1 = OptionalConfig(required_timeout="30s")
config2 = OptionalConfig(
    required_timeout="30s",
    optional_timeout="2m"
)
```

### Field Validation

```python
from duratypes import Duration
from pydantic import BaseModel, Field, field_validator

class ValidatedConfig(BaseModel):
    timeout: Duration = Field(description="Request timeout in seconds")
    
    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v):
        if v < 1:
            raise ValueError('Timeout must be at least 1 second')
        if v > 3600:
            raise ValueError('Timeout cannot exceed 1 hour')
        return v

# Valid
config = ValidatedConfig(timeout="30s")  # 30 seconds

# Invalid - will raise ValidationError
try:
    config = ValidatedConfig(timeout="2h")  # 7200 seconds > 3600
except ValueError as e:
    print(f"Validation error: {e}")
```

### Nested Models

```python
from duratypes import Duration
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    connection_timeout: Duration = "30s"
    query_timeout: Duration = "5m"
    pool_timeout: Duration = "10s"

class CacheConfig(BaseModel):
    ttl: Duration = "1h"
    cleanup_interval: Duration = "5m"

class ApplicationConfig(BaseModel):
    database: DatabaseConfig = DatabaseConfig()
    cache: CacheConfig = CacheConfig()
    global_timeout: Duration = "30s"

# Create with nested configuration
config = ApplicationConfig(
    database=DatabaseConfig(
        connection_timeout="45s",
        query_timeout="10m"
    ),
    cache=CacheConfig(ttl="2h"),
    global_timeout="1m"
)

print(config.database.connection_timeout)  # 45
print(config.cache.ttl)                   # 7200
print(config.global_timeout)              # 60
```

## JSON Serialization

### Model Serialization

```python
from duratypes import Duration
from pydantic import BaseModel
import json

class Config(BaseModel):
    timeout: Duration = "5m"
    retry_delay: Duration = "30s"

config = Config()

# Serialize to dict
config_dict = config.model_dump()
print(config_dict)  # {'timeout': 300, 'retry_delay': 30}

# Serialize to JSON
config_json = config.model_dump_json()
print(config_json)  # '{"timeout":300,"retry_delay":30}'
```

### Deserialization from JSON

```python
from duratypes import Duration
from pydantic import BaseModel
import json

class Config(BaseModel):
    timeout: Duration
    retry_delay: Duration

# From JSON string with duration strings
json_data = '{"timeout": "5m", "retry_delay": "30s"}'
config = Config.model_validate_json(json_data)
print(config.timeout)      # 300
print(config.retry_delay)  # 30

# From JSON string with numeric values
json_data = '{"timeout": 300, "retry_delay": 30}'
config = Config.model_validate_json(json_data)
print(config.timeout)      # 300
print(config.retry_delay)  # 30
```

## Configuration Files

### YAML Configuration

```python
from duratypes import Duration
from pydantic import BaseModel
import yaml

class ServerConfig(BaseModel):
    request_timeout: Duration
    session_timeout: Duration
    cleanup_interval: Duration

# config.yaml content:
yaml_content = """
request_timeout: "30s"
session_timeout: "1h"
cleanup_interval: "5m"
"""

# Load and validate
config_data = yaml.safe_load(yaml_content)
config = ServerConfig(**config_data)

print(config.request_timeout)   # 30
print(config.session_timeout)   # 3600
print(config.cleanup_interval)  # 300
```

### Environment Variables

```python
import os
from duratypes import Duration
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_timeout: Duration = "30s"
    cache_ttl: Duration = "1h"
    retry_delay: Duration = "5s"
    
    class Config:
        env_prefix = "APP_"

# Set environment variables
os.environ["APP_API_TIMEOUT"] = "45s"
os.environ["APP_CACHE_TTL"] = "2h"

# Load settings
settings = Settings()
print(settings.api_timeout)  # 45
print(settings.cache_ttl)    # 7200
print(settings.retry_delay)  # 5 (default)
```

## Error Handling

### Validation Errors

```python
from duratypes import Duration
from pydantic import BaseModel, ValidationError

class Config(BaseModel):
    timeout: Duration

# Invalid format
try:
    config = Config(timeout="invalid")
except ValidationError as e:
    print(f"Validation error: {e}")

# Invalid type
try:
    config = Config(timeout=[])
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Custom Error Messages

```python
from duratypes import Duration
from pydantic import BaseModel, Field, field_validator

class Config(BaseModel):
    timeout: Duration = Field(description="Timeout duration")
    
    @field_validator('timeout')
    @classmethod
    def validate_timeout_range(cls, v):
        if v < 1:
            raise ValueError('Timeout must be positive')
        if v > 86400:  # 24 hours
            raise ValueError('Timeout cannot exceed 24 hours')
        return v

try:
    config = Config(timeout="25h")
except ValidationError as e:
    print(f"Error: {e}")
```

## Performance Optimization

### Direct Adapter Usage

duratypes provides a pre-configured `DurationAdapter` for optimal performance:

```python
from duratypes import DurationAdapter

# Direct validation (bypasses Pydantic overhead)
result = DurationAdapter.validate_python("1h30m")  # 5400
```

### Batch Processing

For processing many duration values:

```python
from duratypes import DurationAdapter
from pydantic import BaseModel

class BatchConfig(BaseModel):
    timeouts: list[int]  # Pre-converted to seconds

# Convert durations in batch
duration_strings = ["30s", "1m", "2h", "45m"]
timeouts = [DurationAdapter.validate_python(d) for d in duration_strings]

config = BatchConfig(timeouts=timeouts)
```

## Type Aliases

All duration types are aliases for the same underlying implementation:

```python
from duratypes import Duration, Seconds, Minutes, Hours
from pydantic import BaseModel

class Config(BaseModel):
    # These are all functionally equivalent
    timeout1: Duration = "5m"    # 300 seconds
    timeout2: Seconds = "5m"     # 300 seconds  
    timeout3: Minutes = "5m"     # 300 seconds
    timeout4: Hours = "5m"       # 300 seconds

config = Config()
# All fields contain the same value: 300
assert config.timeout1 == config.timeout2 == config.timeout3 == config.timeout4
```

The different type names are provided for semantic clarity in your models.

## Best Practices

### Use Semantic Types

Choose type names that match your domain:

```python
from duratypes import Duration, Seconds, Minutes, Hours
from pydantic import BaseModel

class WebServerConfig(BaseModel):
    request_timeout: Seconds = "30s"      # Short durations
    session_timeout: Minutes = "30m"      # Medium durations  
    log_rotation: Hours = "24h"           # Long durations
    cache_ttl: Duration = "1h"            # Generic duration

class TaskConfig(BaseModel):
    execution_timeout: Duration = "5m"    # Generic is fine
    retry_delay: Seconds = "1s"           # Emphasize precision
```

### Provide Sensible Defaults

```python
from duratypes import Duration
from pydantic import BaseModel

class ServiceConfig(BaseModel):
    # Provide reasonable defaults for production use
    connection_timeout: Duration = "30s"
    read_timeout: Duration = "60s"
    write_timeout: Duration = "60s"
    keepalive_timeout: Duration = "5s"
```

### Document Duration Fields

```python
from duratypes import Duration
from pydantic import BaseModel, Field

class Config(BaseModel):
    timeout: Duration = Field(
        default="30s",
        description="Request timeout duration",
        examples=["30s", "1m", "PT30S"]
    )
```

## Next Steps

- Review [Error Handling](errors.md) for comprehensive error management
- Check [Performance](performance.md) for optimization tips
- See [API Reference](api/core.md) for complete function documentation
