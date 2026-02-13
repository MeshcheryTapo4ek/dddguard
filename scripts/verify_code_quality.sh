#!/usr/bin/env bash
# Comprehensive code quality check: tests, linting, type checking, security, and style

set -e

# Run from project root (directory containing pyproject.toml)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Exit codes
EXIT_CODE=0

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         DDDGuard Code Quality Comprehensive Check          ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""


# 1. TESTS

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}1. 🧪 Running Tests${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Ensure project root is on PYTHONPATH so "tests" package is importable
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

if command -v pytest &> /dev/null; then
    if pytest tests/ -q; then
        echo -e "${GREEN}✅ Tests: All passed${NC}"
    else
        echo -e "${RED}❌ Tests: Some tests failed${NC}"
        EXIT_CODE=1
    fi
elif command -v uv &> /dev/null; then
    if uv run pytest tests/ -q; then
        echo -e "${GREEN}✅ Tests: All passed${NC}"
    else
        echo -e "${RED}❌ Tests: Some tests failed${NC}"
        EXIT_CODE=1
    fi
else
    echo -e "${RED}❌ pytest not found. Install: pip install pytest (or use uv run pytest)${NC}"
    EXIT_CODE=1
fi
echo ""


# 2. RUFF LINTING

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}2. 🔍 Running Ruff Linter${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v ruff &> /dev/null; then
    if ruff check src/ --output-format=concise; then
        echo -e "${GREEN}✅ Ruff: No linting issues${NC}"
    else
        echo -e "${RED}❌ Ruff: Found linting issues${NC}"
        EXIT_CODE=1
    fi
else
    echo -e "${RED}❌ Ruff not found. Install: pip install ruff${NC}"
    EXIT_CODE=1
fi
echo ""


# 3. RUFF FORMATTING

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}3. 📐 Checking Code Formatting${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v ruff &> /dev/null; then
    if ruff format --check src/; then
        echo -e "${GREEN}✅ Format: All files properly formatted${NC}"
    else
        echo -e "${YELLOW}⚠️  Format: Some files need formatting (run: ruff format src/)${NC}"
        EXIT_CODE=1
    fi
else
    echo -e "${RED}❌ Ruff not found${NC}"
    EXIT_CODE=1
fi
echo ""


# 4. MYPY TYPE CHECKING

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}4. 🔬 Running MyPy Type Checker${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v mypy &> /dev/null; then
    MYPY_OUTPUT=$(mypy src/ 2>&1 || true)
    ERROR_COUNT=$(echo "$MYPY_OUTPUT" | grep -c "error:" || echo "0")
    
    if [ "$ERROR_COUNT" -eq 0 ]; then
        echo -e "${GREEN}✅ MyPy: No type errors${NC}"
    else
        echo -e "${YELLOW}⚠️  MyPy: Found $ERROR_COUNT type errors${NC}"
        echo "$MYPY_OUTPUT" | head -20
        if [ "$ERROR_COUNT" -gt 20 ]; then
            echo -e "${YELLOW}... (showing first 20 errors)${NC}"
        fi
        echo ""
        echo -e "${YELLOW}💡 Run 'mypy src/' for detailed error messages${NC}"
        # MyPy errors are warnings, not blocking
    fi
else
    echo -e "${RED}❌ MyPy not found. Install: pip install mypy${NC}"
    EXIT_CODE=1
fi
echo ""

# 5. DDDGUARD LINTER (Architecture Rules)
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}5. 🏛️  Running DDDGuard Architecture Linter${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v dddguard &> /dev/null; then
    # Run dddguard lint in auto mode (non-interactive)
    dddguard lint --auto
    DDDGUARD_EXIT=$?
    
    # Check if linting passed
    if [ $DDDGUARD_EXIT -eq 0 ]; then
        echo -e "${GREEN}✅ DDDGuard: Architecture rules validated${NC}"
    else
        echo -e "${RED}❌ DDDGuard: Architecture violations found${NC}"
        EXIT_CODE=1
    fi
else
    echo -e "${YELLOW}⚠️  DDDGuard not found. Skipping architecture validation.${NC}"
    echo -e "${YELLOW}   Install: uv tool install dddguard${NC}"
fi
echo ""

# 6. SECURITY: SECRET DETECTION (whole repo)
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}6. 🔐 Checking for Secrets and API Keys (repo-wide)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Dirs to skip in repo-wide scans
FIND_EXCLUDE="-path './.git' -prune -o \
    -path './.venv' -prune -o \
    -path './venv' -prune -o \
    -path './.mypy_cache' -prune -o \
    -path './.ruff_cache' -prune -o \
    -path './.pytest_cache' -prune -o \
    -path './__pycache__' -prune -o \
    -path './.eggs' -prune -o \
    -path './dist' -prune -o \
    -path './build' -prune -o \
    -path './htmlcov' -prune -o \
    -path './node_modules' -prune -o \
    -path '*/node_modules' -prune -o"

# File extensions to scan
SCAN_EXTS="-name '*.py' -o -name '*.yaml' -o -name '*.yml' -o -name '*.toml' -o -name '*.cfg' -o -name '*.ini' -o -name '*.json' -o -name '*.env' -o -name '*.sh' -o -name '*.md' -o -name '*.txt'"

# Patterns to detect secrets
PATTERNS=(
    'password\s*=\s*["\047][^"\047]{3,}'
    'api[_-]?key\s*=\s*["\047][^"\047]{10,}'
    'secret\s*=\s*["\047][^"\047]{10,}'
    'token\s*=\s*["\047][^"\047]{10,}'
    'aws[_-]?access[_-]?key'
    'AKIA[0-9A-Z]{16}'
    'sk-[a-zA-Z0-9]{32,}'
    'ghp_[a-zA-Z0-9]{36,}'
    'glpat-[a-zA-Z0-9_-]{20,}'
    'private[_-]?key\s*=\s*["\047]'
    'BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY'
)

SECRETS_FOUND=0

for pattern in "${PATTERNS[@]}"; do
    MATCHES=$(eval "find . $FIND_EXCLUDE -type f \( $SCAN_EXTS \) -print" 2>/dev/null | \
        xargs grep -Eni "$pattern" 2>/dev/null | \
        grep -v 'verify_code_quality.sh\|CODE_QUALITY.md\|README.md.*scripts' || true)

    if [ -n "$MATCHES" ]; then
        if [ $SECRETS_FOUND -eq 0 ]; then
            echo -e "${RED}❌ Potential secrets detected:${NC}"
        fi
        echo "$MATCHES" | head -3
        SECRETS_FOUND=$((SECRETS_FOUND + 1))
    fi
done

if [ $SECRETS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ Security: No hardcoded secrets detected${NC}"
else
    echo -e "${RED}❌ Security: Found potential secrets in $SECRETS_FOUND pattern(s)${NC}"
    EXIT_CODE=1
fi
echo ""

# 7. LANGUAGE CHECK: ENGLISH ONLY (whole repo)
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}7. 🌐 Checking Language (English Only, repo-wide)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check for non-Latin script in source (expect English-only outside excluded paths)
# Exclude: presentation/ (slides), test fixtures with intentional non-ASCII data
NON_LATIN_FILES=$(eval "find . $FIND_EXCLUDE -path './presentation' -prune -o -type f \( $SCAN_EXTS \) -print" 2>/dev/null | \
    xargs grep -l '[а-яА-ЯёЁ]' 2>/dev/null | \
    grep -v 'verify_code_quality.sh\|test_read_file.py' || true)

if [ -n "$NON_LATIN_FILES" ]; then
    NON_LATIN_COUNT=$(echo "$NON_LATIN_FILES" | wc -l)
    echo -e "${RED}❌ Language: Found non-Latin text in $NON_LATIN_COUNT file(s)${NC}"
    echo "$NON_LATIN_FILES" | head -10
    if [ "$NON_LATIN_COUNT" -gt 10 ]; then
        echo -e "${YELLOW}... (showing first 10)${NC}"
    fi
    EXIT_CODE=1
else
    echo -e "${GREEN}✅ Language: Source is English-only ${NC}"
fi
echo ""


# 8. CODE STYLE: VERBOSITY CHECK

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}8. 📝 Checking Code Conciseness${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check for TODO/FIXME markers
ACTION_MARKERS=$(find src -name "*.py" -type f -exec grep -c 'TODO\|FIXME\|XXX\|HACK' {} + 2>/dev/null | \
    awk -F: '{sum += $2} END {print sum}' || echo "0")

if [ "$ACTION_MARKERS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $ACTION_MARKERS TODO/FIXME/XXX markers${NC}"
    find src -name "*.py" -type f -exec grep -Hn 'TODO\|FIXME\|XXX\|HACK' {} \; 2>/dev/null | head -5
else
    echo -e "${GREEN}✅ Style: No action markers${NC}"
fi

# Check for verbose patterns
VERBOSE_PATTERNS=$(find src -name "*.py" -type f -exec grep -i '#.*\(very\|really\|basically\|actually\|simply\|just\|obviously\|clearly\)' {} + 2>/dev/null | wc -l || echo "0")

if [ "$VERBOSE_PATTERNS" -gt 10 ]; then
    echo -e "${YELLOW}⚠️  Found $VERBOSE_PATTERNS potentially verbose comments${NC}"
elif [ "$VERBOSE_PATTERNS" -gt 0 ]; then
    echo -e "${GREEN}✅ Style: $VERBOSE_PATTERNS verbose patterns (acceptable)${NC}"
else
    echo -e "${GREEN}✅ Style: No verbose patterns${NC}"
fi
echo ""


# 9. SUMMARY

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📊 Summary${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

TOTAL_LINES=$(find src -name "*.py" -type f -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
TOTAL_FILES=$(find src -name "*.py" -type f | wc -l)

echo "  • Total Python files: $TOTAL_FILES"
echo "  • Total lines of code: $TOTAL_LINES"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  ✅ ALL CHECKS PASSED                      ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                  ❌ SOME CHECKS FAILED                     ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}💡 Quick fixes:${NC}"
    echo "  • Tests:        pytest tests/ -v"
    echo "  • Ruff issues:  ruff check src/ --fix"
    echo "  • Formatting:   ruff format src/"
    echo "  • Type errors:  mypy src/"
fi

exit $EXIT_CODE
