# Build script for creating Windows binary (.exe)

# This script builds a standalone Windows executable using PyInstaller

import os
import sys
import subprocess
import platform

def build_windows_exe():
    """Build Windows executable using PyInstaller"""
    
    if platform.system() != 'Windows':
        print("This script is designed for Windows. For cross-platform builds,")
        print("use PyInstaller directly with the .spec file.")
        return
    
    print("Building Windows executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-build.txt"])
    
    # Build the executable
    print("Running PyInstaller...")
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "cif-agent.spec"
    ])
    
    print("\nBuild complete!")
    print("Executable location: dist/cif-agent.exe")
    print("\nYou can distribute this .exe file to Windows endpoints.")

if __name__ == '__main__':
    build_windows_exe()

