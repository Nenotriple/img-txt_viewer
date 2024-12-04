# Workpad

Notes, code reference, ideas, etc.


<!--###########################################################################-->


## Window Size on Resize

Prints Tkinter window dimensions on resize:

```python
root.bind("<Configure>", lambda event: print(f"Window size (W,H): {event.width},{event.height}") if event.widget == root else None)
```

Example Output: `Window size (W,H): 800,600`


<!--###########################################################################-->


## Widget Size on Resize

Prints Tkinter widget dimensions on resize:

```python
widget.bind("<Configure>", lambda event: print(f"Widget size (W,H): {event.width},{event.height}"))
```

Example Output: `Widget size (W,H): 200,150`


<!--###########################################################################-->


## Caller Function Name

Prints the name of the function that called the current function:

```python
import inspect

def function_a():
    function_b()

def function_b():
    caller_name = inspect.stack()[1].function
    print(f"Called by function: {caller_name}")
```

Example Output: `Called by function: function_a`


<!--###########################################################################-->


## Timing a Function

Measures the execution time of a function.

`:.2f` formats the `elapsed_time` (float) variable, to two decimal places.

```python
import time

def my_function():
    start_time = time.time()
    # ...Code to measure...
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
```

Example Output: `Elapsed time: 0.50 seconds`


<!--###########################################################################-->



# ImgTxtViewer - Ideas

## General:
- Organize the various alt-UIs into a tabbed tkinter Notebook widget.


<!-- Tools / Features --#########################################################################-->
## New Tool - Group img-txt Pairs
Create an interface to view one image at a time and easily select a folder to send the image to. The interface consists of:
- **Image and Text Pair (left)**:
  - The image is displayed with the text below it.
  - The text is un-editable and shown in a small widget.
- **Treeview Display (right)**:
  - Displays the image name, text, and folder name.
  - Shows the pairs and their respective folders.
- **User-Defined Folder Buttons (bottom)**:
  - An Entry widget to input the folder name and an "Add" button to create a new folder button.
  - Right-click on a folder button to rename or delete it.
Both the image and text pair (if present) are moved to the selected folder. Before starting, define at least two folders. The working directory (where the pairs are initially stored) can be used as the first folder.


## New Tool - Consolidate Similar Tags
Consolidate similar tags based on the following rules: `If a tag is a substring of another, combine them`
- Two modes are supported:
  - **Descriptive**: Combine into the longest possible tag.
    - Example 1: `["hair", "long hair", "black hair"]` → `long black hair`
    - Example 2: `["shirt", "black shirt", "t-shirt"]` → `black t-shirt`
  - **Concise**: Combine into the shortest possible tag.
    - Example 1: `["hair", "long hair", "black hair"]` → `hair`
    - Example 2: `["shirt", "black shirt", "t-shirt"]` → `shirt`


## New Feature - Weighted Tags
- Allow the user to quickly wrap tags in the following brackets: `()`, `[]`, `{}`, `""`, `''`
- When a tag is selected and the user presses one of the following keys `(`, `[`, `{`, `"`, `'`, the tag is wrapped in the corresponding brackets.


<!-- Notebook Tabs --############################################################################-->
## Filter Tab
- Add a listbox to display all filtered img-txt pairs.
- Allow the user to select item(s) from the listbox and:
  - Prefix, Append, or Replace tags.
  - Move to another folder.
  - Delete img-txt pairs.


## MyTags Tab
- Show all tags in a list, with a count of how many times each tag is used.
- Allow the user to quickly insert tags from "ALL" into "MyTags".
- Allow the user to quickly insert tags from "All" into the text box.


## Thumbnail Panel
- It's currently not possible to navigate backwards from the first image, or forwards from the last image by clicking the thumbnails.
  - Show a button at the start and end to go to the first and last image.


## AutoTag Tab
- Add a "Presets" button to quickly save and load tagging presets.


## Filter Tab
- Add more filtering options like:
  - `Resolution`, `Aspect ratio`, `File size`, `File name`:
    - Is equal to `=`
    - Is not equal to `!=`
    - Is greater than `>`
    - Is less than `<`
    - Similar to `*`
  - `File type`:
    - Is equal to `=`
    - Is not equal to `!=`
  - `Tags`:
    - Contains `a,b`
    - Does not contain `!`
    - Starts with `a,b`
    - Ends with `a,b`
    - Similar to `*`
