# img-txt_viewer
Show an image and its corresponding text file side by side to make editing text captions easier.

![image](https://user-images.githubusercontent.com/70049990/220445796-ea8c9b05-3a89-46cb-81f9-e291589d6c07.png)

Store images and text files in a single folder with identical names.

So 01.png and 01.txt and so on. The names in each pair should match, but no particular formatting is required.

.png and .jpg supported.

__________

Use CTRL + S to save the current text file.

Use ALT + Left/Right arrow keys to move between img/txt pairs.

CTRL + Z Sort of works. (use caution and test before saving)

If the auto-save box is checked, text will be saved when moving between img/txt pairs.

If the user chooses a folder with images but no matching text files, they will be prompted to create blank text files. The blank text files will only be created for images that currently don't have any text files.

__________

This uses pillow for image viewing, and tkinter for the gui.

__________

_v1.41 changes:_

Image aspect ratio is now preserved.

_v1.4 changes:_

*The user is now asked whether or not they would like to create blank text files for images that don't already have a matching text pair.*

_v1.3 changes:_

*window minsize now (675, 560) - prevents ui squish.*

*txt files now created for images without them.*

_v1.2 changes:_

*Minor typos fixed.*

_v1.1 changes:_

*Fixed trailing space/new line when saving.*
