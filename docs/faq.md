# Frequently Asked Questions

## General Usage

### Q: What formats does duratypes support?

**A:** duratypes supports three main input formats:

1. **Compound format**: `"30s"`, `"5m"`, `"1h30m"`, `"2h30m45s"`
2. **ISO 8601 format**: `"PT30S"`, `"PT5M"`, `"PT1H30M45S"`
3. **Numeric format**: `30`, `300`, `3600` (integers or floats)

All formats are case-insensitive and support negative values with leading `-` or `+` signs.

### Q: Why does `parse_duration("30")` fail?

**A:** Plain numeric strings without units are not supported to avoid ambiguity. Use:
- `parse_duration("30s")` for 30 seconds
- `parse_duration(30)` for numeric input
- `parse_duration("PT30S")` for ISO 8601 format

### Q: How do I handle parsing errors gracefully?

**A:** Use try-catch blocks with specific exception types:

```python
from duratypes import parse_duration
from duratypes.core import DurationError

def safe_parse(value, default=0):
    try:
        return parse_duration(value)
    except DurationError:
        return default
```

See the [Error Handling](errors.md) guide for comprehensive examples.

### Q: Can I use fractional values?

**A:** Yes, but they're truncated to integers:
- `parse_duration(30.7)` returns `30`
- `parse_duration("PT1.5H")` returns `5400` (1.5 hours)
- `parse_duration("90.5m")` returns `5430` (90.5 minutes)

## Pydantic Integration

### Q: How do I use duratypes with Pydantic models?

**A:** Use the annotated types:

```python
from pydantic import BaseModel
from duratypes import Duration, Seconds, Minutes, Hours

class Task(BaseModel):
    name: str
    duration: Duration  # All types are equivalent
    timeout: Seconds    # Same as Duration
    break_time: Minutes # Same as Duration
    max_time: Hours     # Same as Duration

task = Task(name="Build", duration="2h30m")
```

### Q: What's the difference between Duration, Seconds, Minutes, and Hours?

**A:** They're all aliases for the same type. Use whichever makes your code more readable:

```python
# These are identical
duration: Duration = parse_duration("1h")
seconds: Seconds = parse_duration("1h") 
minutes: Minutes = parse_duration("1h")
hours: Hours = parse_duration("1h")
```

### Q: How do I add validation constraints to duration fields?

**A:** Use Pydantic's Field with constraints:

```python
from pydantic import BaseModel, Field
from duratypes import Duration

class Task(BaseModel):
    duration: Duration = Field(gt=0, le=86400)  # 1 second to 24 hours
    timeout: Duration = Field(default=30, description="Timeout in seconds")
```

### Q: Can I use duratypes with Pydantic v1?

**A:** No, duratypes requires Pydantic v2.5+. For Pydantic v1, you'll need to create custom validators.

## Performance

### Q: Is duratypes fast enough for production use?

**A:** Yes! duratypes is optimized for performance:
- 10,000-50,000 parsing operations per second
- Singleton pattern for Pydantic integration
- Efficient regex patterns
- Minimal memory allocation

See [Performance](performance.md) for detailed benchmarks.

### Q: Should I cache parsed durations?

**A:** For frequently parsed strings, yes:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_parse_duration(duration_str):
    return parse_duration(duration_str)
```

### Q: Which format is fastest?

**A:** In order of speed:
1. Numeric values: `parse_duration(3600)` (fastest)
2. Simple compound: `parse_duration("1h")` 
3. Complex compound: `parse_duration("1h30m45s")`
4. ISO 8601: `parse_duration("PT1H30M45S")` (slowest)

## Formatting

### Q: How do I format durations back to strings?

**A:** Use `format_duration()`:

```python
from duratypes import format_duration

seconds = 5400
formatted = format_duration(seconds)  # "1h30m"
```

### Q: Can I customize the output format?

**A:** Currently, `format_duration()` uses a fixed format. For custom formatting:

```python
def custom_format(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

custom_format(5400)  # "01:30:00"
```

### Q: Why does `format_duration()` include all units?

**A:** It shows the most natural representation:
- `format_duration(90061)` returns `"1d1h1m1s"`
- This includes years, months, weeks, days when applicable

## Edge Cases

### Q: How are negative durations handled?

**A:** Negative durations are fully supported:

```python
parse_duration("-1h30m")    # -5400
parse_duration("-PT1H30M")  # -5400
format_duration(-5400)      # "-1h30m"
```

### Q: What about very large durations?

**A:** duratypes handles large values well:

```python
parse_duration("1y")        # 31536000 (1 year in seconds)
parse_duration("100y")      # 3153600000 (100 years)
format_duration(999999999)  # "31y8mo2w2d9h46m39s"
```

### Q: Are leap years considered?

**A:** No, duratypes uses approximate values:
- 1 year = 365 days = 31,536,000 seconds
- 1 month = 30 days = 2,592,000 seconds

For precise date arithmetic, use Python's `datetime` module.

### Q: How are whitespace and case handled?

**A:** duratypes is forgiving:

```python
parse_duration("  1H 30M  ")  # Works (whitespace ignored)
parse_duration("1h30m")       # Works (lowercase)
parse_duration("1H30M")       # Works (uppercase)
parse_duration("1Hour30Min")  # Works (full words)
```

## Thread Safety

### Q: Is duratypes thread-safe?

**A:** Yes, all functions are thread-safe:
- `parse_duration()` has no shared state
- `format_duration()` has no shared state
- `DurationAdapter` singleton is thread-safe

### Q: Can I use duratypes in async code?

**A:** Yes, duratypes is synchronous and works fine in async contexts:

```python
import asyncio
from duratypes import parse_duration

async def process_duration(duration_str):
    # This is fine - parse_duration is synchronous
    return parse_duration(duration_str)
```

## Troubleshooting

### Q: Why am I getting "Invalid duration format" errors?

**A:** Common causes:
1. Missing units: `"30"` → use `"30s"`
2. Invalid units: `"30x"` → use valid units like `s`, `m`, `h`
3. Typos: `"30sec"` works, but `"30secs"` doesn't
4. Empty strings: `""` → check for empty input

### Q: How do I debug parsing issues?

**A:** Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from duratypes import parse_duration
parse_duration("1h30m")  # Will show debug info
```

### Q: What if I need features not in duratypes?

**A:** Consider:
1. **Feature requests**: Open an issue on GitHub
2. **Custom parsing**: Extend duratypes for your needs
3. **Alternative libraries**: For complex date/time arithmetic, use `dateutil` or `pendulum`

## Migration and Integration

### Q: How do I migrate from other duration libraries?

**A:** See our [Migration Guide](migration.md) for specific examples from:
- `pytimeparse`
- `dateutil`
- `pendulum`
- Custom duration parsers

### Q: Can I use duratypes with FastAPI?

**A:** Yes! duratypes works seamlessly with FastAPI:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from duratypes import Duration

app = FastAPI()

class TaskRequest(BaseModel):
    name: str
    duration: Duration

@app.post("/tasks/")
async def create_task(task: TaskRequest):
    return {"name": task.name, "duration_seconds": task.duration}
```

### Q: Does duratypes work with Django/Flask?

**A:** Yes, but you'll need to handle serialization:

```python
# Django model field
from django.db import models
from duratypes import parse_duration

class Task(models.Model):
    duration_seconds = models.IntegerField()
    
    def set_duration(self, duration_str):
        self.duration_seconds = parse_duration(duration_str)
```

## Contributing

### Q: How can I contribute to duratypes?

**A:** We welcome contributions! See [Contributing](contributing.md) for:
- Bug reports and feature requests
- Code contributions
- Documentation improvements
- Testing and feedback

### Q: How do I report bugs?

**A:** Use our [GitHub issue tracker](https://github.com/dillon-barendt/duratypes/issues) with:
- Python version
- duratypes version
- Minimal reproduction example
- Expected vs actual behavior

---

**Still have questions?** Check our [GitHub Discussions](https://github.com/dillon-barendt/duratypes/discussions) or open an [issue](https://github.com/dillon-barendt/duratypes/issues).
