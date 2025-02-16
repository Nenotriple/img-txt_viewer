

# Index

- [v1.96](#v196)
- [v1.95](#v195)
- [v1.94](#v194)
- [v1.93.1](#v1931)
- [v1.92](#v192)
- [v1.91](#v191)
- [v1.90 🎉🎈](#v190)
- [v1.85](#v185)
- [v1.84](#v184)
- [v1.82](#v182)
- [v1.81](#v181)
- [v1.80](#v180)
- [v1.79](#v179)
- [v1.78](#v178)
- [v1.77](#v177)
- [v1.76](#v176)
- [v1.75](#v175)
- [v1.74](#v174)
- [v1.73](#v173)
- [v1.72](#v172)
- [v1.71](#v171)
- [v1.70](#v170)
- [v1.68](#v168)
- [v1.67](#v167)
- [v1.66](#v166)
- [v1.65](#v165)
- [v1.63](#v163)
- [v1.62](#v162)
- [v1.60](#v160)
- [v1.50](#v150)
- [v1.42](#v142)
- [v1.41](#v141)
- [v1.40](#v140)
- [v1.30](#v130)
- [v1.20](#v120)
- [v1.0](#⬆v10)



<!--###########################################################################-->


## v1.97
- [⬆️](#index)

<details>
  <summary>Release Notes for v1.97</summary>


**New:**
- **Wrap selected text in brackets**:
  - Select text in the primary text box, press a *LEFT / OPENING* bracket key `(`, `[`, `{`, `"`, `'`
  - Useful for weighted captions, example: `((sometext))`
- You can now see a list of all tags from the `MyTags` tab, allowing you to insert these tags into MyTags or the text box.
- Added commands to `AutoTags` context menu:
  - `Add to Exclude` - Quickly add the selected tag(s) to the Exclude entry.
  - `Add to Keep` - Quickly add the selected tag(s) to the Keep entry.
- The `Stats` tab now shows the current character and word count.
- The `Image Grid` is now built into the primary interface.
- New option `Add Comma After Tag` [#51](https://github.com/Nenotriple/img-txt_viewer/issues/51)
  - When enabled (default), a comma and space ", " will be inserted at the end of the text box and after inserting a suggestion.


**Fixed:**
- Fixed errors when:
  - Typing in the primary text box when no dictionary is selected.
  - Resetting the font tab.
  - Closing the Crop image interface.
  - Attempting to open an image using the default editor `MS Paint`.
- Fixed an issue where the incorrect tag-list would be loaded when swapping AutoTag models.


**Other Changes:**
- It's now possible to *loop around* while clicking inside the Thumbnail panel for navigation.
- You can now resize the AutoTag tag list.


</details>
<br>


<!--###########################################################################-->

## v1.96
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.96)


<details>
  <summary>Release Notes for v1.96</summary>


This release introduces several new features and improvements, including AutoTag for automatic image tagging using ONNX vision models (WD14), revamped Batch Tag Edit and Crop tools, a Thumbnail Panel for quick navigation, and an Edit Image Panel for adjusting image properties. Additionally, numerous bugs have been fixed, such as issues with the Delete Pair tool, image quality degradation, and memory leaks.

The app now targets Windows 11, providing a more modern look and feel for most widgets.

Starting from this release, the `Lite` version will no longer be provided. All tools are now built-in.


---


**New:**
- **AutoTag**: Automatically tag images using ONNX vision models like `wd-v1-4-vit-tagger-v2`.
  - Download additional models from [Hugging Face](https://huggingface.co/SmilingWolf).
  - Place models in subfolders within the `onnx_models` directory, located in the same folder as this program. The subfolder name will be used as the model name.
  - Each model subfolder should contain a `model.onnx` file and a `selected_tags.csv` file.
  - Auto-Tagging was primarily tested with the `wd-v1-4-moat-tagger-v2` model.
- **Batch Tag Edit**: Previously known as Batch Tag Delete, this tool has been completely reworked for more versatile tag editing.
  - The interface is now more convenient and user-friendly, allowing you to see all pending changes before committing them.
  - It is no longer supported as a standalone tool.
- **Batch Resize Images**: Integrated into the main app.
  - NEW: A timer is now displayed in the bottom row.
  - FIXED: The following resize modes not working/causing an error: `Longer Side`, and `Height`.
  - FIXED: The resize operation is now threaded, allowing the app to remain responsive during the resizing process.
- **Find Duplicate Files**:
  - Integrated into the main app.
  - New Feature: Added "Move Captions" option.
    - Moves text pairs when found. Only works in "Images" scanning mode.
- **Crop Tool**: Completely reworked with new features and improved usability.
  - Includes all standard cropping features.
  - Special `Auto` fixed aspect ratio mode for quick cropping based on the image's aspect ratio and predefined aspect ratios.
- **Thumbnail Panel**: Displayed below the current image for quick navigation.
- **Edit Image Panel**: Enabled from the options/image menu, this section allows you to edit the `Brightness`, `Contrast`, `Saturation`, `Sharpness`, `Highlights`, and `Shadows` of the current image.
- **Edit Image**: Open the current image in an external editor, with MS Paint as the default.
  - Running `Set Default Image Editor` will open a dialog to select the executable (or `.py`, `.pyw`) path to use as the default image editor.
  - This should work with any app that accepts a file path as a launch argument (e.g., GIMP, Krita, Photoshop).
- **Create Wildcard From Captions**: Combine all image captions into a single text file, each set of image captions separated by a newline.
- **Copy Command**: Added to the right-click textbox context menu.
- **Last Command**: Added to the index entry right-click context menu to quickly jump to the last img-txt pair.
- **Additional Upscale Models**: Added `AnimeSharp-4x` and `UltraSharp-4x`.
- **NCNN Upscale Models**: Additional models can now be loaded by placing them in the `models` directory.
- **Insert Suggestion**: Now you can insert a suggestion by simply clicking it.
- **Guided Setup**: A quick guided setup will run on the app's first launch, or if the settings file is deleted/reset.
  - This will set the preferred autocomplete dictionaries and matching settings.
- **Close Window Shortcut**: Press `CTRL+W` to close the current window.
- **Danbooru (Safe)**: Added to the list of available dictionaries, a great choice to load with the English dictionary.
- **Easter Egg Game**: Can be opened from the ImgTxtViewer About Window.


**Fixed:**
- Fixed issue where the `Delete Pair` tool would overwrite the next index with the deleted text. #31
- Fixed an issue that was degrading the quality of the displayed image and not respecting the `Image Display Quality` setting.
- Fixed a memory leak that could occur whenever the primary image is displayed.
- Fixed Next/Previous button not properly displaying their relief when clicked.
- Fixed an issue where landscape images were improperly scaled, leading to an incorrect aspect ratio.
  - Additionally, large landscape images now scale to fit the window frame better.
- Fixed `Open Text Directory...` not respecting the actual filepath if set by `Set Text File Path...`.
- Fixed issue where the file lists were not updated when using the internal function `jump_to_image()`.
- Fixed an issue where the `alt text path` could be set to `.` when declining to reload the last directory.
- Fixed a bug where the window height would enlarge slightly when dragging the window from by the displayed image.
- Fixed the following tools not respecting the `Loading Order > Descending` setting, causing them to jump to the wrong index:
  - `Image Grid`, `Upscale Image`, `Resize Image`.
- Potential fix for the `Stats > PPI` calculation returning "0.00".
- If `clean-text` is enabled: The primary text box is now properly refreshed when saving.
- Fixed an issue when deleting tags that are a substring of another tag using middle-mouse-click. #38
- Fixed an issue where the system clipboard would become unresponsive after deleting a tag with the middle mouse button. #38
- Fixed an issue where settings were not restored when choosing to not reload the last directory.
- Fixed an error when loading the app and `my_tags.csv` didn't exist.
- Fixed an issue where suggestions weren't generated from `my_tags.csv` if no primary dictionary was loaded.
- Reloading the last directory is a little faster / smoother now.


**Other Changes:**
- Autocomplete suggestions are now cached, so re-typing the same words returns suggestions quicker.
  - Some pre-caching is done for Autocomplete suggestions, which does slow down the initial launch slightly.
- Using `Open Current Directory...` will now automatically select the current image in the file explorer. #30
  - The `Open` button will also select the current image if the path being opened is the same as the image path.
- The Image info (the stats displayed above the image) is now cached for quicker access.
- `Zip Dataset...` Now only zips images and text files in the selected directory, omitting subfolders.
- The `Options` and `Tools` menus have been reorganized.
- The color mode is now displayed in the image info panel.
- You can now close the `Crop Image` window with the `Escape` key.
- The message box is now removed.
  - You can now check the title for a visual indicator of the text state.
  - All tools that used the message box for notifications now use a message popup.
- Custom and duplicate highlights now use a range of pastel colors.
- Saving using the `CTRL + S` hotkey will now highlight the save button for a brief moment.
- The MyTags tab got an overhaul with more features.
- The target operating system for this project is now Windows 11, resulting in some UI changes.
  - Widgets are now made with ttk (when appropriate) for better styling on Windows 11.


**Project Changes:**
- **Upscale, Batch Upscale**: v1.05:
  - FIXED: Prevent the app from hanging while upscaling a GIF.
  - Batch Upscale: Added a label to display the number of images upscaled and the total number of images.
  - Batch Upscale: Added a timer and ETA label to show the total time taken and the estimated time remaining.
  - Batch Upscale: Entry path ToolTips are now updated when the path is changed.
  - Widgets are now made with ttk (when appropriate) for better styling on Windows 11.
- **TkToolTip**: v1.06:
  - NEW: `justify` parameter: Configure text justification in the tooltip. (Default is "center")
  - NEW: `wraplength` parameter: Configure the maximum line width for text wrapping. (Default is 0, which disables wrapping)
  - NEW: `fade_in` and `fade_out` parameters: Configure fade-in and fade-out times. (Default is 75ms)
  - NEW: `origin` parameter: Configure the origin point of the tooltip. (Default is "mouse")
  - FIXED: Issue where the underlying widget would be impossible to interact with after hiding the tooltip.
  - CHANGE: Now uses `TkDefaultFont` instead of Tahoma as the default font for the tooltip text.
  - CHANGE: The default background color is now "#ffffee", less yellow and more "off-white".
- **PopUpZoom**: v1.02:
  - NEW: `Rounded Corners` The popup now supports rounded corners. (Default: 30px)
- **Batch Crop** (v1.03), **Resize Images** (v1.02), **Image Grid** (v1.04):
  - Widgets are now made with ttk (when appropriate) for better styling on Windows 11.
- `crop_image` has been replaced with `CropUI`.


</details>
<br>


<!--###########################################################################-->

## v1.95
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.95)

<details>
  <summary>Release Notes for v1.96</summary>


- New:
  - New tab `Stats`: View file stats related to the current directory, including total files, characters, captions, average characters, words, captions per file, lists of captions, resolutions, common words, and more.
  - New option `Loading Order`: Set the loading order based on name, file size, date, ascending/descending, etc.
  - New option `Reset Settings`: Reset all user settings to their default parameters, with an option to reset “My Tags”.
  - New option `Auto-Delete Blank Files`: Enable this setting to automatically remove blank text files when they're saved. #25
  - New tool `Rename Pair`: Manually rename a single img-txt pair.
  - New tool `Create Blank Text Pairs`: This tool will create a text file for any un-paired image.
  - New tool `Archive Dataset`: Use this to quickly zip the current working folder.
  - New Tool `Batch Upscale`: Same as 'Upscale Image', but this can upscale an entire folder of images.
  - Enhanced text selection for the primary text box and most text entries, treating common punctuation and symbols as word boundaries on double-click and allowing selection of entire entry text strings with a triple-click. #26
  - New text box right-click menu option: `Open Text File...`


<br>


- Fixed:
  - Filtering using regex patterns now works as intended. #27
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
  - This version comes with many small UI tweaks and updates, along with some minor internal code refactoring.


<br>


- Project Changes:
  - **Image-Grid:** v1.03
    - New:
      - Filtering options are now moved to a new menu.
      - You can now filter images by `Resolution`, `Aspect Ratio`, `Filesize`, `Filename`, `Filetype`, and `Tags`.
        - Along with these operators, `=`, `<`, `>`, `*`
      - Resolution and Filesize are now displayed in the image tooltip.
      - `Auto-Close`: This setting is now saved to the `settings.cfg` file. #24
    - Fixed:
      - Fixed the issue of not being able to focus on the image grid window when selecting it from the taskbar. #24
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


Thank you to @MNeMoNiCuZ and @TeKett for your input!


</details>
<br>


<!--###########################################################################-->

## v1.94
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.94)

<details>
  <summary>Release Notes for v1.94</summary>


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


<!--###########################################################################-->

## v1.93.1
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.93.1)

<details>
  <summary>Release Notes for v1.93.1</summary>


- New:
  - New autocomplete matching modes: `Match Whole String`, and `Match Last Word` 732120e
    - `Match Whole String`, This option works exactly as before. All characters in the selected tag are considered for matching.
    - `Match Last Word`, This option will only match (and replace) the last word typed. This allows you to use autocomplete with natural sentences. You can type using an underscore as a space to join words together.
  - New option for image grid view: `Auto-Close`, Unchecking this option allows you to keep the image grid open after making a selection. 67593f4
  - New Tool: `Rename img-txt pairs`, Use this to clean-up the filenames of your dataset without converting the image types. 8f24a7e
  - You can now choose the crop anchor point when using `Batch Crop Images`. 9d247ea


<br>


- Fixed:
  - Fixed issue where Autocomplete was broken with the executable version. (incorrect build command)
  - Fixed issue #23 where initially loading a directory could result in the first text file displayed being erased. ae56143
  - Fixed issue where manually setting a directory, the text box and image index were not reset. 7874a13


<br>


- Other changes:
  - Improved performance of Autocomplete, by handling similar names more efficiently. Up to 40% faster than before. d8be0f2
  - Improved performance when viewing animated GIFs by first resizing all frames to the required size and caching them. c8bd32a
  - Improved efficiency of TkToolTip by reusing tooltip widgets, adding visibility checks, and reducing unnecessary method calls. 8b6c0dc
  - Slightly faster image loading by using PIL's thumbnail function to reduce aspect ratio calculation. 921b4d3


<br>


- Project Changes:
  - `Batch Resize Images`: v1.06 19d5b4d
    - See full list of changes here: https://github.com/Nenotriple/batch_resize_images/releases
  - `Upscale`: v1.02 616ddaa
    - The current and total GIF frames are now displayed in the UI.


</details>
<br>


<!--###########################################################################-->

## v1.92
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.92)

<details>
  <summary>Release Notes for v1.92</summary>


- New:
  - New tag list `Derpibooru`: Created from the top ~100k Derpibooru imageboard tags with additional filtering.
  - Image Grid: View all images as thumbnails in an overview. Access it from the 'Tools' menu, or from the right-click image menu.
    - Click an image to quickly jump to it.
    - Images without a text pair will have a small red flag added to them.
  - GIF support has been added to these tools: Upscale, Resize, Rotate, and Flip.
  - Alternate text path:
    - If an alternate text path has been set, that path will be restored when reloading the last directory on startup.
    - A small indicator to the left of the directory entry changes to blue when an alternate text path is set.
      - Hovering the mouse over this indicator will display a tooltip showing the text path.
  - The mouse wheel can now be used on the index entry to cycle through img-txt pairs.


<br>


- Fixed:
  - Fixed issue where "rename_and_convert_images" would save JPG in RGBA mode, which isn't supported.
  - Fixed error that occurred when double-clicking the image preview to drag the window.
  - Tons of small fixes.


<br>


- Other changes:
  - Small UI tweaks.


<br>


- Project Changes:
  - Refactored img_txt_viewer repo structure.
  - `Upscale`: (v1.01):
    - GIF support added.
    - After upscaling, the index is updated to the upscaled image.
    - Fixed a minor typo in UI.
  - `Resize Image`: (v1.01):
    - GIF support added.
    - After upscaling, the index is updated to the resized image.
    - Improved error handling when processing an image.
  - `Batch Resize Images`: (v1.03):
    - New output type: `Filetype: AUTO`, use this to output with the same filetype as the input image.
    - New options: `Overwrite Output`, when disabled, conflicting files will have "_#" appended to the filename.
    - Cancel button: Stop the resize operation without closing the window.
    - An image counter now displays the number of images in the selected path along with a running count of all resized images.
    - Fixed issue where files with the same basename but different extensions would be overwritten when converting to the same type.
    - Text descriptions are now consolidated into a help button/popup.
    - Many small UI tweaks and adjustments.


</details>
<br>


<!--###########################################################################-->

## v1.91
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.91)

<details>
  <summary>Release Notes for v1.91</summary>


- New:
  - New Tool: `Upscale Image`, Upscale a single image using `realesrgan-ncnn-vulkan`.
  - New Tool: `Resize Image`, This new tool allows you to resize the current image.
  - New Tool: `Batch Crop Images`, Automatically resize and crop images to a specific size (center crop).
  - New option: `Suggestion Threshold`, Use this to tune the performance of autocomplete, which may reduce suggestion diversity.
  - New option: `Image Display Quality`, Adjust the quality of the displayed image. 'High' mostly looks/performs the same as before.
  - New option: `Separate Text File Loading`, Load text files from another path via the "Browse..." button right-click context menu.
  - New hotkey: Press `CTRL+R` to go to a random img-txt pair.
  - The scale of the image is now displayed in the info bar.
  - You can now move the window around by clicking and dragging the current image with the mouse.


<br>


- Fixed:
  - `Goto Random` now always returns a different index.
  - `Autocomplete` now correctly allows typing a 'similar name' and matching it to the 'true name'.
  - Text cleanup no longer converts all text to lowercase.
  - Newline characters are no longer converted to commas when saving text.
  - `Rename and Convert img-txt Pairs` now handles files with duplicate basenames more effectively.
  - Improved handling of `.jfif` and `.jpg_large` files.
  - utf-8 encoding is now enforced when loading text files.
  - Fixed `FileNotFoundError` when the app tried to load an image that no longer exists. Like when a file is renamed.
  - Loading a corrupted image will now remove the offending image from the index (without deleting it) and prevent the app from crashing.
  - The directory entry now reverts to the current working path when moving to the next/prev pairs.
  - `Expand Image` and `Undo Delete` now correctly jump to the appropriate pair.
  - Fixed right-click not taking focus on the text box.
  - Fixed `Expand Image` error when working with ".webp" files.
  - Fixed `Expand Image` error when expanding an image with an uppercase filetype.
  - Pressing "Clear" on the Text Filter tool now restores the disabled widgets when clearing `Empty Files`.
  - `settings.cfg` is removed on version mismatch.
  - Quickly scrolling the mouse wheel to cycle through pairs is now smoother, with less chance of skipping.
  - Improved error handling for various other minor issues.


<br>


- Other changes:
  - Significant speedup when loading and scaling an image in the UI. Average time before ~45ms, now ~5ms.
  - Using `Undo Delete Pair` now displays the files that will be restored.
  - Font size now updates as the slider is dragged instead of when released.
  - Toggling the `Auto-Save` checkbutton will now check if the text file has changed and will properly display the state.
  - The message box now displays "No Change" while typing if the text box is the same as the current text file.
  - Improved UI logic for widgets in the "Filter" tab, the autocomplete suggestion text, and other small tweaks.
  - `Big Comma Mode` has been removed.
  - `dictionary.csv`: Removed all words shorter than 3 characters. ~900 words removed.
  - `settings.cfg` now tracks these user-settings: `Auto-Save`, `Cleaning Text`, `Big Save Button`, `Highlighting Duplicates`, `App Version`.
  - Inserting a suggestion no longer creates leading or trailing spaces.
  - `List View` and `Middle-click to delete tag` are now disabled if text cleanup is also disabled.


<br>


- Project Changes:
  - `Batch Resize Images`: (v1.02):
    - The `resize_images.py` script has been renamed to `batch_resize_images.py`.
    - A new resize mode, `Percentage`, has been added. This allows you to resize images by a percentage scaling factor.
    - The labels for inputs now change based on the selected resize mode.
  - `Batch Tag Delete`: (v1.08):
    - Long folder paths are now displayed more effectively in the UI.
  - `Find Duplicate Files`: (v1.01):
    - The `Pillow` import has been removed, reducing the size of the executable file by ~75%.


</details>
<br>


<!--###########################################################################-->

## v1.90
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.90)

<details>
  <summary>Release Notes for v1.90</summary>


I'm very happy to announce **img-txt_viewer is 1 year old!** 🎉🎈

I love knowing this app has helped at least a few people work faster and easier, and I want to thank everyone so much for your interest and support.

Here's some new tools, fixes, and changes for version 1.90:


---


- New:
  - `Find Duplicate Files`: Quickly find and separate duplicate images in your dataset.
    - This works by checking file hash - 2GB file limit. Can be used for all files
    - Built as a stand alone tool.
  - `Rename/convert img-txt Pairs`: Easily rename and convert your dataset in a clean format.
    - All images are converted to ".jpg" format to prevent duplicate filename issues.
    - JPG conversion quality is set to 100, this ensures a small file size and no visible compression will be added for most conversions.
    - Example: 00001.jpg, 00001.txt.
  - `Expand Current Image`: Expand images to a square resolution without cropping.
    - This tool makes an image square by extending its shorter side to match the length of its longer side, after rounding that length down to the nearest multiple of 8.
    - The empty space is then filled by expanding the border of pixels from the long side.
  - `Crop Image`: Crop the currently displayed image.
    - Currently only supports cropping by square (1:1) or freeform.
    - Double click to quickly create a 512x512 or 1024x1024 rectangle (automatically decided based on image size)
    - Right-click the image to open the context menu and select either Crop, Clear, or Open Directory.
    - Mousewheel to resize the rectangle.
  - `Flip Image`: Flip the currently displayed image horizontally.
  - `Rotate Image`: Rotate the the currently displayed image 90 degrees.
  - `Duplicate Pair`: Duplicate the currently displayed img-txt pair.
  - `Filter Pairs` Changes:
    - New option to display only empty text files.
    - Use `!` before the text to exclude any pairs containing that text.
    - Use `+` between text to include multiple strings when filtering.
    - Example: `!dog + cat` (remove dog pairs, display cat pairs)
  - `Resize Images` v1.01 Changes:
    - You can now choose image filetype for the resized output.
    - You can now set the `Resize Condition` to the following modes:
      - `Upscale and Downscale`, Resize the image to the new dimensions regardless of whether they are larger or smaller than the original dimensions.
      - `Upscale Only`, Resize the image if the new dimensions are larger than the original dimensions.
      - `Downscale Only`, Resize the image if the new dimensions are smaller than the original dimensions
  - `Batch Tag Delete` v1.07 Changes:
    - Significantly improved the speed tags are deleted.
    - You can now choose a new directory after opening the app.
  - Text Box changes:
    - The displayed text can now be refreshed from the right-click text_box context menu. (Hotkey: F5)
    - You can now select text and add it to the custom dictionary with the right click context menu.
  - Image info is now displayed above the current image (filename, resolution, size)
  - The last directory and index can now be quickly restored when launching the app. #21


<br>


- Fixed:
  - Fixed image scaling regression that prevented images from scaling to fill the frame.
  - Fixed issue where the image index would no longer sort correctly after files were added or removed from the working directory.
  - Fixed issue where a new text file wasn't being created when saving the text box.
  - Fixed Auto-Save not triggering when loading a new directory.


<br>


- Other changes:
  - "file_watcher" logic has been removed.
    - This was used to update the index or text box when changes occurred outside the app’s control.
    - It was easier to remove than fix the issues with threading...
  - Removed the following from the script. These changes do not affect exe users:
    - Automatic check and install of Pillow.
    - Automatic check and download of dictionary files.
    - `threading` and `requests` imports removed.
  - UI changes:
    - The directory button has been replaced with a text entry field, browse/open buttons, and a right-click context menu.
    - Added descriptions below each tool along the bottom toolbar.
    - The save button can now be set to double height by right clicking it, or from the Options menu. #19
    - And other small changes.
  - Max Image size values have been slightly reduced to improve performance when scaling the image within the UI.
  - "Delete Pair" keyboard shortcut changed from `Del` to `Shift+Del`. #19
  - You now have the flexibility to choose any combination from the available autocomplete dictionaries.


<br>


</details>
<br>


<!--###########################################################################-->

## v1.85
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.85)

<details>
  <summary>Release Notes for v1.85</summary>


- New:
  - New Text Tool `Filter Pairs`: Use this to search all text files and filter the img-txt pairs to display only those that include the matched text.
    - Also supports regular expressions.
  - New Text Tool `Active Highlights`: Use this to always highlight certain text.
    - Use ` + ` to highlight multiple strings of text, *(Note the spaces!)*. Example: dog + cat


</details>
<br>


<!--###########################################################################-->

## v1.84
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.84)

<details>
  <summary>Release Notes for v1.84</summary>


- New:
  - New tool: `Resize Images`: You can find this in the Tools menu.
    - Resize operations: Resize to Resolution, Resize to Width, Resize to Height, Resize to Shorter Side, Resize to Longer Side
    - Just like "batch_tag_delete.py", "resize_images.py" is a stand-alone tool. You can run it 100% independently of img-txt_viewer.
    - Images will be overwritten when resized.
   - New option: `Colored Suggestions`, Use this to enable or disable the color coded autocomplete suggestions.


<br>


- Fixed:
  - Fixed suggestions breaking when typing a parentheses.


<br>


- Other changes:
  - Batch Tag Delete is no longer bundled within img-txt_viewer. This allows you to run them separately.


---


Batch Tag Delete
v1.06 changes:


- Fixed:
  - Fixed tag list refreshing twice
  - Fixed multi-tag delete when "batch_tag_delete" is ran from "img-txt_viewer"


</details>
<br>


<!--###########################################################################-->

## v1.83
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.83)

<details>
  <summary>Release Notes for v1.83</summary>


- Fixed:
  - Fix text box duplicating when selecting a new directory.
  - Fixed some small issues with the file watcher and image index.


<br>


- Other changes:
  - Minor code cleanup and internal changes.


</details>
<br>


<!--###########################################################################-->

## v1.82
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.82)

<details>
  <summary>Release Notes for v1.82</summary>


The biggest visible change this release is the addition of a new Paned Window that now holds all text tools. (excluding Batch Tag Delete)
This makes it way more simple and easier to use these tools.


- New:
  - Search and Replace, Prefix Text, Append Text, Font Options, and Edit Custom Dictionary are now in a convenient tabbed interface below the text box.
  - You can now refresh the custom dictionary


<br>


- Fixed:
  - Saving a blank text file now deletes it.
  - Fixed error when 'Cleanup Text' was run in a folder where some images had missing text pairs.
  - Fixed an error when attempting to delete an img-txt pair and no text file was present.
  - 'Batch Tag Delete' and 'About' no longer open beside the main window. This prevents the new window from opening off the screen.
  - Running 'Prefix' or 'Append' text now creates text files for images that previously didn't have a pair.


<br>


- Other changes:
  - Basically all text tools were completely redone.
  - I've tried to fix as many small bugs and add polish wherever possible. Too many changes to list them all.


</details>
<br>


<!--###########################################################################-->

## v1.81
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.81)

<details>
  <summary>Release Notes for v1.81</summary>


- New:
  - Added underlining (Alt+Letter) to all menubar commands.


<br>


- Fixed:
  - Prevent app crash when selecting a folder without any text files.
  - Blank text files are no longer created when attempting to save a blank text box.
    - This includes when auto-save is enabled and moving between img-txt pairs.
  - Right clicking the text box no longer clears the text selection.
  - Properly set menu accelerator flags.
  - You can no longer select a directory that doesn't contain images.
  - Some menu options are now disabled before loading a directory.
  - `Edit Custom Suggestions` now opens the ".csv" file as a regular text document if no CSV file editor is present.


</details>
<br>


<!--###########################################################################-->

## v1.80
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.80)

<details>
  <summary>Release Notes for v1.80</summary>


- New:
  - Small ui tweaks. [#22b2764][22b2764]
  - `Fuzzy Search` You can now use an asterisk while typing to "search" for tags. [#05ca179][05ca179]
    - For example: Typing `*lo*b` returns "<ins>**lo**</ins>oking <ins>**b**</ins>ack", and even "yel<ins>**lo**</ins>w <ins>**b**</ins>ackground"
  - You can now undo the last operation for: Search and Replace, Prefix Text, and Append Text. [#c5be6a2][c5be6a2]
  - Batch Tag Delete no longer locks the main img-txt_viewer window. [#f2f8414][f2f8414]
  - You can now swap img-txt pair horizontal and vertical positions. [#ee7d052][ee7d052]
  - About window added. [#e692ebe][e692ebe]
  - The current text file is now scanned every 2 seconds, and refreshed if changed outside the app. [#95910e4][95910e4]


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
  - Other changes: [#f2f8414][f2f8414], [#9c8c580][9c8c580], [#0362e23][0362e23], [#fbcaaec][fbcaaec], [353827d][353827d], [#a41d99c][a41d99c], [#143140e][143140e], [#b38a786][b38a786]


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


</details>
<br>


<!--###########################################################################-->

## v1.79
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.79)

<details>
  <summary>Release Notes for v1.79</summary>


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


---


Batch Token Delete
v1.04 changes:


- Fixed:
  - The window now opens in the center of the screen. [#dfc396d][dfc396d]
  - The window now always opens in focus. [#f886c4f][f886c4f]


[dfc396d]: https://github.com/Nenotriple/img-txt_viewer/commit/dfc396d36b95fe6fc42ad9144008d839eb2e2dd5
[f886c4f]: https://github.com/Nenotriple/img-txt_viewer/commit/f886c4fe51a41fcc4766f3d7b5d0659537ec5ea3


</details>
<br>


<!--###########################################################################-->

## v1.78
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.78)

<details>
  <summary>Release Notes for v1.78</summary>


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


---


Batch Token Delete
v1.03 changes:


- New:
  - Now that text is cleaned within the script, this is a standalone app!
    - Simply launch the "batch_token_delete.py" script and select a folder to manage text/tags in that folder.
  - Deleting tags using a "less than or equal to" threshold now displays the affected tags.
  - A highlight has been added to the buttons/checkboxes.


<br>


- Fixed:
  - The app shares the parent icon, and groups with the main window in the taskbar.


</details>
<br>


<!--###########################################################################-->

## v1.77
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.77)

<details>
  <summary>Release Notes for v1.77</summary>


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


</details>
<br>


<!--###########################################################################-->

## v1.76
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.76)

<details>
  <summary>Release Notes for v1.76</summary>


- New:
   - Duplicate tokens are now removed when saving, cleaning, or inserting text.
   - Periods at the end of words are now replaced with commas when saving or cleaning text.
   - You can now enable or disable `Clean Text on Save`.
   - Pillow is now installed much more gracefully than before. _(Python version only)_
   - Various small UI tweaks


<br>


- Fixed:
  - `Autocomplete Inserting` fixes:
    - Duplicate trailing comma, duplicate first letter, no space inserted, double space inserted.
  - Using undo after inserting a suggestion should no longer be as jarring.


</details>
<br>


<!--###########################################################################-->

## v1.75
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.75)

<details>
  <summary>Release Notes for v1.75</summary>


- New:
  - New tool: `Batch Token Delete` This allows you to see a list of all tokens in the selected folder and delete them easily.
    - This tool can be used "standalone" without img-txt_viewer. Simply double-click the .py file and select a directory.
    - NOTE: v1.0 of Batch Token Delete relies on a cleanup function within img-txt_viewer to properly clean text files.
  - New tool: `Cleanup Text` This fixes common typos in all text files within a chosen folder, such as double commas or spaces and missing spaces after commas.
  - New option: `Suggestion Style` Here you can select from four options. The old style is still there, plus a new default style.
  - New option: `Suggestion Alignment` Here you can select between "Left Aligned", and "Centered". The default is now: Left Aligned.
  - Changes: `Prefix` and `Append`: These tools now insert commas and spaces where appropriate. Prefix=`token, ` Append=`, token`
  - UI Tweaks.


<br>


- Fixed:
  - `cleanup_text` now handles situations like `, ,` *(and repeating)*
  - Further improvements for suggested text insertion and cursor positioning. *(This is a tricky one to nail down)*
  - Pressing “Alt” to cycle a suggestion, then typing, unintentionally cycles the suggestion again.
  - When moving to the next/prev pair using the alt+Arrow hotkeys: The suggestion index would progress by +/-1.
  - The suggestion label now updates after setting the suggestion quantity.
  - Issue where `Big Comma Mode` wouldn't enable when using some features.
  - Error handling is added to check for a directory before running certain tools.


</details>
<br>


<!--###########################################################################-->

## v1.74
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.74)

<details>
  <summary>Release Notes for v1.74</summary>


- New:
    - `Search and Replace`: Replace any text string across all text files in the loaded directory.
    - `Prefix Text Files`: Insert text at the START of all text files.
    - `Append Text Files`: Insert text at the END of all text files.
    - Minor UI tweaks and enhancements.

<br>

- Fixed:
  - Resolved an issue where the app would repeatedly ask: `Do you want to create '...' new text files?` even after selecting `No`.
  - The 'Saved' label now updates correctly upon saving.
  - The image index is now refreshed only when the folder quantity changes, resulting in faster navigation.
  - Re-enabled the 'Undo' function.
  - Extensive internal code refactoring for improved cleanliness and maintainability.


</details>
<br>


<!--###########################################################################-->

## v1.73
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.73)

<details>
  <summary>Release Notes for v1.73</summary>


- New:
  - Big Comma Mode: This will make commas stand out much more, and it also changes the way text is spaced out.
  - Middle-clicking the directory button now opens the selected folder.
  - Right click or middle-click the displayed image to open the image directory.


<br />


- Fixed:
  - The image index now correctly updates with changes from outside the app. (Adding/Removing images)
  - Text files now won't be created even when you select "No". A saveable text box still appears for images without text files.
  - Images without a text pair can now be properly displayed without errors.
  - The displayed text file is now refreshed when saving. This correctly displays changes made by cleanup.
  - `jpg_large` files are now renamed to .jpg before loading.
  - Unresponsive directory button.


</details>
<br>


<!--###########################################################################-->

## v1.72
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.72)

<details>
  <summary>Release Notes for v1.72</summary>


- New:
  - Now you can use the mouse wheel over the displayed image to cycle through images.


- Fixed:
  - Escape characters `\` should now be properly handled during cleanup.


</details>
<br>


<!--###########################################################################-->

## v1.71
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.71)

<details>
  <summary>Release Notes for v1.71</summary>


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


</details>
<br>


<!--###########################################################################-->

## v1.70
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.70)

<details>
  <summary>Release Notes for v1.70</summary>


- Auto-Save
*If auto-save is enabled, changes to the text file are now saved automatically when the window is closed.*
*If auto-save isn’t enabled when closing, a warning is given. This allows the user to cancel and go back and save if needed.*

- *The insert_completed_suggestion function now better positions the cursor at the end of multi-word suggestions.*

- *Autocomplete scorer now prioritizes whole word matches, addressing the bias towards longer tags.*

- Pairs are now logically sorted:
*fixing the issue where filenames like 10 or 100 loaded before 2 or 9.*

- *The unused is_modified definition has been removed.*

- *The Pillow library and danbooru.csv file can now be installed and downloaded respectively, with an option to cancel/ignore.*

- A new “Options” menu has been added:
*Adjust font size.*
*Adjust suggestion quantity, allowing you to set a value between 0-10.*
*Delete img-txt pairs. A warning popup will confirm the choice or give the user an option to cancel.*

- UI enhancements include:
*Improved formatting and font size for info_label.*
*Restructured layout for saved_label and auto-save checkbox.*
*Color and width adjustments for saved_label.*
*highlight_selected_suggestion now uses a “Black Medium-Small Square” as an additional visual indicator.*
*An ellipsis has been added to the idle suggestion label.*


</details>
<br>


<!--###########################################################################-->

## v1.68
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.68)

<details>
  <summary>Release Notes for v1.68</summary>


- *New: Previous/Next buttons are now side-by-side.*
- *New/Fixed: Choosing suggestions is now done with ALT. This prevents suggestions from being inserted erroneously.*
- *Fixed: Inserting suggestions is now possible anywhere in the text field, not just the end of the text box.*
- *Fixed: Duplicates will now be highlighted when selected with the keyboard.*
- *Fixed: Commas are now ignored when matching highlighted duplicates.*


</details>
<br>


<!--###########################################################################-->

## v1.67
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.67)

<details>
  <summary>Release Notes for v1.67</summary>


- *New: Select image viewing size. - small, medium, large, etc.*


</details>
<br>


<!--###########################################################################-->

## v1.66
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.66)

<details>
  <summary>Release Notes for v1.66</summary>


- *New: Image now scales with window size.*
- *New: Zoom has been removed for now.*


</details>
<br>


<!--###########################################################################-->

## v1.65
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.65)

<details>
  <summary>Release Notes for v1.65</summary>


- *New: Zoom into images by clicking them*
- *New: Loop around the image index when hitting the end/start*
- *New: Quickly jump to a specific image*


</details>
<br>


<!--###########################################################################-->

## v1.63
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.63)

<details>
  <summary>Release Notes for v1.63</summary>


- *Autocomplete now returns much better suggestions.*
- *Further improvements to typo correction.*


</details>
<br>


<!--###########################################################################-->

## v1.62
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.62)

<details>
  <summary>Release Notes for v1.62</summary>


- **New:** Tips and features added to startup.
- **New:** Removed directory text widget and replaced it with a button with a dynamic label.
- **Misc:** Error handling added when selecting a directory.
- **Misc:** utf-8 encoding is enforced.
- **Fixed:** Saving now fixes various typos such as: Double and triple commas are replaced with single commas. Extra spaces are reduced to single spaces. leading and trailing spaces/commas are removed.
- **Fixed:** Undo/Redo now works as expected.


</details>
<br>


<!--###########################################################################-->

## v1.60
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.6)

<details>
  <summary>Release Notes for v1.60</summary>


- **New:** Get autocomplete suggestions while you type using danbooru tags.
- Pressing _TAB_ inserts the selected suggestion.
- Pressing _TAB+Left/Right_ selects the autocomplete suggestion.


</details>
<br>


<!--###########################################################################-->

## v1.50
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v15.)

<details>
  <summary>Release Notes for v1.50</summary>


- **New:** Select and highlight duplicates
- You can now select text with the mouse/keyboard and you'll be able to quickly see duplicates. Super helpful when manually editing dense caption files.


</details>
<br>


<!--###########################################################################-->

## v1.42
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.42)

<details>
  <summary>Release Notes for v1.42</summary>


- **New:** Now supports loading `.jpeg` `.webp` `.bmp` image types.
- **Misc:** Minor ui improvements.


</details>
<br>


<!--###########################################################################-->

## v1.41
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.41)

<details>
  <summary>Release Notes for v1.41</summary>


- **Fixed:** Image aspect ratio is now preserved.


</details>
<br>


<!--###########################################################################-->

## v1.40
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.4)

<details>
  <summary>Release Notes for v1.40</summary>


- **New:** The user is now asked whether or not they would like to create blank text files for images that don't already have a matching text pair.


</details>
<br>


<!--###########################################################################-->

## v1.30
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.3)

<details>
  <summary>Release Notes for v1.30</summary>


- **New:** Text files now created for images without them.
- **Misc:** Window minsize now (675, 560) - prevents ui squish.


</details>
<br>


<!--###########################################################################-->

## v1.20
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.2)

<details>
  <summary>Release Notes for v1.20</summary>


- **Fixed:** Now removes trailing space/new line when saving.


</details>
<br>


<!--###########################################################################-->

## v1.0
- [⬆️](#index)
- [💾](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.0)

<details>
  <summary>Release Notes for v1.0</summary>


**This is the first release.**


</details>
<br>



<!--###########################################################################
## TEMPLATE

## v1.
- [⬆️](#index)

<details>
  <summary>Release Notes for v1.</summary>



</details>
<br>


-->
