# Building Windows Binary Release

This document explains how to create a Windows executable (.exe) for the CIF Agent.

## Quick Start

### On Windows Machine

```cmd
cd agent
build_windows.bat
```

The executable will be created at `dist/cif-agent.exe`

## Prerequisites

- Python 3.8+ installed
- pip package manager
- PyInstaller (will be installed automatically)

## Build Methods

### Method 1: Batch Script (Windows)

```cmd
build_windows.bat
```

This script:
1. Checks for Python
2. Installs PyInstaller if needed
3. Installs build dependencies
4. Runs PyInstaller to create the executable

### Method 2: Python Script (Cross-platform)

```bash
python build_windows.py
```

### Method 3: Manual PyInstaller

```bash
pip install pyinstaller
pip install -r requirements-build.txt
pyinstaller --clean cif-agent.spec
```

### Method 4: GitHub Actions (Automated)

Push to the repository and GitHub Actions will automatically build the Windows executable on Windows runners.

## Build Configuration

The build configuration is defined in `cif-agent.spec`:

- **One-file executable**: All dependencies bundled into a single `.exe`
- **Console mode**: Shows command-line output (useful for debugging)
- **UPX compression**: Reduces file size (optional, can be disabled)
- **Hidden imports**: Explicitly includes required modules

## Output

After building, you'll find:
- `dist/cif-agent.exe` - The standalone executable
- `build/` - Temporary build files (can be deleted)

## Distribution

The `cif-agent.exe` file is completely standalone:
- ✅ No Python installation required
- ✅ All dependencies included
- ✅ Single file deployment
- ✅ Works on Windows 7+ (64-bit)

Simply copy `cif-agent.exe` to any Windows machine and run:
```cmd
cif-agent.exe --server-url http://your-server:5000
```

## File Size

The executable is typically 15-25 MB, depending on:
- Included dependencies
- UPX compression settings
- Python version used

## Troubleshooting

### "Failed to execute script"

- Ensure all dependencies are installed before building
- Check that hidden imports are correct in `.spec` file
- Try building without UPX compression (set `upx=False` in `.spec`)

### Antivirus False Positives

Some antivirus software may flag PyInstaller executables. This is a known issue. Options:
- Sign the executable with a code signing certificate
- Whitelist the executable
- Use a different packager (cx_Freeze, Nuitka)

### Missing Modules

If the executable fails at runtime with missing module errors:
1. Add the module to `hiddenimports` in `cif-agent.spec`
2. Rebuild the executable

## Advanced Configuration

Edit `cif-agent.spec` to customize:
- Icon file (add `icon='path/to/icon.ico'`)
- Window mode (change `console=False` for GUI)
- File size optimization
- Additional data files
- Version information

## Security Considerations

- Code signing: Consider signing the executable with a certificate
- Version control: Include version information in the executable
- Updates: Implement update mechanism for deployed agents
- Authentication: Ensure secure communication with server

