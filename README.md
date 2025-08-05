# 📦 duratypes

Typed duration utilities for Python, designed for speed, clarity, and seamless use with **Pydantic v2**.

## Features

- 🚀 **Fast & Lightweight**: Zero external dependencies except Pydantic
- 🎯 **Multiple Input Formats**: Compound (`"1h30m"`), ISO 8601 (`"PT1H30M"`), and numeric (`90`)
- 🔧 **Pydantic Integration**: Seamless validation with `Annotated` types
- 📝 **Type Safety**: Full type hints and comprehensive error messages
- ⚡ **Performance**: Singleton `TypeAdapter` for maximum reuse
- 🛡️ **Robust**: Handles edge cases, negative durations, and validation

---

## Installation

```bash
pip install duratypes
```

For development:
```bash
# Clone the repository
git clone https://github.com/dillon-barendt/duratypes.git
cd duratypes

# Install with development dependencies using uv
uv sync
source .venv/bin/activate

# Or install in editable mode
uv pip install -e .
```

---

## Quick Start

```python
from duratypes import Duration, parse_duration, format_duration
from pydantic import BaseModel

# Direct parsing
seconds = parse_duration("1h30m")  # Returns: 5400
formatted = format_duration(5400)  # Returns: "1h30m"

# Pydantic integration
class Config(BaseModel):
    timeout: Duration = "2.5m"  # Converts to 150 seconds
    retry_delay: Duration = 30   # Direct integer input
    
config = Config()
print(config.timeout)      # 150
print(config.retry_delay)  # 30
```

---

## Supported Input Formats

### 1. Compound Format
Human-readable duration strings with units:

```python
parse_duration("30s")        # 30 seconds
parse_duration("5m")         # 300 seconds  
parse_duration("2h")         # 7200 seconds
parse_duration("1h30m45s")   # 5445 seconds
parse_duration("90 minutes") # 5400 seconds
parse_duration("-1h30m")     # -5400 seconds (negative)
```

**Supported units:**
- **Seconds**: `s`, `sec`, `second`, `seconds`
- **Minutes**: `m`, `min`, `minute`, `minutes`  
- **Hours**: `h`, `hour`, `hours`

### 2. ISO 8601 Duration Format
Standard ISO 8601 duration strings:

```python
parse_duration("PT30S")      # 30 seconds
parse_duration("PT5M")       # 300 seconds
parse_duration("PT2H")       # 7200 seconds
parse_duration("PT1H30M45S") # 5445 seconds
parse_duration("P1DT2H")     # 93600 seconds (1 day + 2 hours)
parse_duration("PT-90S")     # -90 seconds (negative component)
parse_duration("-PT1H30M")   # -5400 seconds (negative duration)
```

### 3. Numeric Input
Direct numeric values (integers or floats):

```python
parse_duration(30)     # 30 seconds
parse_duration(30.5)   # 30 seconds (truncated to int)
parse_duration(-60)    # -60 seconds
```

---

## API Reference

### Core Functions

#### `parse_duration(v: Union[str, int, float]) -> int`
Parse various duration formats into seconds.

**Parameters:**
- `v`: Duration input (string, integer, or float)

**Returns:**
- `int`: Duration in seconds

**Raises:**
- `ValueError`: Invalid format or unsupported input
- `TypeError`: Unsupported input type

**Examples:**
```python
parse_duration("1h30m")    # 5400
parse_duration("PT1H30M")  # 5400  
parse_duration(3600)       # 3600
```

#### `format_duration(seconds: int) -> str`
Format durations into a human-readable string.

**Parameters:**
- `seconds`: Duration in seconds (can be negative)

**Returns:**
- `str`: Formatted duration string

**Examples:**
```python
format_duration(5400)   # "1h30m"
format_duration(90)     # "1m30s"
format_duration(-3600)  # "-1h"
```

### Pydantic Types

All types are aliases of `Annotated[int, BeforeValidator(parse_duration)]`:

- **`Duration`**: General duration type
- **`Seconds`**: Alias for Duration  
- **`Minutes`**: Alias for Duration
- **`Hours`**: Alias for Duration

#### `DurationAdapter: TypeAdapter[Duration]`
Singleton TypeAdapter for direct validation without Pydantic models.

```python
from duratypes import DurationAdapter

result = DurationAdapter.validate_python("1h30m")  # 5400
```

---

## Pydantic Integration Examples

### Basic Usage
```python
from pydantic import BaseModel
from duratypes import Duration, Seconds, Minutes, Hours

class TaskConfig(BaseModel):
    timeout: Duration = "5m"
    retry_delay: Seconds = "30s"
    cache_ttl: Minutes = "15m"
    session_duration: Hours = "2h"

config = TaskConfig()
print(config.timeout)  # 300
```

### Advanced Validation
```python
from pydantic import BaseModel, Field
from duratypes import Duration

class APIConfig(BaseModel):
    request_timeout: Duration = Field(
        default="30s",
        description="HTTP request timeout"
    )
    rate_limit_window: Duration = Field(
        default="1h", 
        ge=60,  # Minimum 1 minute
        description="Rate limiting time window"
    )

# Validation works seamlessly
config = APIConfig(
    request_timeout="45s",
    rate_limit_window="2h30m"
)
```
### JSON Schema Integration
```python
from pydantic import BaseModel
from duratypes import Duration

class Config(BaseModel):
    timeout: Duration

# Generate JSON schema
schema = Config.model_json_schema()
print(schema["properties"]["timeout"])
# Shows integer type with validation
```

---

## Error Handling



duratypes provides clear, specific error messages:

```python
from duratypes import parse_duration

# Invalid format
try:
    parse_duration("invalid")
except ValueError as e:
    print(e)  # Invalid duration format: 'invalid'. Supported formats: ...

# Empty string
try:
    parse_duration("")
except ValueError as e:
    print(e)  # Duration string cannot be empty

# Wrong type
try:
    parse_duration(None)
except ValueError as e:
    print(e)  # Duration cannot be None
```

---

## Performance

duratypes is optimized for performance:

- **Singleton Pattern**: `DurationAdapter` reuses the same TypeAdapter instance
- **Compiled Regex**: Pre-compiled patterns for fast parsing
- **Integer Conversion**: All durations stored as integers for efficiency
- **Minimal Dependencies**: Only depends on Pydantic

---

## Development

### Requirements
- Python ≥3.12
- Pydantic ≥2.5

### Setup Development Environment
```bash
# Clone and setup
git clone https://github.com/dillon-barendt/duratypes.git
cd duratypes

# Install with uv (recommended)
uv sync
source .venv/bin/activate

# Or with pip
pip install -e ".[dev]"
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=duratypes --cov-report=html

# Run specific test
python -m pytest tests/test_core.py::test_parse_and_adapter -v
```

### Code Quality
```bash
# Linting
ruff check src/ tests/

# Formatting  
ruff format src/ tests/

# Type checking
mypy src/
```

---

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Contribution Steps
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`python -m pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## License

This project is licensed under the MIT - License - see the [LICENSE](LICENSE) file for details.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.
