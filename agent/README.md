# Agent installation and usage instructions

## Installation

### Python Installation (Cross-platform)

```bash
cd agent
pip install -e .
```

Or install dependencies manually:
```bash
pip install python-socketio psutil
```

For Windows-specific features (file owner, attributes):
```bash
pip install python-socketio psutil pywin32
```

### Windows Binary (.exe) Installation

For Windows endpoints, you can build a standalone executable that doesn't require Python to be installed.

#### Building on Windows

1. **Using the batch script** (recommended):
```cmd
build_windows.bat
```

2. **Using Python directly**:
```cmd
python build_windows.py
```

3. **Using PyInstaller manually**:
```cmd
pip install pyinstaller
pip install -r requirements-build.txt
pyinstaller --clean cif-agent.spec
```

The executable will be created in `dist/cif-agent.exe`

#### Building from Linux/Mac (requires Windows VM or Docker)

```bash
./build_windows.sh
```

#### Using Pre-built Binary

If a pre-built binary is available, simply download `cif-agent.exe` and run:
```cmd
cif-agent.exe --server-url http://your-server:5000
```

## Usage

### Python Script

Run the agent:
```bash
cif-agent --server-url http://your-server:5000
```

Or directly:
```bash
python agent.py --server-url http://your-server:5000
```

### Windows Executable

```cmd
cif-agent.exe --server-url http://your-server:5000
```

The agent will automatically register with the server and remain connected, ready to respond to file system queries.

## Windows-Specific Features

When running on Windows with `pywin32` installed, the agent provides additional metadata:
- File owner (domain\username)
- Windows file attributes (hidden, system, read-only, etc.)
- Improved path handling for Windows drive letters

## Distribution

The Windows executable (`cif-agent.exe`) is a standalone binary that includes:
- Python runtime
- All required dependencies
- Agent code

No Python installation is required on the target Windows machine. Simply copy the `.exe` file and run it with the `--server-url` parameter.

For detailed build instructions, see [BUILD_WINDOWS.md](BUILD_WINDOWS.md).

## Windows Kernel-Level Agent

For enhanced performance and access to system-protected files, use the **Windows Kernel Agent**:

```cmd
build_kernel_agent.bat
```

This creates `cif-kernel-agent.exe` which uses Windows kernel APIs directly for:
- Faster file system operations
- Access to protected system files (as administrator)
- More accurate timestamps and metadata
- Lower overhead

**Note**: The kernel agent uses Windows kernel APIs from user-mode. It does NOT require a kernel driver but does benefit from administrator privileges.

See [KERNEL_AGENT.md](KERNEL_AGENT.md) for detailed information about kernel-level access.
