"""About Window for img-txt Viewer."""

# --------------------------------------
# Imports
# --------------------------------------


# Standard Library
import os
import webbrowser


# Standard Library - GUI
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, Frame, Label, TclError
import tkinter as tk


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip


# --------------------------------------
# Class - AboutWindow
# --------------------------------------
class AboutWindow:
    def __init__(self, parent, root, version, icon):
        self.parent = parent
        self.root = root
        self.version = version
        self.icon_img = icon
        self._create_header_text()


    def _create_header_text(self):
        self.info_headers = ["Shortcuts", "Tips", "Text Tools", "Other Tools", "Auto-Save"]
        self.info_content = [
            # Shortcuts
            " ⦁ ALT + LEFT/RIGHT: Quickly move between image-text pairs.\n"
            " ⦁ SHIFT + DEL: Move the current pair to a local trash folder.\n"
            " ⦁ ALT: Cycle through auto-suggestions.\n"
            " ⦁ TAB: Insert the highlighted suggestion.\n"
            " ⦁ CTRL + S: Save the current text file.\n"
            " ⦁ CTRL + E: Jump to the next empty text file.\n"
            " ⦁ CTRL + R: Jump to a random image-text pair.\n"
            " ⦁ CTRL + F: Highlight all duplicate words.\n"
            " ⦁ CTRL + Z / CTRL + Y: Undo / Redo.\n"
            " ⦁ CTRL + W: Close the window.\n"
            " ⦁ F1: Toggle Zoom popup.\n"
            " ⦁ F2: Open the Image-Grid.\n"
            " ⦁ F5: Refresh the text box.\n"
            " ⦁ Middle-click on a tag to delete it.\n",

            # Tips
            " ⦁ Highlight matching words by selecting text.\n"
            " ⦁ Insert a suggestion by clicking on it.\n"
            " ⦁ A guided setup will run on first launch to configure your autocomplete dictionaries and matching settings.\n"
            " ⦁ The 'Open Current Directory...' command selects the current image in the file explorer.\n"
            " ⦁ Quickly create text pairs by loading the image and saving the text.\n"
            " ⦁ List Mode: Display tags in a list format while saving them in standard format.\n"
            " ⦁ Use an asterisk (*) while typing for fuzzy search autocomplete suggestions.\n"
            " ⦁ Use 'Match Mode: Last Word' for more natural autocomplete.\n"
            " ⦁ Right-click the 'Browse...' button to set or clear the alternate text path, allowing you to load text files from a separate folder than images.\n",

            # Text Tools
            " ⦁ Search and Replace: Find specific text and replace it with another.\n"
            " ⦁ Prefix: Insert text at the START of all text files.\n"
            " ⦁ Append: Insert text at the END of all text files.\n"
            " ⦁ Filter: Filter pairs based on text, missing text files, and more. Works with Search and Replace, Prefix, and Append.\n"
            " ⦁ Highlight: Always highlight specific text.\n"
            " ⦁ My Tags: Add your custom tags for autocomplete suggestions.\n"
            " ⦁ Batch Tag Edit: Edit and manage tags with a user-friendly interface that previews changes before applying them.\n"
            " ⦁ Create Wildcard From Captions: Combine all image captions into one text file, with each caption set separated by a newline.\n"
            " ⦁ Cleanup Text: Fix typos across all text files, such as duplicate tags, extra spaces, commas, and more.\n",

            # Other Tools
            " ⦁ Batch Resize Images: Resize all images in a folder using different methods and conditions.\n"
            " ⦁ Batch Crop Images: Crop all images to a specified resolution.\n"
            " ⦁ Crop Image: Crop the current image to a square or freeform ratio.\n"
            " ⦁ Resize Image: Resize the current image by exact resolution or percentage.\n"
            " ⦁ Upscale Image: Upscale images using models like RESRGAN, AnimeSharp-4x, and UltraSharp-4x. Additional models can be added to the 'models' folder.\n"
            " ⦁ Find Duplicate Files: Identify and separate duplicate files in a folder.\n"
            " ⦁ Expand: Expand an image to a square ratio instead of cropping.\n"
            " ⦁ Thumbnail Panel: Display thumbnails under the current image for quick navigation.\n"
            " ⦁ Edit Image Panel: Adjust brightness, contrast, saturation, sharpness, highlights, and shadows of the current image.\n"
            " ⦁ Edit Image...: Open the current image in an external editor (e.g., MS Paint).\n"
            " ⦁ Batch Rename/Convert: Rename and optionally convert image and text files, saving them sequentially with padded zeros.\n",

            # Auto-Save
            " ⦁ Check the auto-save box to save text when switching between image-text pairs or closing the window.\n"
            " ⦁ Text cleanup (e.g., removing duplicate tags, trailing commas, extra spaces) happens automatically on save, and can be disabled from the options menu.\n"
            " ⦁ Text cleanup is optimized for CSV-format captions and can be disabled via the Clean-Text option in the menu.\n"
            ]


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
        self.github_url = "https://github.com/Nenotriple/img-txt_viewer"


    def _set_icon(self):
        self.icon_path = os.path.join(self.parent.application_path, "icon.ico")
        try:
            self.about_window.iconbitmap(self.icon_path)
        except TclError:
            pass


    def _create_textbox(self):
        self.info_text = ScrolledText(self.about_window)
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
        self._create_made_by_label()


    def _create_url_button(self):
        self.url_button = ttk.Button(self.bottom_row_frame, text=f"{self.github_url}", command=self._open_github_url)
        self.url_button.pack(side="left", fill="x", padx=10, ipadx=10)
        ToolTip.create(self.url_button, "Click this button to open the repo in your default browser", 10, 6, 12)


    def _create_made_by_label(self):
        self.made_by_label = Label(self.bottom_row_frame, text=f"{self.version} - img-txt_viewer - Created by: Nenotriple (2023-2024)", font=("Segoe UI", 10))
        self.made_by_label.pack(side="right", padx=10, pady=10)
        ToolTip.create(self.made_by_label, "🤍Thank you for using my app!🤍 (^‿^)", 10, 6, 12)


    def _center_window(self):
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (850 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (650 // 2)
        self.about_window.geometry(f"+{x}+{y}")


    def _open_github_url(self):
        webbrowser.open(f"{self.github_url}")


    def close_about_window(self):
        if hasattr(self, 'about_window') and self.about_window:
            self.about_window.destroy()
