#!/bin/bash
# Pre-release verification script
# Run this before your first git commit

echo "🔍 Checking Personal Dashboard for Git release readiness..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Check 1: Verify .gitignore exists
echo "1️⃣  Checking .gitignore..."
if [ -f .gitignore ]; then
    echo -e "${GREEN}✓${NC} .gitignore exists"
else
    echo -e "${RED}✗${NC} .gitignore not found!"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: Verify .env.example exists
echo "2️⃣  Checking .env.example..."
if [ -f .env.example ]; then
    echo -e "${GREEN}✓${NC} .env.example exists"
    # Check if it contains placeholder values
    if grep -q "your_api_key_here\|your_.*_here\|change-this" .env.example; then
        echo -e "${GREEN}✓${NC} .env.example contains placeholder values"
    else
        echo -e "${YELLOW}⚠${NC}  .env.example might contain real values"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}✗${NC} .env.example not found!"
    ERRORS=$((ERRORS + 1))
fi

# Check 3: Verify sensitive files are in .gitignore
echo "3️⃣  Checking sensitive files are ignored..."
SENSITIVE_FILES=(".env" "credentials.json" "token.pickle" "token.json" "data/local_events.json" "*.log")

for file in "${SENSITIVE_FILES[@]}"; do
    if grep -q "$file" .gitignore; then
        echo -e "${GREEN}✓${NC} $file is in .gitignore"
    else
        echo -e "${RED}✗${NC} $file is NOT in .gitignore!"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check 4: Verify example files exist
echo "4️⃣  Checking example files..."
EXAMPLE_FILES=("credentials.example.json" "data/local_events.example.json")

for file in "${EXAMPLE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file exists"
    else
        echo -e "${YELLOW}⚠${NC}  $file not found (recommended for users)"
        WARNINGS=$((WARNINGS + 1))
    fi
done

# Check 5: Look for potential secrets in tracked files
echo "5️⃣  Scanning for potential secrets in code..."
if git ls-files >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠${NC}  Git repository already initialized, checking tracked files..."
    
    # Check if .env or credentials are tracked
    if git ls-files | grep -qE "^\.env$|^credentials\.json$|^token\.pickle$"; then
        echo -e "${RED}✗${NC} DANGER: Sensitive files are tracked by git!"
        echo "  Run: git rm --cached .env credentials.json token.pickle"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓${NC} No sensitive files tracked by git"
    fi
else
    echo -e "${GREEN}✓${NC} Git not initialized yet (good)"
fi

# Check 6: Verify no hardcoded secrets in Python files
echo "6️⃣  Checking for hardcoded secrets in Python files..."
if grep -rn --include="*.py" -E "api[_-]?key\s*=\s*['\"][^'\"]*['\"]|password\s*=\s*['\"][^'\"]*['\"]|secret\s*=\s*['\"][^'\"]*['\"]" app/ 2>/dev/null | grep -vE "getenv|os\.environ|config\.|example"; then
    echo -e "${RED}✗${NC} Found potential hardcoded secrets in Python files!"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} No hardcoded secrets found in Python files"
fi

# Check 7: Verify requirements.txt exists
echo "7️⃣  Checking requirements.txt..."
if [ -f requirements.txt ]; then
    echo -e "${GREEN}✓${NC} requirements.txt exists"
else
    echo -e "${RED}✗${NC} requirements.txt not found!"
    ERRORS=$((ERRORS + 1))
fi

# Check 8: Verify documentation exists
echo "8️⃣  Checking documentation..."
DOC_FILES=("README.md" "SETUP.md")
for file in "${DOC_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file exists"
    else
        echo -e "${YELLOW}⚠${NC}  $file not found (recommended)"
        WARNINGS=$((WARNINGS + 1))
    fi
done

# Check 9: List files that would be committed
echo "9️⃣  Preview of files that would be committed (if git initialized)..."
if [ ! -d .git ]; then
    echo -e "${YELLOW}ℹ${NC}  Simulating git add . (git not initialized)"
    echo "Sample files that would be included:"
    find . -type f ! -path "./.venv/*" ! -path "./__pycache__/*" ! -name "*.pyc" ! -name ".env" ! -name "credentials.json" ! -name "token.pickle" ! -name "*.log" | head -20
    echo "  ... (showing first 20 files)"
fi

# Summary
echo ""
echo "=================================="
echo "📊 SUMMARY"
echo "=================================="

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ Found $ERRORS error(s)${NC}"
    echo "Please fix the errors before committing!"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $WARNINGS warning(s)${NC}"
    echo "You may want to address these before committing."
    exit 0
else
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Your repository is ready for git release! 🚀"
    echo ""
    echo "Next steps:"
    echo "  1. git init"
    echo "  2. git add ."
    echo "  3. git commit -m 'Initial commit'"
    echo "  4. git remote add origin <your-repo-url>"
    echo "  5. git push -u origin main"
    exit 0
fi
