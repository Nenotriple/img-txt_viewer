#region Img-Txt Viewer About


IMG_TXT_VIEWER_ABOUT = """
# Quick Start

Welcome to img-txt Viewer!

This application is designed to help you quickly manage and tag image datasets.

**Supported formats:** *PNG, JPG, JPEG, JFIF, JPG_LARGE, WEBP, BMP, GIF, MP4*

To get started, select a directory containing image-text pairs using the `Browse...` button.

## Tagger Shortcuts

- **ALT + LEFT/RIGHT:** Quickly move between img-txt pairs.
- **SHIFT + DEL:** Move the current pair to a local trash folder.
- **ALT:** Cycle through autocomplete suggestions.
- **TAB:** Insert the highlighted suggestion.
- **CTRL + S:** Save the current text file.
- **CTRL + E:** Jump to the next empty text file.
- **CTRL + R:** Jump to a random img-txt pair.
- **CTRL + F:** Open Find and Replace.
- **CTRL + Z / CTRL + Y:** Undo / Redo.
- **CTRL + W:** Close the window.
- **F1:** Toggle Image-Grid view.
- **F2:** Toggle zoom popup.
- **F4:** Open the current image in your default editor.
- **Middle-click on a tag:** Delete it.

## Tagger Tips

A guided setup will run on first launch to configure your autocomplete dictionaries and matching settings.

- Go to *Options > Reset Settings* to re-run the setup.

Autocomplete suggestions are based on your current dictionary and Suggestions options.

- Go to *Options > Autocomplete* or click the (☰) menu button on the suggestion row to change the settings.
- Use an asterisk (*) while typing for fuzzy search autocomplete suggestions.
- **Match Modes:** 'Last Word' matches only the last word typed, 'Whole String' matches the entire tag between commas.
- Use *Match Mode: Last Word* for more natural and less strict autocomplete.

- Highlight matching words by selecting similar text.
- Quickly create text pairs via *Edit > Create Blank Text Files* or by loading the image and saving the text.
- **List Mode:** Display tags in a list format while saving them in standard format.
- Right-click the *Browse...* button to set or clear the alternate text path, allowing you to load text files from a separate folder than images.
- Right-click the displayed image to access various options and tools.

Use the *View* menu above the displayed image to access additional options like:

- **Image Grid (F1):** Display images in a grid format for easier navigation.
- **Zoom (F2):** Toggle zoom popup for the displayed image.
- **Thumbnail Panel:** Toggle thumbnail panel visibility.
- **Edit Panel:** Toggle image edit panel which allows you to edit image brightness, contrast, and other properties.

## Tagger Toolbar

A variety of tools are available in the bottom toolbar below the text box. Expand the toolbar or click the (?) button for more information.

**Search and Replace (S&R):**
- Search for specific text across all listed files and replace it with another.

**Prefix:**
- Insert text at the START of all listed text files.

**Append:**
- Insert text at the END of all listed text files.

**AutoTag:**
- Automatically tag images using ONNX vision models like *wd-v1-4-vit-tagger-v2*.
- Can also be triggered via image right-click context menu.

**Filter:**
- Filter pairs based on input text.
- Effectively alters the listed files, allowing other tools like S&R, Prefix, and Append to work with the filtered results.
- Can filter just 'empty' text files.
- Supports multi string matching and exclusion patterns using (+) and (!).

**Highlight:**
- Always highlight specific text if it exists in the displayed text.
- Can be used to quickly locate important or repeated tags/words.
- Supports multi string matching using (+).

**Font:**
- Adjust font size and style for better readability.

**My Tags:**
- Add your own custom tags for autocomplete suggestions.
- This tool also displays all tags in the dataset and allows you to quickly add them to your own list or to the current tag file.
- Saved to *my_tags.csv*.

**Stats:**
- View statistics about your dataset, including text/image/video statistics, most common words, a list of all tags, and more.

## Main Toolbar

The main toolbar gives quick access to image and text tools. These use the same directory as set in the Tagger UI. For Tag-Editor and Crop, set a directory in Tagger UI first.

**Tag-Editor:**
- Display and edit image tags. Tags are listed with their occurrences.
- Changes are pending until you apply or save them.
- Respects Tagger UI 'Filter' settings, just remember to refresh the view.

**Crop:**
- Crop images to a specific aspect ratio or resolution.
- Can also extract GIFs into individual frames or crop them.
- Use *Auto Fixed Selection* mode to automatically select the closest aspect ratio based on image dimensions.

**Batch Upscale:**
- Upscale image(s) using *realesrgan-ncnn-vulkan*.
- Supports batch processing for multiple images at once.
- Adjust upscale factor (e.g., 0.5, 2.0, 4.0) to control the final output size.
- Adjust upscale strength to control the level of blending between original and upscaled images.
- Add your own **Real-ESRGAN NCNN models (.bin and .param)** to the *models/ncnn_models* folder.

**Batch Resize:**
- Resize image(s) using various methods and conditions.
- See the (?) help documentation for more details.

**Batch Rename:**
- Used to cleanup file names and quickly rename using a couple presets.
- Choose between Numbered or Dated naming presets.

**Find Duplicates:**
- Used to identify and manage duplicate files in your dataset.
- Uses simple hashing techniques to detect duplicates quickly.
- Can be used for images or any other files.
- Supports a variety of options, see the (?) help documentation for more details.

## Other

- *File > Zip Dataset*: Compress all images and text files into a single ZIP archive.
- *Edit > Cleanup All Text Files*: This operation will clean all text files from typos like:
    - Duplicate tags, Extra commas, Extra spaces, trailing commas/spaces, commas without spaces, and more.
- *Tools > Batch Operations > Batch Crop Images*: Crop all listed images to a specific resolution and crop anchor.
- *Tools > Batch Operations > Create Wildcard From Text Files*: Combine all captions into one text file, each file's content added to a new line.

**Text Options:**
- *Clean-Text*: perform text cleanup when saving.
- *Auto-Delete Blank Files*: Automatically delete blank text files when saving.
- *Highlight Selection*: When selecting text, other matching text will be highlighted.
- *Add Comma After Tag*: Automatically insert a comma after inserting a suggested tag.
- *List View*: Display text in a list format for easier navigation. (expects csv like format)
- *Auto-Save*: Automatically save changes made to text files when navigating between pairs.

**Loading Order:**
- Choose between Name, File Size, Date Created, Extension, Last Access Time, Last Time Written.
- Ascending or Descending order.

**Autocomplete:**
- *Dictionary*: Select the appropriate dictionary(ies) for text suggestions. Multiple selections are allowed, but due to performance reasons, the resulting suggestions may be limited.
- *Threshold*: Essentially widens the range of text considered for suggestions, allowing for more flexible matching. (slower==more flexible)
- *Quantity*: Control the number of suggestions returned.
- *Match Mode*: Controls how text is matched against the selected dictionary(ies) and typed content.
    - *Match Whole String*: Match all text between the commas in the cursor selection.
    - *Match Last Word*: Only the current text under the cursor is used for autocomplete.

- *Options > Restore Last Path*: Restore the last used file path when launching the app.
- *About*: Display this information.

For more detailed information regarding the tools and features, look for (?) buttons throughout the interface or view the `docs/User_Guide.md` file in the repo.
"""


#endregion
#region Batch Tag Edit


BATCH_TAG_EDIT_HELP = """
# Tag-Editor Help

## Overview
Batch Tag Edit lets you view, filter, edit, and delete tags across all text files in your working directory. All changes are staged as *pending* until you **commit** them.

## Technical Notes
- Designed for CSV-like text files. Both commas and periods are treated as tag or caption delimiters.
- Some special characters or formatting may not be handled as expected.
- *Always back up your text files before committing changes.*

## Instructions
1. Use the filter controls to narrow the tag list.
    - *Filter by tag text* or by *tag count* (see Filter Tips).
    - Filtering is disabled while there are pending changes.
2. Select tags to edit or delete (Ctrl+Click or Shift+Click for multi select).
3. To edit: enter a new tag in the Edit box and click **Apply** (or press Enter).
    - To delete: leave the Edit box empty and click **Apply**, or use the right-click menu.
    - Right-click a tag for **Edit / Delete / Copy** and quick actions.
4. Pending changes appear in the *Action* and *New Tag* columns and are highlighted (green = edit, red = delete).
5. Click **Commit Changes** to apply all pending edits and deletes to the text files. This cannot be undone.
6. Use **Refresh** to reload the tag list and clear pending changes and filters.

## Filter Tips
- Filter options:
    - *Contains Text*: show tags containing the input text.
    - *Does Not Contain*: exclude tags containing the input text.
    - *Count Equals / Not Equals*: filter tags by exact count.
    - *Count Less Than / Greater Than*: filter tags by count range.
- For most options you can enter multiple values separated by commas.
- Example: to show tags used exactly 1 or 2 times, select *Count Equals* and enter `1,2`.

## Sorting
- Click column headers to sort by *Count*, *Tag*, *Length*, *Action*, or *New Tag*.
- The Tag column cycles through: *Name*, *Name (reverse)*, *Length*, *Length (reverse)*.

## Context Menu & Quick Actions
- Right-click selected tags for quick actions: **Edit**, **Delete**, **Copy**, **Quick Actions** (transformations), selection tools, and **Revert changes**.
- Quick Actions include: convert case, replace spaces/underscores, add or remove escape characters, strip punctuation or digits, and other text transforms.

## Selection Hotkeys
- **Ctrl+A**: Select All
- **Ctrl+I**: Invert Selection
- **Esc**: Clear Selection
- **Ctrl+C**: Copy selected tags

## Pending Changes
- Pending edits are highlighted *green*; deletes are *red*.
- Filtering is disabled while pending changes exist.
- Use **Revert Selection** or **Refresh** to discard pending changes.

## Other Features
- Double-click a tag to quickly edit it.
- Tooltips show long tag names on hover.
- The info bar displays total, filtered, selected, and pending counts.
- Use the *Tagger* tab to change the working directory or file set.
"""


#endregion
#region Crop UI


CROP_UI_HELP = """
# Crop Tool Help

This tool is tied to the *Tagger* tab; the working directory is shared between both tools.

## Supported File types
*.png, .jpg, .jpeg, .webp, .gif*

## Basic Usage
1. Select an image using the navigation controls.
2. Click and drag on the image to create a selection.
3. Adjust the selection using handles or input fields.
4. Click **Crop Selection** to apply the crop.
5. Choose how to save the cropped image.

## Selection Controls
- Click and drag to create a selection.
- Double-click for a centered selection maintaining the displayed image's aspect ratio.
- Click outside the selection to clear it.
- Use corner and edge handles to resize the selection.
- Click inside the selection and drag to move it.
- Use mouse wheel to resize: *Shift+wheel* for width, *Ctrl+wheel* for height, *Ctrl+Shift+wheel* for both.

## Size & Position
- **W (px):** Width of selection in pixels.
- **H (px):** Height of selection in pixels.
- **X (px):** Horizontal position from top-left.
- **Y (px):** Vertical position from top-left.

All values can be entered manually or adjusted via spinbox controls.

## Fixed Selection
- **Aspect Ratio:** Maintain a specific width-to-height ratio (e.g., *16:9*, *1:1*, *3:2*).
- **Width:** Lock the width and freely adjust height.
- **Height:** Lock the height and freely adjust width.
- **Size:** Lock both width and height to specific dimensions.
- **Auto:** Automatically select the closest aspect ratio from predefined options.
- Use the **'<'** button to insert current selection dimensions into the field.

## Guidelines
- **No Guides:** No guidelines displayed.
- **Center Lines:** Display horizontal and vertical center lines.
- **Rule of Thirds:** Display a 3x3 grid.
- **Diagonal Lines:** Display diagonal guides from corners.

## Options
- **Expand Center:** Selection expands equally from its center point.
- **Highlight:** Toggle darkened overlay outside the selection.

## Transform Tools
- **Rotate:** Rotate image 90° clockwise.
- **Flip X:** Mirror the image horizontally.
- **Flip Y:** Mirror the image vertically.

## GIF Handling
- For GIF files, frames are displayed as thumbnails.
- Click a thumbnail to select that frame for editing.
- Use the timeline slider to navigate through frames.
- **Extract GIF:** Save all frames as individual PNG files.

## After Crop
- **Save and Close:** Apply the crop and close the tab.
- **Save and Next:** Apply the crop and load the next image.
- **Save as...:** Choose a save location and filename for the cropped image.
- **Save:** Apply the crop and save in the same location with a unique filename.
"""


#endregion
#region Batch Upscale


BATCH_UPSCALE_HELP = """
# Batch Upscale Help

## Supported File types
*.png, .webp, .jpg, .jpeg, .jpg_large, .jfif, .tif, .tiff, .bmp, .gif*

## Upscale Models
- *realesr-animevideov3-x4*
- *RealESRGAN_General_x4_v3*
- *realesrgan-x4plus*
- *realesrgan-x4plus-anime*
- *AnimeSharp-4x*
- *UltraSharp-4x*
- *Any additional "ESRGAN x4" models found in the `ncnn_models` directory will be added automatically.*

## Upscale Strength
Adjusts the blend between the original and upscaled images:
- *0%* — returns the original image.
- *100%* — applies the full upscaling effect.

## Processing Modes

### Single Mode
1. Select an image using the *Browse...* button or from the file list.
2. Adjust *Upscale Model*, *Upscale Factor*, and *Upscale Strength*.
3. Click **Upscale** to process the image.

### Batch Mode
1. Enable *Batch Mode*.
2. Select an input directory containing the images to upscale.
3. Click **Upscale** to process all supported images.
4. Click **Cancel** to stop processing at any time.

## Auto Output Naming
When enabled, output filenames and directories are generated automatically relative to the input path.

## Additional Note
- The tool performs an initial *4x* upscaling before applying the selected resize factor.
- Adjusting the upscale factor controls final size but does not change the internal 4x upscale step's behavior.

## Tips & Recommendations
- Add your own Real-ESRGAN NCNN models (.bin and .param) to *models/ncnn_models*.
- Use lower upscale factors for faster processing; use higher factors when larger outputs are required.
"""


#endregion
#region Batch Resize Images


BATCH_RESIZE_IMAGES_HELP = """
# Batch Resize Help

## Supported File types
- *.jpg*, *.jpeg*, *.png*, *.webp*, *.bmp*, *.tif*, *.tiff*

## Overview
A tool to resize or convert many images at once. Choose a resize method, set output options, then run the operation.

## Resize Modes
- **Resize to Resolution**
    - Resize to a specific width and height. *This ignores aspect ratio.*
- **Resize to Percentage**
    - Scale the image by a percent value (e.g., 50% = half size).
- **Resize to Width**
    - Target a specific width; height is adjusted to preserve aspect ratio.
- **Resize to Height**
    - Target a specific height; width is adjusted to preserve aspect ratio.
- **Resize to Shorter Side**
    - Resize so the shorter side matches the target while preserving aspect ratio.
- **Resize to Longer Side**
    - Resize so the longer side matches the target while preserving aspect ratio.

## Scaling Rules
- **Upscale and Downscale** - Apply the resize regardless of whether the result is larger or smaller than the original.
- **Upscale Only** - Resize only if the new dimensions are larger than the original.
- **Downscale Only** - Resize only if the new dimensions are smaller than the original.

## Quality & Output Format
- **Quality** - Controls output quality for *JPG* and *WEBP*. Higher values produce higher quality output. *Ignored for PNG.*
- **File type** - Choose *AUTO* to keep the input file type, or select a specific format to force all outputs to that type.

## Output Location & Overwrite
- **Use Output Folder** - When enabled, a folder named *Resize Output* is created inside the source folder and resized images are saved there.
- **Overwrite Files** - If disabled, conflicting filenames receive a unique suffix (e.g., _1). If enabled, existing files with the same basename are overwritten.

## PNG Metadata
- **Save PNG Info** - If saving as PNG, preserved PNG chunk info is written to the output. If converting from PNG to another format, a text file containing PNG chunk info is created alongside the converted file.

## Convert Only
- **Convert Only** - When enabled, images are converted to the chosen file type without changing dimensions. Resize settings are ignored.

## Tips
- Test with a small set of images to verify settings before processing large folders.
- Use *AUTO* file type to preserve original formats when you only need resizing.
- Be cautious with *Overwrite Files* as there is no automatic undo.
"""


#endregion
#region Batch Rename


BATCH_RENAME_HELP = """
# Batch Rename Help

## Supported File types
- *.txt, *.jpg, *.jpeg, *.png, *.webp, *.bmp, *.tif, *.tiff, *.gif*

## Instructions
1. *Select a folder containing files to rename.*
2. *Select files to rename by clicking on them.*
   - Use **Ctrl+Shift** and click for multi-select.
3. *Adjust options as needed:*
   - **Handle Duplicates:** Rename, Move to Folder, Overwrite, Skip
   - **Respect Img-Txt Pairs:** Keep image-text pairs matched when renaming
4. *Choose a preset for renaming:*
   - **Numbering:** Sequential numbering
   - **Auto-Date:** Use modified date and numbering
5. *Click **Rename Files** to apply changes.*
6. *Confirm the operation if prompted.*

## Note
- **There is no undo for this operation!**
- Use caution when renaming files.

## Hotkeys
- **Ctrl+Click:** Select/Deselect
- **Ctrl+A:** Select All
- **Ctrl+D:** Deselect All
- **Ctrl+I:** Invert Selection
- **F5:** Refresh
"""


#endregion
#region Batch Image Edit


BATCH_IMAGE_EDIT_HELP = """
# Batch Image Edit Help

A tool to apply image adjustments to many files at once. The UI is divided into three panels:
- *Left:* Image file list (select images, multi-select, preview)
- *Center:* Live preview (original and adjusted)
- *Right:* Adjustment controls (sliders + advanced options)

## Supported File types
*.jpg, .jpeg, .png, .webp, .bmp, .tif, .tiff, .jfif*

## Adjustment Controls
- **Brightness:** Adjust overall brightness (*-100 to +100*)
- **Contrast:** Enhance or reduce contrast (*-100 to +100*)
- **AutoContrast:** Automatic contrast optimization (*-100 to +100*)
- **Highlights:** Control bright areas (*-200 to +200*, *advanced: threshold*)
- **Shadows:** Control dark areas (*-200 to +200*, *advanced: threshold*)
- **Saturation:** Adjust color intensity (*-100 to +100*)
- **Vibrance:** Boost muted colors (*-100 to +100*)
- **Hue:** Shift the color spectrum (*-100 to +100*)
- **Color Temp:** Adjust warm/cool tones (*-100 to +100*)
- **Sharpness:** Enhance or soften details (*-100 to +100*, *advanced: boost*)
- **Clarity:** Enhance mid-tone contrast (*-100 to +100*, *advanced: radius*)

*Advanced options* (threshold, boost, radius) are available via the **+** button next to applicable sliders.

## Instructions
1. Select an input directory containing images (top row controls).
2. Adjust sliders in the right panel. Click value labels to type values directly.
3. Use **+** to open advanced options for fine-tuning.
4. Click **Apply!** to process the selected images.
5. Monitor progress and status in the bottom row.

## Options
- **Save To**
    - *Subfolder:* Save edited images to an "Edited Images" subfolder.
    - *Same Folder:* Save into the original folder.
- **Save As**
    - *Same Format:* Keep original file type.
    - *JPEG / PNG:* Force output format.
- **Overwrite**
    - *Always:* Overwrite originals.
    - *On Conflict:* Overwrite when filename matches; otherwise create unique name.
    - *Never:* Always create unique filenames to avoid overwriting.

## Preview & Workflow
- The center preview shows live adjustments for the selected image.
- *Right-click* the preview to temporarily show the original image.
- Adjustments are applied only when sliders differ from zero.
- Click **Reset** to return all sliders and advanced options to defaults.
- Reset individual sliders by right-clicking their handle.
- Click value labels to enter numeric values via keyboard.

## Tips
- Use the directory entry or **Browse...** to change the working folder.
- **Open** opens the current folder in File Explorer.
- **Refresh** reloads the file list from disk.
- The help button **?** opens this help window.
- Processing time depends on image size, image count, and selected adjustments.
- Only supported file types are shown and processed.
- All adjustments are *non-destructive* until you click **Apply!**.
"""


#endregion
#region Find Dupe File


FIND_DUPLICATE_FILE_HELP = """
# Find Duplicate Files Help

## Processing Modes
- **MD5 - Fast:**
    - Quick file comparison but slightly less accurate (*Recommended*)
- **SHA-256 - Slow:**
    - More thorough comparison but takes longer to process

## Duplicate Handling
- **Single Mode:**
    - Moves only the duplicate files, leaving one copy in the original location
- **Both Mode:**
    - Moves all duplicate files to the duplicates folder and groups them together

## Scanning Options
- **Images:**
    - Only scans supported image file types
  - Enables the *Move Captions* option for handling associated text files
- **All Files:**
    - Scans all files regardless of type
- **Recursive:**
    - Includes subfolders in the scan (only compares files within the same folder)
- **Move Captions:**
    - Moves associated *.txt* files when moving duplicate images

## File Menu Features
- **Select Folder:** Choose a directory to scan
- **Open Folder:** Open the current directory in File Explorer
- **Restore Moved Duplicates:** Return files to their original locations
- **Move All Duplicates Upfront:** Consolidate duplicates to the root folder
- **Delete All Duplicates:** Permanently remove duplicate files

## Options Menu Features
- **Process Mode:** Choose between MD5 (*fast*) or SHA-256 (*thorough*) comparison
- **Max Scan Size:** Set maximum file size limit for scanning (*in MB*)
- **File types to Scan:** Customize which file extensions to check
- **Recursive Scanning:** Enable or disable subfolder scanning
- **Scanning Mode:** Choose between Images-only or All Files
- **Duplication Handling:** Select Single or Both mode

## Usage Instructions

### Basic Usage
1. Select a folder using the Browse button or File menu
2. Choose your scanning options (*Images/All Files, Single/Both mode*)
3. Enable Recursive if you want to scan subfolders
4. Click *Find Duplicates* to begin scanning

### Managing Results
- Duplicates are moved to a *'_Duplicate__Files'* folder
- Use the Undo button to restore moved files
- The status bar shows progress and duplicate count

## Important Notes
- The tool uses file hash comparison for accurate duplicate detection
- Large files may take longer to process, especially in SHA-256 mode
- Recursive mode only compares files within their respective folders
- The original file structure is preserved when restoring files
- Actions like deletion and upfront moves cannot be undone
"""


#endregion
#region MyTags


MY_TAGS_HELP = """
# MyTags - Information

Curate your own tags (with optional folders) for autocomplete and quick insertion into the caption box.

## Layout

- *My Tags (left):* your library as a tree (groups and items).
- *All Tags (right):* tags aggregated from your files (toggle via Options - Show: All Tags).

## Add & Organize

- Type in the box and press Enter or click Add.
- To add inside a folder: select exactly one folder, then add; or right-click a folder -> New Tag...
- New group: right-click in the My Tags tree -> New Group...
- From All Tags: select and click "<" or right-click -> Add to MyTags.
- From elsewhere: right-click selected text or the AutoTag list -> Add to MyTags.

## Selecting & Menus

- Use Ctrl / Shift to multi-select; right-click for context actions.
- Selection tools: All, Invert, Select All Groups, Select All Tags.
- Move to...: move selected items into any folder (choose (Root) for top level).

## Insert Into Text

- *Prefix* inserts before existing text; *Append* inserts after.
- Double-click any tag to Append. Works from both panes.

## Edit, Move, Reorder

- Edit / Rename: select and click Edit or right-click -> Rename...
- Remove: deletes selected rows (deleting a group removes its contents).
- Reorder: drag with the middle mouse button (within the same parent) or use Move Up / Down.
- Drag-and-drop shows a blue placeholder; multi-select reorder is supported.

## Save & Refresh

- Save Tags writes changes to *my_tags.yaml* and updates autocomplete.
- Refresh My Tags reloads from file (unsaved changes are discarded).
- Refresh All Tags recomputes the right pane from your files.

## Options & Appearance

- Use: MyTags - enable or disable MyTags for autocomplete.
- Show: All Tags - toggle the All Tags panel.
- Hide: controls - show or hide button rows under each pane.
- MyTags Font Style - set font, size, bold, italic, underline, overstrike and colors separately for Groups and Items; Reset restores defaults; row height auto-adjusts.
- Open MyTags File... - open *my_tags.yaml* in your editor.

## Maintenance

- Cleanup MyTags removes duplicates (case-sensitive), empty or quoted tags, and empty groups. This cannot be undone.

## Notes

- Data is stored in *my_tags.yaml*. If a legacy *my_tags.csv* exists, it is imported automatically once.
- Ordering controls autocomplete priority and the default insertion order.
"""


#endregion
