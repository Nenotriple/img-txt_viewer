*"Making something... Nurturing something is really great. You can see and learn so many things from the process."*


# User Guide


img-txt_viewer comes with many tools that help ease the process of manually creating a training dataset, as well as some others that may be helpful outside of this scope.

The following guide will provide an overview of the various tools and features available in the application, along with detailed instructions on how to use them effectively.

If you have any questions, need further assistance, or anything else, please feel free to [create an issue](https://github.com/Nenotriple/img-txt_viewer/issues/new) in the repo.


# Index

**✂️ Shortcuts**
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
- [`Middle-click`](#middle-click) - Middle-click a tag to delete it.

**📜 Text Tools**
- [`Search and Replace`](#search-and-replace) - Find and replace text across all text files.
- [`Prefix`](#prefix) - Insert text at the start of all text files.
- [`Append`](#append) - Insert text at the end of all text files.
- [`AutoTag`](#autotag) - Automatically tag images using ONNX vision models.
- [`Filter`](#filter) - Filter pairs based on text, missing text files, and more.
- [`Highlight`](#highlight) - Always highlight specific text.
- [`My Tags`](#my-tags) - Add your custom tags for autocomplete suggestions.
- [`Batch Tag Edit`](#batch-tag-edit) - Edit and manage tags with a user-friendly interface.
- [`Create Wildcard From Captions`](#create-wildcard-from-captions) - Combine all captions into one text file.
- [`Cleanup Text`](#cleanup-text) - Fix typos across all text files.

**📷 Image Tools**
- [`Batch Resize Images`](#batch-resize-images) - Resize all images using different methods and conditions.
- [`Resize Image`](#resize-image) - Resize the current image by exact resolution or percentage.
- [`Batch Crop Images`](#batch-crop-images) - Crop all images to a specified resolution.
- [`Crop Image`](#crop-image) - Crop an image or GIF using various methods and tools.
- [`Batch Upscale`](#upscale-image) - Upscale images using models like R-ESRGAN.
- [`Upscale Image`](#upscale-image) - Upscale an image using models like R-ESRGAN.
- [`Find Duplicate Files`](#find-duplicate-files) - Identify and separate duplicate files.
- [`Expand`](#expand) - Expand images to square ratio for simple backgrounds.
- [`Edit Image Panel`](#edit-image-panel) - Adjust image properties like brightness, contrast, etc.

**📦 Other Tools**
- [`Batch Rename/Convert`](#batch-renameconvert) - Rename and convert images sequentially with padded zeros.
- [`Thumbnail Panel`](#thumbnail-panel) - Display thumbnails for quick navigation.
- [`Auto-Save`](#auto-save) - Save text automatically when switching pairs.
- [`Image-Grid`](#image-grid) - Open the Image-Grid view.


---


<!--####################################################################################################-->
<!--####################################################################################################-->
<!--####################################################################################################-->


# ✂️Shortcuts


### ALT+LEFT/RIGHT
#### *(Navigate between img-txt pairs)*

With the primary text box in focus, press `ALT+LEFT` or `ALT+RIGHT` to move between img-txt pairs.

- `ALT+LEFT` moves back to the previous image.
- `ALT+RIGHT` moves forward to the next image.


---


### SHIFT+DEL
#### *(Delete the current pair)*

Press `SHIFT+DEL` to move the displayed image and text file to a trash folder.

- The trash folder is created in the same directory as the image file.
- When closing the app, you'll be asked if you want to permanently delete the trash folder.
- Also available via the `Tools` menu and the image right-click context menu.
- If the trash folder already contains a file with the same name, you will be prompted to overwrite it or cancel the operation.


---


### ALT
#### *(Cycle through autocomplete suggestions)*

With the primary text box in focus, press `LEFT ALT` or `RIGHT ALT` to move the autocomplete selector left or right.


---


### TAB
#### *(Insert the selected autocomplete tag)*

With the primary text box in focus, press `TAB` to insert the selected autocomplete tag.


---


### CTRL+S
#### *(Save the current text file)*

With the primary text box in focus, press `CTRL+S` to save the text to the paired text file.

- If the text box is blank, the paired text file will be deleted if `Auto-Delete Blank Files` is enabled.
- If the paired text file does not exist, it will be created.
- Also available via the `Save` button.


---


### CTRL+E
#### *(Jump to the next empty text file)*

With the primary text box in focus, press `CTRL+E` to jump to the next empty text file from the current index position.

- Also available via the index entry right-click context menu.


---


### CTRL+R
#### *(Jump to a random img-txt pair)*

With the primary text box in focus, press `CTRL+R` to jump to a random img-txt pair.

- Also available via the index entry right-click context menu.


---


### CTRL+F
#### *(Highlight all duplicate words)*

With the primary text box in focus, press `CTRL+F` to highlight any duplicate words.

- All matching words will be highlighted with the same color, but colors are randomized each time the hotkey is pressed.
- This matches any duplicate string of text (minimum of 3 characters) and not just tags or words.
- Words shorter than 3 characters or words that appear only once will not be highlighted.
- Example text: "this cute **dog**, happy **dog**gy, small **dog**"
- Also available via the primary text box right-click context menu.


---


### CTRL+Z / CTRL+Y
#### *(Undo/Redo)*

With the primary text box in focus, press `CTRL+Z` to undo the last action or `CTRL+Y` to redo the last undo.

- Limited to keyboard and autocomplete actions.
- Also available via the primary text box right-click context menu.


---


### CTRL+W
#### *(Close the app)*

Press `CTRL+W` to immediately close the app.

---


### F1 (Popup Zoom)
#### *(toggle zoom popup)*

The Popup Zoom feature allows you to create a small popup window beside the mouse that displays a zoomed view of the image underneath.

#### Shortcuts:
- **F1**: Press `F1` to toggle the zoom popup.
- **Mouse Wheel**: Scroll to adjust the zoom factor or popup size.
  - Hold `Shift` while scrolling to adjust the popup size.


---


### F2
#### *(Open the Image-Grid view)*

With the primary text box in focus, press `F2` to open the Image-Grid view.

- See the [Image-Grid](#image-grid) section for more information.


---


### F4
#### *(Open the current image in your default editor)*

Once you have set your default image editor, you can open the current image in it by pressing `F4` with the image in focus.

- **Set Default Image Editor:**
  - Open the application.
  - Navigate to the `Options` menu.
  - Select `Set Default Image Editor`.
  - Choose the executable file of your preferred image editor.
- **Tips:**
  - Ensure that the path to the image editor is correctly set to avoid any issues when opening images.
  - You can change the default image editor at any time by repeating the steps above.


---


### F5
#### *(Open Batch Tag Edit)*

With the primary text box in focus, press `F5` to open Batch Tag Edit.

- See the [Batch Tag Edit](#batch-tag-edit) section for more information.


---


### Middle-click
#### *(Delete a tag)*

- **Usage:**
  - **Hover Over the Tag**: Move your mouse cursor over the tag you want to delete.
  - **Middle-Click**: Press the middle mouse button to delete the entire tag.
- **Tips:**
  - The entire comma-separated value will be deleted.
  - Ensure that the text cleaning feature is enabled for the deletion to work.


<!--####################################################################################################-->
<!--####################################################################################################-->
<!--####################################################################################################-->


# 📜Text Tools


### Search and Replace
#### *(Find and replace text across all text files)*

Use this tool to search for a string of text across all text files in the selected directory. If a match is found, it will be replaced exactly with the given text.

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


---


### Prefix
#### *(Insert text at the start of all text files)*

Use this tool to prefix all text files in the selected directory with the entered text. This means that the entered text will appear at the start of each text file.

- **Usage:**
  - Enter the text you want to insert at the start of all text files.
  - Press the `Go!` button or hit `Enter` to apply the prefix.
- **Tips:**
  - Ensure the text you want to prefix is entered exactly as you want it to appear.
  - If a filter is applied, only text files that match the filter will be affected.
  - The `Undo` button can revert the last prefix action if needed.


---


### Append
#### *(Insert text at the end of all text files)*

Use this tool to append all text files in the selected directory with the entered text. This means that the entered text will appear at the end of each text file.

- **Usage:**
  - Enter the text you want to insert at the end of all text files.
  - Press the `Go!` button or hit `Enter` to apply the append.
- **Tips:**
  - Ensure the text you want to append is entered exactly as you want it to appear.
  - If a filter is applied, only text files that match the filter will be affected.
  - The `Undo` button can revert the last append action if needed.


---


### AutoTag
#### *(Automatically tag images using ONNX vision models)*

Use this tool to automatically analyze images and generate tags based on the ONNX vision model.

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


---


### Filter
#### *(Filter pairs based on text, missing text files, and more)*

Use this tool to filter img-txt pairs based on specific criteria.

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


---


### Highlight
#### *(Always highlight specific text)*

Specify text to highlight when moving to a new img-txt pair.

- **Example Inputs:**
  - `dog` *(highlights "dog")*
  - `dog + cat` *(highlights both "dog" and "cat")*

- **Tips:**
  - Use ` + ` to include multiple strings or tags.
  - Enable `Regex` for regular expression matching.
  - Press `Go!` or hit `Enter` to apply highlighting.
  - Press `Clear` to remove highlights.


---


### Font Settings
#### *(Adjust the font size and line height)*

Customize text appearance by adjusting font size and line height.

- **Usage:**
  - Navigate to the **Font** tab.
  - Use sliders or input fields to adjust settings.
  - Changes apply in real-time.


---


### My Tags
#### *(Add your custom tags for autocomplete suggestions)*

Quickly edit the `my_tags.csv` file to add custom tags to the autocomplete dictionary.

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


---


### Stats
#### *(Display various file stats)*

Display statistics about the current datasets images and text contents.

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
  - Unique Captions

---


### Batch Tag Edit
#### *(Edit and manage tags with a user-friendly interface)*

Use the Batch Tag Edit tool to edit and manage tags across all files.

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


---


### Create Wildcard From Captions
#### *(Combine all captions into one text file)*

Combine all image captions into a single file.

- **Usage:**
  - Select the directory with img-txt pairs.
  - Go to `Tools` > `Batch Operations` > `Create Wildcard From Captions...`.
  - Captions are saved as `combined_captions.txt` in the directory.


---


### Cleanup Text
#### *(Fix typos across all text files)*

Clean text files to fix issues like duplicate tags and extra spaces.

- **Usage:**
  - Open `Tools` > `Batch Operations` > `Cleanup All Text Files...`
  - Confirm to proceed when prompted.

- **Tips:**
  - Enable `Clean-Text` to auto-clean when saving.
  - Regular cleaning maintains readability.

- **Example:**
  - Before: `dog,, ,dog,solo,  ,happy  ,,`
  - After: `dog, solo, happy`

- **Operations Include:**
  - Removing duplicates.
  - Fixing punctuation and spacing.
  - Trimming leading/trailing commas and spaces.
  - Adding spaces after commas.


---


<!--####################################################################################################-->
<!--####################################################################################################-->
<!--####################################################################################################-->


# 📷Image Tools


### Batch Resize Images
#### *(Resize all images using various methods and conditions)*

Use this tool to resize all images in a folder according to your needs.

- **Access:** Via `Tools` > `Batch Operations` > `Batch Resize Images`.

- **Supported File Types:** `jpg`, `jpeg`, `png`, `webp`, `bmp`, `tif`, `tiff`.

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


---


### Resize Image
#### *(Resize the current image by exact resolution or percentage)*

Adjust the size of the currently displayed image.

- **Access:** Via `Tools` menu or image right-click context menu.

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
  - Decide whether to overwrite the original file or save a new one.
  - Real-time updates show new dimensions and estimated size.


---


### Batch Crop Images
#### *(Crop all images to a specified resolution)*

Crop and resize multiple images to a specific resolution.

- **Access:** Via `Tools` > `Batch Operations` > `Batch Crop Images`.

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


---


### Crop Image
#### *(Crop an image or GIF using various methods and tools)*

Use the **CropUI** tool to precisely crop the current image or GIF.

- **Access:** Via `Tools` menu or image right-click context menu.

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


---


### Upscale Image
#### *(Upscale images using models like R-ESRGAN, AnimeSharp-4x, and UltraSharp-4x)*

Enhance image resolution using upscaling models.

- **Access:** Via `Tools` menu or image right-click context menu.

- **Upscale Models:**
  - Choose from models like `realesrgan-x4plus`, `AnimeSharp-4x`, etc.

- **Settings:**
  - **Upscale Factor:** From 0.25x to 8.00x (default 2.00x).
  - **Upscale Strength:** Blend between original and upscaled image (0% to 100%).

- **Usage Steps:**
  1. Open the Upscale tool.
  2. Select the desired model.
  3. Adjust the upscale factor and strength.
  4. Click `Upscale` to start.

- **Batch Mode:**
  - Upscale multiple images at once.
  - Choose input and output folders.

- **Tips:**
  - Add additional models to the `ncnn_models` folder.
  - Models should be in NCNN format (`.bin` and `.param` files).
  - Upscaling may take time depending on image size and model.


---


### Find Duplicate Files
#### *(Identify and manage duplicate files)*

Scan folders to find and handle duplicate files.

- **Access:** Via `Tools` > `Batch Operations` > `Find Duplicate Files`.

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


---


### Expand
#### *(Expand images to a square ratio)*

Expand the current image to a square aspect ratio.

- **Access:** Via `Tools` menu or image right-click context menu.

- **Functionality:**
  - Expands the shorter side to match the longer side.
  - Ideal for images with simple backgrounds.

- **Output:**
  - Saves a new image with `_ex` appended to the filename.
  - Copies associated text files with `_ex` appended.

- **Example:**
  - Portrait image before: `|-|`
  - After expansion: `|--|`


---


### Edit Image Panel
#### *(Adjust image properties like brightness, contrast, etc.)*

Fine-tune image appearance by adjusting various properties.

- **Access:** Via the image editing options.

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
  - Some adjustments require the image to be in RGB mode.
  - Decide whether to overwrite the original image when saving.


<!--####################################################################################################-->
<!--####################################################################################################-->
<!--####################################################################################################-->


# 📦Other Tools

### Batch Rename/Convert
#### *(Rename and convert images sequentially with padded zeros)*

Rename and optionally convert images in bulk.

- **Access:** Via `Tools` > `Batch Operations` > `Batch Rename/Convert`.

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


---


### Thumbnail Panel
#### *(Display thumbnails for quick navigation)*

View and navigate images using thumbnails.

- **Features:**
  - **Quick Navigation:** Click thumbnails to open images.
  - **Context Menu:** Right-click for options like deleting or editing.
  - **Thumbnail Size:** Adjust size for better visibility.

- **Tips:**
  - Use the thumbnail panel for efficient browsing.
  - Customize thumbnail size to suit your preference.


---


### Auto-Save
#### *(Save text automatically when switching pairs)*

Automatically save text when certain actions occur.

- **Triggers:**
  - Switching between img-txt pairs.
  - Changing the active directory.
  - Closing the application.

- **Features:**
  - Works with `Clean-Text` option to tidy text before saving.


---


### Image-Grid
#### *(Open the Image-Grid view)*

Browse images in a grid layout for easy selection.

- **Access:** Press `F2` or via the menu.

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


---
