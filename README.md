# img-txt_viewer
Display an image and text file side-by-side for easy manual caption editing.

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

[v1.80 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.80)
  - New:
    - Small ui tweaks. [#22b2764][22b2764]
    - `Fuzzy Search` You can now use an asterisk while typing to "search" for tags. [#05ca179][05ca179]
      - For example: Typing `*lo*b` returns "<ins>**lo**</ins>oking <ins>**b**</ins>ack", and even "yel<ins>**lo**</ins>w <ins>**b**</ins>ackground"
    You can now undo the last operation for: Search and Replace, Prefix Text, and Append Text. [#c5be6a2][c5be6a2]
    - Batch Tag Delete no longer locks the main img-txt_viewer window. [#f2f8414][f2f8414]
      - While Batch Tag Delete is open, text files are scanned for changes and automatically updated. [#143140e][143140e], [#b38a786][b38a786]
    - You can now swap img-txt pair horizontal and vertical positions. [#ee7d052][ee7d052]
    - About window added. [#e692ebe][e692ebe]
    - The current text file is now scanned every 2 seconds, and refreshed if changed outside the app.

<br>

  - Fixed:
    - Huge fix: Batch Tag Delete now properly opens when launched from the executable version. [#95910e4][95910e4]
    - Fixed autosave bug causing warning on window close without directory selection. [#b3f00a2][b3f00a2]
    - Batch Tag Delete now opens beside the main window. [#f75362f][f75362f]
    - Selecting a new directory now removes the left over text backups. [#b1f4655][b1f4655]
    - Closing the app now removes the "Trash" folder if empty. [#f8144ab][f8144ab]
    - Prevent multiple instances of a tool window from opening. [#3320d8e][3320d8e]

<br>

  - Other changes:
    - PanedWindow adjustments. [#2bfdb3a][2bfdb3a]
    - Other changes: [#f2f8414][f2f8414], [#9c8c580][9c8c580], [#0362e23][0362e23], [#fbcaaec][fbcaaec], [353827d][353827d], [#a41d99c][a41d99c]

<!-- New -->
[22b2764]: https://github.com/Nenotriple/img-txt_viewer/commit/22b2764edbf16e4477dce16bebdf08cf2d3459df
[05ca179]: https://github.com/Nenotriple/img-txt_viewer/commit/05ca179914d3288108206465d78ab199874b6cc2
[c5be6a2]: https://github.com/Nenotriple/img-txt_viewer/commit/c5be6a2861192d634777d5c0d5c6d9a8804bbc72
[143140e]: https://github.com/Nenotriple/img-txt_viewer/commit/143140efc4bca1515579d3ce0d73c68837ac5c30
[b38a786]: https://github.com/Nenotriple/img-txt_viewer/commit/b38a786c4f75edf0ad03d2966076f32c7d870d3e
[ee7d052]: https://github.com/Nenotriple/img-txt_viewer/commit/ee7d0527d006803f4bf1377e5e95cebf13af429f
[e692ebe]: https://github.com/Nenotriple/img-txt_viewer/commit/e692ebe56e34433ad5697ab2c1a3404b62b7c7c8

<!-- Fixed -->
[95910e4]: https://github.com/Nenotriple/img-txt_viewer/commit/95910e42c8f8212a66c0eb68d3d75db7078587cb
[b3f00a2]: https://github.com/Nenotriple/img-txt_viewer/commit/b3f00a28c82beb2300e78693df5d771802b2cfe4
[f75362f]: https://github.com/Nenotriple/img-txt_viewer/commit/f75362feea79e088d40af05c3fdc4e62881e64ab
[b1f4655]: https://github.com/Nenotriple/img-txt_viewer/commit/b1f465555306d3ff9bf169dcc085de80dd96cc81
[f8144ab]: https://github.com/Nenotriple/img-txt_viewer/commit/f8144abf49cfbd5e34294a8a8e868010741a6956
[3320d8e]: https://github.com/Nenotriple/img-txt_viewer/commit/3320d8e7647ddb194d874f172976c05dab4f2910

<!-- Other changes -->
[2bfdb3a]: https://github.com/Nenotriple/img-txt_viewer/commit/2bfdb3a6e4d075f26b6c89ef160e990190d27dc3
[f2f8414]: https://github.com/Nenotriple/img-txt_viewer/commit/f2f84141f2481fc555fc3a74393f1816f9a199ec
[9c8c580]: https://github.com/Nenotriple/img-txt_viewer/commit/9c8c580dab9ff0e569df0f45fdf26d3914511497
[0362e23]: https://github.com/Nenotriple/img-txt_viewer/commit/0362e23f0e684eb5b1ce73b89c1b0267af144ba8
[fbcaaec]: https://github.com/Nenotriple/img-txt_viewer/commit/fbcaaecd83cf6c6a38de33baef41981b61de243e
[353827d]: https://github.com/Nenotriple/img-txt_viewer/commit/353827d1648f64d9f54cee709e6cb857a75387de
[a41d99c]: https://github.com/Nenotriple/img-txt_viewer/commit/a41d99cccb368e6e6faa3b9598b22032a07fc441

___

### Batch Tag Delete
v1.05 changes:

  - New:
    - `Undo All` You can now restore the text files to their original state from when Batch Tag Delete was launched. [#7d574a8][7d574a8]
    - Implement Auto-Refresh Feature. [#4f78be5][4f78be5]
    - Renamed to: Batch Tag Delete [#f7e9389][f7e9389]
    - Window position can be controlled with cmd arguments. This is used to position this window beside img-txt_viewer. [#9fe7499][9fe7499]
     - Example: `python batch_tag_delete.py /path/to/directory 500 800`

<br>

  - Fixed:
    - Properly set app icon. [#358ee1d][358ee1d]
    - Improved popup handling when clicking `Delete Selected` when no tags are selected. [#3a0a60b][3a0a60b]
    - Fixed error related to file refresh being called after closing when launched from img-txt_viewer.

  - Other: [#7ccd0fb][7ccd0fb], [3a0a60b][3a0a60b]

[7d574a8]: https://github.com/Nenotriple/img-txt_viewer/commit/7d574a85b300f60bd01015aeadfca4e3d38cdf71
[4f78be5]: https://github.com/Nenotriple/img-txt_viewer/commit/4f78be5df917f6af19796591fbbff05e64f8e944
[f7e9389]: https://github.com/Nenotriple/img-txt_viewer/commit/f7e9389d77ed86508ccb4f9705c3d709eb00ab0e
[9fe7499]: https://github.com/Nenotriple/img-txt_viewer/commit/9fe7499d89d5689606a3e576554c03c8c3f4f4c8

[358ee1d]: https://github.com/Nenotriple/img-txt_viewer/commit/358ee1d93636d0001a3e9b96d72ba3230697fcdd

[7ccd0fb]: https://github.com/Nenotriple/img-txt_viewer/commit/7ccd0fb7c41a82eb31e128b656b16fbccd78c784
[3a0a60b]: https://github.com/Nenotriple/img-txt_viewer/commit/3a0a60bbf41a2da0c5b943624bfe61dceba71703
