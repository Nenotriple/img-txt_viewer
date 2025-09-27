"""About Window for img-txt Viewer."""


#region Imports


# Standard Library
import os
import webbrowser


# Standard Library - GUI
import tkinter as tk
from tkinter import ttk, Frame, scrolledtext, Label, TclError


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as Tip
from main.scripts import PyTrominos


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region AboutWindow


class AboutWindow:
    def __init__(self, parent: 'Main', root: 'tk.Tk', icon):
        self.parent = parent
        self.root = root
        self.icon_img = icon
        self.icon_path = None
        self.info_headers, self.info_content = self._create_header_text()


    def _create_header_text(self):
        headers = [
            " Quick Start",
            " Tagger Shortcuts",
            " Tagger Tips",
            " Tagger Toolbar",
            " Main Toolbar",
            " Other"
        ]
        content = [
            # General
            "Welcome to img-txt Viewer!\n"
            "This application is designed to help you quickly manage and tag image datasets.\n"
            "Supported formats: PNG, JPG, JPEG, JFIF, JPG_LARGE, WEBP, BMP, GIF, MP4\n"
            "To get started, select a directory containing image-text pairs using the `Browse...` button.",

            # Tagger Shortcuts
            "⦁ ALT + LEFT/RIGHT: Quickly move between img-txt pairs.\n"
            "⦁ SHIFT + DEL: Move the current pair to a local trash folder.\n"
            "⦁ ALT: Cycle through autocomplete suggestions.\n"
            "⦁ TAB: Insert the highlighted suggestion.\n"
            "⦁ CTRL + S: Save the current text file.\n"
            "⦁ CTRL + E: Jump to the next empty text file.\n"
            "⦁ CTRL + R: Jump to a random img-txt pair.\n"
            "⦁ CTRL + F: Open Find and Replace.\n"
            "⦁ CTRL + Z / CTRL + Y: Undo / Redo.\n"
            "⦁ CTRL + W: Close the window.\n"
            "⦁ F1: Toggle Image-Grid view.\n"
            "⦁ F2: Toggle zoom popup.\n"
            "⦁ F4: Open the current image in your default editor.\n"
            "⦁ Middle-click on a tag to delete it.\n",

            # Tagger Tips
            "A guided setup will run on first launch to configure your autocomplete dictionaries and matching settings.\n"
            "  ⦁ Go to 'Options > Reset Settings' to re-run the setup.\n\n"
            "Autocomplete suggestions are based on your current dictionary and Suggestions options.\n"
            "  ⦁ Go to 'Options > Autocomplete' or click the (☰) menu button on the suggestion row to change the settings.\n"
            "  ⦁ Use an asterisk (*) while typing for fuzzy search autocomplete suggestions.\n"
            "  ⦁ Match Modes: 'Last Word' matches only the last word typed, 'Whole String' matches the entire tag between commas.\n"
            "  ⦁ Use 'Match Mode: Last Word' for more natural and less strict autocomplete.\n\n"
            "⦁ Highlight matching words by selecting similar text.\n"
            "⦁ Quickly create text pairs via 'Edit > Create Blank Text Files' or by loading the image and saving the text.\n"
            "⦁ List Mode: Display tags in a list format while saving them in standard format.\n"
            "⦁ Right-click the 'Browse...' button to set or clear the alternate text path, allowing you to load text files from a separate folder than images.\n"
            "⦁ Right-click the displayed image to access various options and tools.\n\n"
            "Use the 'View' menu above the displayed image to access additional options like:\n"
            "  ⦁ Image Grid (F1): Display images in a grid format for easier navigation.\n"
            "  ⦁ Zoom (F2): Toggle zoom popup for the displayed image.\n"
            "  ⦁ Thumbnail Panel: Toggle thumbnail panel visibility.\n"
            "  ⦁ Edit Panel: Toggle image edit panel which allows you to edit image brightness, contrast, and other properties.\n",

            # Tagger Toolbar
            "A variety of tools are available in the bottom toolbar below the text box. Expand the toolbar or click the (?) button for more information.\n\n"
            "Search and Replace (S&R):\n"
            "  ⦁ Search for specific text across all listed files and replace it with another.\n\n"
            "Prefix:\n"
            "  ⦁ Insert text at the START of all listed text files.\n\n"
            "Append:\n"
            "  ⦁ Insert text at the END of all listed text files.\n\n"
            "AutoTag:\n"
            "  ⦁ Automatically tag images using ONNX vision models like `wd-v1-4-vit-tagger-v2`.\n"
            "  ⦁ Can also be triggered via image right-click context menu.\n\n"
            "Filter:\n"
            "  ⦁ Filter pairs based on input text.\n"
            "  ⦁ Effectively alters the listed files, allowing other tools like S&R, Prefix, and Append to work with the filtered results.\n"
            "  ⦁ Can filter just 'empty' text files.\n"
            "  ⦁ Supports multi string matching and exclusion patterns using (+) and (!).\n\n"
            "Highlight:\n"
            "  ⦁ Always highlight specific text if it exists in the displayed text.\n"
            "  ⦁ Can be used to quickly locate important or repeated tags/words.\n"
            "  ⦁ Supports multi string matching using (+).\n\n"
            "Font:\n"
            "  ⦁ Adjust font size and style for better readability.\n\n"
            "My Tags:\n"
            "  ⦁ Add your own custom tags for autocomplete suggestions.\n"
            "  ⦁ This tool also displays all tags in the dataset and allows you to quickly add them to your own list or to the current tag file.\n"
            "  ⦁ Saved to 'my_tags.csv'.\n\n"
            "Stats:\n"
            "  ⦁ View statistics about your dataset, including text/image/video statistics, most common words, a list of all tags, and more.\n",

            # Main Toolbar
            "The main toolbar gives quick access to image and text tools. These use the same directory as set in the Tagger UI. For Tag-Editor and Crop, set a directory in Tagger UI first.\n\n"
            "Tag-Editor:\n"
            "  ⦁ Display and edit image tags. Tags are listed with their occurrences.\n"
            "  ⦁ Changes are pending until you apply save them.\n"
            "  ⦁ Respects Tagger UI 'Filter' settings, just remember to refresh the view.\n\n"
            "Crop:\n"
            "  ⦁ Crop images to a specific aspect ratio or resolution.\n"
            "  ⦁ Can also extract GIFs into individual frames or crop them.\n"
            "  ⦁ Use 'Auto Fixed Selection' mode to automatically select the closest aspect ratio based on image dimensions.\n\n"
            "Batch Upscale:\n"
            "  ⦁ Upscale image(s) using realesrgan-ncnn-vulkan.\n"
            "  ⦁ Supports batch processing for multiple images at once.\n"
            "  ⦁ Adjust upscale factor (e.g., 0.5, 2.0, 4.0) to control the final output size.\n"
            "  ⦁ Adjust upscale strength to control the level of blending between original and upscaled images.\n"
            "  ⦁ Add your own RESRGAN NCNN models (.bin and .param) to the 'models/ncnn_models' folder.\n\n"
            "Batch Resize:\n"
            "  ⦁ Resize image(s) using various methods and conditions.\n"
            "  ⦁ See the (?) help documentation for more details.\n\n"
            "Batch Rename:\n"
            "  ⦁ Used to cleanup file names and quickly rename using a couple presets.\n"
            "  ⦁ Choose between Numbered or Dated naming presets.\n\n"
            "Find Duplicates:\n"
            "  ⦁ Used to identify and manage duplicate files in your dataset.\n"
            "  ⦁ Uses simple hashing techniques to detect duplicates quickly.\n"
            "  ⦁ Can be used for images or any other files.\n"
            "  ⦁ Supports a variety of options, see the (?) help documentation for more details.\n\n",

            # Other
            "⦁ 'File > Zip Dataset' Compress all images and text files into a single ZIP archive.\n\n"
            "⦁ 'Edit > Cleanup All Text Files' This operation will clean all text files from typos like:\n"
            "  ⦁ Duplicate tags, Extra commas, Extra spaces, trailing commas/spaces, commas without spaces, and more.\n\n"
            "⦁ 'Tools > Batch Operations > Batch Crop Images' Crop all listed images to a specific resolution and crop anchor.\n\n"
            "⦁ 'Tools > Batch Operations > Create Wildcard From Captions' Combine all captions into one text file, each files content added to a new line.\n\n"
            "Text Options:\n"
            "  ⦁ Clean-Text: perform text cleanup when saving.\n"
            "  ⦁ Auto-Delete Blank Files: Automatically delete blank text files when saving.\n"
            "  ⦁ Highlight Selection: When selecting text, other matching text will be highlighted.\n"
            "  ⦁ Add Comma After Tag: Automatically insert a comma after inserting a suggested tag.\n"
            "  ⦁ List View: Display text in a list format for easier navigation. (expects csv like format)\n"
            "  ⦁ Auto-Save: Automatically save changes made to text files when navigating between pairs.\n\n"
            "Loading Order:\n"
            "  ⦁ Choose between Name, File Size, Date Created, Extension, Last Access Time, Last Time Written.\n"
            "  ⦁ Ascending or Descending order.\n\n"
            "Autocomplete:\n"
            "  ⦁ Dictionary: Select the appropriate dictionary(s) for text suggestions. Multiple selections are allowed, but due to performance reasons, the resulting suggestions may be limited.\n"
            "  ⦁ Threshold: Essentially widens the range of text considered for suggestions, allowing for more flexible matching. (slower==more flexible)\n"
            "  ⦁ Quantity: Control the number of suggestions returned.\n"
            "  ⦁ Match Mode: Controls how text is matched against the selected dictionary(s) and typed content.\n"
            "    ⦁ Match Whole String: Match all text between the commas in the cursor selection.\n"
            "    ⦁ Match Last Word: Only the current text under the cursor is used for autocomplete.\n\n"
            "⦁ 'Options > Restore Last Path': Restore the last used file path when launching the app.\n"
            "⦁ About: Display this information.\n"

            "\n\nFor more detailed information regarding the tools and features, look for (?) buttons throughout the interface or view the `docs/User_Guide.md` file in the repo.\n\n"
            "github.com/Nenotriple/img-txt_viewer\n"
        ]
        return headers, content


#endregion
#region Methods


    def create_about_window(self):
        """Create the About window."""
        self._initialize_window()
        self._set_icon()
        self._create_textbox()
        self._create_bottom_row()
        self._center_window()
        self.about_window.focus_force()


    def _initialize_window(self):
        self.about_window = tk.Toplevel(self.root)
        self.about_window.title("About - img-txt Viewer")
        self.about_window.geometry("850x650")
        self.about_window.minsize(675, 300)
        self.about_window.protocol("WM_DELETE_WINDOW", self.close_about_window)
        self.github_url = "https://github.com/Nenotriple/img-txt_viewer"


    def _set_icon(self):
        self.icon_path = os.path.join(self.parent.app_root_path, "icon.ico")
        try:
            self.about_window.iconbitmap(self.icon_path)
        except TclError:
            pass


    def _create_textbox(self):
        self.info_text = scrolledtext.ScrolledText(self.about_window, padx=5, pady=5)
        self.info_text.pack(expand=True, fill='both')
        # Insert headers and sections. Add an extra blank line after each section for visual separation.
        for header, section in zip(self.info_headers, self.info_content):
            self.info_text.insert("end", header + "\n", "header")
            self.info_text.insert("end", section + "\n\n", "section")
        # Tag styling:
        self.info_text.tag_config("header", font=("Segoe UI", 9, "bold"), spacing3=8)  # spacing3 = extra space after header
        self.info_text.tag_config("section", font=("Segoe UI", 9), lmargin1=10, lmargin2=20, spacing1=2, spacing3=6, rmargin=8)
        # Additional tag for bullet lines (increase indentation for lines that begin with the bullet char).
        self.info_text.tag_config("bullet", lmargin1=22, lmargin2=36)
        total_lines = int(self.info_text.index('end-1c').split('.')[0])
        for line_no in range(1, total_lines + 1):
            line_start = f"{line_no}.0"
            line_end = f"{line_no}.0 lineend"
            line_text = self.info_text.get(line_start, line_end)
            if line_text.lstrip().startswith("⦁") or line_text.lstrip().startswith("•"):
                self.info_text.tag_add("bullet", line_start, line_end)
        # Final widget config
        self.info_text.config(state='disabled', wrap="word", height=1)


    def _create_bottom_row(self):
        self.bottom_row_frame = Frame(self.about_window)
        self.bottom_row_frame.pack(fill="x")
        self._create_url_button()
        self._create_game_button()
        self._create_made_by_label()


    def _create_url_button(self):
        self.url_button = ttk.Button(self.bottom_row_frame, text=f"{self.github_url}", command=self._open_github_url)
        self.url_button.pack(side="left", fill="x", padx=10, ipadx=10)
        Tip.create(widget=self.url_button, text="Click this button to open the repo in your default browser", show_delay=10)


    def _create_game_button(self):
        self.game_button = ttk.Button(self.bottom_row_frame, text=f"Play PyTrominos!", command=self.open_game)
        self.game_button.pack(side="left", fill="x", padx=10, ipadx=10)
        Tip.create(widget=self.game_button, text="Click this button to play PyTrominos", show_delay=10)


    def _create_made_by_label(self):
        self.made_by_label = Label(self.bottom_row_frame, text=f"{self.parent.app_version} - img-txt_viewer - Created by: Nenotriple (2023-2025)", font=("Segoe UI", 10))
        self.made_by_label.pack(side="right", padx=10, pady=10)
        Tip.create(widget=self.made_by_label, text="🤍Thank you for using my app!🤍 (^‿^)", show_delay=10)


    def _center_window(self):
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (850 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (650 // 2)
        self.about_window.geometry(f"+{x}+{y}")


    def _open_github_url(self):
        webbrowser.open(f"{self.github_url}")


    def open_game(self):
        self.close_about_window()
        icon_path = self.icon_path
        game = PyTrominos.PyTrominosGame(self.root, icon_path)
        game.run()


    def close_about_window(self):
        if hasattr(self, 'about_window') and self.about_window:
            self.parent.about_window_open = False
            self.about_window.destroy()
