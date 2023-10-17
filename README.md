[comment]: <> (CTRL+K V: Open preview side-by-side)

# img-txt_viewer
Display an image and text file side-by-side for easy manual caption editing.

![v1 74_img-txt_viewer](https://github.com/Nenotriple/img-txt_viewer/assets/70049990/7949c61d-c507-4dd2-934c-906feef3b9fe)

# 📝 Usage

- Prepare Your Files:
  - Put each image and its matching text file in the same folder. They must have the same name.
  - For example: `01.png` and `01.txt`, `02.jpg` and `02.txt`...
  - Supported image types: `.png` `.jpg` `.jpeg` `.webp` `.bmp`

# 💡 Tips and Features

- Hotkeys:
  - `ALT+Left/Right`: Quickly move between img-txt pairs.
  - `Del`: Send the current pair to a local trash folder.
  - `ALT`: Cycle through auto-suggestions.
  - `TAB`: Insert the highlighted suggestion.
  - `CTRL+S`: Save the current text file.
  - `CTRL+Z` / `CTRL+Y`: Undo/Redo.

- Tips:
  - Highlight duplicates by selecting text.
  - Right-click the directory button to copy the path.
  - Middle-click the directory button to open the folder.
  - Right-click or Middle-click the displayed image to open its folder.
  - Get autocomplete suggestions while you type using Danbooru tags.
  - Enable `Big Comma Mode` for more visual separation between captions.
  - Blank text files can be created for images without any matching files when loading a directory.

- Text Tools:
  - Search and Replace: Edit all text files at once.
  - Prefix Text Files: Insert text at the START of all text files.
  - Append Text Files: Insert text at the END of all text files.

 - Auto-Save
   - Check the auto-save box to save text when navigating between img/txt pairs or closing the window.
   - Text is cleaned up when saved, so you can ignore things like trailing commas/spaces, double commas/spaces, etc.

# 🚩 Requirements

You don't need to worry about anything if you're using the [portable/executable](https://github.com/Nenotriple/img-txt_viewer/releases?q=executable&expanded=true) version.

___

You must have **Python 3.10+** installed to the system PATH.

**Running the script will automatically fulfill all requirements.**

The `pillow` library will be downloaded and installed *(if not already available)* upon launch.

The `danbooru.csv` file will be downloaded *(if not already available)* upon launch.

# 📜 Version History

- [v1.74 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.74)
  - New:
    - `Search and Replace`: Replace any text string across all text files in the loaded directory.
    - `Prefix Text Files`: Insert text at the START of all text files.
    - `Append Text Files`: Insert text at the END of all text files.
    - Minor UI tweaks and enhancements.

  - Fixed:
    - Resolved an issue where the app would repeatedly ask: `Do you want to create '...' new text files?` even after selecting `No`.
    - The 'Saved' label now updates correctly upon saving.
    - The image index is now refreshed only when the folder quantity changes, resulting in faster navigation.
    - Re-enabled the 'Undo' function.
    - Extensive internal code refactoring for improved cleanliness and maintainability.
___
- [v1.73 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.73)
  - New:
    - `Big Comma Mode`: This will make commas stand out much more, and it also changes the way text is spaced out.
    - Middle-clicking the directory button now opens the selected folder.
    - Right click or middle-click the displayed image to open the image directory.

  - Fixed:
    - The image index now correctly updates with changes from outside the app. (Adding/Removing images)
    - Text files now won't be created even when you select "No". A saveable text box still appears for images without text files.
    - Images without a text pair can now be properly displayed without errors.
    - The displayed text file is now refreshed when saving. This correctly displays changes made by cleanup.
    - `jpg_large` files are now renamed to `.jpg` when loading.
    - Unresponsive directory button.
