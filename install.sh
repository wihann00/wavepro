#!/bin/bash
# Installation script for WaveDump Processor

set -e  # Exit on error

echo "=========================================="
echo "WaveDump Processor - Installation"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Found Python $PYTHON_VERSION"

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ Error: pip is not installed"
    echo "Please install pip for Python 3"
    exit 1
fi

echo "✓ Found pip"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "wdenv" ]; then
    echo "Creating virtual environment 'wdenv'..."
    python3 -m venv wdenv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment 'wdenv' already exists"
fi

echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source wdenv/bin/activate

echo "✓ Virtual environment activated"
echo ""

# Upgrade pip in virtual environment
echo "Upgrading pip..."
pip install --upgrade pip

echo ""

# Install requirements
echo "Installing requirements from requirements.txt..."
pip install -r requirements.txt

echo ""

# Install package in editable mode
echo "Installing WaveDump Processor..."
pip install -e .

echo ""
echo "=========================================="
echo "✓ Installation Complete!"
echo "=========================================="
echo ""
echo "IMPORTANT: The virtual environment needs to be activated."
echo ""
echo "Please run this command now:"
echo "  source wdenv/bin/activate"
echo ""
echo "Then you can use the command:"
echo "  wavepro --help"
echo ""
echo "Example usage:"
echo "  wavepro input.dat output.root"
echo "  wavepro /data/parent/ --batch"
echo ""
echo "To deactivate the virtual environment when done:"
echo "  deactivate"
echo ""
echo "For more information, see README.md"
echo "=========================================="