#!/bin/bash
# Install voice interaction dependencies for Wintermute POC

echo "Installing voice interaction packages..."
echo ""

# Check if espeak-ng is installed
if ! command -v espeak-ng &> /dev/null; then
    echo "⚠ espeak-ng not found. Please install it:"
    echo ""
    echo "  On Ubuntu/Debian:"
    echo "    sudo apt-get install espeak-ng"
    echo ""
    echo "  On macOS:"
    echo "    brew install espeak-ng"
    echo ""
    echo "Press Enter to continue with Python packages, or Ctrl+C to abort..."
    read
fi

# Install Python packages
echo "Installing Python packages..."
pip install sounddevice numpy soundfile useful-moonshine-onnx kokoro

echo ""
echo "✓ Installation complete!"
echo ""
echo "To test the voice POC, run:"
echo "  python voice_poc.py"
