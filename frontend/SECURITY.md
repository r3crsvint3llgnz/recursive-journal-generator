# Security Policy

## Current Security Status

### Known Vulnerabilities

#### Development Dependencies (Non-Critical)

**esbuild <=0.24.2** (Moderate Severity)

- **Impact**: Development server only - allows any website to send requests to dev server
- **Affected**: `vite@5.4.1` depends on vulnerable esbuild version
- **Risk Level**: Low (development only, not deployed to production)
- **Mitigation**:
  - Only run dev server on localhost
  - Do not expose dev server to public networks
  - Use firewall rules to restrict access
- **Fix Available**: `npm audit fix --force` (upgrades to vite@7.x - breaking change)
- **Decision**: Monitor - will upgrade during next major frontend refactor

### Security Best Practices

#### Development Environment

1. **Never expose dev server publicly**: Always use `localhost` or `127.0.0.1`
2. **Use environment variables**: Never commit secrets to `.env` files
3. **Review dependencies regularly**: Run `npm audit` monthly

#### Production Build

1. **Static site only**: Vite produces static HTML/JS/CSS - no server vulnerabilities
2. **CDN deployment**: Serve through CloudFront or similar CDN
3. **CSP headers**: Configure Content Security Policy in deployment

#### Dependency Management

1. **Lock file committed**: `package-lock.json` ensures reproducible builds
2. **Automated scanning**: Set up Dependabot or similar in CI/CD
3. **Update strategy**: Test updates in branches before merging

## Reporting Security Issues

If you discover a security vulnerability, please email the development team rather than opening a public issue.

## Security Update Schedule

### Critical Vulnerabilities

- **Response Time**: Within 24 hours
- **Action**: Immediate patch and deployment

### High Severity

- **Response Time**: Within 1 week
- **Action**: Scheduled update and testing

### Moderate Severity

- **Response Time**: Within 30 days
- **Action**: Included in next release cycle

### Low Severity

- **Response Time**: Quarterly review
- **Action**: Batch updates during maintenance window

## Current Action Items

- [ ] Document esbuild/vite vulnerability in issue tracker
- [ ] Schedule vite 7.x upgrade during Q1 2026 major refactor
- [ ] Add automated security scanning to CI/CD pipeline
- [ ] Review and rotate any exposed API keys

## Compliance

### Dependencies

- All production dependencies are vetted
- Development dependencies isolated from production builds
- Regular audits scheduled (see FRONTEND_DEPENDENCIES.md)

### Data Handling

- No PII stored in frontend code
- All sensitive data handled via AWS Amplify SDK
- Authentication tokens managed by Cognito

---

**Last Security Review**: November 29, 2025  
**Next Scheduled Review**: February 29, 2026  
**Security Contact**: Development Team
