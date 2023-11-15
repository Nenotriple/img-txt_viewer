[comment]: <> (CTRL+K V: Open preview side-by-side)

# img-txt_viewer
Display an image and text file side-by-side for easy manual caption editing.

![v1 74_img-txt_viewer](https://github.com/Nenotriple/img-txt_viewer/assets/70049990/7949c61d-c507-4dd2-934c-906feef3b9fe)

# 📝 Usage

- Prepare Your Files:
  - Put each image and its matching text file in the same folder.
  - If you choose to include a text pair for an image, ensure they are located in the same folder and have identical names.
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
  - `CRTL+F`: Highlight all duplicate words.

- Tips:
  - `Highlight duplicates` by selecting text.
  - `Autocomplete Suggestions` while you type using Danbooru tags.
  - Enable `List View` to display text in a vertical list format.
  - Enable `Big Comma Mode` for more visual separation between captions.
  - Middle-click a token to quickly delete it.
  - Right-click the directory button to copy the path.
  - Right-click the image/text for a context menu.
  - Blank text files can be created for images without any matching files when loading a directory.

- Text Tools:
  - `Batch Token Delete`: View all tokens in a directory as a list, and quickly delete them.
  - `Cleanup Text`: Fix simple typos in all text files of the selected folder.
  - `Prefix Text Files`: Insert text at the START of all text files.
  - `Append Text Files`: Insert text at the END of all text files.
  - `Search and Replace`: Edit all text files at once.

 - Auto-Save
   - Check the auto-save box to save text when navigating between img/txt pairs or closing the window.
   - Text is cleaned when saved, so you can ignore typos such as duplicate tokens, multiple spaces or commas, missing spaces, and more.
   - `Clean text on save` Can be disabled from the options menu. *(Disabling this may have adverse effects when inserting a suggestion)*

# 🚩 Requirements

You don't need to worry about anything if you're using the [portable/executable](https://github.com/Nenotriple/img-txt_viewer/releases?q=executable&expanded=true) version.

___

You must have **Python 3.10+** installed to the system PATH.

**Running the script will automatically fulfill all requirements.**

The `pillow` library will be downloaded and installed *(if not already available)* upon launch.

The `danbooru.csv` file will be downloaded *(if not already available)* upon launch.

# 📜 Version History

[v1.77 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.77)
  - New:
    - `List View`: Display text files in a list format. Text is always saved in the standard single-line CSV format.
    - `Always on Top`: Enable this to keep the window in focus.
    - `Highlight All Duplicates`: Highlight all matching words in the text box.
    - `Delete entire tokens`: By middle-clicking them.
    - `Text Context menu`
    - `Image Context menu`
    - Enable or disable highlighting duplicate words when selecting text. _(Default = On)_
    - You can now swap the image and text/control positions.
    - Various UI tweaks, the biggest change being: Image scaling is now more flexible.

<br>

  - Fixed:
    - When highlighting words: Any _selected_ words longer than 3 characters would be _highlighted_. Now, only exact matches are highlighted.
    - Window size no longer changes when changing maximum image size.
    - You can no longer insert a suggestion "inside" an existing token.
    - Code refactoring for improved cleanliness and maintainability.

**Batch Delete, v1.02 Changes:**

 - New:
   - You can now select multiple tokens then delete them all at once.

 - Fixed:
   - Newlines should be properly handled/deleted now.
