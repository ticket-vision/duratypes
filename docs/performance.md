# Performance Benchmarks

This document provides performance benchmarks and optimization guidelines for the duratypes package.

## Overview

duratypes is designed for high performance with minimal overhead. The package uses optimized regex patterns, singleton patterns, and efficient parsing algorithms to ensure fast duration processing.

## Benchmark Results

The following benchmarks were conducted on a typical development machine. Your results may vary depending on hardware and system configuration.

### Parsing Performance

#### Compound Format Parsing
- **Format**: `"1h30m45s"`, `"30m"`, `"2h"`
- **Performance**: ~10,000-50,000 operations per second
- **Use Case**: Most common format for user input

```python
# Example compound formats
parse_duration("30s")      # Fast: simple single unit
parse_duration("1h30m")    # Fast: common multi-unit
parse_duration("2h30m45s") # Moderate: complex multi-unit
```

#### ISO 8601 Format Parsing
- **Format**: `"PT1H30M45S"`, `"PT30M"`, `"PT2H"`
- **Performance**: ~8,000-40,000 operations per second
- **Use Case**: Standards-compliant applications

```python
# Example ISO 8601 formats
parse_duration("PT30S")      # Fast: simple single unit
parse_duration("PT1H30M")    # Fast: common multi-unit
parse_duration("PT2H30M45S") # Moderate: complex multi-unit
```

#### Numeric Parsing
- **Format**: `30`, `1800`, `3600`
- **Performance**: ~100,000+ operations per second
- **Use Case**: Pre-calculated values or internal processing

```python
# Example numeric inputs
parse_duration(30)    # Fastest: direct integer
parse_duration(30.5)  # Fast: float (truncated to int)
```

### Formatting Performance

#### Duration Formatting
- **Performance**: ~20,000-80,000 operations per second
- **Varies by**: Complexity of output format (number of units)

```python
# Performance varies by complexity
format_duration(30)     # Fastest: "30s" (single unit)
format_duration(3600)   # Fast: "1h" (single unit)
format_duration(3661)   # Moderate: "1h1m1s" (multiple units)
format_duration(999999) # Slower: "1w4d13h46m39s" (many units)
```

### Pydantic Integration Performance

#### DurationAdapter Performance
- **Performance**: ~15,000-60,000 operations per second
- **Benefit**: Singleton pattern provides optimal reuse
- **Use Case**: Pydantic model validation

```python
# DurationAdapter is optimized for repeated use
from duratypes import DurationAdapter

# Reuses singleton instance for maximum performance
adapter = DurationAdapter
result = adapter.validate_python("1h30m")
```

### Round-Trip Performance

#### Parse + Format Operations
- **Performance**: ~5,000-25,000 complete cycles per second
- **Use Case**: Data transformation and validation workflows

```python
# Round-trip example
original = "1h30m"
seconds = parse_duration(original)
formatted = format_duration(seconds)
# formatted == "1h30m"
```

## Performance Optimization Tips

### 1. Use Numeric Values When Possible

For maximum performance, use pre-calculated numeric values instead of parsing strings:

```python
# Fastest
duration = 3600  # 1 hour

# Slower
duration = parse_duration("1h")
```

### 2. Cache Parsed Results

If you're parsing the same duration strings repeatedly, cache the results:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_parse_duration(duration_str):
    return parse_duration(duration_str)
```

### 3. Use Simple Formats

Simpler duration formats parse faster:

```python
# Faster
parse_duration("30m")

# Slower
parse_duration("30 minutes")
```

### 4. Prefer Compound Over ISO 8601

Compound formats generally parse slightly faster than ISO 8601:

```python
# Slightly faster
parse_duration("1h30m")

# Slightly slower
parse_duration("PT1H30M")
```

### 5. Leverage DurationAdapter Singleton

The DurationAdapter uses a singleton pattern for optimal performance in Pydantic models:

```python
from pydantic import BaseModel
from duratypes import Duration

class TaskModel(BaseModel):
    duration: Duration  # Automatically uses optimized singleton adapter
```

## Memory Usage

### Memory Efficiency
- **Parsing**: Minimal memory allocation during parsing
- **Formatting**: Efficient string building with minimal intermediate objects
- **Singleton**: DurationAdapter singleton reduces memory overhead
- **No Dependencies**: Zero external dependencies except Pydantic

### Memory Patterns
```python
# Memory-efficient patterns
duration = parse_duration("1h")  # Minimal allocation
formatted = format_duration(3600)  # Efficient string building

# Less efficient (but still reasonable)
durations = [parse_duration(f"{i}m") for i in range(100)]  # Multiple allocations
```

## Thread Safety

All duratypes functions are thread-safe:

- **parse_duration()**: Thread-safe, no shared state
- **format_duration()**: Thread-safe, no shared state  
- **DurationAdapter**: Thread-safe singleton implementation

```python
import threading
from duratypes import parse_duration

def worker():
    # Safe to call from multiple threads
    result = parse_duration("1h30m")

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
```

## Benchmarking Your Usage

To benchmark duratypes performance in your specific use case:

```python
import time
from duratypes import parse_duration, format_duration

def benchmark_parsing(duration_str, iterations=10000):
    start = time.time()
    for _ in range(iterations):
        parse_duration(duration_str)
    end = time.time()
    
    ops_per_second = iterations / (end - start)
    print(f"Parsing '{duration_str}': {ops_per_second:.0f} ops/sec")

def benchmark_formatting(seconds, iterations=10000):
    start = time.time()
    for _ in range(iterations):
        format_duration(seconds)
    end = time.time()
    
    ops_per_second = iterations / (end - start)
    print(f"Formatting {seconds}s: {ops_per_second:.0f} ops/sec")

# Run benchmarks
benchmark_parsing("1h30m")
benchmark_parsing("PT1H30M")
benchmark_formatting(5400)
```

## Performance Regression Testing

The test suite includes performance regression tests to ensure performance doesn't degrade:

```bash
# Run performance tests
uv run pytest tests/test_core.py::TestPerformanceBenchmarks -v

# Run with timing details
uv run pytest tests/test_core.py::TestPerformanceBenchmarks -v -s
```

## Comparison with Alternatives

duratypes is optimized for:
- **Speed**: Fast parsing and formatting
- **Memory**: Minimal memory usage
- **Integration**: Seamless Pydantic integration
- **Simplicity**: Zero external dependencies (except Pydantic)

For applications requiring maximum performance, consider:
1. Pre-calculating duration values when possible
2. Caching frequently used duration strings
3. Using numeric values for internal calculations
4. Leveraging the singleton DurationAdapter pattern

---

*Performance benchmarks are approximate and may vary based on hardware, Python version, and system configuration. Benchmarks were conducted using Python 3.12+ on a typical development machine.*
