# Code Quality Verification

Automated code quality validation for DDDGuard.

## Quick Start

**Run all quality checks:**
```bash
./scripts/verify_code_quality.sh
```

This comprehensive script performs:
- ✅ Ruff linting
- ✅ Code formatting validation
- ✅ MyPy type checking
- ✅ DDDGuard architecture linting
- ✅ Secret/API key detection
- ✅ English-only language validation
- ✅ Code style analysis

## What It Checks

### 1. 🔍 Ruff Linting
Validates code quality and style rules:
- Import sorting
- Code complexity
- Common bugs
- Best practices

### 2. 📐 Code Formatting
Ensures consistent formatting:
- Line length (100 chars)
- Quote style
- Indentation
- Line endings

### 3. 🔬 MyPy Type Checking
Static type analysis (non-blocking):
- Type annotations
- Type safety
- Return types
- Argument types

### 4. 🏛️ DDDGuard Architecture Linting
Validates S-DDD architecture rules:
- Layer boundaries
- Import restrictions
- Context isolation
- Dependency direction

### 5. 🔐 Security Scan
Detects hardcoded secrets:
- Passwords
- API keys
- Tokens
- AWS credentials
- GitHub tokens
- OpenAI keys

### 6. 🌐 Language Check
Ensures English-only code:
- Cyrillic detection
- Non-ASCII characters
- (Excludes UI emojis)

### 7. 📝 Style Analysis
Checks code conciseness:
- TODO/FIXME markers
- Verbose patterns
- Code statistics

## Usage

### Before Committing

```bash
# Auto-fix issues
ruff check src/ --fix
ruff format src/

# Verify everything
./scripts/verify_code_quality.sh
```

### CI/CD Integration

```yaml
# GitHub Actions
- name: Install dependencies
  run: uv sync --group dev

- name: Verify code quality
  run: ./scripts/verify_code_quality.sh
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Verifying code quality..."
./scripts/verify_code_quality.sh || {
    echo "Quality checks failed. Fix issues before committing."
    exit 1
}
```

## Exit Codes

- `0` - All checks passed ✅
- `1` - One or more checks failed ❌

## Example Output

```
╔════════════════════════════════════════════════════════════╗
║         DDDGuard Code Quality Comprehensive Check          ║
╚════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 🔍 Running Ruff Linter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Ruff: No linting issues

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. 📐 Checking Code Formatting
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Format: All files properly formatted

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. 🔬 Running MyPy Type Checker
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  MyPy: Found 27 type errors
💡 Run 'mypy src/' for detailed error messages

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. 🔐 Checking for Secrets and API Keys
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Security: No hardcoded secrets detected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. 🌐 Checking Language (English Only)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Language: All code in English

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. 📝 Checking Code Conciseness
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Style: No action markers
✅ Style: 7 verbose patterns (acceptable)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Total Python files: 136
  • Total lines of code: 10,641

╔════════════════════════════════════════════════════════════╗
║                  ✅ ALL CHECKS PASSED                      ║
╚════════════════════════════════════════════════════════════╝
```

## Fixing Issues

### Ruff Issues
```bash
# Auto-fix linting issues
ruff check src/ --fix

# Format code
ruff format src/
```

### MyPy Issues
```bash
# View detailed errors
mypy src/

# Common fixes:
# - Add type hints: def func(x: int) -> str:
# - Use type: ignore for known issues: result = func()  # type: ignore[arg-type]
```

### Security Issues
If secrets are detected:
1. Remove hardcoded credentials
2. Use environment variables: `os.getenv("API_KEY")`
3. Add to `.gitignore`: `.env`, `secrets.json`
4. Rotate compromised keys immediately

### Language Issues
If non-English text is found:
1. Translate comments to English
2. Use English variable names
3. Keep user-facing strings in English

## Troubleshooting

### "Command not found"
Install dependencies:
```bash
pip install ruff mypy
# or
uv sync --group dev
```

### "Permission denied"
Make script executable:
```bash
chmod +x scripts/verify_code_quality.sh
```

### "Too many MyPy errors"
MyPy uses gradual typing - errors are informational, not blocking.
Focus on fixing critical errors first (`[union-attr]`, `[arg-type]`).

## Configuration

- **Ruff:** `ruff.toml`
- **MyPy:** `pyproject.toml` -> `[tool.mypy]`
- **Pytest:** `pyproject.toml` -> `[tool.pytest]`

## Best Practices

1. **Run checks before committing**
2. **Fix auto-fixable issues first** (`ruff check --fix`)
3. **Address security issues immediately**
4. **Keep code in English**
5. **Write concise, clear comments**

## Quick Reference

```bash
# Run all checks
./scripts/verify_code_quality.sh

# Fix Ruff issues
ruff check src/ --fix
ruff format src/

# Check types
mypy src/

# Run tests
pytest
```

---

**Questions?** See [CODE_QUALITY.md](../docs/CODE_QUALITY.md) or open an issue.
