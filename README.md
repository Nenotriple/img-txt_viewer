# img-txt_viewer
Display an image and text file side-by-side for easy manual caption editing.

![v1 67_img-txt_viewer](https://github.com/Nenotriple/img-txt_viewer/assets/70049990/09cb402a-db35-4b15-8ff2-828234b397e0)

# Usage

Store images and text files in a single folder with identical names.
- So 01.png, 01.txt, and so on. The names in each pair should match, but no particular formatting is required.

Supported image types:
- .png .jpg .jpeg .webp .bmp

# Tips and Features

Hotkeys
- CTRL+S: to save the current text file.
- CTRL+Z / CTRL+Y: Undo/Redo.
- ALT+Left/Right arrow keys quickly move between img-txt pairs.
- Pressing TAB inserts the selected suggestion.
- Presing ALT cycles through suggestions.
- Delete img-txt pairs: Del

Tips
- Select text with the mouse or keyboard to see duplicates.
- If the auto-save box is checked, text will be saved when moving between img-txt pairs.
- Blank text files can be created for images without any matching files when loading a directory.
- Get autocomplete suggestions while you type using Danbooru tags.


# Requirements

**Running the script will automatically fulfill all requirements.**

This uses Pillow for image viewing and TKinter for the UI.

TKinter comes preinstalled with Python.

Install Pillow with the following command:
```
pip install pillow
```

The autocomplete function requires the included "danbooru.csv" file to be located in the same folder as the script.

# Version History

v1.71 changes:

- New:
  - Now you can select any font installed on your system.
  - Clicking the displayed image will open it in your default image viewing application.
  - Right clicking the directory button will add the file path to the clipboard.
  - Delete Pair now simply moves the img-txt pair to a local trash folder in the selected directory.
  - Now you can delete an img-txt pair with the "del" keyboard key.
- Fixed:
  - Issue where the proceeding tag would be deleted if inserting a suggestion without encapsulating the input between commas.
  - Improved handling of cursor position after inserting a suggestion. (again)
  - Issue where image index would not update correctly when switching directories.
  - Where "on_closing" message would trigger even if the text file was saved.
  - Further improvements to the way text is cleaned up when saved.
