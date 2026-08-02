@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo  ========================================
echo   ai-audio-notify installer
echo  ========================================
echo.
echo  Scans this PC for Claude Code, the Claude
echo  Desktop app, Cursor, and Antigravity, then
echo  installs sound hooks.
echo.

set "PY_CMD="

:: 1. Try py launcher
where py >nul 2>&1
if !ERRORLEVEL!==0 (
  py -3 -c "import sys" >nul 2>&1
  if !ERRORLEVEL!==0 set "PY_CMD=py -3"
)

:: 2. Try python executable if py not found
if "!PY_CMD!"=="" (
  where python >nul 2>&1
  if !ERRORLEVEL!==0 (
    python -c "import sys" >nul 2>&1
    if !ERRORLEVEL!==0 set "PY_CMD=python"
  )
)

:: 3. Try python3 executable if python not found
if "!PY_CMD!"=="" (
  where python3 >nul 2>&1
  if !ERRORLEVEL!==0 (
    python3 -c "import sys" >nul 2>&1
    if !ERRORLEVEL!==0 set "PY_CMD=python3"
  )
)

:: 4. Search standard Windows Python installation paths if still not found
if "!PY_CMD!"=="" (
  for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python3*\python.exe"
    "C:\Python3*\python.exe"
    "%ProgramFiles%\Python3*\python.exe"
    "%ProgramFiles(x86)%\Python3*\python.exe"
  ) do (
    if "!PY_CMD!"=="" (
      if exist "%%~fP" (
        "%%~fP" -c "import sys" >nul 2>&1
        if !ERRORLEVEL!==0 set "PY_CMD="%%~fP""
      )
    )
  )
)

if "!PY_CMD!"=="" (
  echo  [!] Python 3 was not found on PATH or in standard install locations.
  echo.
  echo  Please install Python 3 from:
  echo    https://www.python.org/downloads/
  echo  During setup, make sure to check "Add python.exe to PATH".
  echo.
  echo  Then run Install.bat again.
  echo.
  pause
  exit /b 1
)

echo  Using Python launcher: !PY_CMD!
echo.
!PY_CMD! "%~dp0install.py" %*
set "EXITCODE=!ERRORLEVEL!"

echo.
if not "!EXITCODE!"=="0" (
  echo  Installer exited with code !EXITCODE!.
) else (
  echo  Installation finished successfully.
)
echo.
pause
exit /b !EXITCODE!
