#!/bin/bash
# Installation script for Pinterest Scraper and Image Analyzer

set -e

echo "=== Pinterest Scraper and Image Analyzer Installation ==="
echo ""

# Check Python version
echo "Checking Python version..."
python3_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python3_version"

# Check if version is >= 3.8
required_version="3.8"
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✓ Python version is sufficient"
else
    echo "✗ Python 3.8 or higher is required"
    exit 1
fi

# Create virtual environment (optional but recommended)
echo ""
read -p "Create a virtual environment? (recommended) [Y/n]: " create_venv
create_venv=${create_venv:-Y}

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
    echo "To activate the virtual environment:"
    echo "  source venv/bin/activate  (Linux/Mac)"
    echo "  venv\\Scripts\\activate    (Windows)"
    echo ""
    read -p "Press Enter to continue..."
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✓ Python dependencies installed"

# Install Playwright browsers
echo ""
echo "Installing Playwright browsers..."
playwright install chromium
echo "✓ Playwright browsers installed"

# Check for Tesseract
echo ""
echo "Checking for Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    tesseract_version=$(tesseract --version 2>&1 | head -n1)
    echo "✓ Found $tesseract_version"
else
    echo "✗ Tesseract OCR not found"
    echo ""
    echo "Please install Tesseract OCR:"
    echo "  Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "  macOS: brew install tesseract"
    echo "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
    echo ""
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. If using a virtual environment, activate it"
echo "2. Install Tesseract OCR if not already installed"
echo "3. Run example scripts:"
echo "   ./examples_pinterest.sh"
echo "   ./examples_analyzer.sh"
echo ""
echo "For more information, see README.md"
