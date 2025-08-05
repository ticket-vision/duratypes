# Security Policy

## Supported Versions

We actively support the following versions of duratypes with security updates:

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of duratypes seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **Do NOT create a public GitHub issue** for security vulnerabilities 
2. Email maintainers with details about the vulnerability
3. Include the following information in your report:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Any suggested fixes or mitigations

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 5 business days
- **Updates**: We will keep you informed of our progress throughout the investigation
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days

### Disclosure Policy

- We follow responsible disclosure practices
- We will coordinate with you on the timing of public disclosure
- We will credit you for the discovery (unless you prefer to remain anonymous)
- We may request that you keep the vulnerability confidential until we have released a fix

## Security Best Practices

When using duratypes in your applications:

1. **Input Validation**: Always validate duration strings from untrusted sources
2. **Error Handling**: Implement proper error handling for invalid duration formats
3. **Dependencies**: Keep duratypes and its dependencies up to date
4. **Monitoring**: Monitor for unusual parsing patterns that might indicate malicious input

## Known Security Considerations

### Input Parsing
- duratypes validates input formats strictly to prevent injection attacks
- Invalid formats raise `ValueError` exceptions rather than failing silently
- Regex patterns are designed to be safe against ReDoS (Regular Expression Denial of Service) attacks

### Dependencies
- duratypes has minimal dependencies (only pydantic >=2.5)
- We regularly review and update dependencies for security vulnerabilities
- All dependencies are pinned to specific version ranges

## Security Updates

Security updates will be:
- Released as patch versions (e.g., 0.1.1 → 0.1.2)
- Documented in the CHANGELOG.md
- Announced through GitHub releases
- Tagged with security labels for easy identification

## Security Maintainers

 - For security-related questions or concerns, please contact the maintainers through the project's GitHub repository.
*This security policy is reviewed and updated regularly to ensure it meets current best practices.*
