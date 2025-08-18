:: This script is used to build the img-txt viewer application using PyInstaller.
:: It assumes that the script is run from the root directory of the project.
:: It also assumes that the virtual environment is located in a folder named '.venv' or 'env'.
::
:: The script will activate the virtual environment, upgrade PyInstaller, build the executable,
:: copy necessary folders and files to the 'dist' directory, and create a zip package of the build.
::


@echo off
setlocal ENABLEDELAYEDEXPANSION


:: -------------------- Configurable variables --------------------


set "APP_NAME=img_txt_viewer_v1.97b10"
:: Output filename for the executable.


set "VENV_DIR=.venv"
:: Name or path to the virtual environment directory.


set "PACKAGE_MODE=full"
:: - none: Skip packaging step entirely
:: - full: Bundle everything (exe and models) into a single zip file
:: - split: Package models separately in models.zip, leaving the executable alone


set "COMPRESS_LEVEL=NoCompression"
:: Compression level for the zip package. Options: NoCompression, Fastest, Optimal


:: -------------------- Models path configuration --------------------


:: Determine script directory (always ends with backslash)
set "SCRIPT_DIR=%~dp0"


:: Set default models base path
set "MODELS_BASE=%SCRIPT_DIR%models"


:: Normalize potential quotes around MODELS_BASE (remove surrounding quotes)
for /f "delims=" %%A in ("%MODELS_BASE%") do set "MODELS_BASE=%%~fA"


:: Set model source paths
set "NCNN_SRC=%MODELS_BASE%\ncnn_models"
set "ONNX_SRC=%MODELS_BASE%\onnx_models"


:: Echo resolved paths
echo.
echo ===== Building img-txt Viewer =====


echo Models base path resolved to:
echo     %MODELS_BASE%
echo Looking for:
echo     %NCNN_SRC%
echo     %ONNX_SRC%


:: -------------------- Build steps --------------------


echo.
echo Step 1: Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Virtual environment activation failed.
    echo Please modify this script to use the correct path to your virtual environment.
    goto :end
)


echo.
echo Step 2: Upgrading PyInstaller...
pip install --upgrade pyinstaller
if %ERRORLEVEL% NEQ 0 (
    echo Failed to upgrade PyInstaller.
    goto :end
)


echo.
echo Step 3: Building executable with PyInstaller...
pyinstaller app.py --name %APP_NAME% --onefile --windowed --icon=icon.ico --add-data="icon.ico;." --add-data="main;main"
if %ERRORLEVEL% NEQ 0 (
    echo Build process failed.
    goto :end
)


echo.
echo Build completed successfully!
echo Executable should be available in the dist directory.


echo.
echo ===== Beginning packaging process =====


echo.
echo Step 1: Copying required files to dist...
:: Ensure dist exists
if not exist "dist" mkdir "dist"
:: Copy NCNN models
if exist "%NCNN_SRC%" (
    echo Copying ncnn_models from "%NCNN_SRC%" ...
    xcopy /y /i /e "%NCNN_SRC%" "dist\ncnn_models" >nul && echo Copied ncnn_models successfully || echo Failed to copy ncnn_models
) else (
    echo ncnn_models not found at "%NCNN_SRC%", skipping
)
:: Copy ONNX models
if exist "%ONNX_SRC%" (
    echo Copying onnx_models from "%ONNX_SRC%" ...
    xcopy /y /i /e "%ONNX_SRC%" "dist\onnx_models" >nul && echo Copied onnx_models successfully || echo Failed to copy onnx_models
) else (
    echo onnx_models not found at "%ONNX_SRC%", skipping
)


echo.
echo Step 2: Creating zip package...


:: full
if /I "%PACKAGE_MODE%"=="full" (
    echo Packaging in FULL mode - creating single package with executable and models...
    powershell -command "Compress-Archive -Path 'dist\%APP_NAME%.exe', 'dist\ncnn_models', 'dist\onnx_models' -DestinationPath 'dist\%APP_NAME%.zip' -Force -CompressionLevel %COMPRESS_LEVEL%" 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create zip package.
    ) else (
        echo Zip package created successfully as dist\%APP_NAME%.zip!
    )


:: split
) else if /I "%PACKAGE_MODE%"=="split" (
    echo Packaging in SPLIT mode - creating separate models package...
    powershell -command "Compress-Archive -Path 'dist\ncnn_models', 'dist\onnx_models' -DestinationPath 'dist\models.zip' -Force -CompressionLevel %COMPRESS_LEVEL%" 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create models zip package.
    ) else (
        echo Models zip package created successfully as dist\models.zip!
        echo Executable is available separately as dist\%APP_NAME%.exe
    )


:: none
) else if /I "%PACKAGE_MODE%"=="none" (
    echo PACKAGE_MODE=none - skipping packaging step.
) else (
    echo Unknown PACKAGE_MODE: %PACKAGE_MODE%
    echo Valid options are: full, split, none
    echo Skipping packaging step.
)


echo ===== Packaging process completed =====


:end
echo.
echo Press any key to exit...
pause > nul
endlocal
