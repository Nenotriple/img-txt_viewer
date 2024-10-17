@echo off
setlocal


REM ============================
REM Author: Nenotriple
REM Version: v1.00
REM ============================
REM Script to set up a Python virtual environment, install dependencies, and run a specified Python script.


REM ============================
REM Variables
REM ============================

REM The name of the Python script to be executed after setting up the virtual environment.
REM If left empty, no script will be executed.
set "PYTHON_SCRIPT=img-txt_viewer.pyw"

REM The directory where the virtual environment will be created.
REM By default, it is set to "venv".
set "VENV_DIR=venv"

REM The directory of the current script.
REM %~dp0 is a batch parameter that expands to the drive and path of the script.
set "SCRIPT_DIR=%~dp0"


REM ============================
REM Navigate to the script directory
REM ============================
cd /d "%SCRIPT_DIR%" || (
    powershell -Command "Write-Host 'Set current directory... ' -NoNewline; Write-Host 'FAIL' -ForegroundColor Red"
    pause
    exit /b 1
)
powershell -Command "Write-Host 'Set current directory... ' -NoNewline; Write-Host 'OK' -ForegroundColor Green"


REM ============================
REM Check Python install
REM ============================
python --version >nul 2>&1 || (
    powershell -Command "Write-Host 'Python... ' -NoNewline; Write-Host 'FAIL' -ForegroundColor Red; Write-Host 'Python is not installed. Please install Python and try again.' -ForegroundColor Red"
    pause
    exit /b 1
)
powershell -Command "Write-Host 'Python... ' -NoNewline; Write-Host 'OK' -ForegroundColor Green"


REM ============================
REM Check pip install
REM ============================
pip --version >nul 2>&1 || (
    powershell -Command "Write-Host 'pip... ' -NoNewline; Write-Host 'FAIL' -ForegroundColor Red; Write-Host 'pip is not installed. Please install pip and try again.' -ForegroundColor Red"
    pause
    exit /b 1
)
powershell -Command "Write-Host 'pip... ' -NoNewline; Write-Host 'OK' -ForegroundColor Green"


REM ============================
REM Check if the virtual environment already exists
REM ============================
echo.
if exist "%VENV_DIR%" (
    powershell -Command "Write-Host 'Virtual environment already exists: ' -ForegroundColor Yellow -NoNewline; Write-Host '\"%SCRIPT_DIR%\%VENV_DIR%\"' -ForegroundColor Green -NoNewline; Write-Host ' OK' -ForegroundColor Blue"
) else (
    powershell -Command "Write-Host 'Creating a Python virtual environment: ' -ForegroundColor Yellow -NoNewline; Write-Host '\"%SCRIPT_DIR%\%VENV_DIR%\"' -ForegroundColor Green -NoNewline"
    python -m venv "%VENV_DIR%" || (
        powershell -Command "Write-Host 'An error occurred while creating the virtual environment.' -ForegroundColor Red"
        pause
        exit /b 1
    )
    powershell -Command "Write-Host ' OK' -ForegroundColor Blue"
)


REM ============================
REM Check for requirements.txt and install dependencies
REM ============================
if exist "requirements.txt" (
    powershell -Command "Write-Host 'Found requirements.txt: ' -ForegroundColor Yellow -NoNewline; Write-Host 'Installing dependencies...' -ForegroundColor Green"
    echo.
    call "%SCRIPT_DIR%\%VENV_DIR%\Scripts\activate.bat"
    pip install -r "requirements.txt" || (
        powershell -Command "Write-Host 'Installing dependencies... ' -NoNewline; Write-Host 'FAIL' -ForegroundColor Red"
        pause
        exit /b 1
    )
    echo.
    powershell -Command "Write-Host 'Installing dependencies... ' -ForegroundColor Yellow -NoNewline; Write-Host 'OK' -ForegroundColor Green"
) else (
    powershell -Command "Write-Host 'No requirements.txt found: ' -ForegroundColor Yellow -NoNewline; Write-Host 'Skipping dependency installation.' -ForegroundColor Green"
)


REM ============================
REM Activate the virtual environment and launch the user-defined Python script
REM ============================
echo.
powershell -Command "Write-Host 'Activating the virtual environment...' -ForegroundColor Blue"
call "%SCRIPT_DIR%\%VENV_DIR%\Scripts\activate.bat" || (
    powershell -Command "Write-Host 'Activating the virtual environment... ' -NoNewline; Write-Host 'FAIL' -ForegroundColor Red"
    pause
    exit /b 1
)


REM ============================
REM Launch the user-defined Python script
REM ============================
echo.
if "%PYTHON_SCRIPT%"=="" (
    powershell -Command "Write-Host 'Auto-Launch: ' -ForegroundColor Yellow -NoNewline; Write-Host 'Skipping' -ForegroundColor Green"
) else (
    powershell -Command "Write-Host 'Launching: ' -ForegroundColor Blue -NoNewline; Write-Host '%PYTHON_SCRIPT%' -ForegroundColor Green"
    python "%PYTHON_SCRIPT%" || (
        powershell -Command "Write-Host 'Launching... ' -NoNewline; Write-Host 'FAIL' -ForegroundColor Red"
        pause
        exit /b 1
    )
)


REM ============================
REM Keep the command prompt open
REM ============================


echo.
call cmd /k


REM ============================
REM End of script
REM ============================
endlocal
