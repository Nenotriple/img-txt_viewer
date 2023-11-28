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

- Shortcuts:
  - `ALT+Left/Right`: Quickly move between img-txt pairs.
  - `Del`: Send the current pair to a local trash folder.
  - `ALT`: Cycle through auto-suggestions.
  - `TAB`: Insert the highlighted suggestion.
  - `CTRL+F`: Highlight all duplicate words. 
  - `CTRL+S`: Save the current text file.
  - `CTRL+Z` / `CTRL+Y`: Undo/Redo.
  - `Middle-click`: a token to quickly delete it.

- Tips:
  - `Highlight duplicates` by selecting text.
  - Enable `List View` to display text in a vertical list format.
  - Enable `Big Comma Mode` for more visual separation between captions.
  - Blank text files can be created for images without any matching files when loading a directory.
  - `Autocomplete Suggestions` while you type using Danbooru/Anime tags, the English Dictionary, or both. 
  - Running `Edit Custom Suggestions` will create the file 'my_tags.csv' where you can add your own words to the suggestion dictionary.

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

The `danbooru.csv` and `dictionary.csv` files will be downloaded *(if not already available)* upon launch.

# 📜 Version History

[v1.78 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.78)
  - New:
    - You can now use the English dictionary as a suggestion library while you type.
      - Enable this from: Options > Suggestion Dictionary > English Dictionary
      - Just like the danbooru.csv file, this dictionary can be downloaded from the script version.
      - Over 20,000 typos for just over 8,000 words also match the correct spelling while typing.
      - You can also use both anime tags and the English dictionary at the same time. _(Can be slow)_
    - `Custom Suggestions:` You can now define custom tags that will be used for autocomplete suggestions.
      - Run the command from: Options > Edit Custom Suggestions
      - Running this command will create a file called "my_tags.csv" if it doesn't already exist, then open it up for you to edit.
      - Running the command again after saving "my_tags.csv" will refresh the dictionary with your changes.

<br>

  - Fixed:
    - Fix autosave for first and last index navigation.
    - List mode: The cursor is now placed at the end of the text file on a newline when navigating between pairs.
    - App icon now displays properly in the taskbar.
    - Further improvements to cursor positioning after inserting a suggestion.

**Batch Delete, v1.03 Changes:**

  - New:
    - Now that text is cleaned within the script, this is a standalone app!
      - Simply launch the "batch_token_delete.py" script and select a folder to manage text/tags in that folder.
    - Deleting tags using a "less than or equal to" threshold now displays the affected tags.
    - A highlight has been added to the buttons/checkboxes.

<br>

  - Fixed:
    - The app shares the parent icon, and groups with the main window in the taskbar.
