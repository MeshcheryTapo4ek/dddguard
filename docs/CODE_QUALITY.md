# Code Quality Tools

DDDGuard uses modern tools to ensure code quality.

## 🔍 Available Tools

### 1. **Ruff** - Linter and Formatter
Fast Rust-based linter replacing multiple Python tools (Flake8, isort, pyupgrade, etc.).

```bash
# Check code
ruff check src/ tests/

# Auto-fix issues
ruff check src/ tests/ --fix

# Format code
ruff format src/ tests/
```

**Configuration:** `ruff.toml` in project root.

### 2. **MyPy** - Static Type Checker
Validates type annotations.

```bash
# Basic check
mypy src/

# Detailed output
mypy src/ --show-error-codes
```

**Configuration:** `[tool.mypy]` in `pyproject.toml`.

### 3. **Pytest** - Testing Framework
Runs the full test suite (173 tests).

```bash
# Run all tests
pytest

# With coverage
pytest --cov=dddguard --cov-report=html
```

**Configuration:** `[tool.pytest.ini_options]` in `pyproject.toml`.

## 🚀 Quick Start

### Comprehensive Quality Check

Run one script for all checks:

```bash
./scripts/verify_code_quality.sh
```

This script performs:
1. ✅ **Ruff linter** - Style and potential errors
2. ✅ **Ruff formatter** - Formatting validation
3. ⚠️  **MyPy** - Type checking (non-blocking, informational)
4. 🔐 **Security scan** - Hardcoded secrets detection
5. 🌐 **Language check** - English-only validation
6. 📝 **Style analysis** - Code conciseness

### Quick Fixes

```bash
# Fix Ruff issues
ruff check src/ --fix

# Format code
ruff format src/

# Check types
mypy src/
```

## 📊 Results

### Current Project Status

```
✅ Ruff: All checks passed
✅ Formatting: 136 files formatted
⚠️  MyPy: 27 errors in 8/136 files (gradual typing)
✅ Tests: 173/173 passed
✅ Security: No hardcoded secrets
✅ Language: English only
```

### Fix Priority

1. **Critical** (blocks CI):
   - Ruff errors
   - Failing tests
   - Security issues (hardcoded secrets)

2. **Important** (improves reliability):
   - MyPy `[union-attr]` errors - may cause runtime errors
   - MyPy `[arg-type]` errors - incorrect argument types

3. **Cosmetic** (improves readability):
   - MyPy `[no-any-return]` errors
   - MyPy `[var-annotated]` errors

## 🔧 Configuration

### Ruff (`ruff.toml`)

Configured for S-DDD architecture:
- Allows relative imports within contexts
- Excludes overly strict rules for DI patterns
- Different rules for tests vs production code

Key settings:
```toml
line-length = 100
target-version = "py310"
select = ["F", "E", "W", "I", "N", "UP", "B", "SIM", "RET", "ARG", "PTH", "PL", "RUF"]
```

### MyPy (`pyproject.toml`)

Configured for gradual typing:
- `check_untyped_defs = true` - Checks types even without full annotation
- `disallow_untyped_defs = false` - Doesn't require annotations everywhere (yet)
- `namespace_packages = true` - Supports S-DDD structure

```toml
[tool.mypy]
python_version = "3.10"
mypy_path = "src"
namespace_packages = true
explicit_package_bases = true
```

### Pytest (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

## 🎯 Recommendations

### Before Committing

```bash
# Fix style
ruff check src/ tests/ --fix
ruff format src/ tests/

# Verify everything
./scripts/verify_code_quality.sh
```

### CI/CD

Use `verify_code_quality.sh` in your CI pipeline:

```yaml
# .github/workflows/quality.yml
- name: Check code quality
  run: |
    uv sync --group dev
    ./scripts/verify_code_quality.sh
```

### Git Hooks

Set up pre-commit hook:

```bash
# .git/hooks/pre-commit
#!/bin/bash
./scripts/verify_code_quality.sh || {
    echo "Quality checks failed. Fix issues before committing."
    exit 1
}
```

## 📚 Additional Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)

## ❓ FAQ

### Why doesn't MyPy block the build?

MyPy is configured as "informational" rather than "blocking" because:
1. Gradual typing - we improve types iteratively
2. Some MyPy errors relate to external libraries
3. Ruff + tests already ensure baseline quality

### How to fix MyPy errors?

1. Run `mypy src/` for full error list
2. Fix errors in files (add type hints, None checks, etc.)
3. Run mypy again to verify
4. Use `# type: ignore[error-code]` for known issues

### Which Ruff rules are enabled?

See `ruff.toml` -> `[lint] select` section. Main categories:
- **F** - Pyflakes (basic errors)
- **E/W** - pycodestyle (PEP8 style)
- **I** - isort (import sorting)
- **B** - bugbear (potential bugs)
- **PTH** - pathlib (use Path instead of os.path)
- **RUF** - Ruff-specific rules

### How to add a new Ruff rule?

Edit `ruff.toml`:

```toml
[lint]
select = [
    # ... existing rules ...
    "NEW",  # Add new rule category
]
```

Then run `ruff check` to verify.

### What secrets does the security scan detect?

Patterns detected:
- `password = "..."`
- `api_key = "..."`
- `secret = "..."`
- `token = "..."`
- AWS keys: `AKIA...`
- GitHub tokens: `ghp_...`
- OpenAI keys: `sk-...`

If detected, remove hardcoded credentials and use environment variables.
