:: This script is used to build the img-txt viewer application using PyInstaller.
:: It assumes that the script is run from the root directory of the project.
:: It also assumes that the virtual environment is located in a folder named 'venv' or 'env'.

:: The script will activate the virtual environment, upgrade PyInstaller, build the executable,
:: copy necessary folders and files to the 'dist' directory, and create a zip package of the build.


@echo off


set "APP_NAME=img_txt_viewer_v1.97b10"
:: This is the output filename for the executable.


set "VENV_DIR=venv"
:: This is the name of the virtual environment directory.


set "PACKAGE_MODE=full"
:: - none: Skip packaging step entirely
:: - full: Bundle everything (exe and models) into a single zip file
:: - split: Package models separately in models.zip, leaving the executable alone
:: - full-split: Perform both full and split packaging operations


set "COMPRESS_LEVEL=NoCompression"
:: Compression level for the zip package. Options: NoCompression, Fastest, Optimal


echo ===== Building img-txt Viewer =====


echo Step 1: Activating virtual environment...
:: Note: You may need to modify VENV_DIR to point to your specific virtual environment
call "%VENV_DIR%\Scripts\activate.bat" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Virtual environment activation failed.
    echo Please modify this script to use the correct path to your virtual environment.
    goto :end
)


echo Step 2: Upgrading PyInstaller...
pip install --upgrade pyinstaller
if %ERRORLEVEL% NEQ 0 (
    echo Failed to upgrade PyInstaller.
    goto :end
)


echo Step 3: Building executable with PyInstaller...
pyinstaller app.py --name %APP_NAME% --onefile --windowed --icon=icon.ico --add-data="icon.ico;." --add-data="main;main"
if %ERRORLEVEL% NEQ 0 (
    echo Build process failed.
    goto :end
)


echo Build completed successfully!
echo Executable should be available in the dist directory.
echo ===== Beginning packaging process =====


echo Step 1: Copying required files to dist...
echo Copying ncnn_models...
xcopy /y /i /e "ncnn_models" "dist\ncnn_models" 2>nul && echo Copied ncnn_models successfully || echo ncnn_models not found, skipping
echo Copying onnx_models...
xcopy /y /i /e "onnx_models" "dist\onnx_models" 2>nul && echo Copied onnx_models successfully || echo onnx_models not found, skipping


echo Step 2: Creating zip package...
if "%PACKAGE_MODE%"=="full" (
    echo Packaging in FULL mode - creating single package with executable and models...
    powershell -command "Compress-Archive -Path 'dist\%APP_NAME%.exe', 'dist\ncnn_models', 'dist\onnx_models' -DestinationPath 'dist\%APP_NAME%.zip' -Force -CompressionLevel %COMPRESS_LEVEL%" 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create zip package.
    ) else (
        echo Zip package created successfully as dist\%APP_NAME%.zip!
    )
) else if "%PACKAGE_MODE%"=="split" (
    echo Packaging in SPLIT mode - creating separate models package...
    powershell -command "Compress-Archive -Path 'dist\ncnn_models', 'dist\onnx_models' -DestinationPath 'dist\models.zip' -Force -CompressionLevel %COMPRESS_LEVEL%" 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create models zip package.
    ) else (
        echo Models zip package created successfully as dist\models.zip!
        echo Executable is available separately as dist\%APP_NAME%.exe
    )
) else if "%PACKAGE_MODE%"=="full-split" (
    echo Packaging in FULL-SPLIT mode - creating both packages...
    powershell -command "Compress-Archive -Path 'dist\%APP_NAME%.exe', 'dist\ncnn_models', 'dist\onnx_models' -DestinationPath 'dist\%APP_NAME%.zip' -Force -CompressionLevel %COMPRESS_LEVEL%" 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create full zip package.
    ) else (
        echo Full zip package created successfully as dist\%APP_NAME%.zip!
    )
    powershell -command "Compress-Archive -Path 'dist\ncnn_models', 'dist\onnx_models' -DestinationPath 'dist\models.zip' -Force -CompressionLevel %COMPRESS_LEVEL%" 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create models zip package.
    ) else (
        echo Models zip package created successfully as dist\models.zip!
    )
) else (
    echo Unknown PACKAGE_MODE: %PACKAGE_MODE%
    echo Valid options are: full, split, full-split
    echo Skipping packaging step.
)


:end
echo.
echo Press any key to exit...
pause > nul
