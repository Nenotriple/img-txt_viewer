
################################################################################################################################################
#region -  Imports


# Standard Library
import os


# Standard Library - GUI
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip



#endregion
################################################################################################################################################
#region - CLS BatchUpscale


class BatchUpscale:
    def __init__(self):
        self.parent = None
        self.root = None
        self.working_dir = None

        self.supported_filetypes = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")


    def setup_window(self, parent, root):
        self.parent = parent
        self.root = root
        self.working_dir = self.parent.image_dir.get()
        self.setup_ui()
        self.set_working_directory(self.working_dir)


#endregion
################################################################################################################################################
#region -  Interface


    def setup_ui(self):
        self.setup_primary_frame()
        self.create_directory_row()
        self.create_control_row()
        self.create_bottom_row()


    def setup_primary_frame(self):
        # Configure the tab to expand properly
        self.parent.batch_upscale_tab.grid_rowconfigure(0, weight=1)
        self.parent.batch_upscale_tab.grid_columnconfigure(0, weight=1)
        # Create and configure the main frame
        self.batch_upscale_frame = tk.Frame(self.parent.batch_upscale_tab)
        self.batch_upscale_frame.grid(row=0, column=0, sticky="nsew")
        # Configure the main frame's grid
        self.batch_upscale_frame.grid_rowconfigure(1, weight=1)
        self.batch_upscale_frame.grid_columnconfigure(0, weight=1)


    def create_directory_row(self):
        self.top_frame = tk.Frame(self.batch_upscale_frame)
        self.top_frame.pack(fill="x", padx=2, pady=2)
        # Info
        self.info_label = tk.Label(self.top_frame, anchor="w", text="Select a directory...")
        self.info_label.pack(side="left", fill="x", padx=2)
        # Directory
        self.entry_directory = ttk.Entry(self.top_frame)
        self.entry_directory.insert(0, os.path.normpath(self.working_dir) if self.working_dir else "...")
        self.entry_directory.pack(side="left", fill="x", expand=True, padx=2)
        self.entry_directory.bind("<Return>", lambda event: self.set_working_directory(self.entry_directory.get()))
        self.entry_directory.bind("<Button-1>", lambda event: self.entry_directory.delete(0, "end") if self.entry_directory.get() == "..." else None)
        # Browse
        self.browse_button = ttk.Button(self.top_frame, width=8, text="Browse...", command=self.set_working_directory)
        self.browse_button.pack(side="left", padx=2)
        # Open
        self.open_button = ttk.Button(self.top_frame, width=8, text="Open", command=self.open_folder)
        self.open_button.pack(side="left", padx=2)
        # Help
        self.help_button = ttk.Button(self.top_frame, text="?", width=2, command=self.show_help)
        self.help_button.pack(side="right", fill="x", padx=2)


    def create_control_row(self):
        self.frame_control_row = tk.Frame(self.batch_upscale_frame, borderwidth=2)
        self.frame_control_row.pack(side="top", fill="x", padx=2, pady=2)


    def create_bottom_row(self):
        self.frame_bottom_row = tk.Frame(self.batch_upscale_frame)
        self.frame_bottom_row.pack(side="bottom", fill="both", expand=True)


#endregion
################################################################################################################################################
#region -  UI Functions


    def update_info_label(self, filecount=None, text=None):
        if filecount:
            count = sum(1 for file in os.listdir(self.working_dir) if file.endswith(self.supported_filetypes))
            self.info_label.config(text=f"{count} {'Image' if count == 1 else 'Images'} Found")
        if text:
            self.info_label.config(text=text)


    def set_working_directory(self, path=None):
        if path is None:
            path = filedialog.askdirectory(initialdir=self.working_dir)
            if not os.path.isdir(path):
                return
            self.working_dir = path
        else:
            self.working_dir = path
        self.entry_directory.delete(0, "end")
        self.entry_directory.insert(0, os.path.normpath(self.working_dir))
        self.update_info_label(filecount=True)


    def open_folder(self):
        path = self.working_dir
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Open Folder Error", f"Failed to open folder: {e}")


    def show_help(self):
        help_text = (
            "Batch Upscale\n\n"
            "This tool allows you to upscale multiple images at once.\n\n"
            "1. Select a directory containing images you wish to upscale.\n"
            "2. Specify upscaling options in the settings.\n"
            "3. Click the 'Upscale Images' button to apply the changes.\n\n"
            "Options:\n"
            "- Select the scaling factor for the upscaling process.\n"
        )
        messagebox.showinfo("Help", help_text)
