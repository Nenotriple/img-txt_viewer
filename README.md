<h1 align="center"><img src="https://github.com/Nenotriple/img-txt_viewer/assets/70049990/8342e197-25c7-4e78-a27d-38daa79b4330" alt="icon" width="50"> img-txt Viewer</h1>
<p align="center">A Windows application for side-by-side image and text viewing, designed to streamline manual captioning or tagging.</p>
<p align="center"><img src="https://github.com/Nenotriple/img-txt_viewer/assets/70049990/d7d9c754-aae4-4add-882d-fef105cd0531" alt="cover"></p>


<div align="center">

![GitHub last commit](https://img.shields.io/github/last-commit/Nenotriple/img-txt_viewer)
![GitHub contributors](https://img.shields.io/github/contributors/Nenotriple/img-txt_viewer)
![GitHub repo size](https://img.shields.io/github/repo-size/Nenotriple/img-txt_viewer)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FNenotriple%2Fimg-txt_viewer&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
![GitHub all release downloads](https://img.shields.io/github/downloads/Nenotriple/img-txt_viewer/total)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/Nenotriple/img-txt_viewer)


</div>


<br>


- [📝 Usage](#-usage)
- [💡 Tips and Features](#-tips-and-features)
- [🛠️ Install](#-install)
- [🔒 Privacy Policy](#-privacy-policy)
- [📜 Version History](#-version-history)
- [✨ User Guide](https://github.com/Nenotriple/img-txt_viewer/blob/v1.96_dev/docs/UserGuide.md)
- [💾 Download](https://github.com/Nenotriple/img-txt_viewer/releases?q=executable&expanded=true)


<br>


# 📝 Usage


> [!NOTE]
>
> Prepare Your Files:
>
> - If you choose to include a text pair for an image, ensure they share the same basename.
>   - For example: `01.png, 01.txt`, `02.jpg, 02.txt`, etc.
>
> Supported image formats: `.png`, `.jpg`, `.jpeg`, `.jfif`, `.jpg_large`, `.webp`, `.bmp`, `.gif`.


Images and text files can be loaded from different folder paths. Expand the section below to learn more.


<details>


  <summary>Selecting an alternate text path...</summary>


---


By default, text files are loaded from the selected directory. To load text files from a different path:

1. Select a directory as usual.
2. Right-click the `Browse...` button and choose `Set Text File Path`.
3. When an alternate path is chosen, a blue indicator appears to the left of the directory entry. Hover over the indicator to view the selected text path.


<br>


Example folder structures:
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


<br>


# 💡 Tips and Features

- **Shortcuts:**
  - `ALT + LEFT/RIGHT`: Quickly move between img-txt pairs.
  - `SHIFT + DEL`: Move the current pair to a local trash folder.
  - `ALT`: Cycle through auto-suggestions.
  - `TAB`: Insert the highlighted suggestion.
  - `CTRL + S`: Save the current text file.
  - `CTRL + E`: Jump to the next empty text file.
  - `CTRL + R`: Jump to a random img-txt pair.
  - `CTRL + F`: Highlight all duplicate words.
  - `CTRL + Z` / `CTRL + Y`: Undo / Redo.
  - `CTRL + W`: Close the window.
  - `F1`: Toggle zoom popup.
  - `F2`: Open the Image-Grid view.
  - `F4`: Open the current image in your default editor.
  - `F5`: Open Batch Tag Edit.
  - `Middle-click`: A tag to delete it.

- **Tips:**
  - A guided setup will run on first launch to configure your autocomplete dictionaries and matching settings.
  - Insert a suggestion by clicking on it or pressing TAB.
  - Highlight matching words by selecting similar text.
  - Quickly create text pairs by loading the image and saving the text.
  - List Mode: Display tags in a list format while saving them in standard format.
  - Get `Autocomplete Suggestions` while you type using Danbooru/Anime tags, the English Dictionary, etc.
  - Match Modes: `Last Word` matches only the last word typed, `Whole String` matches the entire tag between commas.
  - Use `Match Mode: Last Word` for more natural and less strict autocomplete.
  - Use an asterisk (*) while typing for fuzzy search autocomplete suggestions.
  - Right-click the `Browse...` button to set or clear the alternate text path, allowing you to load text files from a separate folder than images.

- **Text Tools:**
  - `Search and Replace`: Find specific text and replace it with another.
  - `Prefix`: Insert text at the START of all text files.
  - `Append`: Insert text at the END of all text files.
  - `AutoTag`: Automatically tag images using ONNX vision models like `wd-v1-4-vit-tagger-v2`.
  - `Filter`: Filter pairs based on text, missing text files, and more. Works with Search and Replace, Prefix, and Append.
  - `Highlight`: Always highlight specific text.
  - `My Tags`: Add your custom tags for autocomplete suggestions.
  - `Batch Tag Edit`: Edit and manage tags with a user-friendly interface that previews changes before applying them.
  - `Create Wildcard From Captions`: Combine all image captions into one text file, with each caption set separated by a newline.
  - `Cleanup Text`: Fix typos across all text files, such as duplicate tags, extra spaces, commas, and more.

- **Image Tools:**
  - `Batch Resize Images`: Resize all images in a folder using different methods and conditions.
  - `Resize Image`: Resize the current image by exact resolution or percentage.
  - `Batch Crop Images`: Crop all images to a specified resolution.
  - `Crop Image`: Crop an image or GIF using a variety of methods and tools.
  - `Upscale Image`: Upscale images using models like RESRGAN, AnimeSharp-4x, and UltraSharp-4x. Additional models can be added to the `ncnn_models` folder.
  - `Find Duplicate Files`: Identify and separate duplicate files from your dataset.
  - `Expand`: Expand an image to a square ratio instead of cropping. Designed for images with simple backgrounds and centered subjects.
  - `Edit Image Panel`: Adjust brightness, contrast, saturation, sharpness, highlights, and shadows of the current image.

- **Other:**
  - `Batch Rename/Convert`: Rename and optionally convert image and text files, saving them sequentially with padded zeros.
  - `Thumbnail Panel`: Display thumbnails under the current image for quick navigation.
  - `Edit Image...`: Open the current image in an external editor (e.g., MS Paint).
  - `Auto-Save` Save text when switching between img-txt pairs, changing the active directory, or closing the app.
  - `Text cleanup`: (e.g., removing duplicate tags, trailing commas, extra spaces) happens automatically on save, and can be disabled from the options menu.
  - Text cleanup is optimized for CSV-format captions and can be disabled via the Clean-Text option in the menu.

For more detailed information regarding the tools and features, please refer to the [UserGuide✨](https://github.com/Nenotriple/img-txt_viewer/blob/v1.96_dev/docs/UserGuide.md)found in the repo docs.


<br>


# 🛠️Install
### Portable Setup
![Static Badge](https://img.shields.io/badge/Windows-gray)

1. Download the Windows executable from the [releases page](https://github.com/Nenotriple/img-txt_viewer/releases?q=executable&expanded=true).
2. Run the executable to launch the app.


### Python Package Setup
![Static Badge](https://img.shields.io/badge/git-gray) ![Static Badge](https://img.shields.io/badge/Windows-Python_3.10%2B-green)

1. Download the source code package from the latest [releases page](https://github.com/Nenotriple/img-txt_viewer/releases?q=executable&expanded=true).
2. Run the `Start.bat` file to automatically create and activate a virtual environment, then launch the app.
3. `Start.bat` can be used to launch the app in the future.


<br>


<details>


  <summary>Manual Python Setup...</summary>


![Static Badge](https://img.shields.io/badge/git-gray) ![Static Badge](https://img.shields.io/badge/Windows-Python_3.10%2B-green)


<br>


1. **Clone the repository:**
```
git clone https://github.com/Nenotriple/img-txt_viewer.git
```


3. **Navigate into the project directory:**
```
cd img-txt_viewer`
```


5. **Create and activate a virtual environment:**
```
python -m venv venv
venv\Scripts\activate
```


6. **Install the required dependencies:**
```
pip install -r requirements.txt
```


7. **Launch the app:**
```
python img-txt_viewer.py
```


</details>


<br>


# 🔒 Privacy Policy

**img-txt Viewer** is completely private, in every sense of the word.
- The app operates entirely on your device, ensuring your data remains solely under your control.
- **No data is collected, transmitted, or stored**, aside from a basic configuration file for app settings.
- The app functions 100% offline and never connects to external servers. **No data is ever shared or sent elsewhere.**


<br>


# 📜 Version History


Please see the [changelog](https://github.com/Nenotriple/img-txt_viewer/blob/v1.96_dev/docs/Changelog.md) for a detailed history of all changes made in each version.
