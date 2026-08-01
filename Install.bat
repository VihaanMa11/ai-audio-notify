@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo  ========================================
echo   ai-audio-notify installer
echo  ========================================
echo.
echo  Scans this PC for Claude Code, Cursor,
echo  and Antigravity, then installs sound hooks.
echo.

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  py -3 -c "import sys" >nul 2>&1
  if %ERRORLEVEL%==0 (
    echo  Using: py -3
    echo.
    py -3 "%~dp0install.py" %*
    goto :finish
  )
)

where python >nul 2>&1
if %ERRORLEVEL%==0 (
  python -c "import sys" >nul 2>&1
  if %ERRORLEVEL%==0 (
    echo  Using: python
    echo.
    python "%~dp0install.py" %*
    goto :finish
  )
)

where python3 >nul 2>&1
if %ERRORLEVEL%==0 (
  python3 -c "import sys" >nul 2>&1
  if %ERRORLEVEL%==0 (
    echo  Using: python3
    echo.
    python3 "%~dp0install.py" %*
    goto :finish
  )
)

echo  [!] Python 3 was not found on PATH.
echo.
echo  Install Python 3 from:
echo    https://www.python.org/downloads/
echo  During setup, enable "Add python.exe to PATH".
echo.
echo  Then double-click Install.bat again.
echo.
pause
exit /b 1

:finish
set "EXITCODE=%ERRORLEVEL%"
echo.
if not "%EXITCODE%"=="0" (
  echo  Installer exited with code %EXITCODE%.
) else (
  echo  You can close this window.
)
echo.
pause
exit /b %EXITCODE%
