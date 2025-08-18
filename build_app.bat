@echo off
setlocal ENABLEDELAYEDEXPANSION


:: Project Directories
set "BASE_DIR=%~dp0img-txt_viewer\"
set "VENV_DIR=%BASE_DIR%.venv"
set "DIST_DIR=%BASE_DIR%dist"

:: Application Settings
set "APP_ENTRY_POINT=%BASE_DIR%app.py"
set "APP_NAME=img_txt_viewer_v1.97b10"
set "APP_ICON=%BASE_DIR%main\icon.ico"
set "MAIN_DATA=%BASE_DIR%main"

:: Packaging Settings
set "ENABLE_PACKAGE_MODE=true"
set "MODELS_FOLDER=%BASE_DIR%models"
set "PACKAGE_NAME=%APP_NAME%_package"

:: Build Cleanup
set "CLEAN_BUILD_ARTIFACTS=true"


:: ---- Main execution ----
call :main_process_flow
goto :end


:: ---- Process Flow Method ----
:main_process_flow

:: Start
call :print_header "Build Start"
call :set_base_directory
if ERRORLEVEL 1 goto :build_failed

:: Activate
call :activate_virtual_environment
if ERRORLEVEL 1 goto :build_failed

:: Upgrade PyInstaller
call :upgrade_pyinstaller
if ERRORLEVEL 1 goto :build_failed

:: Build
call :build_executable
if ERRORLEVEL 1 goto :build_failed

:: Package
if /i "%ENABLE_PACKAGE_MODE%"=="true" (
    call :package_distribution
    if ERRORLEVEL 1 goto :build_failed
)

:: Cleanup
if /i "%CLEAN_BUILD_ARTIFACTS%"=="true" (
    call :clean_build_artifacts
    if ERRORLEVEL 1 goto :build_failed
)

:: End
call :build_completed_successfully
exit /b 0


:: ---- Build Methods ----
:set_base_directory
call :print_step "Setting base directory to %BASE_DIR%"
cd /d "%BASE_DIR%"
if ERRORLEVEL 1 (
    call :print_error "Failed to change to base directory."
    exit /b 1
)
call :print_success "Base directory set."
exit /b 0


:activate_virtual_environment
call :print_step "Activating venv..."
call "%VENV_DIR%\Scripts\activate.bat" 2>nul
if ERRORLEVEL 1 (
    call :print_error "Venv activation failed."
    exit /b 1
)
call :print_success "Venv activated."
exit /b 0


:upgrade_pyinstaller
call :print_step "Upgrading PyInstaller..."
pip install --upgrade pyinstaller
if ERRORLEVEL 1 (
    call :print_error "PyInstaller upgrade failed."
    exit /b 1
)
call :print_success "PyInstaller upgraded."
exit /b 0


:build_executable
call :print_step "Building executable..."
pyinstaller %APP_ENTRY_POINT% --name %APP_NAME% --onefile --windowed --icon=%APP_ICON% --add-data="%APP_ICON%;." --add-data="%MAIN_DATA%;main"
if ERRORLEVEL 1 (
    call :print_error "Build failed."
    exit /b 1
)
call :print_success "Build complete."
exit /b 0


:: ---- Package Methods ----
:package_distribution
call :print_step "Creating package distribution..."
call :copy_models_folder
if ERRORLEVEL 1 exit /b 1

call :create_zip_package
if ERRORLEVEL 1 exit /b 1

call :print_success "Package distribution created."
exit /b 0


:copy_models_folder
call :print_step "Copying models folder to dist..."
if not exist "%MODELS_FOLDER%" (
    call :print_error "Models folder not found: %MODELS_FOLDER%"
    exit /b 1
)

if not exist "%DIST_DIR%" (
    call :print_error "Dist directory not found: %DIST_DIR%"
    exit /b 1
)

xcopy "%MODELS_FOLDER%" "%DIST_DIR%\%MODELS_FOLDER%" /E /I /Y >nul
if ERRORLEVEL 1 (
    call :print_error "Failed to copy models folder."
    exit /b 1
)
call :print_success "Models folder copied."
exit /b 0


:create_zip_package
call :print_step "Creating zip package..."
cd /d "%DIST_DIR%"
if ERRORLEVEL 1 (
    call :print_error "Failed to change to dist directory."
    exit /b 1
)

powershell -Command "Compress-Archive -Path '%APP_NAME%.exe', '%MODELS_FOLDER%' -DestinationPath '%PACKAGE_NAME%.zip' -CompressionLevel NoCompression -Force"
if ERRORLEVEL 1 (
    call :print_error "Failed to create zip package."
    cd /d "%BASE_DIR%"
    exit /b 1
)

cd /d "%BASE_DIR%"
call :print_success "Zip package created: %DIST_DIR%\%PACKAGE_NAME%.zip"
exit /b 0


:: ---- Utility Methods ----
:print_header
echo.
echo === %~1 ===
echo.
exit /b 0


:print_step
echo.
echo %~1
echo.
exit /b 0


:print_success
echo.
echo [+] %~1
echo.
exit /b 0


:print_error
echo.
echo [!] %~1
echo.
exit /b 0


:build_completed_successfully
call :print_header "Build Success"
echo Executable in dist\
if /i "%ENABLE_PACKAGE_MODE%"=="true" (
    echo Package created: %DIST_DIR%\%PACKAGE_NAME%.zip
)
exit /b 0


:build_failed
call :print_header "Build Failed"
echo See errors above.
exit /b 1


:: ---- Cleanup ----
:clean_build_artifacts
call :print_step "Cleaning build artifacts..."
if exist "build" (
    rmdir /s /q "build"
    if ERRORLEVEL 1 (
        call :print_error "Failed to remove build directory."
        exit /b 1
    )
)
for %%f in (*.spec) do (
    del /f /q "%%f"
    if ERRORLEVEL 1 (
        call :print_error "Failed to remove spec file: %%f"
        exit /b 1
    )
)
call :print_success "Build artifacts cleaned."
exit /b 0


:: ---- End ----
:end
echo.
echo Press any key to exit...
pause >nul
