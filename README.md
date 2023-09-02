# img-txt_viewer
Display an image and text file side-by-side for easy manual caption editing.

![image](https://user-images.githubusercontent.com/70049990/220445796-ea8c9b05-3a89-46cb-81f9-e291589d6c07.png)

# Usage

Store images and text files in a single folder with identical names.

So 01.png and 01.txt and so on. The names in each pair should match, but no particular formatting is required.

.png .jpg .jpeg .webp .bmp image filetypes supported.

# Tips and Features

CTRL+S: to save the current text file.

ALT+Left/Right arrow keys: to move between img/txt pairs.

Select text with the mouse or keyboard to see duplicates.

Get autocomplete suggestions while you type using danbooru tags.

Pressing TAB inserts the selected suggestion.

Pressing TAB+Left/Right selects the autocomplete suggestion.

If the auto-save box is checked, text will be saved when moving between img/txt pairs.

If the user chooses a folder with images but no matching text files, they will be prompted to create blank text files. The blank text files will only be created for images that currently don't have any text files.

~~CTRL+Z: Sort of works for undo. (Use caution and test before saving)~~ *Disabled until improved*

# Requirements

This uses pillow for image viewing, and tkinter for the gui.

tkinter comes preinstalled with Python.

Install pillow with the following command:
```
pip install pillow
```

You will need the included "danbooru.csv" file located in the same folder as the script for autcomplete to function.

# Version History

*v1.6 changes:*

*New feature: Autocomplete using danbooru tags* 

*v1.5 changes:*

*New feature: Select and highlight duplicates*

v1.42 changes:

*Misc ui improvements*

*Now supports loading .jpeg/.webp/.bmp image types*

v1.41 changes:

*Image aspect ratio is now preserved.*

v1.4 changes:

*The user is now asked whether or not they would like to create blank text files for images that don't already have a matching text pair.*
