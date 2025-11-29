# Frontend Dependency Management

## Dependency Version Rationale

### ESLint Ecosystem (Pinned to v8.x)

**Decision**: Use ESLint v8.57.1 (exact version, no `^` prefix)

**Rationale**:

- ESLint v9 was released in April 2024 with breaking changes
- Critical ecosystem plugins (especially `eslint-plugin-react-hooks@4.6.2`) only support ESLint v3-8
- ESLint v8.x still receives security updates and is production-ready
- Exact version pinning prevents accidental major version upgrades

**Migration Path to v9**:
When the ecosystem is ready (check plugin compatibility):

1. Upgrade to `eslint-plugin-react-hooks@5.0.0+` (supports ESLint v9)
2. Migrate to flat config format (`eslint.config.js`)
3. Update to `eslint@^9.x.x`

### Core Dependencies

- **React 18.3.x**: Latest stable, using `^` for minor/patch updates
- **Vite 5.4.x**: Fast build tool, compatible with our stack
- **AWS Amplify 6.x**: Authentication and API integration

### Development Dependencies

All ESLint-related packages are compatible with ESLint v8:

- `eslint-plugin-react@^7.35.0` - React-specific linting rules
- `eslint-plugin-react-hooks@^4.6.2` - Hooks rules (requires ESLint ≤8)
- `eslint-plugin-react-refresh@^0.4.7` - Vite hot reload compatibility

## Dependency Update Strategy

### Safe Updates (Automated)

Run `npm update` to get latest compatible versions within semver ranges:

```bash
npm update
```

### Major Version Updates (Manual Review Required)

1. Check compatibility: `npm outdated`
2. Review changelog for breaking changes
3. Test in a separate branch
4. Update one major package at a time

### Security Updates

Run regularly and address immediately:

```bash
npm audit
npm audit fix
```

## Installation Best Practices

### Clean Install (Recommended)

Always use `npm ci` in CI/CD environments:

```bash
npm ci
```

Benefits:

- Installs exact versions from `package-lock.json`
- Fails if lock file is out of sync
- Faster and more reliable than `npm install`

### Development Install

For local development:

```bash
npm install
```

### Troubleshooting Peer Dependency Conflicts

If you encounter peer dependency warnings:

1. **First**: Check if versions are actually incompatible
2. **Prefer**: Update the conflicting package to a compatible version
3. **Avoid**: Using `--legacy-peer-deps` or `--force` (creates technical debt)

## Lock File Management

### Commit Strategy

- ✅ **Always commit** `package-lock.json` to version control
- ✅ Regenerate lock file when updating `package.json`
- ❌ **Never** commit `node_modules/`

### Lock File Sync

If `package-lock.json` gets out of sync:

```bash
rm -rf node_modules package-lock.json
npm install
```

## Hardening Measures

### 1. Engine Constraints

We enforce minimum Node.js and npm versions in `package.json`:

```json
"engines": {
  "node": ">=18.0.0",
  "npm": ">=9.0.0"
}
```

### 2. Exact Versions for Critical Packages

ESLint is pinned to exact version to prevent breaking changes:

- `"eslint": "8.57.1"` (no `^`)

### 3. CI/CD Integration

Add to GitHub Actions or CI pipeline:

```yaml
- name: Install dependencies
  run: npm ci

- name: Security audit
  run: npm audit --audit-level=moderate
```

### 4. Pre-commit Hooks (Future Enhancement)

Consider adding Husky + lint-staged:

```bash
npm install -D husky lint-staged
```

## Common Issues and Solutions

### Issue: `npm install` fails with peer dependency error

**Solution**: Check this document's "ESLint Ecosystem" section for compatible versions

### Issue: Lock file conflicts in git

**Solution**:

```bash
git checkout --theirs package-lock.json
npm install
git add package-lock.json
```

### Issue: "Cannot find module" errors after install

**Solution**: Clear node_modules and reinstall:

```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: Outdated dependencies showing in `npm outdated`

**Solution**: Review major version updates individually, test thoroughly

## Monitoring and Maintenance

### Weekly

- [ ] Run `npm outdated` to check for available updates
- [ ] Review and plan non-breaking updates

### Monthly

- [ ] Run `npm audit` and address vulnerabilities
- [ ] Check for major version updates of key dependencies
- [ ] Review ESLint ecosystem for v9 compatibility

### Quarterly

- [ ] Audit all dependencies for deprecation notices
- [ ] Review and update this documentation
- [ ] Test against latest LTS Node.js version

## References

- [npm Semantic Versioning](https://docs.npmjs.com/about-semantic-versioning)
- [ESLint v9 Migration Guide](https://eslint.org/docs/latest/use/migrate-to-9.0.0)
- [React Hooks ESLint Plugin](https://www.npmjs.com/package/eslint-plugin-react-hooks)
- [Vite Documentation](https://vitejs.dev/)

---

**Last Updated**: November 29, 2025  
**Maintainer**: Development Team  
**Status**: Active - ESLint v8 stable, monitoring for v9 ecosystem readiness
