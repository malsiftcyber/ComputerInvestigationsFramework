@echo off
REM Build script for Windows executable

echo Building CIF Agent Windows executable...

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

REM Build the executable
python -m PyInstaller --clean cif-agent.spec

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful!
echo Executable location: dist\cif-agent.exe
echo.
echo You can now distribute dist\cif-agent.exe to Windows endpoints.
pause

