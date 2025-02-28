#endregion
#region - Batch Upscale


BATCH_UPSCALE_HELP = {
"Batch Upscale Help": "",

"Supported Filetypes:": "\n",
"Upscale Models:":      "realesr-animevideov3-x4\nRealESRGAN_General_x4_v3\nrealesrgan-x4plus\nrealesrgan-x4plus-anime\nAnimeSharp-4x\nUltraSharp-4x\n",
"Additional Models:":   "Any additional 'ESRGAN x4' models found in the 'ncnn_models' directory will be added to the list of available upscale models.\n",
"Upscale Strength:":    "Adjusts the blend between the original and upscaled images (0% yields the original, 100% applies the full upscaling effect).\n",
"Batch Processing:":    "Process all eligible images in a directory\n",
"Auto Output Naming:":  "When enabled, output filenames and directories are generated automatically relative to the input path.\n",
"Additional Note:":     "The tool always performs an initial 4x upscaling before applying your selected resizing factor.\nAdjusting the upscale factor does not affect the quality or performance of the upscale process.\n",

"Usage Instructions:":
    "Single Mode:\n"
    "  1. Select an image file via the 'Browse...' button, or by selecting it from the file list.\n"
    "  2. Adjust settings (Upscale Model, Upscale Factor, Upscale Strength) as desired.\n"
    "  3. Click 'Upscale' to process the image.\n\n"
    "Batch Mode:\n"
    "  1. Ensure 'Batch Mode' is enabled.\n"
    "  2. Select an input directory via the 'Browse...' button containing the images you wish to upscale.\n"
    "  3. Click 'Upscale' to begin processing all supported images.\n"
    "  4. Use the 'Cancel' button to stop batch processing at any time.\n\n",
}


#endregion
#region - Batch Tag Edit


BATCH_TAG_EDIT_HELP = {
"Batch Tag Edit Help": "",

"Technical Note:":
    "- This tool is designed to work with CSV-like text files. Both commas and periods are treated as caption delimiters.\n"
    "- It may not work as expected with certain combinations of characters, text or their formatting.\n"
    "- You should always make backups of your text files before saving any changes.\n",

"Instructions:":
    "1) Use the filter or sort options to refine the File and Tag Lists.\n"
    "   - You can input multiple filter values separated by commas.\n"
    "2) Select the tags you want to modify from the Tag-List.\n"
    "3) Choose an edit option:\n"
    "   - **Edit**: Enter the new text to replace the selected tags.\n"
    "   - **Delete**: The selected tags will be deleted.\n"
    "4) Pending changes will be displayed in the Tag-List.\n"
    "5) Click *'Save Changes'* to apply any pending changes to the text files. This action cannot be undone, so make sure to backup your files.\n",

"Tips:":
    "- *Adjust* the working directory in the *'Tagger'* tab to work with different sets of text files.\n"
    "- Use the context menu in the listbox to quickly copy, delete, or edit tags.\n"
    "- Use the *'Revert'* options to undo pending changes made to the selected tags, or use the *'Reset'* buttons to reset any changes or filters.",
}


#endregion
#region -  Batch Resize Images


BATCH_RESIZE_IMAGES_HELP = {
"Batch Resize Help":        "",

"Supported Filetypes:":
    ".jpg, .jpeg, .png, .webp, .bmp, .tif, .tiff\n",

"Resize to Resolution:":
    "Resize to a specific width and height ignoring aspect ratio.\n\n(The following 'Resize to' options preserve aspect ratio)",
"Resize to Percentage:":
    "Resize the image by a percent scale.",
"Resize to Width:":
    "Target the image width and resize it.",
"Resize to Height:":
    "Target the image height and resize it.",
"Resize to Shorter side:":
    "Resize the shorter side of the image.",
"Resize to Longer side:":
    "Resize the longer side of the image.\n",

"Quality:":
    "Used to control the output quality of JPG and WEBP images. A higher value results in a higher quality output. (Ignored for PNG)\n",

"Upscale and Downscale:":
    "Resize the image to the new dimensions regardless of whether they're larger or smaller than the original dimensions.",
"Upscale Only:":
    "Resize the image if the new dimensions are larger than the original dimensions.",
"Downscale Only:":
    "Resize the image if the new dimensions are smaller than the original dimensions.\n",

"Filetype:":
    "Select 'AUTO' to output with the same filetype as the input image. Alternatively, choose a specific filetype to force all images to be saved with the chosen type.\n",

"Use Output Folder:":
    "When enabled, a new folder will be created in the image directory called 'Resize Output' where images will be saved.",
"Overwrite Files:":
    "When disabled, conflicting files will have '_#' append to the filename. If enabled, files with the same basename will be overwritten.",
"Save PNG Info:":
    "When enabled, this option will automatically save any PNG chunk info to the resized output if saving as PNG. If converting from PNG to another type, then a text file will be created containing the PNG info.",
"Convert Only:":
    "When enabled, the app will convert images to the selected filetype without resizing them. Resize settings will be ignored.",
}


#endregion
#region -  Batch Rename


BATCH_RENAME_HELP = {
"Batch Rename Help": "",

"Supported Filetypes:": ".txt, .jpg, .jpeg, .png, .webp, .bmp, .tif, .tiff, .gif\n",

"Instructions:":
    "1. Select a folder containing files to rename.\n"
    "2. Select files to rename by clicking on them.\n"
    "   • Use Ctrl+Shift and click to for multi-select.\n"
    "3. Adjust options as needed:\n"
    "   • Handle Duplicates: Rename, Move to Folder, Overwrite, Skip\n"
    "   • Respect Img-Txt Pairs: keep img-txt pairs matched when renaming\n"
    "4. Choose a preset for renaming:\n"
    "   • Numbering: Sequential numbering\n"
    "   • Auto-Date: Use modified date and numbering\n"
    "5. Click 'Rename Files' to apply changes.\n"
    "6. Confirm the operation if prompted.\n",

"Note:":
    "• There is no undo for this operation!\n"
    "• Use caution when renaming files.\n\n",

"Hotkeys:":
    "• Ctrl+Click: Select/Deselect\n"
    "• Ctrl+A: Select All\n"
    "• Ctrl+D: Deselect All\n"
    "• Ctrl+I: Invert Selection\n"
    "• F5: Refresh\n\n",
}


#endregion
#region -  Find Dupe File


FIND_DUPLICATE_FILE_HELP = {
"Find Duplicate Files Help": "",

"Processing Modes:":
    "**MD5 - Fast:**\n"
    "  Quick file comparison but slightly less accurate *(Recommended)*\n"
    "**SHA-256 - Slow:**\n"
    "  More thorough comparison but takes longer to process\n\n",

"Duplicate Handling:":
    "**Single Mode:**\n"
    "  Moves only the duplicate files, leaving one copy in the original location\n"
    "**Both Mode:**\n"
    "  Moves all duplicate files to the duplicates folder and groups them together\n\n",

"Scanning Options:":
    "**Images:**\n"
    "  Only scans supported image file types\n"
    "  Enables the 'Move Captions' option for handling associated text files\n"
    "**All Files:**\n"
    "  Scans all files regardless of type\n"
    "**Recursive:**\n"
    "  Includes subfolders in the scan *(only compares files within the same folder)*\n"
    "**Move Captions:**\n"
    "  Moves associated .txt files when moving duplicate images\n\n",

"File Menu Features:":
    "**Select Folder:** Choose a directory to scan\n"
    "**Open Folder:** Open the current directory in File Explorer\n"
    "**Restore Moved Duplicates:** Return files to their original locations\n"
    "**Move All Duplicates Upfront:** Consolidate duplicates to the root folder\n"
    "**Delete All Duplicates:** Permanently remove duplicate files\n\n",

"Options Menu Features:":
    "**Process Mode:** Choose between MD5 *(fast)* or SHA-256 *(thorough)* comparison\n"
    "**Max Scan Size:** Set maximum file size limit for scanning *(in MB)*\n"
    "**Filetypes to Scan:** Customize which file extensions to check\n"
    "**Recursive Scanning:** Enable/disable subfolder scanning\n"
    "**Scanning Mode:** Choose between Images-only or All Files\n"
    "**Duplication Handling:** Select Single or Both mode\n\n",

"Usage Instructions:":
    "**Basic Usage:**\n"
    "  1. Select a folder using the Browse button or File menu\n"
    "  2. Choose your scanning options *(Images/All Files, Single/Both mode)*\n"
    "  3. Enable Recursive if you want to scan subfolders\n"
    "  4. Click 'Find Duplicates' to begin scanning\n\n"
    "**Managing Results:**\n"
    "  • Duplicates are moved to a *'_Duplicate__Files'* folder\n"
    "  • Use the Undo button to restore moved files\n"
    "  • The status bar shows progress and duplicate count\n\n",

"Important Notes:":
    "• The tool uses file hash comparison for accurate duplicate detection\n"
    "• Large files may take longer to process, especially in SHA-256 mode\n"
    "• Recursive mode only compares files within their respective folders\n"
    "• The original file structure is preserved when restoring files\n"
    "• Actions like deletion and upfront moves cannot be undone\n\n",

}
