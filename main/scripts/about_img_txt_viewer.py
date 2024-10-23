
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
            " ⦁ALT+LEFT/RIGHT: Quickly move between img-txt pairs.\n"
            " ⦁SHIFT+DEL: Send the current pair to a local trash folder.\n"
            " ⦁ALT: Cycle through auto-suggestions.\n"
            " ⦁TAB: Insert the highlighted suggestion.\n"
            " ⦁CTRL+S: Save the current text file.\n"
            " ⦁CTRL+E: Jump to the next empty text file.\n"
            " ⦁CTRL+R: Jump to a random img-txt pair.\n"
            " ⦁CTRL+F: Highlight all duplicate words.\n"
            " ⦁CTRL+Z / CTRL+Y: Undo/Redo.\n"
            " ⦁F1: Toggle Zoom popup.\n"
            " ⦁F2: Open the Image-Grid.\n"
            " ⦁F5: Refresh the text box.\n"
            " ⦁Middle-click a tag to delete it.\n",

            # Tips
            " ⦁Highlight matching words by selecting text. \n"
            " ⦁Quickly create text pairs by loading the image and saving the text.\n"
            " ⦁List Mode: Display tags in a list format while saving in standard format.\n"
            " ⦁Use an asterisk * while typing to return autocomplete suggestions using a fuzzy search.\n"
            " ⦁Use the Match Mode option: 'Last Word' to allow for more natural autocomplete.\n"
            " ⦁Right-click the 'Browse...' button to set or clear the alternate text path, allowing you to load text files from a separate folder than images.\n",

            # Text Tools
            " ⦁Search and Replace: Search for a specific string of text and replace it with another.\n"
            " ⦁Prefix: Insert text at the START of all text files.\n"
            " ⦁Append: Insert text at the END of all text files.\n"
            " ⦁Filter: Filter pairs based on matching text, blank or missing txt files, and more. Can also be used in relation with: S&R, Prefix, and Append. \n"
            " ⦁Highlight: Always highlight certain text.\n"
            " ⦁My Tags: Quickly add you own tags to be used as autocomplete suggestions.\n"
            " ⦁Batch Tag Edit: View all tags in a directory as a list, and quickly delete or edit them.\n"
            " ⦁Cleanup Text: Fix typos in all text files of the selected folder, such as duplicate tags, multiple spaces or commas, missing spaces, and more.\n",

            # Other Tools
            " ⦁Batch Resize Images: Resize all images in a folder using various methods and conditions\n"
            " ⦁Batch Crop Image: Crop all images to a specific resolution.\n"
            " ⦁Crop Image: Crop the current image to a square or freeform ratio.\n"
            " ⦁Resize Image: Resize the current image either by exact resolution or percentage.\n"
            " ⦁Upscale Image: Upscale the current image using RESRGAN.\n"
            " ⦁Find Duplicate Files: Find and separate any duplicate files in a folder.\n"
            " ⦁Expand: Expand an image to a square ratio instead of cropping.\n"
            " ⦁Batch Rename and/or Convert: Rename and optionally convert all image and text files in the current directory, saving them in sequential order with padded zeros.\n",

            # Auto Save
            " ⦁Check the auto-save box to save text when navigating between img/txt pairs or closing the window, etc.\n"
            " ⦁By default, text is cleaned up when saved, so you can ignore things like duplicate tags, trailing comma/spaces, double comma/spaces, etc.\n"
            " ⦁Text cleanup was designed for CSV format captions and can be disabled from the options menu (Clean-Text).",
            ]



# --------------------------------------
# Class - AboutWindow
# --------------------------------------
    def create_about_window(self):
        self.about_window = tk.Toplevel(self.root)
        self.about_window.title("About - img-txt Viewer")
        self.about_window.geometry("850x650")
        self.about_window.maxsize(900, 900)
        self.about_window.minsize(630, 300)
        self.github_url = "https://github.com/Nenotriple/img-txt_viewer"
        self.set_icon()
        self._create_header_text()
        self._create_textbox()
        self._create_bottom_row()
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (850 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (650 // 2)
        self.about_window.geometry(f"+{x}+{y}")
        self.about_window.focus_force()



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
        bottom_row_frame = Frame(self.about_window)
        bottom_row_frame.pack(fill="x")

        self.url_button = ttk.Button(bottom_row_frame, text=f"{self.github_url}", command=self._open_github_url)
        self.url_button.pack(side="left", fill="x", padx=10, ipadx=10)
        ToolTip.create(self.url_button, "Click this button to open the repo in your default browser", 10, 6, 12)

        self.made_by_label = Label(bottom_row_frame, text=f"{self.version} - img-txt_viewer - Created by: Nenotriple (2023-2024)", font=("Segoe UI", 10))
        self.made_by_label.pack(side="left", expand=True, pady=10)
        ToolTip.create(self.made_by_label, "🤍Thank you for using my app!🤍 (^‿^)", 10, 6, 12)


    def _open_github_url(self):
        webbrowser.open(f"{self.github_url}")


    def set_icon(self):
        self.icon_path = os.path.join(self.parent.application_path, "icon.ico")
        try:
            self.about_window.iconbitmap(self.icon_path)
        except TclError: pass


    def close_about_window(self):
        if hasattr(self, 'about_window') and self.about_window:
            self.about_window.destroy()
