# Build Instructions for img-txt Viewer

## Steps to Build the Executable:

1. Activate the Project Virtual Environment
2. Upgrade PyInstaller
```
pip install --upgrade pyinstaller
```
3. Run PyInstaller
```
pyinstaller img-txt_viewer.py --onefile --windowed --icon=icon.ico --add-data="icon.ico;." --add-data="main;main"
```

## Breakdown of the PyInstaller Command:

1. Main command to run PyInstaller.
   - `pyinstaller`
2. The Python script to convert into an executable.
   - `img-txt_viewer.py`
3. Bundle everything into a single executable file.
   - `--onefile`
4. Run the executable without opening a console window.
   - `--windowed`
5. Path to the icon file for the executable.
    - `--icon=icon.ico`
6. Include the icon file in the root directory of the bundled application.
   - `--add-data="icon.ico;."`
7. Include the `main` directory in the bundled application.
   - `--add-data="main;main"`
