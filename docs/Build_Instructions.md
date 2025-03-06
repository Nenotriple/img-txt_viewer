# Build Instructions for img-txt Viewer

## Steps to Build the Executable:

1. Activate the Project Virtual Environment
2. Upgrade PyInstaller
```
pip install --upgrade pyinstaller
```
3. Run PyInstaller
```
pyinstaller app.py --onefile --windowed --icon=icon.ico --add-data="icon.ico;." --add-data="main;main"
```

## Breakdown of the PyInstaller Command:

1. `pyinstaller`
   - Main command to run PyInstaller.
2. `app.py`
   - The Python script to convert into an executable. This is the main entry point of the application.
3. `--onefile`
   - Bundle everything into a single executable file.
4. `--windowed`
   - Run the executable without opening a console window.
5. `--icon=icon.ico`
   - Path to the icon file for the executable. This is used to set the icon of the executable file itself.
6. `--add-data="icon.ico;."`
   - Include the icon file in the root directory of the bundled application. This is used to set the UI icon.
7. `--add-data="main;main"`
   - Include the `main` directory in the bundled application. This is required to load the dictionaries, upscale mode, etc.