#region Img-Txt Viewer About


IMG_TXT_VIEWER_ABOUT = """
# Quick Start

Welcome to img-txt Viewer.

This application helps you organize, tag, and edit image datasets and their matching captions. An *image-text pair* is an image file and a text (.txt) file that share the same base filename.

**Supported formats:** *PNG, JPG, JPEG, JFIF, JPG_LARGE, WEBP, BMP, GIF, MP4*

To begin, select the folder that contains your image-text pairs using the `Browse...` button.

## Tagger Shortcuts

- **Alt + Left/Right**: Move between image-text pairs.
- **Shift + Del**: Move the current pair to a local Trash folder.
- **Alt**: Cycle autocomplete suggestions.
- **Tab**: Insert the highlighted suggestion.
- **Ctrl + S**: Save the current text file.
- **Ctrl + E**: Jump to the next empty text file.
- **Ctrl + R**: Jump to a random pair.
- **Ctrl + F**: Open Find and Replace.
- **Ctrl + Z / Ctrl + Y**: Undo / Redo.
- **Ctrl + W**: Close the window.
- **F1**: Toggle Image Grid view.
- **F2**: Toggle zoom popup.
- **F4**: Open the current image in your default editor.
- **Middle-click on a tag**: Delete that tag.

## Tagger Tips

A guided setup runs on first launch to configure autocomplete dictionaries and matching settings.

- Re-run the setup: *Options > Reset Settings*.
- Configure autocomplete: *Options > Autocomplete* or use the menu button on the suggestion row.
- Use an asterisk (*) while typing for fuzzy autocomplete suggestions.
- *Match Modes*:
    - **Match Last Word**: Use only the last typed word (recommended for natural suggestions).
    - **Match Whole String**: Match the whole comma-separated tag.

- Right-click the *Browse...* button to set or clear an alternate text folder if captions are stored separately.
- Right-click the displayed image to access image-specific tools.

## Tagger Toolbar

Tools appear below the text box. Click (?) for detailed help.

- **Search and Replace (S&R)**: Search across files and replace text.
- **Prefix**: Insert text at the start of selected files.
- **Append**: Insert text at the end of selected files.
- **AutoTag**: Generate tags using an ONNX vision model.
    - ONNX (Open Neural Network Exchange) is a portable model format for running pre-trained AI models.
    - Place models under `onnx_models/<model_name>/model.onnx` and `selected_tags.csv`, then restart.
- **Filter**: Show only pairs that match or exclude specified text.
    - Use `+` to include multiple strings and `!` to exclude strings.
- **Highlight**: Always highlight specified words when viewing files.
- **Font**: Adjust font size and style for the text editor.
- **My Tags**: Save custom tags for autocomplete; saved to *my_tags.csv*.
- **Stats**: View dataset statistics and most common tags.

## Main Toolbar

Quick tools operating on the current working folder.

- **Tag-Editor**: Edit tags across files; edits are staged until committed.
- **Crop**: Crop images, extract GIF frames, or use fixed aspect ratios.
- **Batch Upscale**: Upscale images using Real-ESRGAN NCNN models.
    - Add `.bin` and `.param` model files to `models/ncnn_models`.
- **Batch Resize**: Resize and convert many images at once.
- **Batch Rename**: Rename files using presets (numbered or dated).
- **Find Duplicates**: Locate duplicate files using hashing and manage them.

## Other

- *File > Zip Dataset*: Compress images and text into a ZIP archive.
- *Edit > Cleanup All Text Files*: Remove duplicate tags, extra commas/spaces, and similar formatting issues.
- *Tools > Batch Operations*: Includes Batch Crop Images and Create Wildcard From Text Files.

## Text Options & Loading

- **Text Options**:
    - *Clean-Text*: Apply cleanup when saving.
    - *Auto-Delete Blank Files*: Remove empty caption files when saving.
    - *Highlight Selection*: Highlight matching text when selecting.
    - *Add Comma After Tag*: Insert a comma after inserted tags.
    - *List View*: Show tags in a CSV-like list format.
    - *Auto-Save*: Save changes when moving between pairs.

- **Loading Order**: Choose Name, File Size, Date Created, Extension, Last Access Time, or Last Written. Use Ascending or Descending.

## Autocomplete

- **Dictionary**: Select one or more dictionaries for suggestions.
- **Threshold**: Lower values widen matches (may be slower).
- **Quantity**: Limit the number of suggestions returned.
- **Match Mode**: See *Tagger Tips* for guidance.

- Restore the last used path at startup: *Options > Restore Last Path*.
- Open this help: *About*.

For more details and examples, use the (?) help buttons in the app or read `docs/User_Guide.md`.
"""


#endregion
#region Batch Tag Edit


BATCH_TAG_EDIT_HELP = """
# Tag-Editor Help

## Overview

This tool is integrated with the Tagger tab and shares the same working directory.

Batch Tag Edit lets you view, filter, edit, and delete tags across all text files in the current working directory.
All changes are staged as *pending* and are not written to disk until you **commit** them.

## Notes on file parsing

- This tool is designed for CSV-like text files. Tags are parsed by splitting on commas and periods.
- Periods in captions or sentences will be treated as separators and can produce separate tags.
- Some special characters or uncommon formatting may not be handled as expected.
- *Always back up your text files before committing changes.*

## Instructions

- Use the filter controls to narrow the tag list:
    - *Filter by tag text* or by *tag count* (see Filter Tips).
    - Filtering is disabled while there are pending changes to avoid hiding uncommitted edits.
- Select tags to edit or delete (Ctrl+Click or Shift+Click to multi-select).
- To edit:
    - Enter the new tag in the Edit box and click **Apply** (or press Enter).
- To delete:
    - Leave the Edit box empty and click **Apply**, or use the right-click menu.
- Right-click a tag for quick actions: **Edit**, **Delete**, **Copy**, and **Quick Actions**.
- Pending changes appear in the *Action* and *New Tag* columns and are highlighted:
    - *green* = edit; *red* = delete.
    - Icons and column text also indicate the pending actions.
- Click **Commit Changes** to apply all pending edits and deletes to the text files. This action cannot be undone.
- Use **Refresh** to reload the tag list and clear pending changes and filters.

## Filter Tips

- Filter options:
    - *Contains Text*: show tags containing the input text.
    - *Does Not Contain*: exclude tags containing the input text.
    - *Count Equals / Not Equals*: filter tags by exact count.
    - *Count Less Than / Greater Than*: filter tags by count range.
- For most options you can enter multiple values separated by commas.
- Example: to show tags used exactly 1 or 2 times, select *Count Equals* and enter 1,2.

## Sorting

- Click column headers to sort by *Count*, *Tag*, *Length*, *Action*, or *New Tag*.
- The Tag column cycles through: *Name*, *Name (reverse)*, *Length*, *Length (reverse)*.

## Context Menu & Quick Actions

- Right-click selected tags for quick actions: **Edit**, **Delete**, **Copy**, **Quick Actions**, selection tools, and **Revert changes**.
- Quick Actions include:
    - convert case (upper/lower/title),
    - replace spaces or underscores,
    - add or remove escape characters,
    - strip punctuation or digits,
    - trim whitespace and other common text transforms.

## Selection Hotkeys

- **Ctrl+A**: Select All
- **Ctrl+I**: Invert Selection
- **Esc**: Clear Selection
- **Ctrl+C**: Copy selected tags

## Other Features

- Double-click a tag to edit it quickly, this action can also be changed to delete via the Options menu.
- The info bar displays total, filtered, selected, and pending counts.
- Use the *Tagger* tab to change the working directory or file set.
- Tooltips show long tag names on hover.
"""


#endregion
#region Crop UI


CROP_UI_HELP = """
# Crop Tool Help

This tool is integrated with the Tagger tab and shares the same working directory.

Use the Crop tool to select, crop, and transform images, and to extract frames from animated GIFs.

## Supported file types

- *png*, *jpg*, *jpeg*, *webp*, *gif*

## Basic usage

- 1) Select an image using the navigation controls.
- 2) Click and drag on the image to create a selection.
- 3) Adjust the selection using corner/edge handles or the size/position fields.
- 4) Click **Crop Selection** to apply the crop.
- 5) Choose a save option to store the cropped image.

## Selection controls

- Click and drag to create or resize a selection.
- Double-click to create a centered selection constrained to the displayed image's aspect ratio.
- Click outside the selection to clear it.
- Use corner and edge handles to resize the selection.
- Click inside the selection and drag to move it.
- Use the mouse wheel to resize:
    - *Shift + wheel* — adjust width
    - *Ctrl + wheel* — adjust height
    - *Ctrl + Shift + wheel* — adjust both

## Size & position

- **W (px):** Width of the selection in pixels.
- **H (px):** Height of the selection in pixels.
- **X (px):** Horizontal offset from the image's top-left.
- **Y (px):** Vertical offset from the image's top-left.

All values can be entered manually or adjusted using spinbox controls.

## Fixed selection modes

- **Aspect Ratio:** Keep a specific width-to-height ratio (for example, *16:9*, *1:1*, *3:2*).
- **Width:** Lock the width; height is adjustable.
- **Height:** Lock the height; width is adjustable.
- **Size:** Lock both width and height to exact pixel dimensions.
- **Auto:** Select the closest predefined aspect ratio automatically from a list.
- Use the **'<'** button to insert the current selection dimensions into the field.

## Guidelines overlays

- **No Guides:** No overlay guides are shown.
- **Center Lines:** Show horizontal and vertical center lines.
- **Rule of Thirds:** Show a 3x3 grid.
- **Diagonal Lines:** Show diagonal guides across the selection.

## Options

- **Expand Center:** Expand or contract the selection equally from its center point.
- **Highlight:** Toggle a darkened overlay outside the selection to emphasize the crop area.

## Transform tools

- **Rotate:** Rotate the image 90° clockwise.
- **Flip X:** Mirror the image horizontally.
- **Flip Y:** Mirror the image vertically.

## GIF handling

- Animated GIF frames appear as thumbnails.
- Click a frame thumbnail to select it for editing.
- Use the timeline slider to navigate frames.
- **Extract GIF:** Save all frames as separate PNG files.

## After cropping

- **Save and Close:** Apply the crop and switch back to the Tagger tab.
- **Save and Next:** Apply the crop and load the next image.
- **Save as...:** Choose a save location and filename via the file dialog.
- **Save:** Save to the same folder with a unique filename to avoid overwriting; then do nothing.

## Tips

- Use **Save as...** to preserve the original image.
- Use **Extract GIF** when you need individual frames for further editing.
- Right-click the image for additional context actions and keyboard shortcuts.
"""


#endregion
#region Batch Upscale


BATCH_UPSCALE_HELP = """
# Batch Upscale Help

This tool is integrated with the Tagger tab and shares the same working directory.

## Supported file types

- *png*, *webp*, *jpg*, *jpeg*, *jpg_large*, *jfif*, *tif*, *tiff*, *bmp*, *gif*

## Models

These models are included by default:

- realesr-animevideov3-x4
- RealESRGAN_General_x4_v3
- realesrgan-x4plus
- realesrgan-x4plus-anime
- AnimeSharp-4x
- UltraSharp-4x

Add your own models by placing each model in its own folder under `models/ncnn_models`. The folder name becomes the model label.

- Required files:
    - `.bin` (model weights)
    - `.param` (model parameters)

Restart the program after adding models to load them.

Example folder layout:
.
└── img-txt_viewer/
    └── models/
        └── ncnn_models/
            └── realesr-animevideov3-x4/
                ├── realesr-animevideov3-x4.bin
                └── realesr-animevideov3-x4.param


## Upscale strength

This setting blends the original and upscaled images together; lower values preserve more of the original detail

- 0% - returns the original image
- 100% - applies the full upscaling effect

## Upscale factor

Controls the final output size relative to the input size.
- 1x - Returns the original size image.

## Processing modes

### Single mode

1. Select an image with the Browse... button or from the file list
2. Choose Upscale Model, Upscale Factor, and Upscale Strength
3. Click **Upscale** to process the selected image

### Batch mode

1. Enable Batch Mode
2. Choose an input directory containing supported images
3. Click **Upscale** to process all supported images in the directory
4. Click **Cancel** at any time to stop processing after the current image finishes

## Auto output naming

- When enabled, the app generates output folders and filenames automatically using the input path as the base
- This helps organize results and avoid filename conflicts
"""


#endregion
#region Batch Resize Images


BATCH_RESIZE_IMAGES_HELP = """
# Batch Resize Help

This tool is integrated with the Tagger tab and shares the same working directory.

Use this tool to resize or convert many images at once. Select a resize mode, set output and quality options, then run the operation.

## Supported file types

- *jpg*, *jpeg*, *png*, *webp*, *bmp*, *tif*, *tiff*

## Resize Modes

- **Resize to Resolution**
    - Resize to a specific width and height. *This ignores aspect ratio.*
- **Resize to Percentage**
    - Scale the image by a percent value (for example, 50% = half size).
- **Resize to Width**
    - Target a specific width; height is adjusted to preserve aspect ratio.
- **Resize to Height**
    - Target a specific height; width is adjusted to preserve aspect ratio.
- **Resize to Shorter Side**
    - Resize so the shorter side matches the target while preserving aspect ratio.
- **Resize to Longer Side**
    - Resize so the longer side matches the target while preserving aspect ratio.

## Scaling Rules

- **Upscale and Downscale**
    - Apply the resize regardless of whether the result is larger or smaller than the original.
- **Upscale Only**
    - Resize only if the new dimensions are larger than the original (no change if smaller).
    - Example: original 800x600 -> target 1200x900 = *resized*; target 400x300 = *skipped*.
- **Downscale Only**
    - Resize only if the new dimensions are smaller than the original.

## Quality & Output Format

- **Quality**
    - Controls output quality for *JPG* and *WEBP* (typically 1-100). Higher values increase visual quality and file size. *Ignored for PNG.*
- **File type**
    - Choose *AUTO* to keep each input file's original format.
    - Select a specific format to convert all outputs to that format.
    - Note: converting PNG to JPEG removes transparency.

## Output Location & Overwrite

- **Use Output Folder**
    - When enabled, a folder named *Resize Output* is created inside the source folder and resized images are saved there.
    - When disabled, resized images are saved next to the originals.
- **Overwrite Files**
    - If disabled, conflicting filenames receive a unique suffix (for example, _1).
    - If enabled, existing files with the same basename are overwritten.
    - There is no automatic undo for overwrites; back up originals if needed.

## PNG Metadata

For A1111-style PNG metadata preservation.

- When saving as PNG, preserved PNG chunk metadata is written to the output PNG.
- If converting a PNG to another format, a text file containing the PNG chunk metadata is created alongside the converted file.

## Convert Only

When enabled, images are converted to the chosen file type without changing dimensions. Resize settings are ignored.
"""


#endregion
#region Batch Rename


BATCH_RENAME_HELP = """
# Batch Rename Help

This tool is integrated with the Tagger tab and shares the same working directory.

Rename files in bulk using presets and options. Select files, choose a preset, and apply the renaming operation.

## Supported file types

- *txt*, *jpg*, *jpeg*, *png*, *webp*, *bmp*, *tif*, *tiff*, *gif*

## Instructions

1. Select a folder containing files to rename using the Browse... button.
2. Select files to rename by clicking them.
    - Hold Ctrl+Shift and click for multi-select.
3. Adjust options as needed:
    - **Handle duplicates**: Rename, Move to Folder, Overwrite, or Skip.
    - **Respect img-txt pairs**: When enabled, image files and their matching .txt files (same base name) are renamed together.
4. Choose a renaming preset:
    - **Numbering**: Sequential numbering (for example, 0001.jpg).
    - **Auto-Date**: Use the file's modified date plus numbering.
5. Click **Rename Files** to apply changes.
6. Confirm the operation if prompted.

## Notes

- **Naming Conflicts**: If a target filename already exists, the selected duplicate handling option is applied.
    - For *Rename*, a unique suffix (_1, _2, etc.) is added.
    - Run the tool multiple times to resolve conflicts if needed.
- **No undo:** This operation cannot be undone. Back up important files before renaming.

## Hotkeys

- **Ctrl+Click:** Select or deselect a file.
- **Ctrl+A:** Select all.
- **Ctrl+D:** Deselect all.
- **Ctrl+I:** Invert selection.
- **F5:** Refresh the file list.
"""


#endregion
#region Batch Image Edit


BATCH_IMAGE_EDIT_HELP = """
# Batch Image Edit

This tool is integrated with the Tagger tab and shares the same working directory.

A tool to apply image adjustments to multiple files at once. The UI has three panels:
- Left: Image file list (select images, multi-select, preview)
- Center: Live preview (original and adjusted)
- Right: Adjustment controls (sliders + advanced options)

## Supported file types
- *jpg*, *jpeg*, *png*, *webp*, *bmp*, *tif*, *tiff*, *jfif*

## Adjustment Controls
- **Brightness**: Adjust overall brightness
- **Contrast**: Increase or decrease contrast
- **AutoContrast**: Automatic contrast optimization
- **Highlights**: Control bright areas
    - *threshold*: the level considered a highlight
- **Shadows**: Control dark areas
    - *threshold*: the level considered a shadow
- **Saturation**: Adjust color intensity
- **Vibrance**: Boost muted colors
- **Hue**: Shift the color spectrum
- **Color Temp**: Adjust warm/cool tones
- **Sharpness**: Enhance or soften details
    - *boost*: multiplies the sharpness effect
- **Clarity**: Enhance mid-tone contrast
    - *radius*: controls the radius for mid-tone contrast

*Advanced options* are available via the "+" button for applicable sliders.

## Controls & Shortcuts
- Click a slider value to type a numeric value. Press *Enter* to apply, *Esc* to cancel.
- Right-click a slider handle to reset that slider to its default (main sliders default to 0; advanced sliders revert to their advanced defaults).
- Click the **Reset** button to restore all sliders and advanced options to defaults. This clears any temporary preview edits.

## Preview behavior
- *Single view*: the preview shows the edited image. Press and hold the *right mouse button* on the preview to temporarily show the original; release to return to the edited view.
- *Split view (Options > Use Split View)*: left pane shows the original; right pane shows the edited image. Right-click press temporarily shows the original in the right pane.

## Batch processing & files
- The batch operation applies to the current working directory image list (all supported images shown in the left list).
- Selection affects preview only and does not limit which files are processed.
- To process a subset, change the working folder or remove unwanted files from the folder before running.
- Only supported file types are shown and processed.

## Save & Overwrite options
- **Save To**
    - *Subfolder* (default): saves edited images to an "Edited Images" subfolder in the working directory.
    - *Same Folder*: saves edited images to the same folder as the originals.
- **Save As**
    - *Same Format* (default): keep the original file type.
    - *JPEG*: force output to JPEG (saved with quality=100).
    - *PNG*: force output to PNG.
- **Overwrite**
    - *Always*: if combined with Save To = Subfolder, the originals are removed (current behaviour).
    - *On Conflict* (default): overwrite only when a file with the same name exists at the target path.
    - *Never*: always create a unique filename (append _1, _2, ...) to avoid overwriting.

## Running the batch
1. Select a working directory (Browse..., enter a path, or use the app's main image directory).
2. Adjust sliders and advanced options.
3. Use the Options menu to choose Save To, Save As, Overwrite, and Split View.
4. Click **Apply!** to process all images shown in the list.
5. Click **Cancel** to stop processing; the run stops after the current image finishes.
6. A summary is displayed when processing completes or is cancelled.

## Progress & status
- The bottom row shows *Total*, *Processed*, *Elapsed time*, *ETA*, and a progress bar.
- Progress counts and the progress bar update as files are processed.

## Tips & behavior
- Use **Open** to reveal the working folder in File Explorer.
- Use **Refresh** to reload the file list from disk.
- The same image editing pipeline is used for previews and saving; previewed edits represent the final output.

Processing time depends on image size, number of images, and complexity of adjustments. All adjustments are non-destructive until you click **Apply!**.
"""


#endregion
#region Find Dupe File


FIND_DUPLICATE_FILE_HELP = """
# Find Duplicate Files Help

This tool is integrated with the Tagger tab and shares the same working directory.

- Use this tool to locate and manage duplicate files safely.
- Files are compared by computing cryptographic hashes (MD5 or SHA-256).

## Processing Modes

- **MD5 — Fast**
    - Quick comparisons for large sets. *Recommended*.
- **SHA-256 — Thorough**
    - Slower but reduces the risk of false matches **(rare)**.

## Scanning Options

- **Images**
    - Scans only supported image file types.
    - Enables *Move Captions* to move matching `.txt` caption files that share the same base filename.
- **All Files**
    - Scans every file type.
- **Recursive**
    - Includes subfolders in the scan.
    - Files are compared only against other files in the *same* folder (duplicates across different folders are not compared).
- **Move Captions**
    - When enabled, moves associated `.txt` caption files alongside moved images.

## Duplicate Handling

- **Single Mode**
    - Keeps one original file in place and moves detected duplicates.
- **Both Mode**
    - Moves all copies of a duplicate set into the duplicates folder and groups them together.

## File Menu Actions

- **Select Folder** — Choose the folder to scan.
- **Open Folder** — Reveal the current folder in File Explorer.
- **Restore Moved Duplicates** — Return moved files to their original locations (original folder structure is preserved).
- **Move All Duplicates Upfront** — Consolidate duplicates in the scan root before further actions.
- **Delete All Duplicates** — Permanently delete duplicates (this cannot be undone).

## Options

- **Process Mode** — Select MD5 or SHA-256.
- **Max Scan Size** — Skip files larger than this limit (in MB).
- **File types to Scan** — Specify which extensions to include.
- **Recursive Scanning** — Enable or disable subfolder scanning.
- **Scanning Mode** — Choose Images-only or All Files.
- **Duplication Handling** — Choose Single or Both mode.

## Usage

1. Select a folder using *Select Folder* or the Browse button.
2. Choose scanning options and process mode.
3. Enable *Recursive* to include subfolders (see Recursive note).
4. Click *Find Duplicates* to start scanning.

## Managing Results

- Duplicates are moved to a `_Duplicate_Files` folder in the scanned directory.
- Use *Undo* or *Restore Moved Duplicates* to revert moves.
- The status bar shows scan progress and duplicate counts.

## Important Notes

Actions such as deleting duplicates or moving them upfront are irreversible — back up important files first.
"""


#endregion
#region Search and Replace


SEARCH_AND_REPLACE_HELP = """
# Search and Replace

Use this tool to find and replace text across all *text (.txt) files* in the selected folder.

## How it works

- Enter the text to search for and the replacement text.
- By default the search is an exact, case-sensitive string match.
- Enable *Use Regular Expressions* in the menu to treat the search as a regex pattern.
- A backup of affected text files is created automatically before changes are applied.

## Examples

- *Search for:* *the big brown dog*.
- *Replace with:* *the big red dog*.

This replaces every exact occurrence of *the big brown dog* with *the big red dog*.

- *Regex example:* enable regex and use \\d+ to match one or more digits.
- To make a regex case-insensitive, use the inline flag `(?i)`, for example `(?i)dog`.

## Filtering

If a filter is applied, only matching text files will be modified.

## Safety & Undo

- A backup is created automatically before any changes are saved.
- Use *Undo Last Action* in the menu to revert changes if needed.
- Test on a small set of files before running large replacements.

## Notes

- Only text (.txt) files are affected; image files and filenames are not changed.
- Regular expressions are powerful and can change many matches; use them carefully.
"""


PREFIX_HELP = """
# Prefix Tool

Use this tool to insert the provided text at the start of each *text (.txt) file* in the selected folder.

## How it works

- The supplied text is inserted at the very start of each file, before any existing content.
- If the prefix does not end with ", " (a comma and a space), the app will add ", " automatically to keep tag formatting consistent.
- If a .txt file does not exist for an image, a new file is created with the prefixed text.
- A backup of affected files is created before changes are applied. Use *Undo Last Action* to restore backups.

## Filtering

If a filter is active, only matching text files will be changed.

## Tips

- Test prefixing on a small set of files first.
- Use *Undo Last Action* in the menu to revert changes if needed.
"""


APPEND_HELP = """
# Append Tool

Use this tool to add the same text to the end of all *text (.txt) files* in the selected folder.

## How it works

- Enter the text to append in the Append field.
- If your text does not start with ", " (a comma and a space), the app will add a leading ", " automatically to keep tag formatting consistent.
- You will be asked to confirm before changes are applied.
- A backup of affected files is created automatically. Use *Undo Last Action* to restore files if needed.
- If a text file does not exist for an image, a new .txt file will be created.

## Filtering

If a filter is active, only matching text files will be modified.

## Tips

- Test on a small set of files before running large operations.
- To remove appended text later, use Search & Replace with a backup in place.
"""


#endregion
#region AutoTag


AUTOTAG_HELP = """
# Auto-Tag Help

##  Overview

- *Auto-Tagging* analyzes images with an **ONNX** vision model and suggests descriptive tags.
- Suggested tags appear in the Auto-Tag listbox with confidence scores.
- Tags can be inserted into the caption box or saved to all text files during batch operations.

##  Models

Example source: https://huggingface.co/SmilingWolf
Add your own models by placing each model in its own folder under `onnx_models`. The folder name becomes the model label.

- Required files:
    - `model.onnx`
    - `selected_tags.csv`

Restart the program after adding models to load them.

Example folder layout:
.
└── img-txt_viewer/
    └── onnx_models/
        └── wd-v1-4-moat-tagger-v2/
            ├── model.onnx
            └── selected_tags.csv

##  Quick Start

1) Select a **Model** from the dropdown.
2) Set *General Threshold*, *Character Threshold*, and *Max Tags*.
3) Configure *Exclude*, *Keep*, and *Replace / With* lists and the *Keep escape* options.
4) Click **Interrogate** to analyze the current image or video frame.
5) Use the listbox and Insert modes (**Prefix**, **Append**, **Replace**) to add tags to the caption box.
6) To process a folder, enable **Batch**, choose an Auto-Insert mode, then click **Interrogate**.

##  UI Reference and Options

- **Auto-Insert**
    - *Disable* — do not insert automatically.
    - *Prefix* — insert tags at the start.
    - *Append* — insert tags at the end.
    - *Replace* — replace the entire text box.
- **Batch**
    - Processes all images in the current directory.
    - Requires Auto-Insert to be set (Prefix, Append, or Replace).
    - Updates or creates text files for each image.
- **Viewport**
    - When enabled (non-batch), interrogates only the visible portion of the displayed image.
    - Ignored during Batch interrogation.
- **Thresholds & Limits**
    - *General Threshold*: 0.00 - 1.00 (lower is more permissive).
    - *Character Threshold*: 0.00 - 1.00 (used for character tags).
    - *Max Tags*: maximum number of tags returned (default ~40).
- **Preserve Options**
    - *Keep underscores* — preserve `_` instead of replacing with spaces.
    - *Keep escape* — preserve backslashes in tags (for escaped characters).
- **Lists**
    - *Exclude*: comma-separated tags to exclude. Enabling *Auto* adds tags already present in the caption.
    - *Keep*: comma-separated tags that are always included.
    - *Replace / With*: parallel, comma-separated lists; each Replace item maps to the With item at the same index.

##  Listbox and Selection

- Each item displays `score: tag` with the confidence score first.
- Visual cues:
    - Character tags are shown in green.
    - Keep tags are shown in red.
- Multi-select is supported.
- Context menu actions:
    - Insert (Prefix, Append, Replace)
    - Copy Selected Tags
    - Select All, Invert Selection, Clear Selection
    - Add to MyTags
    - Add to Exclude / Add to Keep (escapes are sanitized)

##  Replace Mapping and Edge Cases

- Replace/With mapping is index-based; unmatched entries are ignored.
- Exclude and Keep lists are normalized (trimmed and cleaned).
- Escape handling follows the *Keep escape* option.
- Use Auto Exclude to avoid adding tags already present in the caption.

Example:
- Replace: `cat, dog`
- With: `feline, canine`

##  Video Handling

- For a single (non-batch) .mp4, the current video player frame is interrogated.
- For batch .mp4 files, a frame is extracted at about 2 seconds; if extraction fails, the file is skipped.

##  Tips & Troubleshooting

- If a model does not appear, ensure the folder contains both `model.onnx` and `selected_tags.csv`, then restart the app.
- Use *Auto* exclude to avoid duplicating tags already in captions.
- Use *Add to MyTags* to build your personal tag dictionary.
- Batch operations can take time. The modal shows ETA and can be stopped safely at any time.
"""


#endregion
#region Filter


FILTER_HELP = """
# Filter Tool

Use this tool to show only image-text pairs whose caption text matches the filter.

## How to use

- Enter one or more text terms to search within caption files.
- Use ' + ' (space-plus-space) to require multiple terms; all included terms must be present.
- Prefix a term with '!' to exclude captions that contain that term.
- Matching is a simple substring search by default and is case-sensitive.
    - Enable **Use Regular Expressions** (menu) to treat the filter as a regex.
    - For case-insensitive regex, add the inline flag `(?i)` at the start of your pattern.

## Examples

- *dog* — show pairs with captions that contain *dog*.
- *!dog* — exclude pairs whose captions contain *dog*.
- *dog + cat* — show pairs that contain both *dog* and *cat*.
- *!dog + cat* — show pairs that contain *cat* and do not contain *dog*.
- *!dog + !cat* — exclude pairs containing *dog* or *cat*.

## Notes & tips

- Filters adjust the file list for most tools and operations.
    - Use **Clear And Reset Filter** to restore the full image list.
- Use **Show Empty Text Files Only** (menu) to list images with empty or missing captions.
- Filtering searches caption text only; image or text filenames are not searched.
"""


#endregion
#region Highlight


HIGHLIGHT_HELP = """
# Highlight Tool

Enter words or phrases to highlight in the textbox.
Highlights are applied automatically as you move to a new image-text pair.

## How to use

- Type one or more terms to highlight.
- Use ' + ' (space-plus-space) to highlight multiple terms at once.
- Matching is a plain substring search (case-sensitive) by default.
- To use regular expressions or case-insensitive matches, enable *Use Regular Expressions* from the Highlight menu.

### Example

- *dog + cat*
    - Highlights all occurrences of *dog* and *cat* in the caption text.

### Notes

- Highlights are visual only and do not change the underlying text files.
- Clear the Highlight field to remove highlights.
"""


#endregion
#region MyTags


MY_TAGS_HELP = """
# My Tags

Manage custom tags and optional folders for autocomplete and quick insertion into caption files.

## Layout

- *My Tags (left):* a view of your tag groups and items.
- *All Tags (right):* tags aggregated from your caption files (toggle via Options > Show: All Tags).

## Add and organize

- Type a tag, then press *Enter* or click *Add*.
- To add inside a folder: select exactly one folder, then add; or right-click a folder and choose *New Tag...*
- To add a new group: right-click the My Tags tree and choose *New Group...*
- From All Tags: select tags and click "<" or right-click and choose *Add to MyTags*.
- From other places (editor or AutoTag): right-click selected text and choose *Add to MyTags*.

## Selection and menus

- Use *Ctrl* or *Shift* to multi-select items.
- Right-click for context actions and quick tools.
- Selection tools include: *All, Invert, Select All Groups, Select All Tags*.
- *Move to...* moves selected items into any MyTags folder. Choose *(Root)* to place items at the top level.

## Insert into text

- *Prefix* inserts before existing text.
- *Append* inserts after existing text.
- Double-click any tag to *Append* into the Textbox. Works from both panes.

## Edit, move, and reorder

- Use *Edit / Rename* to change a tag or group name.
- *Remove* deletes selected rows. Deleting a group removes its contents.
- Reorder by dragging with the middle mouse button (within the same parent) or use *Move Up / Move Down*.
- Drag-and-drop shows a blue placeholder. Multi-select reorder is supported.

## Save and refresh

- *Save Tags* writes changes to *my_tags.yaml* and updates autocomplete.
- *Refresh My Tags* reloads the file; unsaved changes are discarded.
- *Refresh All Tags* recomputes the All Tags panel from your files.

## Options and appearance

- *Use: MyTags* toggles whether My Tags are used by autocomplete.
- *Show: All Tags* toggles the All Tags panel.
- *Hide: controls* shows or hides button rows under each pane.
- *MyTags Font Style* lets you configure font family, size, weight, slant, underline, overstrike, and colors separately for Groups and Items. *Reset* restores defaults. Row height adjusts automatically.
- *Open MyTags File...* opens *my_tags.yaml* in your editor.

## Maintenance

- *Cleanup MyTags* removes duplicate tags (case-sensitive), empty or quoted tags, and empty groups. This action cannot be undone.

## Notes

- Data is stored in *my_tags.yaml*. If a legacy *my_tags.csv* exists, it will be imported automatically once.
- Tag order controls autocomplete priority and the default insertion order.
"""


#endregion
