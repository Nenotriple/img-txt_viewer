# img-txt_viewer
Display an image and text file side-by-side for easy manual caption editing.

![v1 67_img-txt_viewer](https://github.com/Nenotriple/img-txt_viewer/assets/70049990/09cb402a-db35-4b15-8ff2-828234b397e0)

# Usage

Store images and text files in a single folder with identical names.
- So 01.png and 01.txt and so on. The names in each pair should match, but no particular formatting is required.

Supported image types:
- .png .jpg .jpeg .webp .bmp

# Tips and Features

Hotkeys
- CTRL+S: to save the current text file.
- CTRL+Z / CTRL+Y: Undo/Redo.
- ALT+Left/Right arrow keys quickly moves between img/txt pairs.
- Pressing TAB inserts the selected suggestion.
- Presing ALT cycles though suggestions.

Tips
- Select text with the mouse or keyboard to see duplicates.
- If the auto-save box is checked, text will be saved when moving between img/txt pairs.
- If the user chooses a folder with images but no matching text files, they will be prompted to create blank text files. The blank text files will only be created for images that currently don't have any text files.
- Click the image to zoom in.
- Get autocomplete suggestions while you type using danbooru tags.


# Requirements

This uses pillow for image viewing, and tkinter for the ui.

tkinter comes preinstalled with Python.

Install pillow with the following command:
```
pip install pillow
```

The autocomplete function requires the included "danbooru.csv" file to be located in the same folder as the script.

# Version History

v1.68 changes:

- *New: Previous/Next buttons are now side-by-side.*
- *New/Fixed: Choosing suggestions is now down with ALT. This prevents suggestions from being inserted erronesly.*
- *Fixed: Inserting suggestions is now possible anywhere in the text field, not just the end of the text box.*
- *Fixed: Duplicates will now be highlighted when selected with the keyboard.*
- *Fixed: Commas are now ignored when matching highlighted duplicates.*

v1.67 changes:

- *New: Select image viewing size. Small, medium, large, etc.*

v1.66 changes:

- *New: Image now scales with window size.*
- *New: Zoom has been removed for now.*

v1.65 changes:

- *New: Zoom into images by clicking them.*
- *New: Loop around the image index when hitting the end/start.*
- *New: Quickly jump to a specific image.*

v1.63 changes:

- *Autocomplete now returns much better suggestions.*
- *Further improvements to typo correction.*
