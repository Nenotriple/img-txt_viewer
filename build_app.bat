:: This script is used to build the img-txt viewer application using PyInstaller.
:: It assumes that the script is run from the root directory of the project.
:: It also assumes that the virtual environment is located in a folder named 'venv' or 'env'.

:: The script will activate the virtual environment, upgrade PyInstaller, build the executable,
:: copy necessary folders and files to the 'dist' directory, and create a zip package of the build.


@echo off
echo ===== Building img-txt Viewer =====

echo Step 1: Activating virtual environment...
:: Note: You may need to modify this line to point to your specific virtual environment
call venv\Scripts\activate.bat 2>nul || call env\Scripts\activate.bat 2>nul
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
pyinstaller app.py --name img_txt_viewer --onefile --windowed --icon=icon.ico --add-data="icon.ico;." --add-data="main;main"
if %ERRORLEVEL% NEQ 0 (
    echo Build process failed.
    goto :end
)
echo Build completed successfully!
echo Executable should be available in the dist directory.

echo Step 4: Copying required folders and files to dist...
echo Copying ncnn_models...
xcopy /y /i /e "ncnn_models" "dist\ncnn_models" 2>nul && echo Copied ncnn_models successfully || echo ncnn_models not found, skipping
echo Copying onnx_models...
xcopy /y /i /e "onnx_models" "dist\onnx_models" 2>nul && echo Copied onnx_models successfully || echo onnx_models not found, skipping
echo Copying my_tags.csv...
copy /y "my_tags.csv" "dist\" 2>nul && echo Copied my_tags.csv successfully || echo my_tags.csv not found, skipping

echo Step 5: Creating zip package...
powershell -command "Compress-Archive -Path 'dist\img_txt_viewer.exe', 'dist\ncnn_models', 'dist\onnx_models', 'dist\my_tags.csv' -DestinationPath 'dist\img_txt_viewer.zip' -Force" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create zip package.
) else (
    echo Zip package created successfully as dist\img_txt_viewer.zip!
)

:end
echo.
echo Press any key to exit...
pause > nul
