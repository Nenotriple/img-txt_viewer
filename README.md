
<h1 align="center">
  <img src="https://github.com/Nenotriple/img-txt_viewer/assets/70049990/8342e197-25c7-4e78-a27d-38daa79b4330" alt="icon" width="50">
  img-txt Viewer
</h1>

<p align="center">Display an image and text file side-by-side for easy manual captioning or tagging. +Tons of features to help you work faster!</p>

<p align="center">
  <img src="https://github.com/Nenotriple/img-txt_viewer/assets/70049990/d7d9c754-aae4-4add-882d-fef105cd0531" alt="cover">
</p>



# 📝 Usage

- Prepare Your Files:
  - If you choose to include a text pair for an image, ensure they share the same basenames.
  - For example: `01.png` and `01.txt`, `02.jpg` and `02.txt`, etc.
  - Supported image types: `.png` `.jpg` `.jpeg` `.jfif` `.jpg_large` `.webp` `.bmp` `.gif`

---

Images and text files can be loaded from different folder paths. Expand the section below to learn more.

<details>
  <summary>Selecting an alternate text path:</summary>

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

</details>

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

Please see the [✨Tools](https://github.com/Nenotriple/img-txt_viewer/wiki/Tools) section of the wiki for a more comprehensive breakdown of the various features.

# 🚩 Requirements

> [!TIP]
> You don't need to worry about any requirements if using the [portable/executable](https://github.com/Nenotriple/img-txt_viewer/releases?q=executable&expanded=true) version.

**Python 3.10+**

You will need `Pillow` and `NumPy`.

 - To install Pillow: `pip install pillow`
 - To install NumPy: `pip install numpy`

Or use the included `requirements.txt` when setting up your venv.

# 📜 Version History

[v1.94 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.94)

<details>
  <summary>Click here to view release notes!</summary>

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
