# img-txt_viewer
Display an image and text file side-by-side for easy manual captioning. + Tons of features to help you work faster!

![v1 74_img-txt_viewer](https://github.com/Nenotriple/img-txt_viewer/assets/70049990/7949c61d-c507-4dd2-934c-906feef3b9fe)

# 📝 Usage

- Prepare Your Files:
  - Put each image and its matching text file in the same folder.
  - If you choose to include a text pair for an image, ensure they are located in the same folder and have identical names.
  - For example: `01.png` and `01.txt`, `02.jpg` and `02.txt`...
  - Supported image types: `.png` `.jpg` `.jpeg` `.jfif` `.jpg_large` `.webp` `.bmp`


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
  - `Fuzzy Search` Use an asterisk * while typing to return a broader range of suggestions.
    - For example: Typing `*lo*b` returns "<ins>**lo**</ins>oking <ins>**b**</ins>ack", and even "yel<ins>**lo**</ins>w <ins>**b**</ins>ackground"

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

`dictionary.csv` `danbooru.csv` `e621.csv` will be downloaded *(if not already available)* upon launch.

# 📜 Version History

[v1.81 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.81) [#a19eed3][a19eed3]
  - New:
    - Added underlining (Alt+Letter) to all menubar commands.

<br>

  - Fixed:
    - Prevent app crash when selecting a folder without any text files.
    - Blank text files are no longer created when attempting to save a blank text box.
      - This includes when auto-save is enabled and moving between img-txt pairs.
    - Right clicking the text box no longer clears the text selection.
    - Propperly set menu accelerator flags.
    - You can no longer select a directory that doesn't contain images.
    - Some menu options are now disabled before loading a directory.
    - `Edit Custom Suggestions` now opens the ".csv" file as a regular text document if no CSV file editor is present.

[a19eed3]: https://github.com/Nenotriple/img-txt_viewer/commit/a19eed3f0720056308655ab43f22b0dace7512f5
