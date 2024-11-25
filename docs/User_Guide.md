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
- [`Batch Upscale`](#batch-upscale) - Upscale images using models like RESRGAN, AnimeSharp-4x, and UltraSharp-4x.
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
  - Open the application.
  - Navigate to the `Options` menu.
  - Select `Set Default Image Editor`.
  - Choose the executable file of your preferred image editor.

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

- **Usage:**
  - **Hover Over the Tag**: Move your mouse cursor over the tag you want to delete.
  - **Middle-Click**: Press the `Middle-Click` mouse button to delete the entire tag.

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

- **Usage:**
  - Search for: `the big brown dog`
  - Replace with: `the big red dog`

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

- **Usage:**
  - Enter the text you want to insert at the start of all text files in the provided entry field.
  - Press the `Go!` button or hit `Enter` to apply the prefix to all text files.
  - A backup of the text files will be created before making any changes.

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

- **Usage:**
  - Enter the text you want to insert at the end of all text files in the provided entry field.
  - Press the `Go!` button or hit `Enter` to apply the append to all text files.
  - A backup of the text files will be created before making any changes.

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

- **Usage:**
  - Select the image you want to tag.
  - Open the AutoTag tool from the toolbar below the text box, or by the right-click image context menu.
  - The tool will automatically analyze the image and generate tags based on the ONNX vision model.

- **Tips:**
  - Ensure that the ONNX models are placed in the `onnx_models` directory.
  - The default model used is `wd-v1-4-vit-tagger-v2`, but you can add additional models to the `onnx_models` folder.
  - Download additional models from [Hugging Face](https://huggingface.co/SmilingWolf).
  - Place models in subfolders within the `onnx_models` directory. The subfolder name will be used as the model name.
  - Each model subfolder should contain a `model.onnx` file and a `selected_tags.csv` file.
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

This tool will filter all img-txt pairs based on the provided text.

Enter any string of text to display only img-txt pairs containing that text.

- **Example input:**
  - `dog` *(shows only pairs containing the text dog)*
  - `!dog` *(removes all pairs containing the text dog)*
  - `!dog + cat` *(remove dog pairs, display cat pairs)*

- **Tips:**
  - Use ` + ` to include multiple strings/tags when filtering.
  - Use `!` before the text to exclude any pairs containing that text.
  - Use the `Regex` checkbox to enable regular expression filtering.
  - Use the `Empty` checkbox to show only empty text files or images without a text pair.
  - Press the `Go!` button or hit `Enter` in the filter entry box to apply the filter.
  - Press the `Clear` button to remove any applied filters.

---

### Highlight
#### *(Always highlight specific text)*

Enter the text you want to highlight each time you move to a new img-txt pair.

- **Example input:**
  - `dog` *(highlight the word dog)*
  - `dog + cat` *(highlight both dog and cat)*

- **Tips:**
  - Use ` + ` to include multiple strings/tags when highlighting.
  - Use the `Regex` checkbox to enable regular expression highlighting.
  - Press the `Go!` button or hit `Enter` in the highlight entry box to apply the highlight.
  - Press the `Clear` button to remove any applied highlights.

---

### Font Settings
#### *(Adjust the font size and line height)*

The Font Settings allow you to customize the appearance of your text by adjusting the font size and line height. This can help improve readability and make your text more visually appealing.

- **Usage:**
  - Navigate to the Font tab from the toolbar.
  - Use the sliders or input fields to adjust the font size and line height to your preference.
  - Changes will be applied in real-time, so you can see the effect immediately.

---

### My Tags
#### *(Add your custom tags for autocomplete suggestions)*

Use this section to quickly edit the `my_tags.csv` file, allowing you to easily add tags to the autocomplete dictionary. Additionally, you can quickly insert tags into the primary text box.

- **Usage:**
  - Open MyTags tab from the toolbar.
  - Add or modify tags as needed, placing higher priority tags at the top.
  - Save your changes to refresh the autocomplete dictionary.

- **Features:**
  - **Add Tags**: Enter a tag in the input box and press `Add` or hit Enter to add it to the list.
  - **Edit Tags**: Select a tag, click `Edit`, modify it in the input box, and press Enter to save changes.
  - **Remove Tags**: Select one or more tags from the list and click `Remove` to delete them.
  - **Prefix Tags**: Select a tag, click `Prefix`, and the tag will be inserted at the start of the text box.
  - **Append Tags**: Select a tag, click `Append`, and the tag will be inserted at the end of the text box.
  - **Move Tags**: Select a tag and use `Move Up` or `Move Down` to change its position/priority in the list.
  - **Context Menu**: Right-click on a tag to quickly access options like `Prefix`, `Append`, `Edit`, `Remove`, `Move Up`, and `Move Down`.
  - **Save Tags**: Click `Save Tags` to save your changes to the `my_tags.csv` file.
  - **Use MyTags**: Toggle the `Use MyTags` checkbox to enable or disable the custom tags in the autocomplete suggestions.

- **Tips:**
  - Go to `Options` > `Open MyTags File...` to quickly access the `my_tags.csv` file.
  - Organize your tags by priority, placing the most important tags at the top of the list.
  - Regularly save and refresh to ensure your changes are up-to-date and reflected in the autocomplete suggestions.

---

### Batch Tag Edit
#### *(Edit and manage tags with a user-friendly interface)*

The Batch Tag Edit tool allows you to quickly edit and manage tags across all files in a folder with an intuitive user interface.

**Features:**

- **Tag Listbox:** View all unique tags from your files in a scrollable list. You can select multiple tags using standard selection methods (Shift+Click, Ctrl+Click).

- **Info Display:** At the top, see real-time counts of:
  - Total unique tags
  - Visible tags (after filtering)
  - Selected tags
  - Pending deletions
  - Pending edits

- **Sort Tags:**
  - **Sort By:** Choose to sort tags by "Frequency" (how often a tag appears), "Name" (alphabetical order), or "Length" (number of characters).
  - **Reverse Order:** Check this option to reverse the sorting order.

- **Filter Tags:**
  - **Filter Options:**
    - `Tag`: Display tags containing the input text.
    - `!Tag`: Display tags that do not contain the input text.
    - `==`: Display tags exactly matching the input text.
    - `!=`: Display tags not matching the input text.
    - `<`: Display tags shorter than the given length.
    - `>`: Display tags longer than the given length.
  - **Multiple Values:** Except for `<` and `>`, you can input multiple values separated by commas.
  - **Apply and Reset:** Use "Apply" to apply the filter and "Reset" to clear any filters or pending changes.

- **Tag Selection Shortcuts:**
  - **All:** Select all tags in the list.
  - **Invert:** Invert the current selection.
  - **Clear:** Clear the current selection.
  - **Revert Sel:** Revert changes made to the selected tags.
  - **Revert All:** Revert all tags to their original state (reset).
  - **Copy:** Copy the selected tags to the clipboard.

- **Tag Editing:**
  - **Edit Tags:** Right-click on selected tags to edit them. You can rename tags or mark them for deletion.
  - **Delete Tags:** Mark selected tags for deletion across all files.
  - **Save Changes:** After making edits or deletions, click "Save Changes" to apply them to all files.

- **Help and Tips:**
  - **Help Button:** Click "?" to toggle help messages and tooltips throughout the interface.
  - **Tooltips:** Hover over buttons and labels to see helpful tooltips.

- **Keyboard Shortcuts:**
  - **F5:** Close the Batch Tag Edit window.
  - **Ctrl+C:** Copy selected tags to the clipboard.

**Usage Tips:**

- **Efficient Tag Management:** Use filtering and sorting to quickly find and manage specific tags.
- **Multiple Edits:** You can select multiple tags and apply edits or deletions to all of them at once.
- **Preview Changes:** Before saving, use the info display to review pending deletions and edits.
- **Undo Changes:** If you change your mind, use "Revert Sel" or "Revert All" before saving to undo changes.

---

### Create Wildcard From Captions
#### *(Combine all captions into one text file)*

Use this tool to combine all image captions into a single text file. Each set of image captions will be separated by a newline. The output file will be saved in the selected directory with a filename like `combined_captions.txt`.

- **Usage:**
  - Select the directory containing the image-text pairs.
  - Open: `Tools` > `Batch Operations` > select `Create Wildcard From Captions...`
  - The tool will process all text files in the selected directory and combine their contents into one text file.

---

### Cleanup Text
#### *(Fix typos across all text files)*

Via the `Tools` menu.

This operation will clean all text files from typos like: duplicate tags, extra commas, extra spaces, trailing commas and spaces, commas without spaces, and more.

This is also performed whenever saving text and the option `Cleaning Text on Save` is enabled.
So if you write all your tags with the app and the option enabled, it won`t do anything.

Example Cleanup:

From: `dog,, ,dog,solo,  ,happy  ,,`

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
  - Remove leading and trailing commas from the end of the text:
    - Input: `,Hello,World,`, Output: `Hello,World`
  - Remove leading and trailing spaces from the end of the text:
    - Input: ` Hello World `, Output: `Hello World`
  - Add a space after a comma if it’s not already there:
    - Input: `Hello,World`, Output: `Hello, World`

- **Usage:**
  - **Initiate Cleanup**: Open: `Tools` > `Batch Operations` > select `Cleanup All Text Files...`
  - **Confirmation**: A confirmation dialog will appear explaining the cleanup process and showing an example. Confirm to proceed.
  - **Processing**: The tool will process all text files, applying the cleanup operations listed above.
  - **Completion**: A success message will appear once the cleanup is complete.

- **Tips:**
  - Enable `Cleaning Text on Save` to automatically clean text files whenever they are saved.
  - If `Cleaning Text on Save` is enabled, the cleanup tool will not perform any operations.
  - Regular use of the cleanup tool helps maintain clean and readable text files.

---

<!--####################################################################################################-->
<!--####################################################################################################-->
<!--####################################################################################################-->

<br>

## 📷Image Tools

### Batch Resize Images
#### *(Resize all images using different methods and conditions)*

Via the `Tools` > `Batch Operations` Menu.

This tool allows you to resize all images in a folder using various methods and conditions.

**Supported Filetypes**: `jpg`, `jpeg`, `png`, `webp`, `bmp`, `tif`, `tiff`

- **Resize To**:
  - *Resize to Resolution*: Resize to a specific width and height, ignoring aspect ratio.
    - *(The following `Resize To` options preserve aspect ratio)*
  - *Resize to Percentage*: Resize the image by a percentage scale.
  - *Resize to Width*: Target the image width and resize it while preserving aspect ratio.
  - *Resize to Height*: Target the image height and resize it while preserving aspect ratio.
  - *Resize to Shorter Side*: Resize the shorter side of the image while preserving aspect ratio.
  - *Resize to Longer Side*: Resize the longer side of the image while preserving aspect ratio.

- **Resize Condition**:
  - *Upscale and Downscale*: Resize the image to the new dimensions, regardless of whether they`re larger or smaller than the original dimensions.
  - *Upscale Only*: Resize the image if the new dimensions are larger than the original dimensions.
  - *Downscale Only*: Resize the image if the new dimensions are smaller than the original dimensions.

- **Quality**:
  - Used to control the output quality of JPG and WEBP images.
  - A higher value results in higher quality output.
  - This setting is ignored for PNG images, as they are lossless.

- **Filetype**:
  - Select `AUTO` to output with the same filetype as the input image.
  - Alternatively, choose a specific filetype (JPG, PNG, or WEBP) to force all images to be saved with the chosen type.

- **Use Output Folder**:
  - If enabled, a folder `Resize Output` will be created, and the resized images will output there.
  - If disabled, the resized images will output to the selected directory.

- **Overwrite Files**:
  - If enabled, images will be overwritten when a filename conflict occurs.
  - If disabled, conflicting files will have `_#` appended to the filename.

- **Save PNG Info**:
  - If enabled, this option will automatically save any PNG chunk info to the resized output if saving as PNG.
  - If converting from PNG to another type, a text file will be created containing the PNG info.

- **Selecting a Directory**:
  - Use the `Browse...` button to select the folder containing the images you wish to resize.
  - Alternatively, enter the path directly into the entry field and press Enter.

- **Adjusting Resize Settings**:
  - Choose the desired `Resize To` mode based on how you want to resize your images.
  - Enter the appropriate dimensions, percentage, or size according to the selected mode.
  - Ensure the values entered are valid numbers to avoid errors.

- **Quality Setting**:
  - Adjust the `Quality` slider to balance between image quality and file size for JPG and WEBP images.
  - Higher values result in better image quality but larger file sizes.

- **Handling Metadata**:
  - Enable `Save PNG Info` to preserve any metadata present in PNG images when resizing or converting.
  - If converting from PNG to another format, the PNG metadata will be saved as a text file.

- **Processing Images**:
  - Click the `Resize` button to start the resizing process.
  - The tool will process all supported image files in the selected directory.

- **Viewing Resized Images**:
  - After resizing, navigate to the output folder to view the resized images.
  - If `Use Output Folder` is enabled, the images will be in the `Resize Output` folder.

- **Help and Information**:
  - Click the `?` button to toggle the help window, which provides detailed information about the tool`s features and options.

---

### Resize Image
#### *(Resize the current image by exact resolution or percentage)*

Accessible via the `Tools` menu or the `image right-click context menu`.

The **Resize Image** tool allows you to resize the currently displayed image either by specifying exact dimensions (in pixels) or by scaling it by a percentage.

- **Resize Condition:**
  - Choose between resizing by **Pixels** or **Percentage** using the radio buttons at the top of the window.

- **Width and Height Entries:**
  - Adjust the **Width** and **Height** values as needed.
  - **Locked Aspect Ratio:** Enable the **Locked** checkbox to maintain the original aspect ratio. When enabled, changing one dimension automatically updates the other.
  - **Unlocked Aspect Ratio:** Uncheck the **Locked** checkbox to adjust width and height independently, allowing you to stretch or squish the image.

- **Quality Adjustment:**
  - For **JPG** and **WEBP** formats, adjust the output quality from **10%** to **100%** using the quality slider.

- **File Type Selection:**
  - Choose the output file type from **JPG**, **PNG**, or **WEBP** using the dropdown menu.

- **Resize Method:**
  - Select the resizing method from the following options:
    - **Lanczos** (recommended)
    - **Nearest** (Fast, Great for pixel art)
    - **Bicubic**
    - **Hamming**
    - **Bilinear**
    - **Box**

- **Real-time Updates:**
  - As you adjust settings, the new dimensions and estimated image size are updated in real time.

- **Tips:**
  - When enlarging images, using a higher quality setting and the **Lanczos** method helps preserve image clarity.
  - Reducing the quality percentage can significantly decrease the file size, which is beneficial for web use.
  - **Right-click** on the **Width** or **Height** entry fields to reset the value to the original dimension.
  - **Overwrite Option:** Decide whether to overwrite the original file or save a new version.

---

### Batch Crop Images
#### *(Crop all images to a specified resolution)*

Via the `Tools` menu.

Crop and resize a batch of images to a specified resolution.

- **Usage:**
  - **Open the Batch Crop Images tool** from the `Tools` menu.
  - **Enter the desired Width and Height** (in pixels) for your images.
  - **Choose the Crop Anchor point** from the dropdown menu. This determines which part of the image is kept when cropping.
  - **Click the "Crop" button** to start processing.

- **Anchor Points:**
   - **Center**: Crops around the center of the image.
   - **North**: Crops from the top center.
   - **South**: Crops from the bottom center.
   - **East**: Crops from the right center.
   - **West**: Crops from the left center.
   - **North-East**: Crops from the top-right corner.
   - **North-West**: Crops from the top-left corner.
   - **South-East**: Crops from the bottom-right corner.
   - **South-West**: Crops from the bottom-left corner.

- **Tips:**
  - Cropped images will be saved in a new folder named `cropped_images` within the current directory. Filenames will include the new resolution (e.g., `image_800x600.jpg`).
  - Images smaller than the target resolution will be automatically resized before cropping.

---

### Crop Image
#### *(Crop an image or GIF using various methods and tools)*

Via the `Tools` menu or the `image right-click context menu`.

Crop the currently displayed image using the **CropUI** tool.

---

**CropUI** provides a user-friendly interface to crop images and GIFs.

- **Selection Modes**:
  - **Free Selection**: Click and drag to create a custom selection of any size.
  - **Fixed Aspect Ratio**: Maintain a specific aspect ratio when creating or resizing the selection. Choose from common ratios or enter custom values.
  - **Fixed Dimensions**: Set exact width and height for the selection area.

- **Selection Adjustment**:
  - **Move Selection**: Click and drag inside the selection to reposition it.
  - **Resize Selection**: Use the handles around the selection rectangle to adjust its size.
  - **Keyboard Shortcuts**:
    - **Arrow Keys**: Move the selection by 1 pixel.
    - **Shift + Arrow Keys**: Move the selection by 10 pixels.
  - **Mouse Wheel Shortcuts**:
    - **Scroll**: Adjust the selection size by scrolling up or down.
    - **Shift + Scroll**: Adjust the selection width by scrolling up or down.
    - **Ctrl + Scroll**: Adjust the selection height by scrolling up or down.

- **Guidelines**:
  - **Rule of Thirds**: Overlay guidelines to help compose your image according to the rule of thirds.
  - **Center Lines**: Display vertical and horizontal center lines for alignment.
  - **Diagonal Lines**: Show diagonal guidelines for balanced composition.

- **Image Transformation**:
  - **Rotate**: Rotate the image by 90-degree increments.
  - **Flip**: Flip the image horizontally or vertically.

- **GIF Support**:
  - **Frame Extraction**: Extract all frames from a GIF.
  - **Frame Navigation**: Navigate through frames using the thumbnail timeline, allowing you to crop any frame of a GIF.

- **Tips:**
  - **Creating a Selection**:
    - Double-click on the image to create a selection that encompasses the entire image.
    - Click and drag to create a custom selection area.
    - Use the selection handles to adjust size and shape.
  - **Fixed Selection**:
    - Enable fixed aspect ratio or dimensions for precise cropping needs.
    - Enter specific values or select from predefined options.
  - **Guidelines**:
    - Toggle guidelines to assist with image composition.
    - Combine different guidelines for more precise alignment.
  - **Cropping the Image**:
    - After adjusting the selection, click the **Crop** button to apply the crop.
    - Choose to overwrite the original image or save as a new file.
  - **Navigating Images**:
    - Use the **Previous** and **Next** buttons to cycle through images in the current directory.
  - **Working with GIFs**:
    - Extract frames for individual editing.
    - View and select frames using the thumbnail timeline.
  - **Help and Support**:
    - Access the **Help** menu for detailed instructions and tips on using CropUI.



---

### Batch Upscale
#### *(Upscale images using models like RESRGAN, AnimeSharp-4x, and UltraSharp-4x)*

...

---

### Upscale Image
#### *(Upscale images using models like RESRGAN, AnimeSharp-4x, and UltraSharp-4x)*

Via the `Tools` menu or the `image right-click context menu`.

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

Via the `Tools` menu.

This stand-alone tool allows you to find all duplicate files in a folder, or subfolder* and move them out for easy sorting.
It works by generating and comparing a hash value for each image. You can use either `MD5`, or `SHA-256`. MD5 is faster and generally shouldn`t result in false positive detections *(99.9% of the time, it`s fine)*. SHA-256 is slower but should be much more resistant to false positives.

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

Via the `Tools` menu or the `image right-click context menu`.

Expand the currently displayed image to a square resolution without cropping.

This tool works by expanding the shorter side to a square resolution divisible by 8 and stretching the pixels around the long side to fill the space.

- For example:
  - A portrait image would expand like this: input=`||`, output=`| |`
  - A portrait image would expand like this: input=`| |`, output=`||`

After expanding, a new image will be saved in the same format and directory as the original, with `_ex` appended to the filename.

This tool works great for images with solid or very smooth gradient backgrounds. It`s not intended to be useful for images without simple backgrounds.

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

Via the `Tools` menu.

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