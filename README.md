# img-txt_viewer
Display an image and text file side-by-side for easy caption editing.

![image](https://user-images.githubusercontent.com/70049990/220445796-ea8c9b05-3a89-46cb-81f9-e291589d6c07.png)

# Usage

Store images and text files in a single folder with identical names.

So 01.png and 01.txt and so on. The names in each pair should match, but no particular formatting is required.

.png and .jpg supported.

# Tips and Features

CTRL + S: to save the current text file.

ALT + Left/Right arrow keys: to move between img/txt pairs.

CTRL + Z: Sort of works for undo. (use caution and test before saving)

If the auto-save box is checked, text will be saved when moving between img/txt pairs.

If the user chooses a folder with images but no matching text files, they will be prompted to create blank text files. The blank text files will only be created for images that currently don't have any text files.

# Requirements

This uses pillow for image viewing, and tkinter for the gui.

tkinter comes preinstalled with Python.

Install pillow with the following command:
```
pip install pillow
```

# Version History

v1.42 changes:

*Misc ui improvements*

*Now supports loading .jpeg/.webp/.bmp image types*

v1.41 changes:

*Image aspect ratio is now preserved.*

v1.4 changes:

*The user is now asked whether or not they would like to create blank text files for images that don't already have a matching text pair.*

v1.3 changes:

*window minsize now (675, 560) - prevents ui squish.*

*txt files now created for images without them.*

v1.2 changes:

*Minor typos fixed.*

v1.1 changes:

*Fixed trailing space/new line when saving.*
