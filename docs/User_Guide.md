img-txt_viewer comes with many tools that help ease the process of manually creating a training dataset, as well as some others that may be helpful outside of this space.


# Index

 **✂️Shortcuts**
- [`ALT+LEFT/RIGHT`](#altleftright) - Quickly move between img-txt pairs.
- [`SHIFT+DEL`](#shiftdel) - Send the current pair to a local trash folder.
- [`ALT`](#alt) - Cycle through auto-suggestions.
- [`TAB`](#tab) - Insert the highlighted suggestion.
- [`CTRL+S`](#ctrls) - Save the current text file.
- [`CTRL+E`](#ctrle) - Jump to the next empty text file.
- [`CTRL+R`](#ctrlr) - Jump to a random img-txt pair.
- [`CTRL+F`](#ctrlf) - Highlight all duplicate words.
- [`CTRL+Z / CTRL+Y`](#ctrlz--ctrly) - Undo/Redo.
- [`CTRL+W`](#ctrlw) - Close the window.
- [`F1`](#f1) - Toggle zoom popup.
- [`F2`](#f2) - Open the Image-Grid view.
- [`F4`](#f4) - Open the current image in your default editor.
- [`F5`](#f5) - Open Batch Tag Edit.
- [`Middle-click`](#middle-click) - Middle-click a tag to delete it.

 **📜Text Tools**
- [`Search and Replace`](#search-and-replace) - Find specific text and replace it with another.
- [`Prefix`](#prefix) - Insert text at the START of all text files.
- [`Append`](#append) - Insert text at the END of all text files.
- [`AutoTag`](#autotag) - Automatically tag images using ONNX vision models.
- [`Filter`](#filter) - Filter pairs based on text, missing text files, and more.
- [`Highlight`](#highlight) - Always highlight specific text.
- [`My Tags`](#my-tags) - Add your custom tags for autocomplete suggestions.
- [`Batch Tag Edit`](#batch-tag-edit) - Edit and manage tags with a user-friendly interface.
- [`Create Wildcard From Captions`](#create-wildcard-from-captions) - Combine all captions into one text file.
- [`Cleanup Text`](#cleanup-text) - Fix typos across all text files.

 **📷Image Tools**
- [`Batch Resize Images`](#batch-resize-images) - Resize all images using different methods and conditions.
- [`Resize Image`](#resize-image) - Resize the current image by exact resolution or percentage.
- [`Batch Crop Images`](#batch-crop-images) - Crop all images to a specified resolution.
- [`Crop Image`](#crop-image) - Crop an image or GIF using various methods and tools.
- [`Upscale Image`](#upscale-image) - Upscale images using models like RESRGAN, AnimeSharp-4x, and UltraSharp-4x.
- [`Find Duplicate Files`](#find-duplicate-files) - Identify and separate duplicate files.
- [`Expand`](#expand) - Expand images to square ratio for simple backgrounds.
- [`Edit Image Panel`](#edit-image-panel) - Adjust image properties like brightness, contrast, etc.

 **📦Other Tools**
- [`Batch Rename/Convert`](#batch-rename-convert) - Rename and convert files sequentially with padded zeros.
- [`Thumbnail Panel`](#thumbnail-panel) - Display thumbnails for quick navigation.
- [`Edit Image...`](#edit-image) - Open images in external editor.
- [`Auto-Save`](#auto-save) - Save text automatically when switching pairs.
- [`Image-Grid`](#image-grid) - Open the Image-Grid view.


---

<!--####################################################################################################-->
<!--####################################################################################################-->
<!--####################################################################################################-->

<br>

## ✂️Shortcuts

### ALT+LEFT/RIGHT
#### *(Navigate between img-txt pairs)*

With the primary text box in focus, press `ALT+LEFT` or `ALT+RIGHT` to move between img-txt pairs.

`ALT+LEFT` Moves back to the previous image.

`ALT+RIGHT` Moves forward to the next image.

---

### SHIFT+DEL
#### *(Delete the current pair)*

Press `SHIFT+DEL` to move the displayed image and text file to a trash folder.

The trash folder is created in the same directory as the image file.

When closing the app, you'll be asked if you want to permanently delete the trash folder.

Also available via the Tools menu and the image right-click context menu.

If the trash folder already contains a file with the same name, you will be prompted to overwrite it or cancel the operation.

---

### ALT
#### *(Cycle through autocomplete suggestions)*

With the primary text box in focus, press `LEFT-ALT` or `RIGHT-ALT` to move the autocomplete selector left or right.

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

Also available via the `Save` button.

---

### CTRL+E
#### *(Jump to the next empty text file)*

With the primary text box in focus, press `CTRL+E` to jump to the next empty text file from the current index position.

Also available via the index entry right-click context menu.

---

### CTRL+R
#### *(Jump to a random img-txt pair)*

With the primary text box in focus, press `CTRL+R` to jump to a random img-txt pair.

Also available via the index entry right-click context menu.

---

### CTRL+F
#### *(Highlight all duplicate words)*

With the primary text box in focus, press `CTRL+F` to highlight any duplicate words.

All matching words will be highlighted with the same color, but colors are randomized each time the hotkey is pressed.

This matches any duplicate string of text (minimum of 3 characters) and not just tags or words. Words shorter than 3 characters or words that appear only once will not be highlighted.

Example text: "this cute **dog**, happy **dog**gy, small **dog**"

Also available via the primary text box right-click context menu.

---

### CTRL+Z / CTRL+Y
#### *(Undo/Redo)*

With the primary text box in focus, press `CTRL+Z` to undo the last action or `CTRL+Y` to redo the last undo.

*(Limited to keyboard and autocomplete actions)*

Also available via the primary text box right-click context menu.

---

### Popup Zoom
#### *(Toggle zoom popup)*

The Popup Zoom feature allows you to create a small popup window beside the mouse that displays a zoomed view of the image underneath.

#### Shortcuts:
- **F1**: Press `F1` to toggle the zoom popup.
- **Mouse Wheel**: Scroll to adjust the zoom factor or popup size.
  - Hold `Shift` while scrolling to adjust the popup size.

---

### F2
#### *(Open the Image-Grid view)*

The Image Grid feature allows you to view and interact with a grid of images.

See the [Image-Grid](#image-grid) section for more information.

**Shortcut:** With the primary text box in focus, press `F2` to open the Image Grid view.

---

### F4
#### *(Open the current image in your default editor)*



- **Set Default Image Editor:**
    1. Open the application.
    2. Navigate to the `Options` menu.
    3. Select `Set Default Image Editor`.
    4. Choose the executable file of your preferred image editor.

Once you have set your default image editor, you can easily open the current image in it by pressing `F4` with the image in focus.

- **Tips:**
  - Ensure that the path to the image editor is correctly set to avoid any issues when opening images.
  - You can change the default image editor at any time by repeating the steps above.

---

### F5
#### *(Open Batch Tag Edit)*

With the primary text box in focus, press `F5` to open Batch Tag Edit.

See the [Batch Tag Edit](#batch-tag-edit) section for more information.

---

### Middle-click
#### *(Middle-click a tag to delete it)*

- **Use:**
  1. **Hover Over the Tag**: Move your mouse cursor over the tag you want to delete.
  2. **Middle-Click**: Press the `Middle-Click` mouse button to delete the entire tag.

- **Tips:**
  - The entire comma-separated value will be deleted.
  - Ensure that the text cleaning feature is enabled for the deletion to work.

---

<!--####################################################################################################-->
<!--####################################################################################################-->
<!--####################################################################################################-->

<br>

## 📜Text Tools

### Search and Replace
#### *(Find and replace text across all text files)*

Use this tool to search for a string of text across all text files in the selected directory.

If a match is found, it will be replaced exactly with the given text.

- **Use:**
  1. Search for: `the big brown dog`
  2. Replace with: `the big red dog`

This will replace all instances of `the big brown dog` with `the big red dog`.

- **Tips:**
  - Ensure that the search string is entered exactly as it appears in the text files.
  - Use the "Regex" option for advanced search patterns using regular expressions.
  - If a filter is applied, only text files that match the filter will be affected.
  - The "Undo" button can revert the last search and replace action if needed.

> [!NOTE]
> - When using `Search and Replace`, `Prefix`, or `Append`, a backup of the text files will be made and saved to the working directory before making any changes.
> - Pressing `Undo` will restore the text backup. `Undo` only creates one history of backups, and using another tool will erase the previous backup.

---

### Prefix
#### *(Insert text at the START of all text files)*

Use this tool to prefix all text files in the selected directory with the entered text.

This means that the entered text will appear at the start of each text file.

- **Use:**
  1. Enter the text you want to insert at the start of all text files in the provided entry field.
  2. Press the `Go!` button or hit `Enter` to apply the prefix to all text files.
  3. A backup of the text files will be created before making any changes.

- **Tips:**
  - Ensure the text you want to prefix is entered exactly as you want it to appear.
  - If a filter is applied, only text files that match the filter will be affected.
  - The "Undo" button can revert the last prefix action if needed.

> [!NOTE]
> - When using `Search and Replace`, `Prefix`, or `Append`, a backup of the text files will be made and saved to the working directory before making any changes.
> - Pressing `Undo` will restore the text backup. `Undo` only creates one history of backups, and using another tool will erase the previous backup.

---

### Append
#### *(Insert text at the END of all text files)*

Use this tool to append all text files in the selected directory with the entered text.

This means that the entered text will appear at the end of each text file.

- **Use:**
  1. Enter the text you want to insert at the end of all text files in the provided entry field.
  2. Press the `Go!` button or hit `Enter` to apply the append to all text files.
  3. A backup of the text files will be created before making any changes.

- **Tips:**
  - Ensure the text you want to append is entered exactly as you want it to appear.
  - If a filter is applied, only text files that match the filter will be affected.
  - The "Undo" button can revert the last append action if needed.

> [!NOTE]
> - When using `Search and Replace`, `Prefix`, or `Append`, a backup of the text files will be made and saved to the working directory before making any changes.
> - Pressing `Undo` will restore the text backup. `Undo` only creates one history of backups, and using another tool will erase the previous backup.

---

### AutoTag
#### *(Automatically tag images using ONNX vision models)*

Automatically tag images using ONNX vision models.

---

### Filter
#### *(Filter pairs based on text, missing text files, and more)*

This tool will filter all img-txt pairs based on the provided text.

Enter any string of text to display only img-txt pairs containing that text.


Use ` + ` to include multiple strings when filtering. *(Note the spaces!)*

Use `!` before the text to exclude any pairs containing that text.

Examples:

`dog` (shows only pairs containing the text dog)

`!dog` (removes all pairs containing the text dog)

`!dog + cat` (remove dog pairs, display cat pairs)

---

### Highlight
#### *(Always highlight specific text)*

Enter the text you want to highlight each time you move to a new img-txt pair.

Use ` + ` to highlight multiple strings of text.

Example: `dog + cat`

---

### My Tags
#### *(Add your custom tags for autocomplete suggestions)*

Use this text box to quickly edit the `my_tags.csv` file, allowing you to easily add tags to the autocomplete dictionary.

- Tags near the top of the list have a higher priority than lower tags.
- Start any line with `###` to create a comment.
- Save and Refresh:
  - Save: Commit your changes to the `my_tags.csv` file.
  - Refresh: Refresh the loaded autocomplete dictionary with your saved changes, or refresh the text box if you've made changes outside the app.
    - Always save first, then refresh to fully commit your changes and update autocomplete.

---

### Batch Tag Edit
#### *(Edit and manage tags with a user-friendly interface)*

Edit and manage tags with a user-friendly interface.

---

### Create Wildcard From Captions
#### *(Combine all captions into one text file)*

Combine all captions into one text file.

---

### Cleanup Text
#### *(Fix typos across all text files)*

Via the `Tools Menu`.

This operation will clean all text files from typos like: duplicate tags, extra commas, extra spaces, trailing commas and spaces, commas without spaces, and more.

This is also performed whenever saving text and the option `Cleaning Text on Save` is enabled.
So if you write all your tags with the app and the option enabled, it won't do anything.

Example Cleanup:

From: ` ,dog,solo,  ,happy  ,,`

To: `dog, solo, happy`

- Full list of cleanup operations:
  - Remove duplicate tags:
    - Input: `apple apple banana banana`, Output: `apple banana`
  - Replace a period followed by a space with a comma and a space:
    - Input: `Hello. World.`, Output: `Hello, World`
  - Replace one or more spaces surrounded by optional commas with a single comma:
    - Input: `Hello , World`, Output: `Hello,World`
  - Replace multiple spaces with a single space:
    - Input: `Hello   World`, Output: `Hello World`
  - Replace multiple commas with a single comma:
    - Input: `Hello,,,World`, Output: `Hello,World`
  - Replace multiple backslashes with a single backslash:
    - Input: `Hello \\(World\)`, Output: `Hello \(World\)`
  - Remove removes leading and trailing commas from the end of the text:
    - Input: `,Hello,World,`, Output: `Hello,World`
  - Remove removes leading and trailing spaces from the end of the text:
    - Input: ` Hello World `, Output: `Hello World`
  - Add a space after a comma if it’s not already there:
    - Input: `Hello,World`, Output: `Hello, World`

---

<!--####################################################################################################-->
<!--####################################################################################################-->
<!--####################################################################################################-->

<br>

## 📷Image Tools

### Batch Resize Images
#### *(Resize all images using different methods and conditions)*

Via the `Tools Menu`.

This stand-alone tool allows you to resize all images in a folder using various methods and conditions.

Supported Filetypes: `jpg`, `jpeg`, `png`, `webp`, `bmp`, `tif`, `tiff`

- Resize To:
  - *Resize to Resolution*: Resize to a specific width and height, ignoring aspect ratio.
  - *Resize to Percentage*: Resize the image by a percent scale.
  - *Resize to Width*: Target the image width and resize it.
  - *Resize to Height*: Target the image height and resize it.
  - *Resize to Shorter Side*: Resize the shorter side of the image.
  - *Resize to Longer Side*: Resize the longer side of the image.

- Resize Condition:
  - *Upscale and Downscale*: Resize the image to the new dimensions, regardless of whether they're larger or smaller than the original dimensions.
  - *Upscale Only*: Resize the image if the new dimensions are larger than the original dimensions.
  - *Downscale Only*: Resize the image if the new dimensions are smaller than the original dimensions.

- Filetype:
  - Select 'AUTO' to output with the same filetype as the input image.
  - Alternatively, choose a specific filetype (JPG, PNG, or WEBP) to force all images to be saved with the chosen type.
  - JPG and WEBP are always saved with the highest quality possible.

- Use Output Folder:
  - If enabled, a folder `Resize Output` will be created, and the resized images will output there.
  - If disabled, the resized images will output to the selected directory.

- Overwrite Files:
  - if enabled, images will be overwritten when a filename conflict occurs.
  - if disabled, conflicting files will have '_#' appended to the filename.

---

### Resize Image
#### *(Resize the current image by exact resolution or percentage)*

Via the `Tools Menu` or the `image right-click context menu`.

Resize the currently displayed image using an exact resolution or by a percent scale.

Lock the aspect ratio to easily edit the width or height values without squishing or stretching the image.

Unlock the aspect ratio to allow entering a value that squishes or stretches the image.

For JPG and WEBP, you can adjust the output quality from 10%, to 100%.

You can choose between the following resize methods: `Lanczos`, `Nearest`, `Bicubic`, `Hamming`, `Bilinear`, and `Box`. Lanczos is the recommended method.

As you adjust the various settings, you can see the new dimensions and image size update in real time.

---

### Batch Crop Images
#### *(Crop all images to a specified resolution)*

Via the `Tools Menu`.

Crop all images to a specified resolution.

---

### Crop Image
#### *(Crop an image or GIF using various methods and tools)*

Via the `Tools Menu` or the `image right-click context menu`.

Crop the currently displayed image in a pop-up window.

- Drag with the mouse to define the area that will be cropped, and then press `Space` or use the `Right-Click Context Menu` to save the crop.
- Click anywhere outside the crop area to clear the rectangle.
- Double-Click to quickly create a 512x512, or 1024x1024 crop rectangle. (Automatic based on image size)
- Enable `Freeform Crop` from the `Right-Click Context Menu` to define a non-square rectangle.
- Each crop will have `_crop##` appended to the filename.
  - Saving multiple crops of the same image will increment the filename like this: `_crop01`, `_crop02`, etc.

---

### Upscale Image
#### *(Upscale images using models like RESRGAN, AnimeSharp-4x, and UltraSharp-4x)*

Via the `Tools Menu` or the `image right-click context menu`.

Upscale the currently displayed image using [R-ESRGAN](https://github.com/xinntao/Real-ESRGAN)

- Upscale Model:
  - realesr-animevideov3-x4 (default)
  - RealESRGAN_General_x4_v3
  - realesrgan-x4plus
  - realesrgan-x4plus-anime

- Upscale Factor: 1x, 2x, 3x, 4x

 The current size and new size are displayed in the UI after selecting an Upscale Factor.

---

### Find Duplicate Files
#### *(Identify and separate duplicate files)*

Via the `Tools Menu`.

This stand-alone tool allows you to find all duplicate files in a folder, or subfolder* and move them out for easy sorting.
It works by generating and comparing a hash value for each image. You can use either `MD5`, or `SHA-256`. MD5 is faster and generally shouldn't result in false positive detections *(99.9% of the time, it's fine)*. SHA-256 is slower but should be much more resistant to false positives.

- Duplicate files will be moved to a `_Duplicate__Files` folder within the scanned directory.
- Single or Both:
  - Single: Choosing this option will move *all but one* of the found duplicates to the `_Duplicate__Files` folder.
  - Both: Choosing this option will move *all* of the found duplicates to the `_Duplicate__Files` folder.
- Images or All Files:
  - Images: Choosing this option will only check image files for duplicate matches, ignoring other files.
  - All Files: Choosing this option will check all files for duplicate matches.
- Recursive*:
  - Enable this option to scan subfolders.
  - NOTE: This only compares files within the same subfolder, not across all scanned folders.
- Set Max Scan Size:
  - Use this option to limit the maximum size of scanned files, ignoring files that are larger. (Default=2048 MB)
- Set Filetypes to Scan:
  - Use this option to limit the scanned files to only those listed, ignoring everything else.

- **Undo**
  - Using undo will restore all moved images back to their original file paths.

---

### Expand
#### *(Expand images to square ratio for simple backgrounds)*

Via the `Tools Menu` or the `image right-click context menu`.

Expand the currently displayed image to a square resolution without cropping.

This tool works by expanding the shorter side to a square resolution divisible by 8 and stretching the pixels around the long side to fill the space.

- For example:
  - A portrait image would expand like this: input=`||`, output=`| |`
  - A portrait image would expand like this: input=`| |`, output=`||`

After expanding, a new image will be saved in the same format and directory as the original, with `_ex` appended to the filename.

This tool works great for images with solid or very smooth gradient backgrounds. It's not intended to be useful for images without simple backgrounds.

---

### Edit Image Panel
#### *(Adjust image properties like brightness, contrast, etc.)*

Adjust image properties like brightness, contrast, etc.

---

<!--####################################################################################################-->
<!--####################################################################################################-->
<!--####################################################################################################-->

<br>

## 📦Other Tools

### Batch Rename/Convert
#### *(Rename and convert files sequentially with padded zeros)*

Via the `Tools Menu`.

This will rename and convert all images and text* files in the selected directory. **(Only rename text files)*

Files are saved to a `Renamed Output` folder, nothing is overwritten.

Images are converted to `JPG` type (except for `GIF` files), and then each img-txt pair is renamed in sequential order using padded zeros to ensure 5 characters.

Example input pair: `aH15520.jpg`, `AH15520.txt`

Example output pair: `00001.jpg`, `00001.txt`

---

### Thumbnail Panel
#### *(Display thumbnails for quick navigation)*

Display thumbnails for quick navigation.

---

### Edit Image...
#### *(Open images in external editor)*

Open images in external editor.

---

### Auto-Save
#### *(Save text automatically when switching pairs)*

Save text automatically when switching pairs.

---

### Image-Grid
#### *(Open the Image-Grid view)*

- **Open:**
  - **Shortcut:** With the primary text box in focus, press `F2` to open the Image Grid view.

- **Features**
    - **Thumbnail Size:** Adjust the size of the thumbnails using the size slider at the bottom of the grid. The sizes range from small to large.
    - **Auto-Close:** Toggle the auto-close feature to automatically close the Image Grid after selecting an image.
    - **Filtering:** Use the filtering options to display all images, only paired images (images with text pairs), or only unpaired images (images without text pairs).
    - **Extra Filtering:** Enable extra filtering to filter images by resolution, aspect ratio, file size, filename, file type, or tags.
    - **Load More:** If there are more images than currently displayed, use the "Load More" button to load additional images. (250 images are loaded at a time)

- **Tips**
    - **Dragging the Window:** Click and drag the title bar to move the Image Grid window around.
    - **Closing the Window:** Click the "X" button at the top right or press `Escape` to close the window.
    - **Image Information:** Hover over an image to see detailed information, including the image index, filename, file size, and resolution.
    - **Refresh:** Use the "Refresh" button to reload the image grid, especially useful if you’ve added or removed images or altered the text pairs.
    - **Load All:** Use the "Load All" button to load all images in the folder. Note that this might be slow if there are many images.

---