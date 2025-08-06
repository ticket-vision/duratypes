# Pull Request

## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring (no functional changes)
- [ ] Test improvements
- [ ] CI/CD improvements
- [ ] Other (please describe):

## Related Issues

<!-- Link to any related issues using "Fixes #123" or "Closes #123" -->

- Fixes #
- Related to #

## Changes Made

<!-- Provide a detailed list of changes made -->

- 
- 
- 

## Testing

<!-- Describe the tests you ran and how to reproduce them -->

### Test Coverage
- [ ] All new code is covered by tests
- [ ] All existing tests pass
- [ ] New tests have been added for new functionality

### Manual Testing
<!-- Describe any manual testing performed -->

- [ ] Tested with Python 3.12
- [ ] Tested with Python 3.13
- [ ] Tested with different Pydantic versions
- [ ] Tested edge cases and error conditions

### Test Commands
```bash
# Commands used to test the changes
uv run pytest
uv run pytest --cov=duratypes --cov-report=term-missing
```

## Performance Impact

<!-- If applicable, describe any performance implications -->

- [ ] No performance impact
- [ ] Performance improvement (describe below)
- [ ] Potential performance regression (describe below and justify)

## Breaking Changes

<!-- If this is a breaking change, describe what breaks and how to migrate -->

- [ ] No breaking changes
- [ ] Breaking changes (describe migration path below)

## Documentation

<!-- Check all that apply -->

- [ ] Documentation has been updated
- [ ] Docstrings have been added/updated
- [ ] README has been updated if needed
- [ ] CHANGELOG has been updated
- [ ] No documentation changes needed

## Code Quality

<!-- Confirm code quality checks -->

- [ ] Code follows the project's style guidelines
- [ ] Self-review of code has been performed
- [ ] Code has been formatted with ruff
- [ ] Code passes linting checks
- [ ] Type hints have been added where appropriate
- [ ] Code passes mypy type checking

## Dependencies

<!-- If dependencies were changed -->

- [ ] No new dependencies added
- [ ] New dependencies added (list below and justify)
- [ ] Dependencies updated (list below)

## Checklist

<!-- Final checklist before submitting -->

- [ ] I have read the [CONTRIBUTING.md](../CONTRIBUTING.md) guidelines
- [ ] My code follows the code style of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Additional Notes

<!-- Add any additional notes, concerns, or context for reviewers -->

## Screenshots (if applicable)

<!-- Add screenshots to help explain your changes -->

---

**Reviewer Guidelines:**
- Check that all tests pass
- Verify code quality and style
- Ensure documentation is updated
- Test the changes locally if needed
- Consider performance and security implications
