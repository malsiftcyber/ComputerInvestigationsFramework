@echo off
REM Build script for Windows Kernel Agent executable

echo Building CIF Kernel Agent Windows executable...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install PyInstaller if not present
python -m pip install pyinstaller --quiet

REM Install build dependencies
python -m pip install -r requirements-build.txt --quiet

REM Install agent dependencies
python -m pip install python-socketio psutil pywin32 --quiet

REM Build the executable
python -m PyInstaller --clean cif-kernel-agent.spec

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful!
echo Executable location: dist\cif-kernel-agent.exe
echo.
echo NOTE: This agent uses Windows kernel APIs and should be run as Administrator
echo for full functionality. Some antivirus software may flag kernel-level access.
pause

