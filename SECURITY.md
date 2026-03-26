# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it
responsibly.

**DO NOT** open a public GitHub issue for security vulnerabilities.

### How to Report

Email: **aid@agentmail.to**

Subject line: `[SECURITY] Brief description`

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 1 week
- **Fix timeline:** Depends on severity

### What Qualifies

- Authentication or authorization bypasses
- Data exposure risks (especially regarding affected populations)
- Injection vulnerabilities
- Dependencies with known CVEs

### What Does NOT Qualify

- Missing security headers on static documentation pages
- Denial of service via API rate limiting (we're a volunteer project)
- Social engineering approaches

## Security Design Principles

This project follows these security principles by design:

1. **No user data collection** — We don't store queries, locations, or personal information
2. **No authentication required** — The bot works without user accounts
3. **Source transparency** — All data comes from publicly available UN reports
4. **Open source** — All code is auditable
5. **Encrypted transport** — Telegram provides end-to-end encryption for bot messages

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |

## Dependencies

We regularly review dependencies for known vulnerabilities. If you notice an
outdated dependency with a known CVE, please open a regular issue.
