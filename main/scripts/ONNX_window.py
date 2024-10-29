"""Onnx Window for img-txt Viewer."""

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
# Class - OnnxWindow
# --------------------------------------
class ONNXWindow:
    def __init__(self, parent, root, version, icon, text):
        self.parent = parent
        self.root = root
        self.version = version
        self.icon_img = icon
        self.tag_results = text


# --------------------------------------
# Class - OnnxWindow
# --------------------------------------

    def create_ONNX_window(self):
        """Create the Onnx window."""
        self._initialize_window()
        self._set_icon()
        self._create_textbox()
        self._create_bottom_row()
        self._center_window()
        self.ONNX_window.focus_force()


    def _initialize_window(self):
        self.ONNX_window = tk.Toplevel(self.root)
        self.ONNX_window.title("Tag Suggestions - img-txt Viewer")
        self.ONNX_window.geometry("850x650")
        self.ONNX_window.minsize(675, 300)
        self.ONNX_window.protocol("WM_DELETE_WINDOW", self.close_ONNX_window)
        self.github_url = "https://github.com/Nenotriple/img-txt_viewer"


    def _set_icon(self):
        self.icon_path = os.path.join(self.parent.application_path, "icon.ico")
        try:
            self.ONNX_window.iconbitmap(self.icon_path)
        except TclError:
            pass


    def _create_textbox(self):
        self.info_text = ScrolledText(self.ONNX_window)
        self.info_text.pack(expand=True, fill='both')
        self.info_text.insert("end", self.tag_results)
        self.info_text.config(state='disabled', wrap="word", height=1)


    def _create_bottom_row(self):
        self.bottom_row_frame = Frame(self.ONNX_window)
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
        self.ONNX_window.geometry(f"+{x}+{y}")


    def _open_github_url(self):
        webbrowser.open(f"{self.github_url}")


    def close_ONNX_window(self):
        if hasattr(self, 'ONNX_window') and self.ONNX_window:
            self.ONNX_window.destroy()
