@echo off
setlocal


REM Set up a Python virtual environment and run a specified Python script.


REM Variables
set "PYTHON_SCRIPT=img-txt_viewer.py"
set "VENV_DIR=venv"
set "SCRIPT_DIR=%~dp0"


REM Navigate to the script directory
cd /d "%SCRIPT_DIR%" || (
    echo Set current directory... FAIL
    pause
    exit /b 1
)
echo Set current directory... OK


REM Check if the virtual environment already exists
if exist "%VENV_DIR%" (
    echo Virtual environment already exists: "%SCRIPT_DIR%\%VENV_DIR%"
) else (
    echo Creating a Python virtual environment: "%SCRIPT_DIR%\%VENV_DIR%"
    python -m venv "%VENV_DIR%" || (
        echo An error occurred while creating the virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created.
)


REM Activate the virtual environment
call "%SCRIPT_DIR%\%VENV_DIR%\Scripts\activate.bat" || (
    echo Activating the virtual environment... FAIL
    pause
    exit /b 1
)
echo Virtual environment activated.


REM Launch the user-defined Python script
if "%PYTHON_SCRIPT%"=="" (
    echo Auto-Launch: Skipping
) else (
    echo Launching: %PYTHON_SCRIPT%
    python "%PYTHON_SCRIPT%" || (
        echo Launching... FAIL
        pause
        exit /b 1
    )
)


echo.
call cmd /k


endlocal
