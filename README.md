# img-txt_viewer
Display an image and text file side-by-side for easy manual captioning. + Tons of features to help you work faster!

![v1 91_img-txt_viewer](https://github.com/Nenotriple/img-txt_viewer/assets/70049990/d7d9c754-aae4-4add-882d-fef105cd0531)

# 📝 Usage

- Prepare Your Files:
  - If you choose to include a text pair for an image, ensure they share the same basenames.
  - For example: `01.png` and `01.txt`, `02.jpg` and `02.txt`, etc.
  - Supported image types: `.png` `.jpg` `.jpeg` `.jfif` `.jpg_large` `.webp` `.bmp` `.gif`

---

Images and text files can be loaded from different folder paths.

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
  - `Batch tag Delete`: View all tag in a directory as a list, and quickly delete them. (Stand alone tool)
  - `Prefix Text Files`: Insert text at the START of all text files.
  - `Append Text Files`: Insert text at the END of all text files.
  - `Search and Replace`: Edit all text files at once.
  - `Filter Pairs`: Filter pairs based on matching text, blank or missing txt files, and more.
  - `Active Highlights`: Always highlight specific text.
  - `My Tags`: Quickly add you own tags to be used as autocomplete suggestions.
  - `Cleanup Text`: Fix simple typos in all text files of the selected folder.

 - Other Tools
   - `Batch Resize Images`: Resize a folder of images using several methods and conditions. (Stand alone tool)
   - `Resize Image`: Resize a single image.
   - `Batch Crop Images`: Crop a folder of images to an exact size, resizing if needed.
   - `Crop Image`: Quickly crop an image to a square or freeform ratio.
   - `Upscale Image`: Upscale an image using `realesrgan-ncnn-vulkan`
   - `Expand Current Image`: Expand an image to a square ratio instead of cropping.
   - `Find Duplicate Files`: Find and separate any duplicate files in a folder (Stand alone tool)
   - `Rename and Convert Pairs`: Automatically rename and convert files using a neat and tidy formatting.

 - Auto-Save
   - Check the auto-save box to save text when navigating between img/txt pairs or closing the window, etc.
   - Text is cleaned when saved, so you can ignore typos such as duplicate tokens, multiple spaces or commas, missing spaces, and more.
   - `Clean text on save` Can be disabled from the options menu.

# 🚩 Requirements

You don't need to worry about anything if you're using the [portable/executable](https://github.com/Nenotriple/img-txt_viewer/releases?q=executable&expanded=true) version.

___

**Python 3.10+**

You will need `Pillow` and `NumPy`.

 - To install Pillow: `pip install pillow`
 - To install NumPy: `pip install numpy`

Or use the included `requirements.txt` when setting up your venv.

# 📜 Version History

[v1.92 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.92)


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
