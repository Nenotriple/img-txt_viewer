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

[v1.79 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.78)
  - New:
    - The img-txt pair is now contained in a PanedWindow, this allows you to drag and resize these frames. [#0237473][0237473]
      - This makes image and text sizing very flexible!
    - Suggestions now display colored text based on the tag color classification. [#1a5cea1][1a5cea1]
      - Danbooru color code: ${\textsf{\color{black}General tags}}$, ${\textsf{\color{#c00004}Artists}}$, ${\textsf{\color{#a800aa}Copyright}}$, ${\textsf{\color{#00ab2c}Characters}}$, ${\textsf{\color{#fd9200}Meta}}$
      - e621 color code: ${\textsf{\color{black}General tags}}$, ${\textsf{\color{#f2ac08}Artists}}$, ${\textsf{\color{#dd00dd}Copyright}}$, ${\textsf{\color{#00aa00}Characters}}$, ${\textsf{\color{#ed5d1f}Species}}$, ${\textsf{\color{#ff3d3d}Meta}}$, ${\textsf{\color{#228822}Lore}}$
    - Several changes and additions to the options and tools menu. Just exposing features, nothing new. [#0e8818d][0e8818d]
    - `.jfif` file support added. Like '.jpg_large', these files are simply renamed to '.jpg' [#9d6e167][9d6e167]
      - Duplicate files are handled by appending an underscore and a padded 3-digit number. E.g. "_001" [#6cdd0d4][6cdd0d4]
    - `e621` tag dictionary added. [#ade503e][ade503e], [#4c92655][4c92655], [#a66938e][a66938e]
    - `Undo Delete` You can now restore deleted img-txt pairs. [#82a59d3][82a59d3]
    - Increase score/priority of tags from 'my_tags.csv' [#e800867][e800867]

<br>

  - Fixed:
    - The app now always opens in the center of the screen. [#3ae6e13][3ae6e13]
    - Most new windows now open directly beside the main window. [#a943cfd][a943cfd]
    - Expression/smiley emotes that should include an underscore now insert and display properly. [#5c41ffe][5c41ffe]
      - Please feel free to submit an issue if you come across any tags that should include an underscore!
    - Fixed annoying behaviour of "Font Options" dropdown boxes. [#e65f107][e65f107]
    - Fix for IndexError in delete_pair function. [#e12a73f][e12a73f]

<br>

  - Other changes:
    - Suggestion style and alignment menu have been removed.  [#1a5cea1][1a5cea1]
    - English Dictionary: ~47,000 words were given an increased priority. [#33d717c][33d717c]
    - Danbooru tags: ~100 unnecessary tags removed. [#8d07b66][8d07b66]
    - Other changes: [#dd863c0][dd863c0], [#9dac3bf][9dac3bf], [#85ebb01][85ebb01], [#2e6804f][2e6804f], [#b3f02fb][b3f02fb], [#dc92a2f][dc92a2f], [#f8ca427][f8ca427], [#56e4519][56e4519], [#723f289][723f289], [#48f8d4f][48f8d4f], [#d36140f][d36140f]

<!-- New -->
[0237473]: https://github.com/Nenotriple/img-txt_viewer/commit/0237473dea9f27d30a959adf49fd6f5cec63d375
[1a5cea1]: https://github.com/Nenotriple/img-txt_viewer/commit/1a5cea1cec326a071ce512519dda35c73a03cd51
[0e8818d]: https://github.com/Nenotriple/img-txt_viewer/commit/0e8818dff7229055441af9871136ca10c981f5de
[9d6e167]: https://github.com/Nenotriple/img-txt_viewer/commit/9d6e1670b6aff6d190041a2f4b9ac9b03649ecd3
[6cdd0d4]: https://github.com/Nenotriple/img-txt_viewer/commit/6cdd0d45927072f0a0792a6b0007a7a7a164f819
[ade503e]: https://github.com/Nenotriple/img-txt_viewer/commit/ade503eaeffbf9f45290c9d0bb5e2fc6b1da8ca5
[4c92655]: https://github.com/Nenotriple/img-txt_viewer/commit/4c9265528f694389571010df7b7dbec67a656733
[a66938e]: https://github.com/Nenotriple/img-txt_viewer/commit/a66938ed25b184452e59b2f60e70e3e733d7c484
[82a59d3]: https://github.com/Nenotriple/img-txt_viewer/commit/82a59d3c66499d97420e92ebe1b1949098e7842d
[e800867]: https://github.com/Nenotriple/img-txt_viewer/commit/e80086755c2320a8152723df6bbe3fe995bd53e2

<!-- Fixed -->
[3ae6e13]: https://github.com/Nenotriple/img-txt_viewer/commit/3ae6e13c87a7b5519762d14f7937fe4d273f87bb
[a943cfd]: https://github.com/Nenotriple/img-txt_viewer/commit/a943cfd2112bc9a7da051900987b0b32269d5cb5
[5c41ffe]: https://github.com/Nenotriple/img-txt_viewer/commit/5c41ffeaa322f8056fb36c3075163b7d132ecbaf
[e65f107]: https://github.com/Nenotriple/img-txt_viewer/commit/e65f107d219f53df95147a96f821ddae05b28961
[e12a73f]: https://github.com/Nenotriple/img-txt_viewer/commit/e12a73f194e26d3c374bb5f241188e0b2475822e

<!-- Other changes -->
[33d717c]: https://github.com/Nenotriple/img-txt_viewer/commit/33d717c4e34d11158a5bd72ab44c56ce36429055
[8d07b66]: https://github.com/Nenotriple/img-txt_viewer/commit/8d07b66078f379658eb13e3d2a87076c4297d3af
[dd863c0]: https://github.com/Nenotriple/img-txt_viewer/commit/dd863c0450cc47b314a91c89566bd2eb59b3041d
[9dac3bf]: https://github.com/Nenotriple/img-txt_viewer/commit/9dac3bfc3fd9998301350bbe056cb92ca16076ce
[85ebb01]: https://github.com/Nenotriple/img-txt_viewer/commit/85ebb01ce599efa533d3cca873629f89f4721574
[2e6804f]: https://github.com/Nenotriple/img-txt_viewer/commit/2e6804ffd046b3927332aa93f14b18d5f534d1b9
[b3f02fb]: https://github.com/Nenotriple/img-txt_viewer/commit/b3f02fb67b85b387959491a29f106689ba3c5ea6
[dc92a2f]: https://github.com/Nenotriple/img-txt_viewer/commit/dc92a2f325fe452ec0d414308f1c7e6310aa3c31
[f8ca427]: https://github.com/Nenotriple/img-txt_viewer/commit/f8ca4279d8ac62b2f96f77ce523e62ce414f999b
[56e4519]: https://github.com/Nenotriple/img-txt_viewer/commit/56e4519b7882c7cb17719815f78e03c4467c9694
[723f289]: https://github.com/Nenotriple/img-txt_viewer/commit/723f289091ab198f58bf055e482d800ae0a76a01
[48f8d4f]: https://github.com/Nenotriple/img-txt_viewer/commit/48f8d4fc5b861620bc3b17262dfb1104e4677fae
[d36140f]: https://github.com/Nenotriple/img-txt_viewer/commit/d36140fcb53fd1a5290fdfcc5db511d236ed89ad

___

### Batch Token Delete
v1.04 changes:

  - Fixed:
    - The window now opens in the center of the screen. [#dfc396d][dfc396d]
    - The window now always opens in focus. [#f886c4f][f886c4f]

[dfc396d]: https://github.com/Nenotriple/img-txt_viewer/commit/dfc396d36b95fe6fc42ad9144008d839eb2e2dd5
[f886c4f]: https://github.com/Nenotriple/img-txt_viewer/commit/f886c4fe51a41fcc4766f3d7b5d0659537ec5ea3
