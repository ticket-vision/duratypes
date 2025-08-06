# Contributing

Thank you for your interest in contributing to duratypes! We welcome contributions from the community.

## Quick Start for Contributors

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/duratypes.git
   cd duratypes
   ```

2. **Set up development environment**:
   ```bash
   # Using uv (recommended)
   uv sync
   source .venv/bin/activate
   
   # Or using pip
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

3. **Verify setup**:
   ```bash
   python -m pytest tests/ -v
   ruff check src/ tests/
   mypy src/
   ```

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Run tests and linting**:
   ```bash
   python -m pytest tests/ -v
   ruff check src/ tests/
   ruff format src/ tests/
   mypy src/
   ```

4. **Submit a pull request**

## Types of Contributions

- 🐛 **Bug Reports**: Help us identify and fix issues
- 🚀 **Feature Requests**: Suggest new functionality  
- 📝 **Documentation**: Improve or add documentation
- 🔧 **Code Contributions**: Bug fixes, features, optimizations
- 🧪 **Tests**: Add or improve test coverage

## Development Guidelines

### Code Quality

- Follow PEP 8 style guidelines (enforced by ruff)
- Add type hints to all functions and methods
- Write comprehensive docstrings for public APIs
- Maintain test coverage above 95%
- Use meaningful variable and function names

### Testing

- Write tests for all new functionality
- Include edge cases and error conditions
- Use property-based testing with Hypothesis where appropriate
- Ensure all tests pass before submitting

### Documentation

- Update documentation for any API changes
- Include code examples in docstrings
- Add entries to CHANGELOG.md for notable changes
- Update README.md if needed

## Code Style

We use several tools to maintain code quality:

- **ruff**: Linting and formatting
- **mypy**: Type checking
- **pytest**: Testing framework
- **pre-commit**: Git hooks for quality checks

### Pre-commit Hooks

Install pre-commit hooks to automatically check your code:

```bash
pre-commit install
```

This will run linting, formatting, and type checking on every commit.

## Submitting Changes

1. **Ensure all tests pass**:
   ```bash
   python -m pytest tests/ -v --cov=duratypes
   ```

2. **Check code quality**:
   ```bash
   ruff check src/ tests/
   ruff format src/ tests/
   mypy src/
   ```

3. **Update documentation** if needed

4. **Create a pull request** with:
   - Clear description of changes
   - Reference to any related issues
   - Test results and coverage information

## Getting Help

- Check existing [issues](https://github.com/dillon-barendt/duratypes/issues)
- Review the [API documentation](api/core.md)
- Read the [usage guide](usage.md)
- Ask questions in pull request discussions

## Complete Contributing Guide

For the complete contributing guidelines, including detailed setup instructions, coding standards, and release process, please see our [full CONTRIBUTING.md](https://github.com/dillon-barendt/duratypes/blob/main/CONTRIBUTING.md) file in the repository root.

---

We appreciate your contributions and look forward to working with you!
