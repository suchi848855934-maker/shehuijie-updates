@echo off
setlocal
cd /d "%~dp0"
set "PYW="
for /f "delims=" %%P in ('py -3 -c "import sys,os; print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))" 2^>nul') do set "PYW=%%P"
if not defined PYW (
  echo Python was not found. Please install Python 3.
  pause
  exit /b 1
)
if not exist "%PYW%" (
  echo pythonw.exe was not found:
  echo "%PYW%"
  pause
  exit /b 1
)
start "" "%PYW%" "%~dp0launcher.py"
endlocal

