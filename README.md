<h1 align="center"><img src="https://github.com/Nenotriple/img-txt_viewer/assets/70049990/8342e197-25c7-4e78-a27d-38daa79b4330" alt="icon" width="50">img-txt Viewer</h1>
<p align="center">A Windows application for side-by-side image and text viewing, designed to streamline manual captioning or tagging.</p>
<p align="center"><img src="https://github.com/Nenotriple/img-txt_viewer/assets/70049990/d7d9c754-aae4-4add-882d-fef105cd0531" alt="cover"></p>


<div align="center">

![GitHub last commit](https://img.shields.io/github/last-commit/Nenotriple/img-txt_viewer)
![GitHub contributors](https://img.shields.io/github/contributors/Nenotriple/img-txt_viewer)
![GitHub repo size](https://img.shields.io/github/repo-size/Nenotriple/img-txt_viewer)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FNenotriple%2Fimg-txt_viewer&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
![GitHub all release downloads](https://img.shields.io/github/downloads/Nenotriple/img-txt_viewer/total)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/Nenotriple/img-txt_viewer)


</div>


<br>


- [📝Usage](#-usage)
- [💡Tips and Features](#-tips-and-features)
- [🛠️Install](#-install)
- [🔒Privacy Policy](#-privacy-policy)
- [📜Version History](#-version-history)
- [✨Wiki](https://github.com/Nenotriple/img-txt_viewer/wiki)
- [💾Download](https://github.com/Nenotriple/img-txt_viewer/releases?q=executable&expanded=true)


<br>


# 📝 Usage


> [!NOTE]
>
> Prepare Your Files:
>
> - If you choose to include a text pair for an image, ensure they share the same basename.
>   - For example: `01.png, 01.txt`, `02.jpg, 02.txt`, etc.
>
> Supported image formats: `.png`, `.jpg`, `.jpeg`, `.jfif`, `.jpg_large`, `.webp`, `.bmp`, `.gif`.


Images and text files can be loaded from different folder paths. Expand the section below to learn more.


<details>


  <summary>Selecting an alternate text path...</summary>


---


By default, text files are loaded from the selected directory. To load text files from a different path:
1. Select a directory as usual.
2. Right-click the `Browse...` button and choose `Set Text File Path`.
3. When an alternate path is chosen, a blue indicator appears to the left of the directory entry. Hover over the indicator to view the selected text path.


<br>


Example folder structures:
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


<br>


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
  - `Batch tag Edit`: View all tag in a directory as a list: Filter, edit, and delete tags all at once.
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

For a more detailed feature guide, please visit the repo [✨Wiki](https://github.com/Nenotriple/img-txt_viewer/wiki).


<br>


# 🛠️Install
### Portable Setup
![Static Badge](https://img.shields.io/badge/Windows-gray)

1. Download the Windows executable from the [releases page](https://github.com/Nenotriple/img-txt_viewer/releases?q=executable&expanded=true).
2. Run the executable to launch the app.


### Python Package Setup
![Static Badge](https://img.shields.io/badge/Windows-Python_3.10%2B-green)

1. Download the app package from the [releases page](https://github.com/Nenotriple/img-txt_viewer/releases?q=package&expanded=true).
2. Run the `Start.bat` file to automatically create and activate a virtual environment, then launch the app.
3. `Start.bat` can be used to launch the app in the future.


<br>


<details>


  <summary>Manual Python Setup...</summary>


![Static Badge](https://img.shields.io/badge/Windows-Python_3.10%2B-green)


<br>


1. **Clone the repository:**
```
git clone https://github.com/Nenotriple/img-txt_viewer.git
```


3. **Navigate into the project directory:**
```
cd img-txt_viewer`
```


5. **Create and activate a virtual environment:**
```
python -m venv venv
venv\Scripts\activate
```


6. **Install the required dependencies:**
```
pip install -r requirements.txt
```


7. **Launch the app:**
```
python img-txt_viewer.pyw
```


</details>


<br>


# 🔒 Privacy Policy

**img-txt Viewer** is completely private, in every sense of the word.
- The app operates entirely on your device, ensuring your data remains solely under your control.
- No data is collected, transmitted, or stored, aside from a basic configuration file for app settings.
- The app functions 100% offline and never connects to external servers. No data is ever shared or sent elsewhere.


<br>


# 📜 Version History


[💾v1.96](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.96)


<details>
  <summary>Release notes for: v1.96</summary>


This release incorporates several new features, including a reworked Batch Tag Edit tool, a Thumbnail Panel for quick navigation, and an Edit Image Panel for adjusting image properties. Additionally, numerous bugs have been fixed, such as issues with the Delete Pair tool, image quality degradation, and memory leaks.

The app now targets Windows 11, and while it doesn't offer an complete `Aero` theme, many widgets have been updated to utilize a more modern theme where appropriate.


  - New:
    - `Batch Tag Delete` has been renamed to `Batch Tag Edit`.
      - This tool has been completely reworked to allow for more versatile tag editing.
      - The interface is now more convenient and user-friendly, allowing you to see all pending changes before committing them.
      - It is no longer supported as a stand-alone tool.
    - New feature `Thumbnail Panel`: Displayed below the current image for quick navigation.
    - New feature `Edit Image Panel`: Enabled from the options/image menu, this section allows you to edit the `Brightness`, `Contrast`, `Saturation`, `Sharpness`, `Highlights`, and `Shadows` of the current image.
    - New feature `Edit Image...`: Open the current image in an external editor, the default is MS Paint.
      - Running `Set Default Image Editor` will open a dialog to select the executable (or `.py`, `.pyw`) path to use as the default image editor.
      - This should work with any app that accepts a file path as a launch argument. (Gimp, Krita, Photoshop, etc.)
    - New tool `Create Wildcard From Captions`: Combine all image captions into a single text file, each set of image captions separated by a newline.
    - Added `Copy` command to the right-click textbox context menu.
    - Added `Last` to the index entry right-click context menu to quickly jump to the last img-txt pair.
    - A quick guided setup will run on the app's first launch, or if the settings file is deleted/reset.
      - This will set the preferred autocomplete dictionaries and matching settings.
    - You can now press `CTRL+W` to close the current window.


<br>


  - Fixed:
    - Fixed issue where the `Delete Pair` tool would overwrite the next index with the deleted text. #31
    - Fixed an issue that was degrading the quality of the displayed image and not respecting the `Image Display Quality` setting.
    - Fixed a memory leak that could occur whenever the primary image is displayed.
    - Fixed Next/Previous button not properly displaying their relief when clicked.
    - Fixed an issue where landscape images were improperly scaled, leading to an incorrect aspect ratio.
      - Additionally, large landscape images now scale to fit the window frame better.
    - Fixed `Open Text Directory...` not respecting the actual filepath if set by `Set Text File Path...`.
    - Fixed issue where the file lists were not updated when using the internal function "jump_to_image()".
    - Fixed an issue where the `alt text path` could be set to `.` when declining to reload the last directory.
    - Fixed a bug where the window height would enlarge slightly when dragging the window from by the displayed image.
    - Fixed the following tools not respecting the `Loading Order > Descending` setting, causing them to jump to the wrong index.
      - `Image Grid`, `Upscale Image`, `Resize Image`
    - Potential fix for the `Stats > PPI` calculation returning "0.00".
    - if `clean-text` is enabled: The primary text box is now properly refreshed when saving.


<br>


  - Other changes:
    - Using `Open Current Directory...` will now automatically select the current image in the file explorer. #30
      - The `Open` button will also select the current image if the path being opened is the same as the image path.
    - The Image info (the stats displayed above the image) is now cached for quicker access.
    - `Zip Dataset...` Now only zips images and text files in the selected directory, omitting subfolders.
    - The `Options`, and `Tools` menus have been reorganized.
    - The color mode is now displayed in the image info panel.
    - You can now close the `Crop Image` window with the `Escape` key.
    - I've switched to Windows 11, so it's now the target operating system for this project. You may notice some UI changes.


<br>


  - Project Changes:
    - `Upscale`, `Batch Upscale`: v1.05:
      - FIXED: Prevent the app from hanging while upscaling a GIF.
      - Batch Upscale: Added a label to display the number of images upscaled and the total number of images.
      - Batch Upscale: Added a timer and ETA label to show the total time taken and the estimated time remaining.
      - Batch Upscale: Entry path ToolTips are now updated when the path is changed.
      - Widgets are now made with ttk (when appropriate) for better styling on Windows 11.
    - `Batch Resize`: v1.07:
      - NEW: A timer is now displayed in the bottom row.
      - FIXED: The following resize modes not working/causing an error: `Longer Side`, and `Height`
      - FIXED: The resize operation is now threaded, allowing the app to remain responsive during the resizing process.
    - `TkToolTip`: v1.06:
      - NEW: `justify` parameter: Configure text justification in the tooltip. (Default is "center")
      - NEW: `wraplength` parameter: Configure the maximum line width for text wrapping. (Default is 0, which disables wrapping)
      - NEW: `fade_in` and `fade_out` parameters: Configure fade-in and fade-out times. (Default is 75ms)
      - NEW: `origin` parameter: Configure the origin point of the tooltip. (Default is "mouse")
      - FIXED: Issue where the underlying widget would be impossible to interact with after hiding the tooltip.
      - CHANGE: Now uses `TkDefaultFont` instead of Tahoma as the default font for the tooltip text.
    - `PopUpZoom`v1.02:
      - New: `Rounded Corners` The popup now supports rounded corners. (Default: 30px)
    - `Batch Crop`(v1.03), `Resize Images`(v1.02), `Image Grid`(v1.04):
      - Widgets are now made with ttk (when appropriate) for better styling on Windows 11.


</details>


<br>


[💾v1.95](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.95)


<details>


  <summary>Release Notes for: v1.95</summary>


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


  <summary>Release Notes for: v1.94</summary>


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


  <summary>Release Notes for: v1.93.1</summary>


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
