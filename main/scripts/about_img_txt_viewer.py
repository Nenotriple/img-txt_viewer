"""About Window for img-txt Viewer."""

# --------------------------------------
# Imports
# --------------------------------------


# Standard Library
import os
import webbrowser


# Standard Library - GUI
import tkinter as tk
from tkinter import ttk, Frame, scrolledtext, Label, TclError


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip
from main.scripts import PyTrominos


# --------------------------------------
# Class - AboutWindow
# --------------------------------------
class AboutWindow:
    def __init__(self, parent, root, icon):
        self.parent = parent
        self.root = root
        self.icon_img = icon
        self.icon_path = None
        self.info_headers, self.info_content = self._create_header_text()


    def _create_header_text(self):
        headers = [
            " Shortcuts",
            " Tips",
            " Text Tools",
            " Image Tools",
            " Other"
        ]
        content = [
            # Shortcuts
            " ⦁ ALT + LEFT/RIGHT: Quickly move between img-txt pairs.\n"
            " ⦁ SHIFT + DEL: Move the current pair to a local trash folder.\n"
            " ⦁ ALT: Cycle through auto-suggestions.\n"
            " ⦁ TAB: Insert the highlighted suggestion.\n"
            " ⦁ CTRL + S: Save the current text file.\n"
            " ⦁ CTRL + E: Jump to the next empty text file.\n"
            " ⦁ CTRL + R: Jump to a random img-txt pair.\n"
            " ⦁ CTRL + F: Highlight all duplicate words.\n"
            " ⦁ CTRL + Z / CTRL + Y: Undo / Redo.\n"
            " ⦁ CTRL + W: Close the window.\n"
            " ⦁ F1: Toggle zoom popup.\n"
            " ⦁ F2: Open the Image-Grid view.\n"
            " ⦁ F4: Open the current image in your default editor.\n"
            " ⦁ F5: Open Batch Tag Edit.\n"
            " ⦁ Middle-click on a tag to delete it.\n",

            # Tips
            " ⦁ A guided setup will run on first launch to configure your autocomplete dictionaries and matching settings.\n"
            " ⦁ Insert a suggestion by clicking on it or pressing TAB.\n"
            " ⦁ Highlight matching words by selecting similar text.\n"
            " ⦁ Quickly create text pairs by loading the image and saving the text.\n"
            " ⦁ List Mode: Display tags in a list format while saving them in standard format.\n"
            " ⦁ Use an asterisk (*) while typing for fuzzy search autocomplete suggestions.\n"
            " ⦁ Match Modes: 'Last Word' matches only the last word typed, 'Whole String' matches the entire tag between commas.\n",
            " ⦁ Use 'Match Mode: Last Word' for more natural and less strict autocomplete.\n"
            " ⦁ Right-click the 'Browse...' button to set or clear the alternate text path, allowing you to load text files from a separate folder than images.\n"

            # Text Tools
            " ⦁ Search and Replace: Find specific text and replace it with another.\n"
            " ⦁ Prefix: Insert text at the START of all text files.\n"
            " ⦁ Append: Insert text at the END of all text files.\n"
            " ⦁ AutoTag: Automatically tag images using ONNX vision models like `wd-v1-4-vit-tagger-v2`.\n"
            " ⦁ Filter: Filter pairs based on text, missing text files, and more. Works with Search and Replace, Prefix, and Append.\n"
            " ⦁ Highlight: Always highlight specific text.\n"
            " ⦁ My Tags: Add your custom tags for autocomplete suggestions.\n"
            " ⦁ Batch Tag Edit: Edit and manage tags with a user-friendly interface that previews changes before applying them.\n"
            " ⦁ Create Wildcard From Captions: Combine all image captions into one text file, with each caption set separated by a newline.\n"
            " ⦁ Cleanup Text: Fix typos across all text files, such as duplicate tags, extra spaces, commas, and more.\n",

            # Image Tools
            " ⦁ Batch Resize Images: Resize all images in a folder using different methods and conditions.\n"
            " ⦁ Resize Image: Resize the current image by exact resolution or percentage.\n"
            " ⦁ Batch Crop Images: Crop all images to a specified resolution.\n"
            " ⦁ Crop Image: Crop an image or GIF using a variety of methods and tools.\n"
            " ⦁ Upscale Image: Upscale images using models like RESRGAN, AnimeSharp-4x, and UltraSharp-4x. Additional models can be added to the 'ncnn_models' folder.\n"
            " ⦁ Find Duplicate Files: Identify and separate duplicate files from your dataset.\n"
            " ⦁ Expand: Expand an image to a square ratio instead of cropping. Designed for images with simple backgrounds and centered subjects.\n"
            " ⦁ Edit Image Panel: Adjust brightness, contrast, saturation, sharpness, highlights, and shadows of the current image.\n"

            # Other
            " ⦁ Batch Rename/Convert: Rename and optionally convert image and text files, saving them sequentially with padded zeros.\n",
            " ⦁ Thumbnail Panel: Display thumbnails under the current image for quick navigation.\n"
            " ⦁ Edit Image...: Open the current image in an external editor (e.g., MS Paint).\n"
            " ⦁ Auto-Save: Save text when switching between img-txt pairs, changing the active directory, or closing the app.\n"
            " ⦁ Text cleanup (e.g., removing duplicate tags, trailing commas, extra spaces) happens automatically on save, and can be disabled from the options menu.\n"
            " ⦁ Text cleanup is optimized for CSV-format captions and can be disabled via the Clean-Text option in the menu.\n"
            "\n"
            "\n"
            " For more detailed information regarding the tools and features, please refer to the User Guide found in the repo docs.\n\n"
            " github.com/Nenotriple/img-txt_viewer\n"
        ]
        return headers, content


# --------------------------------------
# Class - AboutWindow
# --------------------------------------
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
        self.icon_path = os.path.join(self.parent.application_path, "icon.ico")
        try:
            self.about_window.iconbitmap(self.icon_path)
        except TclError:
            pass


    def _create_textbox(self):
        self.info_text = scrolledtext.ScrolledText(self.about_window)
        self.info_text.pack(expand=True, fill='both')
        for header, section in zip(self.info_headers, self.info_content):
            self.info_text.insert("end", header + "\n", "header")
            self.info_text.insert("end", section + "\n", "section")
        self.info_text.tag_config("header", font=("Segoe UI", 9, "bold"))
        self.info_text.tag_config("section", font=("Segoe UI", 9))
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
        ToolTip.create(self.url_button, "Click this button to open the repo in your default browser", 10, 6, 12)


    def _create_game_button(self):
        self.game_button = ttk.Button(self.bottom_row_frame, text=f"Play PyTrominos", command=self.open_game)
        self.game_button.pack(side="left", fill="x", padx=10, ipadx=10)
        ToolTip.create(self.game_button, "Click this button to play PyTrominos", 10, 6, 12)


    def _create_made_by_label(self):
        self.made_by_label = Label(self.bottom_row_frame, text=f"{self.parent.app_version} - img-txt_viewer - Created by: Nenotriple (2023-2024)", font=("Segoe UI", 10))
        self.made_by_label.pack(side="right", padx=10, pady=10)
        ToolTip.create(self.made_by_label, "🤍Thank you for using my app!🤍 (^‿^)", 10, 6, 12)


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
