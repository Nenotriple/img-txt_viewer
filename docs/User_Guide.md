*"Making something... Nurturing something is really great. You can see and learn so many things from the process."* - 🍉


# User Guide


img-txt_viewer comes with many tools that help ease the process of manually creating a training dataset, as well as some others that may be helpful outside of this scope.

The following guide will provide an overview of the various tools and features available in the application, along with detailed instructions on how to use them effectively.

If you have any questions, need further assistance, or anything else, please feel free to [🚩create an issue](https://github.com/Nenotriple/img-txt_viewer/issues/new) in the repo.

Repo link: https://github.com/Nenotriple/img-txt_viewer

Check for updates: https://github.com/Nenotriple/img-txt_viewer/releases

You can also find a copy of this guide in the [✨Wiki](https://github.com/Nenotriple/img-txt_viewer/wiki) section of the repo.


# Index

- ✂️ [**Shortcuts**](#shortcuts)
  - [`ALT+LEFT/RIGHT`](#altleftright) - Quickly move between img-txt pairs.
  - [`SHIFT+DEL`](#shiftdel) - Send the current pair to a local trash folder.
  - [`ALT`](#alt) - Cycle through autocomplete suggestions.
  - [`TAB`](#tab) - Insert the highlighted suggestion.
  - [`CTRL+S`](#ctrls) - Save the current text file.
  - [`CTRL+E`](#ctrle) - Jump to the next empty text file.
  - [`CTRL+R`](#ctrlr) - Jump to a random img-txt pair.
  - [`CTRL+F`](#ctrlf) - Highlight all duplicate words.
  - [`CTRL+Z / CTRL+Y`](#ctrlz--ctrly) - Undo/Redo.
  - [`CTRL+W`](#ctrlw) - Close the window.
  - [`F1`](#f1-popup-zoom) - Toggle zoom popup.
  - [`F2`](#f2) - Open the Image-Grid view.
  - [`F4`](#f4) - Open the current image in your default editor.
  - [`F5`](#f5) - Open Batch Tag Edit.
  - [`Middle-click`](#middle-click) - Delete a tag.
- 📜 [**Text Tools**](#text-tools)
  - [`Search and Replace`](#search-and-replace) - Find and replace text across all text files.
  - [`Prefix`](#prefix) - Insert text at the start of all text files.
  - [`Append`](#append) - Insert text at the end of all text files.
  - [`AutoTag`](#autotag) - Automatically tag images using ONNX vision models.
  - [`Filter`](#filter) - Filter pairs based on text, missing text files, and more.
  - [`Highlight`](#highlight) - Always highlight specific text.
  - [`Font`](#font) - Adjust the font size and line height.
  - [`My Tags`](#my-tags) - Add your custom tags for autocomplete suggestions.
  - [`Stats`](#stats) - Display various file stats.
  - [`Batch Tag Edit`](#batch-tag-edit) - Edit and manage tags with a user-friendly interface.
  - [`Create Wildcard From Captions`](#create-wildcard-from-captions) - Combine all captions into one text file.
  - [`Cleanup Text`](#cleanup-text) - Fix typos across all text files.
- 📷 [**Image Tools**](#image-tools)
  - [`Batch Resize Images`](#batch-resize-images) - Resize all images using various methods and conditions.
  - [`Resize Image`](#resize-image) - Resize the current image by exact resolution or percentage.
  - [`Batch Crop Images`](#batch-crop-images) - Crop all images to a specified resolution.
  - [`Crop Image`](#crop-image) - Crop an image or GIF using various methods and tools.
  - [`Upscale Image`](#upscale-image) - Upscale image(s) using models like R-ESRGAN.
  - [`Find Duplicate Files`](#find-duplicate-files) - Identify and manage duplicate files.
  - [`Expand`](#expand) - Expand images to square ratio for simple backgrounds.
  - [`Edit Image Panel`](#edit-image-panel) - Adjust image properties like brightness, contrast, etc.
- 📦 [**Other Tools**](#other-tools)
  - [`Batch Rename/Convert`](#batch-renameconvert) - Rename and convert images sequentially with padded zeros.
  - [`Image-Grid`](#image-grid) - Browse images in a grid layout for easy selection.
  - [`Thumbnail Panel`](#thumbnail-panel) - Display thumbnails for quick navigation.
- ⚙️ [**Settings**](#settings)
  - [`Auto-Save`](#auto-save) - Save text automatically when switching pairs.
  - [`Clean-Text`](#clean-text) - Automatically clean text files when saving.
  - [`Auto-Delete Blank Files`](#auto-delete-blank-files) - Automatically delete blank text files.
  - [`Colored Suggestions`](#colored-suggestions) - Enable colorized autocomplete suggestions.
  - [`Highlight Selection`](#highlight-selection) - Highlight matching selected text.
  - [`Big Save Button`](#big-save-button) - Enlarge the save button.
  - [`List View`](#list-view) - Display the text box tags in a list view.
  - [`Always On Top`](#always-on-top) - Keep the app window on top of other windows.
  - [`Toggle Zoom`](#toggle-zoom) - Toggle the zoom popup.
  - [`Toggle Thumbnail Panel`](#toggle-thumbnail-panel) - Toggle the thumbnail panel.
  - [`Toggle Edit Panel`](#toggle-edit-panel) - Toggle the edit panel.
  - [`Vertical View`](#vertical-view) - Switch between horizontal and vertical view.
  - [`Swap Image Text Side`](#swap-image-text-side) - Swap the image and text sides.
  - [`Image Display Quality`](#image-display-quality) - Adjust image display quality.
  - [`Loading Order`](#loading-order) - Set the order for loading images and text files.
  - Autocomplete Settings:
    - [`Dictionary`](#dictionary) - Choose the autocomplete dictionary.
    - [`Threshold`](#threshold) - Set the autocomplete threshold.
    - [`Quantity`](#quantity) - Set the number of autocomplete suggestions.
    - [`Match Mode`](#match-mode) - Set the autocomplete match mode.
  - [`Reset Settings`](#reset-settings) - Reset all settings to default.
  - [`Open Settings File...`](#open-settings-file) - Open the settings file.
  - [`Open MyTags File...`](#open-mytags-file) - Open the mytags file.


<!--###########################################################################-->
<!--###########################################################################-->
<!--###########################################################################-->


# Shortcuts


## ALT+LEFT/RIGHT
[⬆️](#index) *(Navigate between img-txt pairs)*

With the primary text box in focus, press `ALT+LEFT` or `ALT+RIGHT` to move between img-txt pairs.

- `ALT+LEFT` moves back to the previous image.
- `ALT+RIGHT` moves forward to the next image.


## SHIFT+DEL
[⬆️](#index) *(Delete the current pair)*

Press `SHIFT+DEL` to move the displayed image and text file to a trash folder.

- The trash folder is created in the same directory as the image file.
- When closing the app, you'll be asked if you want to permanently delete the trash folder.
- Also available via the `Tools` menu and the image right-click context menu.
- If the trash folder already contains a file with the same name, you will be prompted to overwrite it or cancel the operation.


## ALT
[⬆️](#index) *(Cycle through autocomplete suggestions)*

With the primary text box in focus, press `LEFT ALT` or `RIGHT ALT` to move the autocomplete selector left or right.


## TAB
[⬆️](#index) *(Insert the selected autocomplete tag)*

With the primary text box in focus, press `TAB` to insert the selected autocomplete tag.


## CTRL+S
[⬆️](#index) *(Save the current text file)*

With the primary text box in focus, press `CTRL+S` to save the text to the paired text file.

- If the text box is blank, the paired text file will be deleted if `Auto-Delete Blank Files` is enabled.
- If the paired text file does not exist, it will be created.
- Also available via the `Save` button.


## CTRL+E
[⬆️](#index) *(Jump to the next empty text file)*

With the primary text box in focus, press `CTRL+E` to jump to the next img-txt pair where the text file is empty or does not exist.

- Also available via the index entry right-click context menu.


## CTRL+R
[⬆️](#index) *(Jump to a random img-txt pair)*

With the primary text box in focus, press `CTRL+R` to jump to a random img-txt pair.

- Also available via the index entry right-click context menu.


## CTRL+F
[⬆️](#index) *(Highlight all duplicate words)*

With the primary text box in focus, press `CTRL+F` to highlight any duplicate words.

- All matching words will be highlighted with the same color.
- This matches any duplicate string of text (minimum of 3 characters), not just tags or words.
- Also available via the primary text box right-click context menu.


## CTRL+Z / CTRL+Y
[⬆️](#index) *(Undo/Redo)*

With the primary text box in focus, press `CTRL+Z` to undo the last action or `CTRL+Y` to redo the last undo.

- Limited to keyboard and autocomplete actions.
- Also available via the primary text box right-click context menu.


## CTRL+W
[⬆️](#index) *(Close the app)*

Press `CTRL+W` to immediately close the app


## F1 (Popup Zoom)
[⬆️](#index) *(Toggle zoom popup)*

The Popup Zoom feature allows you to create a small popup window beside the mouse that displays a zoomed view of the image underneath.

Shortcuts:
- **F1**: Press `F1` to toggle the zoom popup.
- **Mouse Wheel**: Scroll to adjust the zoom factor or popup size.
  - Hold `Shift` while scrolling to adjust the popup size.


## F2
[⬆️](#index) *(Open the Image-Grid view)*

With the primary text box in focus, press `F2` to open the Image-Grid view.

- **See:** [Image-Grid](#image-grid) for more information.


## F4
[⬆️](#index) *(Open the current image in your default editor)*

Once you have set your default image editor, you can open the current image in it by pressing `F4` with the image in focus.

- **Set Default Image Editor:**
  - Open the application.
  - Navigate to the `Options` menu.
  - Select `Set Default Image Editor`.
  - Choose the executable file of your preferred image editor.
- **Tips:**
  - Ensure that the path to the image editor is correctly set to avoid any issues when opening images.
  - You can change the default image editor at any time by repeating the steps above.


## F5
[⬆️](#index) *(Open Batch Tag Edit)*

With the primary text box in focus, press `F5` to open Batch Tag Edit.

- **See:** [Batch Tag Edit](#batch-tag-edit) for more information.


## Middle-click
[⬆️](#index) *(Delete a tag)*

Hover over the tag you want to delete and press the middle mouse button to delete it.

- The entire comma-separated value will be deleted.
- Ensure the [Clean-Text](#clean-text) setting is enabled for the deletion to work.


<!--###########################################################################-->
<!--###########################################################################-->
<!--###########################################################################-->


# Text Tools


## Search and Replace
[⬆️](#index) *(Find and replace text across all text files)*

Use this tool to search for a string of text across all text files in the selected directory. If a match is found, it will be replaced exactly with the given text.

- **Access:**
  - Via the img-txt Viewer toolbar tab: `S&R`
- **Usage:**
  - Search for: `the big brown dog`
  - Replace with: `the big red dog`
- **Tips:**
  - Ensure that the search string is entered exactly as it appears in the text files.
  - Use the `Regex` option for advanced search patterns using regular expressions.
  - If a filter is applied, only text files that match the filter will be affected.
  - The `Undo` button can revert the last search and replace action if needed.

> **Note:**
> - When using `Search and Replace`, `Prefix`, or `Append`, a backup of the text files will be made and saved to the working directory before making any changes.
> - Pressing `Undo` will restore the text backup. `Undo` only creates one history of backups, and using another tool will erase the previous backup.


## Prefix
[⬆️](#index) *(Insert text at the start of all text files)*

Use this tool to prefix all text files in the selected directory with the entered text. This means that the entered text will appear at the start of each text file.

- **Access:**
  - Via the img-txt Viewer toolbar tab: `Prefix`
- **Usage:**
  - Enter the text you want to insert at the start of all text files.
  - Press the `Go!` button or hit `Enter` to apply the prefix.
- **Tips:**
  - Ensure the text you want to prefix is entered exactly as you want it to appear.
  - If a filter is applied, only text files that match the filter will be affected.
  - The `Undo` button can revert the last prefix action if needed.


## Append
[⬆️](#index) *(Insert text at the end of all text files)*

Use this tool to append all text files in the selected directory with the entered text. This means that the entered text will appear at the end of each text file.

- **Access:**
  - Via the img-txt Viewer toolbar tab: `Append`
- **Usage:**
  - Enter the text you want to insert at the end of all text files.
  - Press the `Go!` button or hit `Enter` to apply the append.
- **Tips:**
  - Ensure the text you want to append is entered exactly as you want it to appear.
  - If a filter is applied, only text files that match the filter will be affected.
  - The `Undo` button can revert the last append action if needed.


## AutoTag
[⬆️](#index) *(Automatically tag images using ONNX vision models)*

Use this tool to automatically analyze images and generate tags using the selected ONNX vision model.

- **Access:**
  - Via the img-txt Viewer toolbar tab: `AutoTag`
- **Usage:**
  - Select the image you want to tag.
  - Open the AutoTag tool from the toolbar below the text box or by the image right-click context menu.
- **Tips:**
  - Ensure that the ONNX models are placed in the `onnx_models` directory.
  - The default model used is `wd-v1-4-vit-tagger-v2`, but you can add additional models from https://huggingface.co/SmilingWolf
  - Place models in subfolders within the `onnx_models` directory. Each model subfolder should contain a `model.onnx` file and a `selected_tags.csv` file.
  - Restart the program to load new models.

Example directory structure for ONNX models:
```plaintext
img-txt_viewer/
  └── onnx_models/
      └── wd-v1-4-moat-tagger-v2/
          ├── model.onnx
          └── selected_tags.csv
```


## Filter
[⬆️](#index) *(Filter pairs based on text, missing text files, and more)*

Use this tool to filter img-txt pairs based on specific criteria.

- **Access:**
  - Via the img-txt Viewer toolbar tab: `Filter`
- **Usage:**
  - Enter any string of text to display only pairs containing that text.
  - **Example Inputs:**
    - `dog` *(shows only pairs containing "dog")*
    - `!dog` *(excludes pairs containing "dog")*
    - `!dog + cat` *(excludes "dog" pairs, includes "cat" pairs)*
- **Tips:**
  - Use ` + ` to include multiple strings or tags.
  - Use `!` before text to exclude pairs containing that text.
  - Enable `Regex` for regular expression filtering.
  - Check `Empty` to show only empty text files or images without a text pair.
  - Press `Go!` or hit `Enter` to apply the filter.
  - Press `Clear` to remove filters.


## Highlight
[⬆️](#index) *(Always highlight specific text)*

Specify text to highlight when moving to a new img-txt pair.

- **Access:**
  - Via the img-txt Viewer toolbar tab: `Highlight`
- **Example Inputs:**
  - `dog` *(highlights "dog")*
  - `dog + cat` *(highlights both "dog" and "cat")*
- **Tips:**
  - Use ` + ` to include multiple strings or tags.
  - Enable `Regex` for regular expression matching.
  - Press `Go!` or hit `Enter` to apply highlighting.
  - Press `Clear` to remove highlights.


## Font
[⬆️](#index) *(Adjust the font size and line height)*

Customize text appearance by adjusting font size and line height.

- **Access:**
  - Via the img-txt Viewer toolbar tab: `Font`
- **Usage:**
  - Navigate to the **Font** tab.
  - Use sliders or input fields to adjust settings.
  - Changes apply in real-time.


## My Tags
[⬆️](#index) *(Add your custom tags for autocomplete suggestions)*

Quickly edit the `my_tags.csv` file to add custom tags to the autocomplete dictionary.

- **Access:**
  - Via the img-txt Viewer toolbar tab: `MyTags`
- **Usage:**
  - Open the **MyTags** tab.
  - Add or modify tags in the list.
  - Save changes to refresh autocomplete.
- **Features:**
  - **Add Tags:** Enter a tag and press `Add` or `Enter`.
  - **Edit Tags:** Select a tag, click `Edit`, modify it, and press `Enter`.
  - **Remove Tags:** Select tags and click `Remove`.
  - **Prefix/Append Tags:** Insert a tag at the start or end of the text box.
  - **Move Tags:** Use `Move Up` or `Move Down` to change priority.
  - **Context Menu:** Right-click a tag for quick actions.
  - **Save Tags:** Click `Save Tags` to update `my_tags.csv`.
  - **Use MyTags:** Toggle the checkbox to enable custom tags.
- **Tips:**
  - Access `my_tags.csv` via `Options` > `Open MyTags File...`.
  - Prioritize important tags by moving them to the top.
  - Regularly save and refresh to update suggestions.


## Stats
[⬆️](#index) *(Display various file stats)*

Display statistics about the current datasets images and text contents.

- **Access:**
  - Via the img-txt Viewer toolbar tab: `Stats`
- **Usage:**
  - Navigate to the **Stats** tab.
  - Click `Refresh` to update statistics.
  - Enable `Process Image Stats` to include image data.
  - Enable `Truncate Captions` to limit caption length if needed.
Calculated statistics include:
- **File Summary**
  - Total Files
  - Total Text Filesize
  - Total Image Filesize
  - Total Filesize
- **Text Statistics**
  - Total Characters
  - Total Words
  - Word Page Count
  - Total Captions
  - Total Sentences
  - Total Paragraphs
  - Unique Words
- **Average Text Statistics**
  - Average Characters per File
  - Average Words per File
  - Average Captions per File
  - Average Caption Length
  - Average Word Length
  - Median Word Length
  - Average Sentence Length
- **Additional Text Statistics**
  - Type-Token Ratio
  - Word Length Standard Deviation
  - Sentence Length Standard Deviation
- **Image Information**
  - Image File Formats
  - Square Images
  - Portrait Images
  - Landscape Images
  - Average PPI for All Images
  - Average Image Width
  - Average Image Height
- **Other Statistics**
  - Image Resolutions
  - Image Aspect Ratios
  - Top 5 Files by Word Count
  - Top 5 Files by Character Count
  - Top 5 Files by Caption Count
  - Top 5 Longest Words
  - Top 50 Most Common Words
  - Character Occurrence
  - Unique Caption


## Batch Tag Edit
[⬆️](#index) *(Edit and manage tags with a user-friendly interface)*

Use the Batch Tag Edit tool to edit and manage tags across all files.

- **Access:**
  - Via the `Tools` > `Batch Operations` > `Batch Tag Edit...` menu.
- **Features:**
  - **Tag List:** View all unique tags.
  - **Info Display:** See counts of total, visible, selected tags, pending deletions, and edits.
  - **Sort Tags:** Sort by "Frequency," "Name," or "Length."
  - **Filter Tags:** Use conditions like `Tag`, `!Tag`, `==`, `!=`, `<`, `>`.
  - **Selection Shortcuts:** Use "All," "Invert," "Clear," "Revert Sel," "Revert All," "Copy."
  - **Tag Editing:** Right-click selected tags to edit or delete.
  - **Save Changes:** Click to apply edits.
  - **Help:** Click "?" for help messages.
  - **Shortcuts:** `F5` to close, `Ctrl+C` to copy tags.
- **Usage Tips:**
  - Filter and sort to manage specific tags.
  - Apply edits to multiple tags simultaneously.
  - Review pending changes before saving.
  - Use revert options before saving to undo changes.


## Create Wildcard From Captions
[⬆️](#index) *(Combine all captions into one text file)*

Combine all image captions into a single file.

- **Access:**
  - Via the `Tools` > `Batch Operations` > `Create Wildcard From Captions...` menu.
- **Usage:**
  - Select the directory with img-txt pairs.
  - Select the menu command.
  - Captions are saved as `combined_captions.txt` in the directory.


## Cleanup Text
[⬆️](#index) *(Fix typos across all text files)*

Clean text files to fix issues like duplicate tags and extra spaces.

- **Access:**
  - Via the `Tools` > `Batch Operations` > `Cleanup Text...` menu.
- **Tips:**
  - Enable the [`Clean-Text`](#clean-text) setting to auto-clean when saving.
  - Regular cleaning maintains readability.
- **Example:**
  - Before: `dog,, ,dog,solo,  ,happy  ,,`
  - After: `dog, solo, happy`
- **Operations Include:**
  - Removing duplicates.
  - Fixing punctuation and spacing.
  - Trimming leading/trailing commas and spaces.
  - Adding spaces after commas.


<!--###########################################################################-->
<!--###########################################################################-->
<!--###########################################################################-->


# Image Tools


## Batch Resize Images
[⬆️](#index) *(Resize all images using various methods and conditions)*

Use this tool to resize all images in a folder according to your needs.

- **Access:**
  - Via the `Tools` > `Batch Operations` > `Batch Resize Images...` menu.
- **Supported File Types:**
 - `jpg`, `jpeg`, `png`, `webp`, `bmp`, `tif`, `tiff`.
- **Resize Options:**
  - **Resize To:**
    - *Resolution:* Resize to specific width and height (ignoring aspect ratio).
    - *Percentage:* Resize images by a percentage scale.
    - *Width:* Resize images to a specific width while preserving aspect ratio.
    - *Height:* Resize images to a specific height while preserving aspect ratio.
    - *Shorter Side:* Resize based on the shorter side while preserving aspect ratio.
    - *Longer Side:* Resize based on the longer side while preserving aspect ratio.
  - **Resize Condition:**
    - *Upscale and Downscale:* Resize regardless of original size.
    - *Upscale Only:* Resize only if the new dimensions are larger.
    - *Downscale Only:* Resize only if the new dimensions are smaller.
- **Quality Settings:**
  - Control output quality for JPG and WEBP images.
  - Higher values yield better quality but larger file sizes.
  - Ignored for PNG images (always lossless).
- **File Type Conversion:**
  - Choose `AUTO` to keep original file types.
  - Select JPG, PNG, or WEBP to convert images.
- **Output Settings:**
  - **Use Output Folder:** Save resized images to a `Resize Output` folder.
  - **Overwrite Files:** Decide whether to overwrite existing files.
  - **Save PNG Info:** Preserve PNG metadata when resizing or converting.
- **Usage Steps:**
  1. Open the tool via the menu.
  2. Select the directory containing images.
  3. Configure resize options and settings.
  4. Click `Resize` to start the process.
- **Tips:**
  - Use valid input values to avoid errors.
  - Click the `?` button for detailed help.


## Resize Image
[⬆️](#index) *(Resize the current image by exact resolution or percentage)*

Adjust the size of the currently displayed image.

- **Access:**
  - Via `Tools` > `Edit Current Pair` menu, or image right-click context menu.
- **Resize Modes:**
  - **Pixels:** Specify exact width and height.
  - **Percentage:** Scale the image by a percentage.
- **Aspect Ratio:**
  - **Locked:** Maintain original aspect ratio.
  - **Unlocked:** Adjust width and height independently.
- **Quality and File Type:**
  - Adjust quality for JPG and WEBP formats.
  - Choose output file type: JPG, PNG, or WEBP.
- **Resize Methods:**
  - Select from methods like Lanczos (recommended), Bicubic, Nearest, etc.
- **Usage Tips:**
  - Right-click width or height fields to reset values.
  - Real-time updates show new dimensions and estimated size.


## Batch Crop Images
[⬆️](#index) *(Crop all images to a specified resolution)*

Crop and resize multiple images to a specific resolution.

- **Access:**
  - Via the `Tools` > `Batch Operations` > `Batch Crop Images...` menu.
- **Usage Steps:**
  1. Enter the desired width and height.
  2. Choose a crop anchor point (e.g., Center, North-West).
  3. Click `Crop` to begin processing.
- **Anchor Points:**
  - Determine which part of the image is kept when cropping.
  - Options include Center, Corners, and Sides.
- **Tips:**
  - Cropped images are saved in a `cropped_images` folder.
  - Filenames include the new resolution (e.g., `image_800x600.jpg`).
  - Images smaller than the target resolution are resized before cropping.


## Crop Image
[⬆️](#index) *(Crop an image or GIF using various methods and tools)*

Use the **CropUI** tool to precisely crop the current image or GIF.

- **Access:**
  - Via `Tools` > `Edit Current Pair` > `Crop` menu, or image right-click context menu.
- **Features:**
  - **Selection Modes:**
    - *Free Selection:* Click and drag to create a custom selection.
    - *Fixed Aspect Ratio:* Maintain a specific aspect ratio.
    - *Fixed Dimensions:* Set exact width and height.
  - **Adjustments:**
    - Move and resize selection using mouse or keyboard.
    - Use guidelines (Rule of Thirds, Center Lines) for composition.
  - **Image Transformations:**
    - Rotate or flip the image as needed.
  - **GIF Support:**
    - Extract and navigate frames for cropping.
- **Usage Tips:**
  - Double-click the image to select the entire area.
  - Save cropped images as new files or overwrite originals.
  - Access the **Help** menu for detailed instructions.


## Upscale Image
[⬆️](#index) *(Upscale images using models like R-ESRGAN, AnimeSharp-4x, and UltraSharp-4x)*

Enhance image quality using AI upscaling models.

This tool utilizes [Xinntao's Portable ESRGAN executable files (NCNN).](https://github.com/xinntao/Real-ESRGAN?tab=readme-ov-file#portable-executable-files-ncnn)

- **Access:**
  - Single: Via `Tools` > `Edit Current Pair` > `Upscale...` menu, or image right-click context menu.
  - Batch: Via the `Tools` > `Batch Operations` > `Batch Upscale...` menu.
- **Upscale Models:**
  - Choose from models like `realesrgan-x4plus`, `AnimeSharp-4x`, etc.
- **Settings:**
  - **Upscale Factor:** From 0.25x to 8.00x (default 2.00x).
  - **Upscale Strength:** Blend between original and upscaled image (0% to 100%).
- **Usage Steps:**
  - Open the Upscale tool.
  - Select the desired model.
  - Adjust the upscale factor and strength.
  - Click `Upscale` to start.
- **Batch Mode:**
  - Upscale multiple images at once.
  - Choose input and output folders.
- **Tips:**
  - Add additional models to the `ncnn_models` folder.
  - Models should be in NCNN format (`.bin` and `.param` files).
  - Upscaling may take time depending on image size and model.


## Find Duplicate Files
[⬆️](#index) *(Identify and manage duplicate files)*

Scan folders to find and handle duplicate files.

- **Access:**
  - Via the `Tools` > `Batch Operations` > `Find Duplicate Files...` menu.
- **Options:**
  - **Hash Algorithms:** Choose MD5 (faster) or SHA-256 (more accurate).
  - **Duplicate Handling:**
    - *Single:* Keep one copy, move others to `_Duplicate__Files`.
    - *Both:* Move all duplicates to `_Duplicate__Files`.
  - **Scanning Mode:**
    - *Images:* Scan image files.
      - Option to move accompanying text files.
    - *All Files:* Scan all file types.
  - **Recursive Scanning:** Include subfolders.
  - **Max Scan Size:** Set a size limit for files to scan.
  - **File Types:** Specify which file types to include.
- **Additional Actions:**
  - **Undo:** Restore moved duplicates.
  - **Move Duplicates Upfront:** Move duplicates to root for easy management.
  - **Delete Duplicates:** Permanently delete duplicates in `_Duplicate__Files`.


## Expand
[⬆️](#index) *(Expand images to a square ratio)*

Expand the current image to a square aspect ratio.

- **Access:**
  - Via `Tools` > `Edit Current Pair` > `Expand...` menu, or image right-click context menu.
- **Functionality:**
  - Expands the shorter side to match the longer side.
  - Ideal for images with simple backgrounds.
- **Output:**
  - Saves a new image with `_ex` appended to the filename.
  - Copies associated text files with `_ex` appended.
- **Output:**
  - A portrait image would expand like this: *input=*`|-|`, *output=*`|--|`
  - A landscape image would expand like this: *input=|`, *output=*`|--|`


## Edit Image Panel
[⬆️](#index) *(Adjust image properties like brightness, contrast, etc.)*

Fine-tune image appearance by adjusting various properties.

- **Access:**
  - Via the `Options` menu, or image `View` menu.
- **Adjustable Properties:**
  - `Brightness`, `Contrast`, `AutoContrast`
  - `Highlights`, `Shadows`
  - `Saturation`, `Sharpness`
  - `Hue`, `Color Temperature`
- **Adjustment Controls:**
  - Use sliders ranging from -100 to 100.
  - **Cumulative Edit:** Apply edits cumulatively when enabled.
  - **Revert Button:** Cancel changes and refresh the image.
    - *Right-click* to reset all adjustments.
- **Additional Parameters:**
  - **Highlights and Shadows:**
    - *Threshold:* Adjusts affected pixels.
    - *Blur Radius:* Controls smoothness.
  - **Sharpness:**
    - *Boost:* Increases sharpening effect.
- **Usage Tips:**
  - Right-Click the *Revert* button to reset all adjustments.
  - Some adjustments require the image to be in RGB mode.
  - Decide whether to overwrite the original image when saving.


<!--###########################################################################-->
<!--###########################################################################-->
<!--###########################################################################-->


# Other Tools


## Batch Rename/Convert
[⬆️](#index) *(Rename and convert images sequentially with padded zeros)*

Rename and optionally convert images in bulk.

- **Access:**
  - Via the `Tools` > `Batch Operations` > `Batch Rename/Convert...` menu.
- **Functionality:**
  - **Image Conversion:** Convert images to JPG format (except GIFs).
    - Option to rename without converting.
  - **Sequential Renaming:** Rename image-text pairs using padded zeros.
- **Example:**
  - **Before:** `aH15520.jpg`, `aH15520.txt`; `bH15521.png`, `bH15521.txt`
  - **After:** `00001.jpg`, `00001.txt`; `00002.jpg`, `00002.txt`
- **Output:**
  - Files are saved to a `Renamed Output` folder to prevent overwriting.
- **Tips:**
  - Only text files are renamed, not converted.
  - Ensure files are properly paired before renaming.


## Image-Grid
[⬆️](#index) *(Open the Image-Grid view)*

Browse images in a grid layout for easy selection.

- **Access:**
  - Press `F2`
  - Via the image `View` menu
  - Via the image right-click context menu.
- **Features:**
  - **Thumbnail Size:** Adjust using the slider.
  - **Auto-Close:** Automatically close after selecting an image.
  - **Filtering:**
    - Show all images, only paired, or only unpaired.
  - **Extra Filtering:**
    - Filter by resolution, aspect ratio, file size, filename, file type, or tags.
  - **Load More:** Load additional images if not all are displayed.
- **Tips:**
  - **Navigation:** Click and drag the title bar to move the window.
  - **Closing:** Click the "X" or press `Escape`.
  - **Image Info:** Hover to see details like filename and resolution.
  - **Refresh:** Reload the grid after making changes.
  - **Load All:** Be cautious as loading many images may be slow.


## Thumbnail Panel
[⬆️](#index) *(Display thumbnails for quick navigation)*

View and navigate images using thumbnails.

- **Access:**
  - Via `Options` > `Toggle Thumbnail Panel`
  - Via image `View` menu.
- **Features:**
  - **Quick Navigation:** Click thumbnails to open images.
  - **Context Menu:** Right-click for options like deleting or editing.
  - **Thumbnail Size:** Adjust size for better visibility.
- **Tips:**
  - Use the thumbnail panel for efficient browsing.
  - Customize thumbnail size to suit your preference.


<!--###########################################################################-->
<!--###########################################################################-->
<!--###########################################################################-->


# Settings


## Auto-Save
[⬆️](#index) *(Save text automatically when switching pairs)*

Automatically save text when certain actions occur.

- **Access:**
  - Via the `Auto-Save` checkbox.
- **Triggers:**
  - Switching between img-txt pairs.
  - Changing the active directory.
  - Closing the application.
- Works with the [Clean-Text](#clean-text) option to tidy text before saving.


## Clean-Text
[⬆️](#index) *(Automatically clean text files when saving)*

Automatically clean up the text when saving, fixing issues like duplicate tags and extra spaces.

- **Access:**
  - Via `Options` > `Clean-Text`.
- **Functionality:**
  - Removes duplicates.
  - Fixes punctuation and spacing.
  - Trims leading/trailing commas and spaces.
  - Adds spaces after commas.
- **See:** [`Cleanup Text`](#cleanup-text) for more information.


## Auto-Delete Blank Files
[⬆️](#index) *(Automatically delete blank text files)*

- **Access:**
  - Via `Options` > `Auto-Delete Blank Files`.
- **Functionality:**
  - Deletes text files with no content when saving.
  - Prevents empty text files from cluttering the directory.
  - If disabled, blank files are created/retained when saving.


## Colored Suggestions
[⬆️](#index) *(Enable colorized autocomplete suggestions)*

Enable this option to colorize autocomplete suggestions based on their category.

- **Access:**
  - Via `Options` > `Colored Suggestions`.
- **Functionality:**
  - Colorizes autocomplete suggestions for better visibility.
  - Colors are related to the dictionary used.
  - Tags from `MyTags` and `English Dictionary` are always black.
- **Color Codes:**
  - **Danbooru:**
    - General: `Black`
    - Artists: `Red`
    - Copyright: `Magenta`
    - Characters: `Green`
    - Meta: `Orange`
  - **e621:**
    - General: `Black`
    - Artists: `Yellow`
    - Copyright: `Magenta`
    - Characters: `Green`
    - Species: `Orange`
    - Meta: `Red`
    - Lore: `Green`
  - **Derpibooru:**
    - General: `Black`
    - Official Content: `Yellow`
    - Species: `Light Orange`
    - OC: `Pink`
    - Rating: `Blue`
    - Body Type: `Gray`
    - Character: `Teal`
    - OC: `Light-Purple`
    - Error: `Red`
    - Official Content: `Dark-Orange`
    - OC: `Light-Pink`


## Highlight Selection
[⬆️](#index) *(Highlight matching text when selecting)*

- **Access:**
  - Via `Options` > `Highlight Selection`.
- **Functionality:**
  - When enabled, selecting text in the text box will automatically highlight all other instances of the selected text.


## Big Save Button
[⬆️](#index) *(Enlarge the save button)*

- **Access:**
  - Via `Options` > `Big Save Button`.
- **Functionality:**
  - Increases the size of the save button for easier access.


## List View
[⬆️](#index) *(Display the text box tags in a list view)*

- **Access:**
  - Via `Options` > `List View`.
- **Functionality:**
  - Changes the appearance of the primary text box tags to a list view.
  - Each tag is displayed on a new line.
  - Pressing `,` or `Enter` adds a new line.
  - Text is reformatted back to a comma-separated list when saving.


## Always On Top
[⬆️](#index) *(Keep the app window on top of other windows)*

- **Access:**
  - Via `Options` > `Always On Top`.
- **Functionality:**
  - Keeps the application window on top of other windows.
  - Useful for multitasking or referencing other content.


## Toggle Zoom
[⬆️](#index) *(Toggle the zoom popup)*

- **Access:**
  - Via `Options` > `Toggle Zoom`.
  - Via image `View` menu.
- **Functionality:**
  - Toggles the zoom popup feature on or off.
  - Use `F1` to toggle the zoom popup.
- **See:** [`F1 (Popup Zoom)`](#f1-popup-zoom) for more information.


## Toggle Thumbnail Panel
[⬆️](#index) *(Display thumbnails for quick navigation)*

- **Access:**
  - Via `Options` > `Toggle Thumbnail Panel`
  - Via image `View` menu.
- **Functionality:**
  - Toggles the thumbnail panel on or off.
- **See:** [`Thumbnail Panel`](#thumbnail-panel) for more information.


## Toggle Edit Panel
[⬆️](#index) *(Toggle the edit panel)*

- **Access:**
  - Via `Options` > `Toggle Edit Panel`
  - Via image `View` menu.
- **Functionality:**
  - Toggles the visibility of the edit image panel.
- **See:** [Edit Image Panel](#edit-image-panel) for more information.


## Vertical View
[⬆️](#index) *(Switch between horizontal and vertical view)*

- **Access:**
  - Via `Options` > `Vertical View`.
  - Via image `View` menu.
- **Functionality:**
  - Switches between horizontal and vertical view modes.
  - Changes the layout of the image and text frames.


## Swap Image Text Side
[⬆️](#index) *(Swap the image and text sides)*

- **Access:**
  - Via `Options` > `Swap img-txt Sides`.
  - Via image `View` menu.
- **Functionality:**
  - Swaps the positions of the image and text frames in the application layout


## Image Display Quality
[⬆️](#index) *(Adjust image display quality)*

- **Access:**
  - Via `Options` > `Image Display Quality`.
  - Via image `View` menu.
- **Functionality:**
  - Adjusts the image display quality for better performance.
  - Options include `Low`, `Medium`, and `High`.
  - The `Medium` *(default)* setting should be sufficient for most users.
  - Lower quality settings may improve performance on slower systems.


## Loading Order
[⬆️](#index) *(Set the order for loading images and text files)*

- **Access:**
  - Via `Options` > `Loading Order`.
- **Functionality:**
  - Choose the order in which files are loaded.
  - Options include:
    - Name *(default)*
    - File size
    - Date created
    - Extension
    - Last Access time
    - Last write time
  - Along with the order, you can choose to sort in ascending or descending order.
  - Only image file stats are used for sorting.


## Dictionary
[⬆️](#index) *(Choose the autocomplete dictionary)*

- **Access:**
  - Via `Options` > `Autocomplete` > `Dictionary`.
  - Via the `☰` menu on the autocomplete row.
- **Functionality:**
  - Choose between the `English dictionary`, `Danbooru`, `Danbooru (safe)`, `e621`, and `Derpibooru` dictionaries.
  - Multiple dictionaries can be enabled at once, but the suggestions are limited by the `Threshold` setting.
  - You can disable all dictionaries and just use only `MyTags`.
- **Usage Tips:**
  - `English Dictionary` + `Danbooru (safe)` is a good choice for general use.


## Threshold
[⬆️](#index) *(Set the autocomplete threshold)*

- **Access:**
  - Via `Options` > `Autocomplete` > `Threshold`.
  - Via the `☰` menu on the autocomplete row.
- **Description:**
  - Adjusts the maximum number of tags the autocomplete engine considers when generating suggestions. A higher threshold may provide more comprehensive suggestions but could impact performance. Lowering the threshold can speed up suggestion generation but might miss some relevant tags.
  - Autocomplete dictionaries are optimized to have `~100,000` tags each.
- **Functionality:**
  - **Slow**: 275,000 tags
  - **Normal** *(default)*: 130,000 tags
  - **Fast**: 75,000 tags
  - **Faster**: 40,000 tags
- **Usage Tips:**
  - Increase the threshold if you want a wider range of suggestions and your system can handle the load.
  - Decrease the threshold to improve performance if you notice slowdowns while typing.


## Quantity
[⬆️](#index) *(Set the number of autocomplete suggestions)*

- **Access:**
  - Via `Options` > `Autocomplete` > `Quantity`.
  - Via the `☰` menu on the autocomplete row.
- **Description:**
  Defines how many autocomplete suggestions are displayed at once. Adjusting this setting allows you to control the number of options you see, helping to keep the interface clean or providing more choices as needed.
- **Usage Tips:**
  - Increase the quantity to view more suggestions simultaneously.
  - Decrease the quantity for a simplified view with fewer suggestions.


## Match Mode
[⬆️](#index) *(Set the autocomplete match mode)*

- **Access:**
  - Via `Options` > `Autocomplete` > `Match Mode`.
  - Via the `☰` menu on the autocomplete row.
- **Description:**
  Determines how your input text is matched against available tags. Different match modes can affect the relevance and ordering of suggestions based on your typing patterns.
- **Functionality:**
  - Mode: `Match Whole String`
    - All text between commas in the current selection is used for matching.
  - Mode: `Match Last Word`
    - Only the last word of the input string is used for matching.
- **Usage Tips:**
  - Experiment with different match modes to find the one that best fits your workflow.
  - Choose a match mode that complements the types of tags or keywords you frequently use.
  - The mode `Match Whole String` is recommended for `booru` tags.
  - The mode `Match Last Word` is recommended for the `English Dictionary`.


## Reset Settings
[⬆️](#index) *(Reset all settings to default)*

- **Access:**
  - Via `Options` > `Reset Settings`.
- **Functionality:**
  - Resets all settings to their default values and restores the program to its initial state.
  - Creates a set of guided dialogs to help reset and set your new settings.
  - Does not affect the currently selected director.


## Open Settings File...
[⬆️](#index) *(Open the settings file)*

- **Access:**
  - Via `Options` > `Open Settings File...`
- **Functionality:**
  - Opens the `settings.cfg` file in your system default text editor.
  - Allows manual editing of settings for advanced users.
- **Usage Tips:**
  - the `settings.cfg` file can also be deleted to reset all settings to default.


## Open MyTags File...
[⬆️](#index) *(Open the mytags file)*

- **Access:**
  - Via `Options` > `Open MyTags File...`
- **Functionality:**
  - Opens the `my_tags.csv` file in your system default text editor.
  - Allows manual editing of custom tags for autocomplete suggestions.
- **Usage Tips:**
  - Prioritize important tags by moving them to the top.
  - Restart the app to update the suggestions.


[⬆️](#index)
