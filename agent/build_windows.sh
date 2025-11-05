#!/bin/bash
# Build script for creating Windows binary (.exe) from Linux/Mac
# Requires Wine or a Windows VM for actual execution

echo "Building Windows executable using PyInstaller..."
echo "Note: This requires PyInstaller and a Windows environment"
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Install build dependencies
echo "Installing build dependencies..."
pip install -r requirements-build.txt

# Build the executable
echo "Running PyInstaller..."
pyinstaller --clean cif-agent.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "Build complete!"
    echo "Executable location: dist/cif-agent.exe"
    echo ""
    echo "Note: For cross-platform builds, consider using:"
    echo "  - A Windows VM"
    echo "  - Docker with Windows container"
    echo "  - GitHub Actions Windows runner"
else
    echo "Build failed!"
    exit 1
fi

