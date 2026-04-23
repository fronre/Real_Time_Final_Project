@echo off
echo ========================================
echo     Installing GCC Compiler
echo ========================================
echo.

echo Checking for GCC...
gcc --version >nul 2>&1
if %errorlevel% equ 0 (
    echo GCC is already installed!
    gcc --version | head -n 1
    goto :end
)

echo GCC not found. Installing MSYS2...
echo.
echo 1. Download MSYS2 from: https://www.msys2.org/
echo 2. Run the installer
echo 3. In MSYS2 terminal, run:
echo    pacman -Syu
echo    pacman -S --needed base-devel mingw-w64-ucrt-x86_64-toolchain
echo.
echo After installation, restart your terminal and try again.
echo.

:end
echo.
pause
