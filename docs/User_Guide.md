# User Guide

*"Making something... Nurturing something is really great. You can see and learn so many things from the process."* - 🍉

img-txt_viewer comes with many tools that help ease the process of manually creating a training dataset, as well as some others that may be helpful outside of this scope.

The following guide will provide an overview of the various tools and features available in the application.

If you have any questions, need assistance with an issue, or anything else, please feel free to [create an issue](https://github.com/Nenotriple/img-txt_viewer/issues/new) in the repo.

- **Repo link:** [img-txt_viewer on GitHub](https://github.com/Nenotriple/img-txt_viewer)
- **Check for updates:** [Releases](https://github.com/Nenotriple/img-txt_viewer/releases)
- **Wiki:** [Documentation Wiki](https://github.com/Nenotriple/img-txt_viewer/wiki)

Last Updated for: `img-txt_viewer v1.97`

## Index

- ✂️ [**Tagger Shortcuts**](#tagger-shortcuts)
  - [ALT+LEFT/RIGHT](#altleftright) – Navigate between image-text pairs
  - [SHIFT+DEL](#shiftdel) – Move pair to trash folder
  - [ALT](#alt) – Cycle autocomplete suggestions
  - [TAB](#tab) – Insert highlighted autocomplete suggestion
  - [CTRL+S](#ctrls) – Save current text file
  - [CTRL+E](#ctrle) – Jump to next empty text file
  - [CTRL+R](#ctrlr) – Jump to random image-text pair
  - [CTRL+F](#ctrlf) – Open Find and Replace panel
  - [CTRL+Z / CTRL+Y](#ctrlz--ctrly) – Undo / Redo actions
  - [CTRL+W](#ctrlw) – Close the app window
  - [F1](#f1) – Toggle image grid view
  - [F2](#f2) – Toggle zoom popup
  - [F4](#f4) – Open in image editor
  - [Middle-click](#middle-click) – Delete tag

- 📜 [**Tagger Toolbar**](#tagger-toolbar)
  - [Search and Replace (S&R)](#search-and-replace)
  - [Prefix](#prefix)
  - [Append](#append)
  - [AutoTag](#autotag)
  - [Filter](#filter)
  - [Highlight](#highlight)
  - [Font](#font)
  - [My Tags](#my-tags)
  - [Stats](#stats)

- 📷 [**Main Toolbar**](#main-toolbar)
  - [Tag-Editor](#tag-editor)
  - [Crop](#crop)
  - [Batch Upscale](#batch-upscale)
  - [Batch Resize](#batch-resize)
  - [Batch Rename](#batch-rename)
  - [Find Duplicates](#find-duplicates)

- ⚙️ [**Menubar**](#menubar)
  - [**File Menu**](#file-menu)
    - [Select Directory](#select-directory)
    - [Open Current Directory](#open-current-directory)
    - [Refresh Files](#refresh-files)
    - [Open Current Image](#open-current-image)
    - [Open Text File](#open-text-file)
    - [Edit Image](#edit-image)
    - [Zip Dataset](#zip-dataset)
    - [Exit](#exit)
  - [**Edit Menu**](#edit-menu)
    - [Save Text](#save-text)
    - [Cleanup All Text Files](#cleanup-all-text-files)
    - [Create Blank Text Files](#create-blank-text-files)
    - [Rename Pair](#rename-pair)
    - [Duplicate Pair](#duplicate-pair)
    - [Delete Pair](#delete-pair)
    - [Undo Delete](#undo-delete)
    - [Next Empty Text File](#next-empty-text-file)
    - [Random File](#random-file)
    - [Open Settings File](#open-settings-file)
    - [Open MyTags File](#open-mytags-file)
  - [**Tools Menu**](#tools-menu)
    - [Batch Operations](#batch-operations)
      - [Batch Crop Images](#batch-crop-images)
      - [Create Wildcard From Text Files](#create-wildcard-from-text-files)
    - [Edit Current Pair](#edit-current-pair)
      - [Upscale](#batch-upscale)
      - [Crop](#_crop)
      - [Resize](#resize)
      - [Expand](#expand)
      - [Rotate](#rotate)
      - [Flip](#flip)
      - [Auto-Tag](#auto-tag)
  - [**Options Menu**](#options-menu)
    - [Text Options](#text-options)
      - [Clean Text](#clean-text)
      - [Auto-Delete Blank Files](#auto-delete-blank-files)
      - [Highlight Selection](#highlight-selection)
      - [Add Comma After Tag](#add-comma-after-tag)
      - [List View](#list-view)
      - [Auto-Save](#auto-save)
    - [Loading Order](#loading-order)
    - [Autocomplete](#autocomplete)
      - [Dictionary](#autocomplete-dictionary)
      - [Threshold](#autocomplete-threshold)
      - [Quantity](#autocomplete-quantity)
      - [Match Mode](#autocomplete-match-mode)
    - [Set Default External Editor](#set-default-external-editor)
    - [Restore Last Path](#restore-last-path)
    - [Reset Settings](#reset-settings)
  - [About Menu](#about-menu)

- ⚙️ [**Tagger View Menu**](#tagger-view-menu)
  - [Toggle Image Grid](#toggle-image-grid)
  - [Toggle Zoom](#toggle-zoom)
  - [Toggle Thumbnail Panel](#toggle-thumbnail-panel)
  - [Toggle Edit Panel](#toggle-edit-panel)
  - [Always On Top](#always-on-top)
  - [Big Save Button](#big-save-button)
  - [UI: Vertical View](#ui-vertical-view)
  - [UI: Swap img-txt Sides](#ui-swap-img-txt-sides)

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Tagger Shortcuts

These shortcuts are accessible with the `Tagger` interface open.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### ALT+LEFT/RIGHT

Navigate between img-txt pairs.

- `ALT+LEFT` moves back to the previous image.
- `ALT+RIGHT` moves forward to the next image.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### SHIFT+DEL

Move the displayed image and text file pair to a trash folder.

- The trash folder is created in the same directory as the image file.
- When closing the app, you'll be asked if you want to permanently delete the trash folder.
- Also available via the `Tools` menu and the image right-click context menu.
- If the trash folder already contains a file with the same name, you will be prompted to overwrite it or cancel the operation.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### ALT

- Cycle through autocomplete suggestions.
- With an autocomplete dictionary selected, you will see suggestions based on the currently typed text.

Press `LEFT ALT` or `RIGHT ALT` to move the autocomplete selector left or right.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### TAB

- Insert the highlighted suggestion.
- Press `TAB` to insert the selected autocomplete tag.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### CTRL+S

- Save the current text file.
- Press `CTRL+S` to save the text to the paired text file.

If [Auto-Delete Blank Files](#auto-delete-blank-files) is enabled, the text file will be deleted if it is empty after saving.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### CTRL+E

- Jump to the next empty text file.
- Press `CTRL+E` to jump to the next image file where its text file is empty or does not exist.

Also available via the index entry right-click context menu.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### CTRL+R

- Jump to a random img-txt pair.
- Press `CTRL+R` to jump to a random img-txt pair.

Also available via the index entry right-click context menu.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### CTRL+F

- Open Find and Replace panel.
- With the primary text box in focus, press `CTRL+F` to open the Find and Replace panel.

Toggle `Match Case`, `Match Whole Word`, and `Use Regular Expressions` options via the (☰) menu.

Expand the panel using the (>) button to reveal the Replace options.

Select text in the primary text box and press `CTRL+F` to populate the Find field.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### CTRL+Z / CTRL+Y

- Undo / Redo.
- With the primary text box in focus, press `CTRL+Z` to undo the last action or `CTRL+Y` to redo the last undo.

Due to the nature of the text processor, there may be some unexpected behavior. In most cases the original text will be restored, but there may be exceptions or strange artifacts.

Also available via the primary text box right-click context menu.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### CTRL+W

- Close the window.
- Press `CTRL+W` to immediately close the app.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### F1

- Toggle the Image-Grid view.
- Press `F1` to toggle the Image-Grid view.

The image-grid replaces the primary displayed image with a grid of thumbnails.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### F2

- Toggle zoom popup.
- Press `F2` to toggle the zoom popup.

The zoom popup displays a zoomed in view of the currently displayed image.

Using the mouse wheel, you can zoom in and out of the image. Hold `shift` while scrolling to adjust the popup size.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### F4

- Open the current image in your default editor.
- Press `F4` to open the current image in your default editor. *(Default mspaint)*

See the [Set Default External Editor](#set-default-external-editor) section for more information.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Middle-click

- Delete a tag by middle-clicking it.
- Hover over the tag you want to delete and press the middle mouse button to delete it.

Ensure the [Clean-Text](#clean-text) setting is enabled for the deletion to work.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Tagger Toolbar

A variety of tools are available in the bottom toolbar below the Tagger text box. Additional information can be found by expanding the toolbar or clicking the (?) button for more information.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Search and Replace

Search and replace text across all listed text files.

Use this tool to search for a string of text across all listed text files in the selected directory. If a match is found, it will be replaced exactly with the given text.

- **Usage:**
  - Search for: `the big brown dog`
  - Replace with: `the big red dog`
- **Tips:**
  - Ensure the search string is entered exactly as it appears in the text files.
  - Use the `Regex` option for advanced search patterns using regular expressions.
  - If a filter is applied, only text files that match the filter will be affected (all *listed* files).
  - The `Undo` button can revert the last search and replace action if needed.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Prefix

Insert text at the start of all listed text files.

Use this tool to prefix all listed text files in the selected directory with the entered text. This means that the entered text will appear at the start of each text file.

- **Usage:**
  - Enter the text you want to insert at the start of all text files.
- **Tips:**
  - Commas/spaces are always appended to the prefixed text.
  - Ensure the text you want to prefix is entered exactly as you want it to appear.
  - If a filter is applied, only text files that match the filter will be affected (all *listed* files).
  - The `Undo` button can revert the last prefix action if needed.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Append

Insert text at the end of all listed text files.

Use this tool to append all listed text files in the selected directory with the entered text. This means that the entered text will appear at the end of each text file.

- **Usage:**
  - Enter the text you want to insert at the end of all text files.
- **Tips:**
  - Commas/spaces are always prepended to the appended text.
  - Ensure the text you want to append is entered exactly as you want it to appear.
  - If a filter is applied, only text files that match the filter will be affected (all *listed* files).
  - The `Undo` button can revert the last append action if needed.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### AutoTag

Automatically tag images using ONNX vision models.

Use this tool to automatically analyze images and generate tags using the selected ONNX vision model.

- **Usage:**
  - Navigate to the image you want to tag.
  - Click the Interrogate button to analyze the image and generate tags.

- **Tips:**
  - Enable `Batch` mode to process all listed images at once. (requires an `Auto-Insert` setting selected)
  - Adjust the `Auto-Insert` settings to customize how tags are automatically applied to the text file.
    - Disable: Do nothing after tags are generated.
    - Prefix: Add the generated tags to the beginning of the text file.
    - Append: Add the generated tags to the end of the text file.
    - Replace: Replace the entire content of the text file with the generated tags.
  - Adjust `Threshold` and `Max Tags` settings to control tag generation sensitivity.
  - Toggle `Keep: _` and `Keep: \` options to manage how generated tags are formatted.
    - `Keep: _` enabled will keep underscores in generated tags, otherwise replaces with spaces.
    - `Keep: \` enabled will keep backslashes in generated tags, otherwise removes.
  - Add tags to the `Exclude` field to filter out unwanted tags.
    - Use `Auto` mode to automatically exclude tags that already exist in the text file.
  - Add tags to the `Keep` field to always include specific tags in the generated output.
  - Use the `Replace` and `With` fields to customize tag replacement behavior.
    - `Replace` field allows you to specify a tag to be replaced.
    - `With` field allows you to specify the tag to replace it with.
    - Separate multiple tags with commas, allowing you to replace multiple tags at once.
  - Use the Selection buttons to quickly insert, copy, or adjust taglist selection.

- **Add your own models:**
  - Ensure that the ONNX models are placed in the `models\onnx_models` directory.
  - The default model used is `wd-v1-4-vit-tagger-v2`, but you can add additional models from [Hugging Face SmilingWolf](https://huggingface.co/SmilingWolf)
  - Place models in subfolders within the `models\onnx_models` directory. Each model subfolder should contain a `model.onnx` file and a `selected_tags.csv` file.
  - Restart the program to load new models.

Example directory structure for ONNX models:

```plaintext
img-txt_viewer/
  └── models/
    └── onnx_models/
        └── wd-v1-4-moat-tagger-v2/
            ├── model.onnx
            └── selected_tags.csv
```

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Filter

Filter pairs based on text, missing text files, and more.

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
  - The `Clear` button turns red when filters are applied.
  - Remember to press `Clear` to remove filters when not needed.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Highlight

Always highlight specific text if it exists in the displayed text.

Use this tool to quickly find and highlight important information.

- **Usage:**
  - Enter any string of text to highlight it in the displayed text.
- **Example Inputs:**
  - `dog` *(highlights "dog")*
  - `dog + cat` *(highlights both "dog" and "cat")*
- **Tips:**
  - Use ` + ` to include multiple strings or tags.
  - Enable `Regex` for regular expression matching.
  - Highlighting remains active until the field is cleared.
  - Press `Clear` to remove highlights.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Font

Adjust font size and style for better readability.

Customize text appearance by adjusting font and text size.

- Use sliders or input fields to adjust settings.
- Changes are made in real-time.
- Use the `Reset` button to revert to default settings.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### My Tags

Add your own custom tags for autocomplete suggestions.

Quickly edit the `my_tags.csv` file to add custom tags to the autocomplete dictionary. Also display a list of all tags in the selected directory.

- **Usage:**
  - Add tags via:
    - Inputting them into the MyTags text field and selecting `Add`.
    - Selecting tag(s) from the All Tags list and selecting `<`
    - Selecting text in the Tagger and choosing `Add to MyTags` from the context menu.
- **Tips:**
  - Access `my_tags.csv` via `Edit` > `Open MyTags File...`.
  - Prioritize important tags by moving them to the top.
  - Regularly save and refresh to update suggestions.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Stats

Display various file stats.

- **Usage:**
  - Click `Refresh` to update statistics.
  - Enable `Process Image/Video Stats` to include image and video data.
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

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Main Toolbar

The main toolbar gives access to image and text tools. These use the same directory as set in the Tagger UI. For Tag-Editor and Crop, set a directory in Tagger UI first.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Tag-Editor

Edit and manage tags with a user-friendly interface.

> **Note:** This tool is designed for CSV-like tag files. Tags should be separated by commas, not written in sentence or paragraph format.
> **Note:** Set a directory in the Tagger UI before using Tag-Editor.

- The `Tags` list displays all tags from the Tagger UI.
- Active filters in Tagger affect which files and tags are available in Tag-Editor.
- Each tag shows its occurrence count in the dataset (e.g., `004, long hair` means "long hair" appears 4 times).
- Selecting a tag for edit/delete selects all instances of that tag.

**Sorting and Filtering:**

- Tags can be sorted via the `Sort & Filter` options.
- Sorting/filtering cannot be changed while Tag-Edit has pending changes.
- Commit or clear all pending changes to adjust sorting options.

**Editing and Deleting Tags:**

1. Use the `Tags` list to select one or more tags.
2. Choose an action:
   - To edit: Type in the `Edit` field and click `Apply` to create pending edit changes.
   - To delete: Click `Delete` to create pending delete changes.

**Saving or Reverting Changes:**

- When finished, click **Save Changes** to commit edits or deletions.
- Use the **Reset** buttons to revert all pending changes.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Crop

Crop images to a specific aspect ratio or resolution.

This tool allows you to quickly crop images using a variety of useful features.

> **Note:** Set a directory in the Tagger UI before using the Crop tool.

- **GIF support:** A timeline will appear for GIF images, allowing you to select individual frames to crop.

**How to crop:**

- Click and drag over the image to create a crop selection.
- Click and drag a selection handle to adjust the crop area.
- Click and drag the selection itself to move it around.

**Adjust crop dimensions:**

- Use the mouse wheel to adjust crop selection height (`Mouse-Wheel` up/down).
- Hold `Shift` and use the mouse wheel to adjust crop selection width.

**Quick selection:**

- Double-click the image to instantly create an automatically sized crop selection.
- Enable `Fixed Selection` > `Fixed` and `Auto` modes for enhanced function.

**After Crop settings:**
Define what happens after pressing `Crop Selection`:

- **Save and close:** Save the cropped image and return to the Tagger interface.
- **Save and Next:** Save the cropped image and go to the next image index.
- **Save as...:** Save the image using a file dialog.
- **Save:** Save the cropped image.
- **Overwrite:** Overwrite the original image with the cropped version.

After making a selection and adjusting settings, click **Crop Selection** to apply the crop.

#### Fixed Selection

- The `Fixed Selection` > `Fixed` setting allows you to maintain specific selection dimensions.
- Enter the desired value for the selected setting in the `Fixed Selection` text entry.
- Use the `<` button beside the text entry to automatically insert the current selection dimensions relative to the selected mode.

**Fixed Selection modes:**

- **Fixed Aspect Ratio:** Lock the crop selection to a fixed aspect ratio (e.g., 1:1).
- **Fixed Width:** Lock the crop selection to a fixed width, allowing height to change.
- **Fixed Height:** Lock the crop selection to a fixed height, allowing width to change.
- **Fixed Size:** Lock the crop selection to a fixed size.

The `Fixed Selection` > `Auto` setting allows you to define a list of aspect ratios. The app will try to find the best fit for the current image dimensions.
> **Note:** This setting requires both `Fixed` and `Aspect Ratio` modes enabled.

#### Additional Options

- **Expand from Center:** Makes the crop selection expand equidistantly from the center, instead of from the selected handle/edge.
- **Highlight:** Toggles the dark overlay that helps visualize how the image will look once cropped. Disabling it can help performance.
- **Guidelines:** Change the crop selection visual markers to help align the crop in various ways.
- **Transform:** Rotate or flip images, and extract all GIF frames.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Batch Upscale

Upscale images using `realesrgan-ncnn-vulkan`.

> **Note:** Use pre-packaged models or add your own. Models must use the RESRGAN architecture in NCNN format (`.bin` and `.param`).
> Add models to the `models\ncnn_models` folder and restart the app after adding new models.

**How to use:**

- Toggle the `Batch Mode` option to switch between batch or single image upscaling.
  - If `Batch Mode` is enabled, input and output paths should be folders.
  - If disabled, input and output paths should be files.
  - *(The app tries to handle this automatically.)*

- Toggle the `Auto Name` option to automatically create an output filename or filepath for the selected mode and file(s).

- Use the `Browse...` buttons to select paths.
- Use the `Open` buttons to open the selected paths in your file explorer.

- If `Batch Mode` is disabled, the selected image will be upscaled.
- If enabled, all images in the selected directory will be upscaled.

**Settings:**

- Select an upscale model from the `Upscale Model` dropdown.
- Adjust the `Upscale Factor` to define the final output size (e.g., `0.5`, `2.0`).
- Adjust the `Upscale Strength` to control blending between input and output images:
  - `100%` = full output (no blending)
  - `0%` = full input (no blending)

**Tips:**

- Click the `Refresh` button to update the file list if it appears out of date.
- Click `Upscale` when ready.
  The process may take a long time depending on input image size and GPU speed.

Example directory structure for NCNN models:

```plaintext
img-txt_viewer/
  └── models/
    └── ncnn_models/
          ├── UltraSharp-4x.bin
          └── UltraSharp-4x.param
```

### Batch Resize

Resize images using various methods and conditions.

- Click the `Refresh` button to update the file list if it appears out of date.
- After adjusting settings, click `Resize!` to process the displayed images.
- Adjust the working path first via the Tagger interface or by using the `Browse...` button.

> **Tip:** This tool only supports resizing all images in batch.
> To resize a single image, use the `Tagger > image context > Resize...` menu.

#### Resize To Options

- **Resize to Resolution:**
  Resize to a specific width and height, ignoring aspect ratio.

- **Resize to Percentage:**
  Resize the image by a percent scale, preserving aspect ratio.

- **Resize to Width:**
  Target the image width and resize it. Height is adjusted automatically to maintain aspect ratio.

- **Resize to Height:**
  Target the image height and resize it. Width is adjusted automatically to maintain aspect ratio.

- **Resize to Shorter Side:**
  Resize the shorter side of the image. The longer side is adjusted automatically to maintain aspect ratio.

- **Resize to Longer Side:**
  Resize the longer side of the image. The shorter side is adjusted automatically to maintain aspect ratio.

#### Condition Options

- **Upscale and Downscale:**
  Resize the image to the new dimensions, regardless of whether they're larger or smaller than the original.

- **Upscale Only:**
  Resize only if the new dimensions are larger than the original.

- **Downscale Only:**
  Resize only if the new dimensions are smaller than the original.

#### Output Options

- Use the `Filetype` dropdown to select the output filetype: `AUTO`, `JPEG`, `PNG`, or `WEBP`.
  `AUTO` mode tries to save using the original filetype.

- Use the `Quality` slider to adjust the output quality for `JPEG` and `WEBP` files (e.g., `20-100`).

- Enable `Use Output Folder` to save resized images to a new folder in the selected directory.

- Enable `Overwrite Output` to overwrite any conflicting files.

- Enable `Save PNG Info` to attempt to read PNG chunk metadata from the original image and write it back to the resized image.
  *(This is designed for A1111-webui/Forge-webui style metadata and may not work with other systems.)*

- Enable `Convert Only` to skip resizing and only convert the image to the selected filetype.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Batch Rename

Cleanup file names and quickly rename using presets.

Simple rename operation for sequential numbered or dated filenames.

- Click the `Refresh` button to update the file list if it appears out of date.
- After selecting some files and adjusting settings, click `Rename Files` to process the selected files.

- Options:
  - `Handle Duplicates`
    - `Rename`: Attempt to rename *(Conflicts can occur)*
    - `Move to Folder`: Move to a specified folder
    - `Overwrite`: Overwrite existing files
    - `Skip`: Skip renaming for existing files
  - `Respect img-txt Pairs`: Rename both image and text file together as a pair.
  - `Show Warning`: Display a warning message before overwriting files.

- Presets
  - `Numbering`: Rename files in sequential numbered format like `00006.jpg, 00007.jpg, 00008.jpg, ...`
  - `Auto-Date`: Rename files using their modified date and sequential numbers like `2025-03-15_00001.jpg`.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Find Duplicates

- Identify and manage duplicate files in your dataset.
- This tool uses file hashing to scan for duplicate images or other file types.
- Use the directory selected in the Tagger interface, or choose a new directory with the `Browse...` button.

#### Duplicate File Menu

- **Select Folder:** Select a new directory (same as `Browse...`).
- **Open Folder:** Open the current folder in your file explorer (same as `Open`).
- **Restore Moved Duplicates:** Restore duplicates that were moved during the previous run.
- **Move All Duplicates Upfront:** Move all duplicate files into a single folder, removing subfolders.
- **Delete All Duplicates:** Permanently delete all detected duplicate files.

#### Duplicate Options Menu

- **Process Mode:**
  - `MD5-Fast`: Use MD5 hashing for quick duplicate detection.
  - `SHA-256`: Use SHA-256 hashing for more secure duplicate detection.
- **Scanning Options:**
  - `Max Scan Size`: Limit scanned file size (default 2GB).
  - `Filetypes`: Specify file types to scan.
  - `Recursive`: Scan subdirectories (finds duplicates within each folder, not across folders).
  - `Set Scanning Mode`: Choose between `Images` and `All Files`.
- **Duplicate Handling:**
  - `Single`: Move only the duplicate files, leaving one copy in the original location.
  - `Both`: Move both the original and duplicate files to the specified location.

- **Move Captions:** Moves associated `.txt` files when moving duplicate images.

#### Usage

1. Click the **Find Duplicates** button to start scanning.
2. Click the **Stop!** button to cancel the process early.

The text log displays progress and results. The bottom status bar shows information about the current operation, such as how many duplicates are found, how many files were checked, status, and progress.

> **Note:**
> Duplicates are automatically moved to a `_Duplicate__Files` folder in the selected directory.
> If the folder does not exist, it will be created. The folder structure is preserved when moving duplicates, so files may end up in nested folders if that's where they came from.

After duplicates have been found and moved, review the `_Duplicate__Files` folder to see the results.
From this point, you can:

- Restore moved duplicates
- Delete all duplicates
- Move all duplicates upfront

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Menubar

Detailed breakdown of the main app menubar and its submenus. These settings and tools are generally used along with the Tagger interface and are disabled when other tools are active.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### File Menu

Options for managing files and directories.

#### Select Directory

- Choose the app working directory used by all tools.
- Same as using the `Browse...` button in the Tagger interface.

#### Open Current Directory

- Open the currently selected working directory in your file explorer.

#### Refresh Files

- Refresh the list of files in the currently selected working directory.
- The app tries to reload file lists when it notices changes, but some changes may require a manual refresh.

#### Open Current Image

- Open the current image in your default image viewer (such as Windows Photos).

#### Open Text File

- Open the current text file in your default text editor (such as Notepad).

#### Edit Image

- Edit the current image using the selected external editor.
- By default, this opens the image in MS Paint.
- See the [Set Default External Editor](#set-default-external-editor) section for more information.

#### Zip Dataset

- Compress all images, videos, and text files into a zip file.
- All viable files will be included in the zip archive.

#### Exit

- Close the application.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Edit Menu

Basic editing actions for text and file pairs.

#### Save Text

- Save the currently displayed text to the associated text file.
- If [Clean-Text](#clean-text) is enabled, the text will be automatically cleaned before saving.
- If [List-View](#list-view) is enabled, the text will be reformatted back to normal before saving.

#### Cleanup All Text Files

- Fix various typos across all text files.
- Runs the [Clean-Text](#clean-text) tool on all text files.

#### Create Blank Text Files

- Automatically creates a blank text file for each unpaired image found in the selected directory.
- Text files are automatically named after their corresponding images.

#### Rename Pair

- Rename the current image and text file pair.

#### Duplicate Pair

- Create a copy of the current image and text file pair.

#### Delete Pair

- Delete the current image and text file pair.

#### Undo Delete

- Restore the last deleted image and text file pair.

#### Next Empty Text File

- Navigate to the next empty or missing text file.

#### Random File

- Navigate to a random image and text file pair.

#### Open Settings File

- Open the `settings.cfg` file in your default text editor.
- You can safely delete this file.

#### Open MyTags File

- Open the `my_tags.csv` file in your default text editor.
- You can safely delete this file.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Tools Menu

Batch and current image processing tools.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#### Batch Operations

- Perform batch operations on images and text files.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

##### Batch Crop Images

1. Define a width and height.
2. Select the `Crop Anchor`.
3. Select `Crop`.

> The crop anchor dictates the area of the image to keep.

##### Create Wildcard From Text Files

- Combine all text files into a single `wildcard` text file where each line corresponds to the tags of an image.
- Works great in combination with the [AutoTag](#autotag) tool to create diverse wildcard tags.
- Wildcard files are designed to be loaded alongside image generators to create more diverse outputs.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#### Edit Current Pair

- Edit the current image and text file pair.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

##### Upscale

- Enter [Batch Upscale](#batch-upscale) with the current image selected.
- Quickly switches to the `Batch Upscale` tool, disables `Batch` mode, and allows you to upscale the current image from the Tagger interface.

##### _Crop

- Enter [Crop](#crop) with the current image selected.
- Quickly switches to the `Crop` tool with the current image from the Tagger interface selected.

##### Resize

- Open image resize dialog.
- Resize the current image by specifying exact dimensions or using a percentage input.
- Width and height can be adjusted independently or locked together.
- Supports resizing GIFs and different sampling methods such as `Lanczos`, `Nearest`, and `Bicubic`.
- Provides detailed output stats of the resizing operation such as new dimensions and filesize.

##### Expand

- Expand and fill the image, fitting it to a square.
- Expands the shorter side to match the longer side, making the image a square.
- Fills the empty space by stretching the pixels around the long side.
- Intended for images with simple or soft gradient backgrounds.
- Not recommended for images with complex or detailed backgrounds.

##### Rotate

- Rotate the image clockwise.

##### Flip

- Flip the image horizontally.

##### Auto-Tag

- Quickly interrogate the image using the [AutoTag](#autotag) tool.
- Runs the `AutoTag` tool using the defined settings and opens the AutoTag toolbar.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Options Menu

Options related to text, load order, autocomplete, and more.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#### Text Options

- Settings for text file handling and display.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

##### Clean Text

Automatically cleans text when saving.

- Cleans text by:
  - Removing duplicate tags.
  - Collapsing extra commas/spaces/backslashes.
  - Normalizing commas or newlines depending on list mode.
  - Trimming leading/trailing punctuation and whitespace.

##### Auto-Delete Blank Files

- Automatically delete blank text files when saving.

##### Highlight Selection

- Highlight matching selected text. Can be useful for quickly seeing repeated tags.

##### Add Comma After Tag

- Insert a comma at the end of the text/after inserting a tag.

Ensures you can type immediately after inserting a tag or navigating to the next image pair.

##### List View

- Display the text box tags in a list view.
- Text is always reformatted back to normal when saving.

This method is designed to work with CSV style text formatting.

##### Auto-Save

- Save text automatically when navigating between image text pairs or when closing the app.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#### Loading Order

- Set the file loading order.

Changes the order in which files are loaded and displayed.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#### Autocomplete

- Configure autocomplete settings.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

##### Autocomplete Dictionary

- Choose the autocomplete dictionary.

- Select between:
  - English Dictionary
  - Danbooru
  - Danbooru (Safe)
  - Derpibooru
  - e621

Multiple selections are allowed, but due to performance reasons, the resulting suggestions may be limited by the Threshold setting.

##### Autocomplete Threshold

- Essentially widens the range of text considered for suggestions, allowing for more flexible matching. *(slower==more flexible)*

##### Autocomplete Quantity

- Set the number of autocomplete suggestions returned and displayed.
- Lowering this value may improve performance.

##### Autocomplete Match Mode

Controls how text is matched against the selected dictionary(s) and typed content.

- Match Mode:
  - `Match Whole String`: Match all text between the commas in the cursor selection.
  - `Match Last Word`: Only the current text under the cursor is used for autocomplete.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#### Set Default External Editor

Set the default external image editor.

Choose the executable file of your preferred image editor, such as GIMP, Paint. NET, Photoshop, or any other image editor.

Press [F4](#f4) to quickly open the image in the external editor.

#### Restore Last Path

- Restore the last used file path when restarting the app.

#### Reset Settings

- Reset all settings to default and re-run the setup dialog.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### About Menu

Display the app startup/help information.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Tagger View Menu

Options for customizing the tagger view layout and behavior.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

### Toggle Image Grid

Show or hide the image grid.

- The image grid replaces the current image display with a grid layout.

### Toggle Zoom

Show or hide the image zoom popup.

- Hover your mouse over the image to reveal the zoom popup.
- Use the `mouse-wheel` to zoom in and out.
- Use `Shift` + `mouse-wheel` to adjust popup size.

### Toggle Thumbnail Panel

Show or hide the thumbnail panel.

- The thumbnail panel displays a carousel of image thumbnails for quick navigation below the displayed image.
- Right-click on a thumbnail for more options.

### Toggle Edit Panel

Show or hide the quick edit panel.

- The quick edit panel allows for fast adjustments to the current image such as:
  - Brightness
  - Contrast
  - Auto Contrast
  - Highlights
  - Shadows
  - Saturation
  - Sharpness
  - Hue
  - Color Temperature

1. Select a adjustment option from the dropdown.
2. Adjust the slider to change the selected value.
3. Click `Save` to save a copy of the edited image.

- Click the `Revert` button to toggle between no adjustments and the last applied adjustments.
  - Right click to totally revert all adjustments.
- Enable the checkbox to enable cumulative mode which allows multiple adjustments to be applied in sequence.

### Always On Top

- Keep the application window always on top.

### Big Save Button

- Make the save button more prominent.

### UI: Vertical View

- Switch to a vertical view layout.

In this layout, the `image` and `text` frames are positioned one above the other instead of side-by-side.

### UI: Swap img-txt Sides

- Swap the positions of the image and text frames.

Swap the current `image` and `text` frames, either horizontally or vertically depending on the layout direction.
