# img-txt_viewer
Display an image and text file side-by-side for easy manual captioning. + Tons of features to help you work faster!

![v1 83_img-txt_viewer](https://github.com/Nenotriple/img-txt_viewer/assets/70049990/0c98427f-bbe7-478c-8972-a10a7df0fd86)

# 📝 Usage

- Prepare Your Files:
  - Put each image and its matching text file in the same folder.
  - If you choose to include a text pair for an image, ensure they are located in the same folder and have identical names.
  - For example: `01.png` and `01.txt`, `02.jpg` and `02.txt`...
  - Supported image types: `.png` `.jpg` `.jpeg` `.jfif` `.jpg_large` `.webp` `.bmp`


# 💡 Tips and Features

- Shortcuts:
  - `ALT+LEFT/RIGHT`: Quickly move between img-txt pairs.
  - `SHIFT+DEL`: Send the current pair to a local trash folder.
  - `ALT`: Cycle through auto-suggestions.
  - `TAB`: Insert the highlighted suggestion.
  - `CTRL+F`: Highlight all duplicate words.
  - `CTRL+E`: Quickly jump to the next empty text file. 
  - `CTRL+S`: Save the current text file.
  - `CTRL+Z` / `CTRL+Y`: Undo/Redo.
  - `F5`: Refresh the text box.
  - `Middle-click`: A token to quickly delete it.

- Tips:
  - `Highlight duplicates` by selecting text.
  - Enable `List View` to display text in a vertical list format.
  - Enable `Big Comma Mode` for more visual separation between captions.
  - Quickly create text pairs by loading the image and saving the text.
  - `Autocomplete Suggestions` while you type using Danbooru/Anime tags, the English Dictionary, or both. 
  - `Fuzzy Search` Use an asterisk * while typing to return a broader range of suggestions.
    - For example: Typing `*lo*b` returns "<ins>**lo**</ins>oking <ins>**b**</ins>ack", and even "yel<ins>**lo**</ins>w <ins>**b**</ins>ackground"

- Text Tools:
  - `Batch Token Delete`: View all tokens in a directory as a list, and quickly delete them. (Stand alone tool)
  - `Cleanup Text`: Fix simple typos in all text files of the selected folder.
  - `Prefix Text Files`: Insert text at the START of all text files.
  - `Append Text Files`: Insert text at the END of all text files.
  - `Search and Replace`: Edit all text files at once.
  - `Filter Pairs`: Filter img-txt pairs text.
  - `Active Highlights`: Always highlight specific words.

 - Other Tools
   - `Resize Images`: Resize images using several methods and conditions. (Stand alone tool)
   - `Crop Image`: Quickly crop an image to a square or freeform ratio.
   - `Expand Current Image`: Expand an image to a square ratio instead of cropping.
   - `Find Duplicate Files`: Find and separate any duplicate files in a folder (Stand alone tool)
   - `Rename and Convert Pairs`: Automatically rename and convert files using a neat and tidy formatting.

 - Auto-Save
   - Check the auto-save box to save text when navigating between img/txt pairs or closing the window.
   - Text is cleaned when saved, so you can ignore typos such as duplicate tokens, multiple spaces or commas, missing spaces, and more.
   - `Clean text on save` Can be disabled from the options menu. *(Disabling this may have adverse effects when inserting a suggestion)*

# 🚩 Requirements

You don't need to worry about anything if you're using the [portable/executable](https://github.com/Nenotriple/img-txt_viewer/releases?q=executable&expanded=true) version.

___

You must have **Python 3.10+** installed to the system PATH.

You will need `Pillow` installed to the system.

To install Pillow, run this from the terminal: `pip install pillow`

# 📜 Version History

[v1.90 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.90)

I'm very happy to announce **img-txt_viewer is 1 year old!** 🎉🎈

I love knowing that this app has helped at least a few people work faster and easier. I want to thank everyone so much for your interest and support.

There's a lot to cover this release, so please see the [v1.90 release page](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.90) for the change notes.
