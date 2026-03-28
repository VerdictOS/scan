#!/bin/bash
# VerdictOS Scan - One-Line Installer
# Usage: curl -fsSL https://verdictos.tech/install.sh | sh

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  VerdictOS Scan - Security Scanner for AI-Generated Code"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=Mac;;
    CYGWIN*)    PLATFORM=Windows;;
    MINGW*)     PLATFORM=Windows;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo "→ Detected platform: ${PLATFORM}"

# Check for Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✅ Python ${PYTHON_VERSION} found"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo "✅ Python ${PYTHON_VERSION} found"
    PYTHON_CMD="python"
else
    echo "❌ Python not found"
    echo ""
    
    if [ "$PLATFORM" = "Mac" ]; then
        echo "Installing Python via Homebrew..."
        if ! command -v brew &> /dev/null; then
            echo "→ Installing Homebrew first..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python3
        PYTHON_CMD="python3"
    elif [ "$PLATFORM" = "Linux" ]; then
        echo "Installing Python..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3 python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3 python3-pip
        else
            echo "Please install Python 3 manually: https://www.python.org/downloads/"
            exit 1
        fi
        PYTHON_CMD="python3"
    else
        echo "Please install Python 3 manually: https://www.python.org/downloads/"
        exit 1
    fi
fi

# Check for pip
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "❌ pip not found"
    echo "→ Installing pip..."
    $PYTHON_CMD -m ensurepip --upgrade
    PIP_CMD="pip3"
fi

echo ""
echo "→ Installing VerdictOS Scan..."
$PIP_CMD install --upgrade verdictos-scan

echo ""
echo "✅ Installation complete!"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Quick Start"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "  Scan your code:"
echo "    verdictos-scan --path ."
echo ""
echo "  With auto-fix suggestions:"
echo "    verdictos-scan --path . --with-fixes"
echo ""
echo "  Generate HTML report:"
echo "    verdictos-scan --path . --html"
echo ""
echo "  Get help:"
echo "    verdictos-scan --help"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "  Documentation: https://github.com/VerdictOS/scan"
echo "  Issues: https://github.com/VerdictOS/scan/issues"
echo "  Support: admin@verdictos.tech"
echo ""
echo "════════════════════════════════════════════════════════════════"

# Verify installation
if command -v verdictos-scan &> /dev/null; then
    echo ""
    echo "🎉 VerdictOS Scan is ready to use!"
    verdictos-scan --version
else
    echo ""
    echo "⚠️  Installation succeeded but 'verdictos-scan' not in PATH"
    echo "   Try: $PYTHON_CMD -m verdictos_scan --help"
fi
