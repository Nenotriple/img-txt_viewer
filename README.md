
<h1 align="center">
  <img src="https://github.com/Nenotriple/img-txt_viewer/assets/70049990/8342e197-25c7-4e78-a27d-38daa79b4330" alt="icon" width="50">
  img-txt Viewer
</h1>

<p align="center">A Windows application to display an image and text file side-by-side for easy manual captioning or tagging.</p>
<p align="center">+Tons of features to help you work faster!</p>

<p align="center">
  <img src="https://github.com/Nenotriple/img-txt_viewer/assets/70049990/d7d9c754-aae4-4add-882d-fef105cd0531" alt="cover">
</p>

- [📝Usage](#-usage)
- [💡Tips and Features](#-tips-and-features)
- [🔒 Privacy](#-privacy)
- [🚩Requirements](#-requirements)
- [📜Version History](#-version-history)
- [✨Wiki](https://github.com/Nenotriple/img-txt_viewer/wiki)
- [💾Download](https://github.com/Nenotriple/img-txt_viewer/releases?q=executable&expanded=true)

---

# 📝 Usage

> [!NOTE]
> - Prepare Your Files:
>    - If you choose to include a text pair for an image, ensure they share the same basename.
>      - For example: `01.png, 01.txt`, `02.jpg, 02.txt`, etc.
>  - Supported image types: `.png` `.jpg` `.jpeg` `.jfif` `.jpg_large` `.webp` `.bmp` `.gif`


Images and text files can be loaded from different folder paths. Expand the section below to learn more.

<details>
  <summary>Selecting an alternate text path...</summary>

By default, text files are loaded from the chosen path. To load text files from a different path, first select a directory as usual, then right-click the `Browse...` button and select `Set Text File Path`. An indicator to the left of the Directory entry will turn blue when a different path is chosen, and hovering the mouse over the indicator will display the selected text path.

 - Example folder structures:


```
.
└── dataset/
    ├── 01.png
    ├── 01.txt
    ├── 02.jpg
    └── 02.txt
```
*(Images and text files in same folder)*

```
.
└── dataset/
    ├── images/
    │   ├── 01.png
    │   └── 02.jpg
    └── captions/
        ├── 01.txt
        └── 02.txt
```
*(Images and text files in separate folder)*

</details>

# 💡 Tips and Features

- Shortcuts:
  - `ALT+LEFT/RIGHT`: Quickly move between img-txt pairs.
  - `SHIFT+DEL`: Send the current pair to a local trash folder.
  - `ALT`: Cycle through auto-suggestions.
  - `TAB`: Insert the highlighted suggestion.
  - `CTRL+S`: Save the current text file.
  - `CTRL+E`: jump to the next empty text file.
  - `CTRL+R`: Jump to a random img-txt pair.
  - `CTRL+F`: Highlight all duplicate words.
  - `CTRL+Z` / `CTRL+Y`: Undo/Redo.
  - `F5`: Refresh the text box.
  - `Middle-click`: A tag to quickly delete it.

- Tips:
  - Highlight matching words by selecting text.
  - Enable `List View` to display text in a vertical list format.
  - Quickly create text pairs by loading the image and saving the text.
  - Get `Autocomplete Suggestions` while you type using Danbooru/Anime tags, the English Dictionary, etc.
  - `Fuzzy Search` Use an asterisk * while typing to return a broader range of suggestions.
    - For example: Typing `*lo*b` returns "<ins>**lo**</ins>oking <ins>**b**</ins>ack", and even "yel<ins>**lo**</ins>w <ins>**b**</ins>ackground"

- Text Tools:
  - `Batch tag Delete`: View all tag in a directory as a list, and quickly delete them._<sup>[1]</sup>_
  - `Prefix Text Files`: Insert text at the START of all text files.
  - `Append Text Files`: Insert text at the END of all text files.
  - `Search and Replace`: Edit all text files at once.
  - `Filter Pairs`: Filter pairs based on matching text, blank or missing txt files, and more.
  - `Active Highlights`: Always highlight specific text.
  - `My Tags`: Quickly add you own tags to be used as autocomplete suggestions.
  - `Cleanup Text`: Fix simple typos in all text files of the selected folder.

 - Other Tools
   - `Batch Resize Images`: Resize a folder of images using several methods and conditions._<sup>[1]</sup>_
   - `Resize Image`: Resize a single image.
   - `Batch Crop Images`: Crop a folder of images to an exact size, resizing if needed.
   - `Crop Image`: Quickly crop an image to a square or freeform ratio.
   - `Upscale Image`: Upscale an image using `realesrgan-ncnn-vulkan` _<sup>[1]</sup>_
   - `Expand Current Image`: Expand an image to a square ratio instead of cropping.
   - `Find Duplicate Files`: Find and separate any duplicate files in a folder. _<sup>[1]</sup>_
   - `Rename and Convert Pairs`: Automatically rename and convert files using a neat and tidy formatting.

 - Auto-Save
   - Check the auto-save box to save text when navigating between img/txt pairs or closing the window, etc.
   - Text is cleaned when saved, so you can ignore typos such as duplicate tokens, multiple spaces or commas, missing spaces, and more.
   - `Clean text on save` Can be disabled from the options menu.

_<sup>[1]</sup>These are stand alone tools and/or not available in the Lite version._

Please see the [✨Tools](https://github.com/Nenotriple/img-txt_viewer/wiki/Tools) section of the wiki for a more comprehensive breakdown of the various features.


# 🔒 Privacy

img-txt Viewer is completely private, in every sense of the word.
- The app runs entirely on your device, so your data stays with you.
- It does not collect any data, or require an internet connection.


# 🚩 Requirements

> [!TIP]
> You don't need to worry about any requirements with the Windows [💾portable/executable](https://github.com/Nenotriple/img-txt_viewer/releases?q=executable&expanded=true) version.

<details>
  <summary>Python requirements...</summary>

**Python 3.10+**

You will need `Pillow` and `NumPy`:
- `pip install pillow numpy`

Or use the included `requirements.txt` when setting up your venv.
</details>

# 📜 Version History

[💾v1.95](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.95)

<details>
  <summary>Click here to view release notes for v1.95</summary>

  - New:
    - New tab `Stats`: View file stats related to the current directory, including total files, characters, captions, average characters, words, captions per file, lists of captions, resolutions, common words, and more.
    - New option `Loading Order`: Set the loading order based on name, file size, date, ascending/descending, etc.
    - New option `Reset Settings`: Reset all user settings to their default parameters, with an option to reset “My Tags”.
    - New option `Auto-Delete Blank Files`: Enable this setting to automatically remove blank text files when they're saved. [#25](https://github.com/Nenotriple/img-txt_viewer/issues/25)
    - New tool `Rename Pair`: Manually rename a single img-txt pair.
    - New tool `Create Blank Text Pairs`: This tool will create a text file for any un-paired image.
    - New tool `Archive Dataset`: Use this to quickly zip the current working folder.
    - New Tool `Batch Upscale`: Same as 'Upscale Image', but this can upscale an entire folder of images.
    - Enhanced text selection for the primary text box and most text entries, treating common punctuation and symbols as word boundaries on double-click and allowing selection of entire entry text strings with a triple-click. [#26](https://github.com/Nenotriple/img-txt_viewer/issues/26)
    - New text box right-click menu option: `Open Text File...`


<br>


  - Fixed:
    - Filtering using regex patterns now works as intended. [#27](https://github.com/Nenotriple/img-txt_viewer/issues/27)
    - Fixed right-click not triggering the primary text box context menu if the textbox wasn't initially focused with a left-click.
    - Fixed AttributeError when refreshing the custom dictionary.
    - Fixed the issue where using the `CTRL+S` hotkey to save the text wouldn't display *Saved* in the message label.
    - Fixed `Rename and Convert` improperly naming text file pairs.
    - Improved image loading to prevent [WinError 32], also fixing issues with the “Delete Pair” tool.
    - Improved UI handling of situations where filtering would result in zero matches.
    - Prevented the Image-Grid from opening when there aren't any images to display.
    - The file filter is now cleared when changing the selected directory.
    - Fixed issue where settings were not reset when clicking NO to reset "my_tags"


<br>


  - Other changes:
    - Toggle Zoom - The popup is now centered next to the mouse and behaves better around the screen edges.
    - `Delete img-txt Pair` now allows you to send the pair to the recycle bin.
    - Navigating pairs while auto-save is enabled is now much faster.
    - You can now set a filter by using the enter/return key with the filter widget in focus.
    - You can now quickly open the "settings.cfg", and "my_tags.csv" files in your default system app.
    - You can now use Regex patterns in the `Search` field of the Search and Replace tool, along with the Highlight tool.
    - You can now use the Up/Down arrow keys to navigate while the img-txt index entry is focus.
    - You can now hold Shift when navigating (all methods) to advance by 5 instead of 1.
    - This message label now displays "No Changes" when attempting to save a file without making changes to it.
    - Ensured auto_save_var is properly restored to its original value if the text box does not exist when changing the working directory.
    - The "Clear" button in the Filter tab now turns red when the filter is active, and the tooltip also changes to show the filter state.
    - The tools *'Rename img-txt Pairs'* and *'Rename and Convert img-txt Pairs'* have been combined into a single tool called `Batch Rename and/or Convert`.
    - Using Undo after S&R/Prefix/Append, will now delete text files that previously didn't exist at the time when those tools were ran.
    - This version comes with many small tweaks and updates, along with some minor internal code refactoring.


<br>


  - Project Changes:
    - **Image-Grid:** v1.03
      - New:
        - Filtering options are now moved to a new menu.
        - You can now filter images by `Resolution`, `Aspect Ratio`, `Filesize`, `Filename`, `Filetype`, and `Tags`.
          - Along with these operators, `=`, `<`, `>`, `*`
        - Resolution and Filesize are now displayed in the image tooltip.
        - `Auto-Close`: This setting is now saved to the `settings.cfg` file. [#24](https://github.com/Nenotriple/img-txt_viewer/issues/24)
      - Fixed:
        - Fixed the issue of not being able to focus on the image grid window when selecting it from the taskbar. [#24](https://github.com/Nenotriple/img-txt_viewer/issues/24)
      - Other changes:
        - Increased the default number of images loaded from 150 to 250.
        - Improved image and text cache.
        - Update index logic to support new loading order options.
    - **Upscale Image:** v1.04
      - New:
        - Now supports batch upscaling a folder of  images.
        - The `Upscale Factor` widget is now a slider allowing you to select `from 0.25`, `to 8.0`, in `0.25 increments`.
        - New settings: `Strength` Set this from 0%, to 100% to define how much of the original image is visible after upscaling.
      - Fixed:
        - Settings are now disabled while upscaling to prevent them from being adjusted while upscaling.
        - Fixed issues with opening and holding-up images in the process.
    - **TkToolTip:** v1.04
      - New:
        - Now supports an ipadx, or ipady value for interior spacing. The default value is 2.
      - Other changes:
        - x_offset, and y_offset have been renamed to padx, and pady.

</details>
<br>

[💾v1.94](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.94)

<details>
  <summary>Click here to view release notes for v1.94</summary>

  - New:
    - New option: `Toggle Zoom`, This allows you to hover the mouse over the current image and display a zoomed in preview.
      - Use the Mouse-Wheel to zoom in and out.
      - Use Shift+Mouse-Wheel to increase or decrease the popup size.


<br>


  - Fixed:
    - `Image Grid`, Fixed issue where supported file types were case sensitive, leading to images not appearing, and indexing issues.


<br>


  - Other changes:
    - Improved performance of Autocomplete by optimizing: data loading, similar names, string operations, and suggestion retrieval. Up to 50% faster than v1.92
    - `Image Grid`, Now reuses image cache across instances to speed up loading.

</details>
<br>

[💾v1.93.1](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.93.1)

<details>
  <summary>Click here to view release notes for v1.93.1</summary>

  - New:
    - New autocomplete matching modes: `Match Whole String`, and `Match Last Word` [732120e](https://github.com/Nenotriple/img-txt_viewer/commit/732120e61dbe0758f8f00c4852edf3f435b32c29)
      - `Match Whole String`, This option works exactly as before. All characters in the selected tag are considered for matching.
      - `Match Last Word`, This option will only match (and replace) the last word typed. This allows you to use autocomplete with natural sentences. You can type using an underscore as a space to join words together.
    - New option for image grid view: `Auto-Close`, Unchecking this option allows you to keep the image grid open after making a selection. [67593f4](https://github.com/Nenotriple/img-txt_viewer/commit/67593f4876daf0cdbc6170dbb7c8820b99d8636d)
    - New Tool: `Rename img-txt pairs`, Use this to clean-up the filenames of your dataset without converting the image types. [8f24a7e](https://github.com/Nenotriple/img-txt_viewer/commit/8f24a7e41a4fb4770fb5bd06d9dd2337b31c6270)
    - You can now choose the crop anchor point when using `Batch Crop Images`. [9d247ea](https://github.com/Nenotriple/img-txt_viewer/commit/9d247ea582218366be7969b4c30d20fb7e8fbe87)

<br>


  - Fixed:
    - Fixed issue #23 where initially loading a directory could result in the first text file displayed being erased. [ae56143](https://github.com/Nenotriple/img-txt_viewer/commit/ae561433a8a98fbcbbb3c1a1a6a35c05b412d9cc)


<br>


  - Other changes:
    - Improved performance of Autocomplete, by handling similar names more efficiently. Up to 40% faster than before. [d8be0f2](https://github.com/Nenotriple/img-txt_viewer/commit/d8be0f28ff681be45beb8ca7694e9fc4fb4aa55c)
    - Improved performance when viewing animated GIFs by first resizing all frames to the required size and caching them. [c8bd32a](https://github.com/Nenotriple/img-txt_viewer/commit/c8bd32a408213fab5cba0dd5842c9f9bb050e4fa)
    - Improved efficiency of TkToolTip by reusing tooltip widgets, adding visibility checks, and reducing unnecessary method calls. [8b6c0dc](https://github.com/Nenotriple/img-txt_viewer/commit/8b6c0dc70c7547bbb0c873cbc9e02235a8725cdd)
    - Slightly faster image loading by using PIL's thumbnail function to reduce aspect ratio calculation. [921b4d3](https://github.com/Nenotriple/img-txt_viewer/commit/921b4d38132e82078c34316fd12b45fc4e61694b)


<br>


  - Project Changes:
    - **Batch Resize Images:** v1.06 [19d5b4d](https://github.com/Nenotriple/img-txt_viewer/commit/19d5b4d5fbe3ac6629d0755e24f3b560be800125)
      - See full list of changes here: https://github.com/Nenotriple/batch_resize_images/releases
    - **Upscale:** v1.02 [616ddaa](https://github.com/Nenotriple/img-txt_viewer/commit/616ddaa6ebd897b3f63cf921406f0e5ed958f930)
      - The current and total GIF frames are now displayed in the UI.

</details>
<br>
