
################################################################################################################################################
#region -  Imports


# Standard Library
import os


# Standard Library - GUI
import tkinter as tk
from tkinter import ttk


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip



#endregion
################################################################################################################################################
#region - CLS BatchRename


class BatchRename:
    def __init__(self):
        self.parent = None
        self.root = None
        self.working_dir = None

        self.supported_filetypes = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")


    def setup_window(self, parent, root, path=None):
        self.parent = parent
        self.root = root
        self.working_dir = path
        self.setup_ui()


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
        self.parent.batch_rename_tab.grid_rowconfigure(0, weight=1)
        self.parent.batch_rename_tab.grid_columnconfigure(0, weight=1)
        # Create and configure the main frame
        self.batch_rename_frame = tk.Frame(self.parent.batch_rename_tab)
        self.batch_rename_frame.grid(row=0, column=0, sticky="nsew")
        # Configure the main frame's grid
        self.batch_rename_frame.grid_rowconfigure(1, weight=1)
        self.batch_rename_frame.grid_columnconfigure(0, weight=1)


    def create_directory_row(self):
        self.top_frame = tk.Frame(self.batch_rename_frame)
        self.top_frame.pack(fill="x", padx=2, pady=2)

        self.info_label = tk.Label(self.top_frame, anchor="w", text="Select a directory...")
        self.info_label.pack(side="left", fill="x", padx=2)

        self.entry_directory = ttk.Entry(self.top_frame)
        self.entry_directory.insert(0, os.path.normpath(self.working_dir) if self.working_dir else "...")
        self.entry_directory.pack(side="left", fill="x", expand=True, padx=2)
        self.entry_directory.bind("<Return>", lambda event: self.select_folder(self.entry_directory.get()))
        self.entry_directory.bind("<Button-1>", lambda event: self.entry_directory.delete(0, "end") if self.entry_directory.get() == "..." else None)

        self.select_button = ttk.Button(self.top_frame, width=8, text="Browse...", command=self.select_folder)
        self.select_button.pack(side="left", padx=2)

        self.open_button = ttk.Button(self.top_frame, width=8, text="Open", command=self.open_folder)
        self.open_button.pack(side="left", padx=2)


    def create_control_row(self):
        self.frame_control_row = tk.Frame(self.batch_rename_frame, borderwidth=2)
        self.frame_control_row.pack(side="top", fill="x", padx=2, pady=2)


    def create_bottom_row(self):
        self.frame_bottom_row = tk.Frame(self.batch_rename_frame)
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


    def select_folder(self, path=None):
        pass


    def open_folder(self):
        pass