#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Verifying development environment...${NC}"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ "$PYTHON_VERSION" != "3.13" ]]; then
    echo -e "${RED}Error: Python 3.13 is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

# Verify dependencies match CI requirements
echo -e "\n${YELLOW}Checking dependencies...${NC}"
python3 scripts/compare_environments.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Missing required dependencies${NC}"
    exit 1
fi

# Run pre-commit checks
echo -e "\n${YELLOW}Running pre-commit checks...${NC}"
pre-commit run --all-files
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Pre-commit checks failed${NC}"
    exit 1
fi

# Run tests
echo -e "\n${YELLOW}Running tests...${NC}"
pytest
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Tests failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}All checks passed! Environment is ready for development.${NC}"
