# img-txt_viewer
Display an image and text file side-by-side for easy manual caption editing.

![image](https://user-images.githubusercontent.com/70049990/220445796-ea8c9b05-3a89-46cb-81f9-e291589d6c07.png)

# Usage

Store images and text files in a single folder with identical names.
- So 01.png and 01.txt and so on. The names in each pair should match, but no particular formatting is required.

Supported image types:
- .png .jpg .jpeg .webp .bmp

# Tips and Features

Hotkeys
- CTRL+S: to save the current text file.
- CTRL+Z / CTRL+Y: Undo/Redo
- ALT+Left/Right arrow keys: to move between img/txt pairs.
- Pressing TAB inserts the selected suggestion.
- Pressing TAB+Left/Right selects the autocomplete suggestion.

Tips
- Select text with the mouse or keyboard to see duplicates.
- If the auto-save box is checked, text will be saved when moving between img/txt pairs.
- If the user chooses a folder with images but no matching text files, they will be prompted to create blank text files. The blank text files will only be created for images that currently don't have any text files.
- Get autocomplete suggestions while you type using danbooru tags.


# Requirements

This uses pillow for image viewing, and tkinter for the ui.

tkinter comes preinstalled with Python.

Install pillow with the following command:
```
pip install pillow
```

The autocomplete function requires the included "danbooru.csv" file to be located in the same folder as the script

# Version History

v1.62 changes:

- *Tips and features added to startup.*

- *Removed directory text widget and replaced it with a button with a dynamic label*

- *Error handling added when selecting a directory*

v1.61 changes:

- *Saving now fixes various typos such as: Double and triple commas are replaced with single commas. Extra spaces are reduced to single spaces. leading and trailing spaces/commas are removed*

- *utf-8 encoding is enforced.*

- *Undo now works as expected*

v1.6 changes:

- *New feature: Autocomplete using danbooru tags* 

v1.5 changes:

- *New feature: Select and highlight duplicates*

v1.42 changes:

- *Misc ui improvements*

- *Now supports loading .jpeg/.webp/.bmp image types*
