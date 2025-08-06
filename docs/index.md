# DuraTypes

**Typed duration utilities for Python and Pydantic**

duratypes is a Python package that provides fast, type-safe duration parsing and formatting with seamless Pydantic v2 integration. Convert intuitive duration formats like `"30s"`, `"5m"`, `"1.5h"` to integer seconds internally while maintaining strong typing support.

## Key Features

- **Multiple Input Formats**: Support for compound (`"1h30m"`), ISO 8601 (`"PT1H30M"`), and numeric formats
- **Pydantic Integration**: Seamless integration with Pydantic v2 models using annotated types
- **Type Safety**: Comprehensive type hints and validation
- **High Performance**: Optimized parsing with singleton patterns and efficient regex
- **Zero Dependencies**: Only requires Pydantic (>=2.5) as external dependency
- **Thread Safe**: All operations are thread-safe for concurrent applications

## Quick Example

```python
from pydantic import BaseModel
from duratypes import Duration, parse_duration, format_duration

# Parse various duration formats
parse_duration("1h30m")     # 5400 (seconds)
parse_duration("PT1H30M")   # 5400 (ISO 8601)
parse_duration(5400)        # 5400 (numeric)

# Format durations back to human-readable strings
format_duration(5400)       # "1h30m"

# Use with Pydantic models
class Task(BaseModel):
    name: str
    duration: Duration

task = Task(name="Build", duration="2h30m")
print(task.duration)  # 9000
```

## Supported Formats

### Compound Format
Human-readable format with units:
- `"30s"`, `"5m"`, `"2h"` - Single units
- `"1h30m"`, `"2h30m45s"` - Multiple units
- `"1y2mo3w4d5h6m7s"` - All units (years, months, weeks, days, hours, minutes, seconds)

### ISO 8601 Format
Standards-compliant duration format:
- `"PT30S"`, `"PT5M"`, `"PT2H"` - Single units
- `"PT1H30M"`, `"PT2H30M45S"` - Multiple units
- Supports fractional values: `"PT1.5H"`

### Numeric Format
Direct numeric input:
- `30`, `300`, `3600` - Integer seconds
- `30.5`, `90.5` - Float seconds (truncated to integers)

## Installation

```bash
pip install duratypes
```

For development:
```bash
git clone https://github.com/dillon-barendt/duratypes.git
cd duratypes
uv sync --dev
```

## Why duratypes?

- **Developer Friendly**: Intuitive API that just works
- **Production Ready**: Comprehensive error handling and validation
- **Well Tested**: 100% test coverage with property-based testing
- **Fast**: Optimized for performance with minimal overhead
- **Standards Compliant**: Supports ISO 8601 duration format
- **Type Safe**: Full type safety with mypy support

## Getting Started

Ready to get started? Check out our [Quick Start Guide](quickstart.md) or dive into the [User Guide](usage.md).

For Pydantic users, see our [Pydantic Integration Guide](pydantic.md).

## Community

- **GitHub**: [dillon-barendt/duratypes](https://github.com/dillon-barendt/duratypes)
- **PyPI**: [duratypes](https://pypi.org/project/duratypes/)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/dillon-barendt/duratypes/issues)

## License

DuraTypes is released under the MIT License. See [LICENSE](https://github.com/dillon-barendt/duratypes/blob/main/LICENSE) for details.
