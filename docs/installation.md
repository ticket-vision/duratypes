# Installation

## Requirements

duratypes requires:
- **Python 3.12+**
- **Pydantic 2.5+** (only external dependency)

## Install from PyPI

The easiest way to install duratypes is from PyPI using pip:

```bash
pip install duratypes
```

Or using uv (recommended):

```bash
uv add duratypes
```

## Development Installation

For development or to get the latest features:

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/dillon-barendt/duratypes.git
cd duratypes

# Install with development dependencies
uv sync --dev

# Activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/dillon-barendt/duratypes.git
cd duratypes

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

## Verify Installation

Test your installation:

```python
import duratypes
print(duratypes.__version__)

# Test basic functionality
from duratypes import parse_duration
result = parse_duration("1h30m")
print(f"1h30m = {result} seconds")  # Should print: 1h30m = 5400 seconds
```

## Optional Dependencies

duratypes has minimal dependencies by design. The only required dependency is Pydantic.

### Development Dependencies

If you're contributing to duratypes, you'll need these additional packages:

- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **hypothesis** - Property-based testing
- **ruff** - Linting and formatting
- **mypy** - Type checking
- **black** - Code formatting
- **pre-commit** - Git hooks

These are automatically installed with `uv sync --dev` or `pip install -e ".[dev]"`.

### Documentation Dependencies

For building documentation locally:

```bash
uv add mkdocs mkdocs-material mkdocstrings[python]
```

## Troubleshooting

### Python Version Issues

duratypes requires Python 3.12 or later. Check your Python version:

```bash
python --version
```

If you have an older version, consider using [pyenv](https://github.com/pyenv/pyenv) to manage multiple Python versions.

### Import Errors

If you get import errors, ensure duratypes is installed in the correct environment:

```python
import sys
print(sys.path)

# This should show duratypes in the installed packages
import importlib.metadata
print([dist.metadata['name'] for dist in importlib.metadata.distributions()])
```

### Pydantic Version Conflicts

duratypes requires Pydantic v2.5+. If you have an older version:

```bash
pip install --upgrade pydantic>=2.5
```

### Virtual Environment Issues

If you're having issues with virtual environments:

```bash
# Deactivate current environment
deactivate

# Remove old environment
rm -rf .venv

# Create fresh environment
python -m venv .venv
source .venv/bin/activate
pip install duratypes
```

## Next Steps

Once installed, check out:

- [Quick Start Guide](quickstart.md) - Get up and running quickly
- [Basic Usage](usage.md) - Learn the core functionality
- [Pydantic Integration](pydantic.md) - Use with Pydantic models

## Getting Help

If you encounter installation issues:

1. Check the [FAQ](faq.md) for common solutions
2. Search [existing issues](https://github.com/dillon-barendt/duratypes/issues)
3. Create a [new issue](https://github.com/dillon-barendt/duratypes/issues/new) with:
   - Your Python version (`python --version`)
   - Your operating system
   - The complete error message
   - Steps to reproduce the issue
