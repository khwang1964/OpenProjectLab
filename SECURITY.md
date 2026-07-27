# Security Policy

## Supported Versions

The following table describes the current support policy for OpenProjectLab.

| Version        | Supported |
| -------------- | --------- |
| main           | ✅ Yes     |
| Latest release | ✅ Yes     |
| Older releases | ❌ No      |

Security fixes are provided only for the current development branch and the latest released version.

---

## Reporting a Vulnerability

If you discover a security vulnerability, **please do not create a public GitHub issue immediately.**

Instead, report it privately by contacting the project maintainers.

When reporting a vulnerability, please include as much information as possible:

* Description of the vulnerability
* Steps to reproduce
* Expected behavior
* Actual behavior
* A minimal reproducible example
* Affected version
* Operating system
* Python version
* Additional logs or screenshots if applicable

We will acknowledge your report as soon as possible.

---

## Response Process

OpenProjectLab follows the following response process.

1. Acknowledge the report.
2. Confirm and reproduce the issue.
3. Assess the impact.
4. Develop and test a fix.
5. Publish a security update.
6. Credit the reporter (if permission is granted).

---

## Security Scope

The following areas are considered security-sensitive.

* Project generators
* Template rendering
* Plugin loading
* Configuration parsing
* Upgrade package verification
* File-system operations
* Archive extraction
* Manifest validation

---

## Security Principles

OpenProjectLab follows these security principles.

* Validate all external input.
* Never trust template content automatically.
* Prevent directory traversal.
* Verify upgrade package integrity.
* Minimize required permissions.
* Fail safely.
* Prefer explicit configuration over implicit behavior.

---

## Third-party Dependencies

Dependencies should be kept up to date.

Security updates should be applied as soon as practical.

All dependency changes should pass:

* Ruff
* pytest
* pre-commit
* GitHub Actions

before merging.

---

## Responsible Disclosure

We appreciate responsible disclosure.

Please allow reasonable time for investigation and remediation before publicly disclosing a vulnerability.
