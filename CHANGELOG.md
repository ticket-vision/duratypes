# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-08-05

### Added
- Initial release of duratypes package
- Core duration parsing functionality supporting multiple input formats:
  - Compound formats: `"30s"`, `"5m"`, `"1h30m45s"`
  - ISO 8601 formats: `"PT30S"`, `"PT5M"`, `"PT1H30M45S"`
  - Numeric values: `30`, `30.5` (integers/floats)
- Duration formatting functionality to convert seconds back to human-readable format
- Pydantic v2 integration with annotated types:
  - `Duration` - Generic duration type
  - `Seconds` - Duration in seconds
  - `Minutes` - Duration in minutes  
  - `Hours` - Duration in hours
- Comprehensive error handling with custom exception hierarchy:
  - `DurationError` - Base exception class
  - `InvalidFormatError` - For malformed duration strings
  - `InvalidTypeError` - For unsupported input types
  - `InvalidValueError` - For invalid duration values
- Singleton `DurationAdapter` for optimal performance
- Support for negative durations with proper sign handling
- Case-insensitive parsing for all string formats
- Comprehensive test suite with 100% code coverage including:
  - Edge case testing
  - Property-based testing with Hypothesis
  - Performance benchmarks
  - Thread safety validation
- Full type safety with comprehensive type hints
- Development tooling setup:
  - Ruff for linting and formatting
  - MyPy for type checking
  - Pytest with coverage reporting
  - Pre-commit hooks
- CI/CD pipeline with GitHub Actions
- Comprehensive documentation and contributing guidelines

### Technical Details
- Python 3.12+ support
- Zero external dependencies except Pydantic (>=2.5)
- Optimized regex patterns for efficient parsing
- Thread-safe singleton pattern implementation
- Robust input validation and sanitization

[Unreleased]: https://github.com/dillon-barendt/duratypes/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/dillon-barendt/duratypes/releases/tag/v0.1.0
