# img-txt_viewer
Display an image and text file side-by-side for easy manual caption editing.

![v1 72_img-txt_viewer](https://github.com/Nenotriple/img-txt_viewer/assets/70049990/01073c55-3ce8-43d5-98b0-1cc76d6ea2a1)

# Usage

- Prepare Your Files:
  - Put each image and its matching text file in the same folder. They should have the same name. For example, `01.png` and `01.txt`.
  - Supported image types: `.png` `.jpg` `.jpeg` `.webp` `.bmp`

# Tips and Features

Hotkeys
- `CTRL+S`: Save the current text file.
- `CTRL+Z` / `CTRL+Y`: Undo/Redo.
- `ALT`+`Left/Right`: Quickly move between img-txt pairs.
- `ALT`: Cycle through auto-suggestions.
- `TAB`: Insert highlighted suggestion.
- `Del`: Send the current pair to a local trash folder.

Tips
- Select text with the mouse or keyboard to see duplicates.
- If the auto-save box is checked, text will be saved when moving between img-txt pairs.
- Text is cleaned up when saved, so you can ignore things like trailing comma/spaces, double comma/spaces, etc.
- Blank text files can be created for images without any matching files when loading a directory.
- Get autocomplete suggestions while you type using Danbooru tags.


# Requirements
You must have **Python 3.10+** installed to the system PATH.

**Running the script will automatically fulfill all requirements.**

The `pillow` library will be downloaded and installed *(if not already available)* upon launch.

The `danbooru.csv` file will be downloaded *(if not already available)* upon launch.

# Version History

v1.73 changes:

- New:
  - Big Comma Mode: This will make commas stand out much more, and it also changes the way text is spaced out.
  - Middle-clicking the directory button now opens the selected folder.
  - Right click or middle-click the displayed image to open the image directory.
- Fixed:
  - The image index now correctly updates with changes from outside the app. (Adding/Removing images)
  - Text files now won't be created even when you select "No". A saveable text box still appears for images without text files.
  - Images without a text pair can now be properly displayed without errors.
  - The displayed text file is now refreshed when saving. This correctly displays changes made by cleanup.
  - `jpg_large` files are now renamed to .jpg before loading.
  - Unresponsive directory button.
