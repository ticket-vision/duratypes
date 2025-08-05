# Contributing to duratypes

Thank you for your interest in contributing to duratypes! We welcome contributions from the community and are pleased to have you join us.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python ≥3.12
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git

### Types of Contributions

We welcome several types of contributions:

- 🐛 **Bug Reports**: Help us identify and fix issues
- 🚀 **Feature Requests**: Suggest new functionality
- 📝 **Documentation**: Improve or add documentation
- 🔧 **Code Contributions**: Bug fixes, features, optimizations
- 🧪 **Tests**: Add or improve test coverage
- 📊 **Performance**: Optimize existing functionality

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/duratypes.git
cd duratypes

# Add the original repository as upstream
git remote add upstream https://github.com/dillon-barendt/duratypes.git
```

### 2. Set Up Development Environment

#### Using uv (Recommended)

```bash
# Install dependencies and create virtual environment
uv sync

# Activate the virtual environment
source .venv/bin/activate

# Verify installation
python -c "import duratypes; print('Setup successful!')"
```

#### Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

### 3. Verify Setup

```bash
# Run tests to ensure everything works
python -m pytest tests/ -v

# Run linting
ruff check src/ tests/

# Run type checking
mypy src/
```

## Making Changes

### Branch Strategy

1. **Create a feature branch** from `main`:
   ```bash
   git checkout main
   git pull upstream main
   git checkout -b feature/your-feature-name
   ```

2. **Use descriptive branch names**:
   - `feature/add-week-support` - for new features
   - `fix/iso-parsing-bug` - for bug fixes
   - `docs/api-reference` - for documentation
   - `test/edge-cases` - for test improvements

### Coding Standards

#### Code Style

- **PEP 8**, the Style Guide for Python Code, recommends limiting all lines of code to a maximum of 79 characters. For docstrings and comments, the line  length should be limited to 72 characters
- **Use type hints** for all function parameters and return values
- **Write descriptive variable names** and avoid abbreviations
- **Add docstrings** to all public functions and classes

#### Example Function

```python
def parse_duration(v: str | int | float) -> int:
    """
    Parse a duration string, integer, or float into seconds.
    
    Args:
        v: Duration input in various formats:
           - String: "30s", "5m", "1h30m", "PT1H30M", etc.
           - Integer/Float: Direct seconds value
    
    Returns:
        Duration in seconds as an integer
        
    Raises:
        ValueError: If the input format is invalid or unsupported
        TypeError: If the input type is not supported
    """
    # Implementation here...
```

#### Error Handling

- **Provide specific error messages** that help users understand what went wrong
- **Use appropriate exception types** (ValueError for invalid input, TypeError for wrong types)
- **Include examples of valid input** in error messages when possible

```python
raise ValueError(f"Invalid duration format: {str}", f"Supported formats: compound ('30s', '5m', '1h30m'), f" ('PT30S', 'PT5M', 'PT1H30M'), )

```
#### Performance Considerations

- **Use constants** instead of magic numbers
- **Compile regex patterns** at module level
- **Minimize object creation** in hot paths
- **Consider caching** for expensive operations

### Adding New Features

When adding new features:

1. **Check existing issues** to see if it's already planned
2. **Open an issue** to discuss the feature before implementing
3. **Update documentation** including README.md and docstrings
4. **Add comprehensive tests** covering normal and edge cases
5. **Consider backward compatibility** and migration paths

### Common Development Tasks

#### Adding New Duration Units

To add support for new time units (e.g., weeks):

1. **Add constants**:
   ```python
   SECONDS_PER_WEEK = 604800  # 7 * 24 * 60 * 60
   ```

2. **Update regex patterns**:
   ```python
   _COMPOUND_RE = re.compile(
       r"(?P<value>\d+(?:\.\d+)?)\s*"
       r"(?P<unit>w(?:eek)?s?|...)",  # Add week support
       re.IGNORECASE
   
3. **Update parsing logic**:
4. ```pythone if unit.startswith("w"):```
5. total += val * SECONDS_PER_WEEK
6. **Add tests** for the new functionality
7. **Update documentation** with examples

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=duratypes --cov-report=html

# Run specific test file
python -m pytest tests/test_core.py -v

# Run specific test
python -m pytest tests/test_core.py::test_parse_and_adapter -v
```

### Writing Tests

#### Test Structure

```python
import pytest
from duratypes import parse_duration, format_duration


class TestNewFeature:
    """Test class for new feature."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        result = parse_duration("1w")
        assert result == 604800  # 1 week in seconds

    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("invalid")

    @pytest.mark.parametrize("input_val,expected", [
        ("1w", 604800),
        ("2w", 1209600),
        ("1w3d", 864000),
    ])
    def test_paramaterized(self, input_val: str, expected: object) -> None:
        """Test multiple inputs with parametrize."""
        assert parse_duration(input_val) == expected
```
test_parameterized
#### Test Coverage Areas

Ensure your tests cover:

- **Valid input formats** (all supported variations)
- **Invalid input handling** (ValueError/TypeError cases)
- **Edge cases** (empty strings, None, negative values, etc.)
- **Pydantic integration** (model validation, JSON schema)
- **Performance** (if adding potentially slow operations)

### Property-Based Testing

For complex features, consider using Hypothesis:

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=86400))
def test_format_parse_roundtrip(seconds):
    """Test that format -> parse is a roundtrip for valid inputs."""
    from duratypes import parse_duration, format_duration
    formatted = format_duration(seconds)
    parsed = parse_duration(formatted)
    assert parsed == seconds
```

## Code Quality

### Automated Checks

Before submitting, ensure all checks pass:

```bash
# Linting
ruff check src/ tests/

# Formatting
ruff format src/ tests/

# Type checking
mypy src/

# Tests with coverage
python -m pytest tests/ --cov=duratypes --cov-report=term-missing
```

### Pre-commit Hooks (Optional)

Set up pre-commit hooks to automatically run checks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Code Review Checklist

Before submitting your PR, review:

- [ ] **Code follows style guidelines** (ruff/black formatting)
- [ ] **All tests pass** locally
- [ ] **Type hints are present** and correct
- [ ] **Docstrings are comprehensive**
- [ ] **Error messages are helpful** and specific
- [ ] **Performance impact** is considered
- [ ] **Documentation is updated** (README, docstrings)
- [ ] **Backward compatibility** is maintained
- [ ] **Edge cases are tested**

## Submitting Changes

### Pull Request Process

1. **Ensure your branch is up to date**:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run all checks locally**:
   ```bash
   python -m pytest tests/ -v
   ruff check src/ tests/
   mypy src/
   ```

3. **Commit your changes** with descriptive messages:
   ```bash
   git add .
   git commit -m "Add support for week duration units
   
   - Add SECONDS_PER_WEEK constant
   - Update regex to match 'w', 'week', 'weeks'
   - Add comprehensive tests for week parsing
   - Update documentation with week examples"
   ```

4. **Push to your fork**:
   ```bash
   git push origin your-feature-branch
   ```

5. **Create a Pull Request** on GitHub with:
   - **Clear title** describing the change
   - **Detailed description** of what was changed and why
   - **Reference to related issues** (e.g., "Fixes #123")
   - **Testing notes** if applicable

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated existing tests if needed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)
```

### Review Process

1. **Automated checks** will run on your PR
2. **Maintainers will review** your code
3. **Address feedback** by pushing new commits
4. **Squash and merge** once approved

## Release Process

Releases follow semantic versioning (SemVer):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backward-compatible functionality additions
- **PATCH** version for backward-compatible bug fixes

### Version Bumping

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with release notes
3. Create a git tag: `git tag v1.2.3`
4. Push tag: `git push origin v1.2.3`

## Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: Maintainers will provide feedback on PRs

## Recognition

Contributors will be recognized in:
- **CHANGELOG.md** for significant contributions
- **GitHub contributors** page
- **Release notes** for major features

---

Thank you for contributing to duratypes! Your efforts help make this project better for everyone. 🚀
