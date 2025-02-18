################################################################################################################################################
#region -  Imports


# Standard Library
import os
import time

# Standard Library - GUI
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, BooleanVar


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

        self.supported_filetypes = (".txt", ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif")
        self.sort_column = "Name"  # Track which column we're sorting by
        self.sort_reverse = False  # Track sort direction
        self.respect_img_txt_pairs_var = BooleanVar(value=True)
        self.prevent_duplicates_var = BooleanVar(value=True)
        self.show_warning = BooleanVar(value=True)
        self.show_confirmation = BooleanVar(value=True)



    def setup_window(self, parent, root):
        self.parent = parent
        self.root = root
        self.working_dir = self.parent.image_dir.get()
        self.setup_ui()
        self.select_folder(self.working_dir)


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
        # Info Label
        self.info_label = tk.Label(self.top_frame, anchor="w", text="Select a directory...")
        self.info_label.pack(side="left", fill="x", padx=2)
        # Entry
        self.entry_directory = ttk.Entry(self.top_frame)
        self.entry_directory.insert(0, os.path.normpath(self.working_dir) if self.working_dir else "...")
        self.entry_directory.pack(side="left", fill="x", expand=True, padx=2)
        self.entry_directory.bind("<Return>", lambda event: self.select_folder(self.entry_directory.get()))
        self.entry_directory.bind("<Button-1>", lambda event: self.entry_directory.delete(0, "end") if self.entry_directory.get() == "..." else None)
        # Browse
        self.select_button = ttk.Button(self.top_frame, width=8, text="Browse...", command=self.select_folder)
        self.select_button.pack(side="left", padx=2)
        # Open
        self.open_button = ttk.Button(self.top_frame, width=8, text="Open", command=self.open_folder)
        self.open_button.pack(side="left", padx=2)

        self.help_button = ttk.Button(self.top_frame, text="?", width=2, command=self.show_help)
        self.help_button.pack(side="right", fill="x", padx=2)


    def create_control_row(self):
        self.frame_control_row = tk.Frame(self.batch_rename_frame, borderwidth=2)
        self.frame_control_row.pack(side="top", fill="both", expand=True, padx=2, pady=2)
        self.create_tree_view()


    def create_tree_view(self):
        self.file_tree_view = ttk.Treeview(self.frame_control_row, columns=("Name", "New Name", "Type", "Size", "Modified"), show="headings")
        # Configure column headings with sort bindings
        for col in self.file_tree_view["columns"]:
            header_text = f"{col} ↑" if col == "Name" else col
            self.file_tree_view.heading(col, text=header_text, command=lambda c=col: self.sort_treeview(c))
        # Configure column widths and stretch properties
        self.file_tree_view.column("Name", width=200, minwidth=150, stretch=True)
        self.file_tree_view.column("New Name", width=200, minwidth=150, stretch=True)
        self.file_tree_view.column("Type", width=50, minwidth=0, stretch=False)
        self.file_tree_view.column("Size", width=90, minwidth=0, stretch=False)
        self.file_tree_view.column("Modified", width=160, minwidth=0, stretch=False)
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(self.frame_control_row, orient="vertical", command=self.file_tree_view.yview)
        self.file_tree_view.configure(yscrollcommand=v_scrollbar.set)
        # Grid layout for treeview and scrollbars
        self.file_tree_view.grid(column=0, row=0, sticky='nsew')
        v_scrollbar.grid(column=1, row=0, sticky='ns')
        # Configure grid weights
        self.frame_control_row.grid_columnconfigure(0, weight=1)
        self.frame_control_row.grid_rowconfigure(0, weight=1)


    def create_bottom_row(self):
        self.frame_bottom_row = tk.Frame(self.batch_rename_frame)
        self.frame_bottom_row.pack(side="bottom", fill="both")
        # Options
        self.options_menu = ttk.Menubutton(self.frame_bottom_row, text="Options")
        self.options_menu.pack(side="left", fill="x", padx=2, pady=2)
        self.options_menu.menu = tk.Menu(self.options_menu, tearoff=0)
        self.options_menu["menu"] = self.options_menu.menu
        self.options_menu.menu.add_checkbutton(label="Respect Img-Txt Pairs", variable=self.respect_img_txt_pairs_var)
        self.options_menu.menu.add_checkbutton(label="Prevent Duplicates", variable=self.prevent_duplicates_var)
        self.options_menu.menu.add_separator()
        self.options_menu.menu.add_checkbutton(label="Show Warning", variable=self.show_warning)
        self.options_menu.menu.add_checkbutton(label="Show Confirmation", variable=self.show_confirmation)
        # Presets
        self.presets_menu = ttk.Menubutton(self.frame_bottom_row, text="Presets")
        self.presets_menu.pack(side="left", fill="x", padx=2, pady=2)
        self.presets_menu.menu = tk.Menu(self.presets_menu, tearoff=0)
        self.presets_menu["menu"] = self.presets_menu.menu
        self.presets_menu.menu.add_command(label="Numbering")
        self.presets_menu.menu.add_command(label="Auto-Date")
        # Rename
        self.rename_button = ttk.Button(self.frame_bottom_row, text="Rename Files")
        self.rename_button.pack(side="left", fill="both", expand=True, padx=2, pady=2)

#endregion
################################################################################################################################################
#region -  UI Functions


    def update_info_label(self, filecount=None, text=None):
        if filecount:
            count = sum(1 for file in os.listdir(self.working_dir) if file.endswith(self.supported_filetypes))
            self.info_label.config(text=f"{count} {'File' if count == 1 else 'Files'} Found")
        if text:
            self.info_label.config(text=text)


    def select_folder(self, path=None):
        if path is None:
            path = filedialog.askdirectory(initialdir=self.working_dir)
        else:
            self.working_dir = path
            self.entry_directory.delete(0, "end")
            self.entry_directory.insert(0, os.path.normpath(self.working_dir))
            self.update_info_label(filecount=True)
            self.update_file_tree_view()


    def open_folder(self):
        path = self.working_dir
        try:
            os.startfile(path)
        except Exception as e:
            print(f"Error opening folder: {e}")


    def update_file_tree_view(self):
        """Update the treeview with files from the working directory."""
        # Get the sort key from the parent
        sort_key = self.parent.get_file_sort_key()
        # List all supported files in the working directory
        files = [f for f in os.listdir(self.working_dir) if f.lower().endswith(self.supported_filetypes)]
        # Sort files using the parent's sort key; prepend working_dir for full path if needed
        files = sorted(files, key=lambda f: sort_key(f))
        # Clear existing treeview items
        for item in self.file_tree_view.get_children():
            self.file_tree_view.delete(item)
        # Insert file details for each file
        for file in files:
            full_path = os.path.join(self.working_dir, file)
            name, ext = os.path.splitext(file)
            size = os.path.getsize(full_path)
            if size < 1024:
                size_kb = f"{(size/1024):.1f} KB"
            else:
                size_kb = f"{int(size/1024):,} KB"
            modified_time = time.strftime("%Y-%m-%d, %I:%M:%S %p", time.localtime(os.path.getmtime(full_path)))
            # Insert row with "New Name" matching original name
            self.file_tree_view.insert("", "end", values=(file, file, ext, size_kb, modified_time))


    def sort_treeview(self, column):
        """Sort treeview contents by the selected column."""
        items = [(self.file_tree_view.set(item, column), item) for item in self.file_tree_view.get_children("")]
        # If clicking the same column, reverse the sort
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            self.sort_column = column
        # Sort based on column type
        if column == "Size":
            items.sort(key=lambda x: float(x[0].replace(' KB', '').replace(',', '')), reverse=self.sort_reverse)
        elif column == "Modified":
            items.sort(key=lambda x: time.strptime(x[0], "%Y-%m-%d, %I:%M:%S %p"), reverse=self.sort_reverse)
        else:
            items.sort(key=lambda x: x[0].lower(), reverse=self.sort_reverse)
        # Rearrange items in sorted order
        for index, (_, item) in enumerate(items):
            self.file_tree_view.move(item, "", index)
        # Add or update sort indicator in column heading
        for col in self.file_tree_view["columns"]:
            if col == column:
                self.file_tree_view.heading(col, text=f"{col} {'↓' if self.sort_reverse else '↑'}")
            else:
                self.file_tree_view.heading(col, text=col)


    def show_help(self):
        help_text = (
            "Batch Rename\n\n"
            "This tool allows you to rename multiple files at once.\n\n"
            "1. Select a directory containing files you wish to rename.\n"
            "2. Use the treeview to sort and select files for renaming.\n"
            "3. Choose from the options and presets menus to customize the renaming process.\n"
            "4. Click the 'Rename Files' button to apply the changes.\n\n"
            "Options:\n"
            "- Respect Img-Txt Pairs: Rename image and text files together.\n\n"
            "Presets:\n"
            "- Numbering: Rename files with a numbered sequence.\n"
            "- Auto-Date: Rename files with the modified date.\n"
        )
        messagebox.showinfo("Help", help_text)


#endregion
