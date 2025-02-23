################################################################################################################################################
#region -  Imports


# Standard Library
import os
import time

# Standard Library - GUI
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, BooleanVar, StringVar

# Local
from main.scripts.help_window import HelpWindow


#endregion
################################################################################################################################################
#region - CLS BatchRename


class BatchRename:
    def __init__(self):
        self.parent = None
        self.root = None
        self.working_dir = None
        self.help_window = None
        # Variables
        self.supported_filetypes = (".txt", ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif")
        self.sort_column = "Name"
        self.sort_reverse = False
        self.selected_items = set()
        self.last_preview_count = 0
        # Settings
        self.respect_img_txt_pairs_var = BooleanVar(value=True)
        self.handle_duplicates_var = StringVar(value="Rename")
        self.show_warning_var = BooleanVar(value=True)
        self.rename_preset_var = StringVar(value="Numbering")


    def setup_window(self, parent, root):
        self.parent = parent
        self.root = root
        self.working_dir = self.parent.image_dir.get()
        self.help_window = HelpWindow(self.root)
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
        self.info_label = tk.Label(self.top_frame, anchor="w", text="Select a directory...", width=25)
        self.info_label.pack(side="left", fill="x", padx=2)
        # Entry
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
        self.help_button = ttk.Button(self.top_frame, text="?", width=2, command=self.open_help_window)
        self.help_button.pack(side="right", fill="x", padx=2)


    def create_control_row(self):
        self.frame_control_row = tk.Frame(self.batch_rename_frame, borderwidth=2)
        self.frame_control_row.pack(side="top", fill="both", expand=True, padx=2, pady=2)
        self.create_tree_view()


    def create_tree_view(self):
        self.file_treeview = ttk.Treeview(self.frame_control_row, columns=("Name", "New Name", "Type", "Size", "Modified"), show="headings", selectmode="extended")
        # Configure column headings with sort bindings
        for col in self.file_treeview["columns"]:
            header_text = f"{col} ↑" if col == "Name" else col
            self.file_treeview.heading(col, text=header_text, command=lambda c=col: self.sort_treeview(c))
        # Configure column widths and stretch properties
        self.file_treeview.column("Name", width=200, minwidth=150, stretch=True)
        self.file_treeview.column("New Name", width=200, minwidth=150, stretch=True)
        self.file_treeview.column("Type", width=50, minwidth=0, stretch=False)
        self.file_treeview.column("Size", width=90, minwidth=0, stretch=False)
        self.file_treeview.column("Modified", width=160, minwidth=0, stretch=False)
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(self.frame_control_row, orient="vertical", command=self.file_treeview.yview)
        self.file_treeview.configure(yscrollcommand=v_scrollbar.set)
        # Grid layout for treeview and scrollbars
        self.file_treeview.grid(column=0, row=0, sticky='nsew')
        v_scrollbar.grid(column=1, row=0, sticky='ns')
        # Configure grid weights
        self.frame_control_row.grid_columnconfigure(0, weight=1)
        self.frame_control_row.grid_rowconfigure(0, weight=1)
        self.file_treeview.bind('<<TreeviewSelect>>', self.on_selection_change)
        self.file_treeview.bind("<Control-a>", lambda event: self.file_treeview.selection_set(self.file_treeview.get_children()))
        self.file_treeview.bind("<Control-d>", lambda event: self.file_treeview.selection_remove(self.file_treeview.selection()))
        self.file_treeview.bind("<Control-i>", lambda event: self.file_treeview.selection_toggle(self.file_treeview.get_children()))
        self.file_treeview.bind("<F5>", lambda event: self.update_file_tree_view())


    def create_bottom_row(self):
        self.frame_bottom_row = tk.Frame(self.batch_rename_frame)
        self.frame_bottom_row.pack(side="bottom", fill="both")
        # Options
        self.options_menu = ttk.Menubutton(self.frame_bottom_row, text="Options")
        self.options_menu.pack(side="left", fill="x", padx=2, pady=2)
        self.options_menu.menu = tk.Menu(self.options_menu, tearoff=0)
        self.options_menu["menu"] = self.options_menu.menu
        # Handle Duplicates
        self.handle_duplicates_menu = tk.Menu(self.options_menu.menu, tearoff=0)
        self.options_menu.menu.add_cascade(label="Handle Duplicates", menu=self.handle_duplicates_menu)
        self.handle_duplicates_menu.add_radiobutton(label="Rename", variable=self.handle_duplicates_var, value="Rename", command=self.update_rename_preview)
        self.handle_duplicates_menu.add_radiobutton(label="Move to Folder", variable=self.handle_duplicates_var, value="Move to Folder", command=self.update_rename_preview)
        self.handle_duplicates_menu.add_separator()
        self.handle_duplicates_menu.add_radiobutton(label="Overwrite", variable=self.handle_duplicates_var, value="Overwrite", command=self.update_rename_preview)
        self.handle_duplicates_menu.add_radiobutton(label="Skip", variable=self.handle_duplicates_var, value="Skip", command=self.update_rename_preview)
        self.options_menu.menu.add_checkbutton(label="Respect Img-Txt Pairs", variable=self.respect_img_txt_pairs_var, command=self.update_rename_preview)
        self.options_menu.menu.add_separator()
        self.options_menu.menu.add_checkbutton(label="Show Warning", variable=self.show_warning_var)
        # Actions
        self.actions_menu = ttk.Menubutton(self.frame_bottom_row, text="Actions")
        self.actions_menu.pack(side="left", fill="x", padx=2, pady=2)
        self.actions_menu.menu = tk.Menu(self.actions_menu, tearoff=0)
        self.actions_menu["menu"] = self.actions_menu.menu
        self.actions_menu.menu.add_command(label="Select All", accelerator="Ctrl+A", command=lambda: self.file_treeview.selection_set(self.file_treeview.get_children()))
        self.actions_menu.menu.add_command(label="Deselect All", accelerator="Ctrl+D", command=lambda: self.file_treeview.selection_remove(self.file_treeview.selection()))
        self.actions_menu.menu.add_command(label="Invert Selection", accelerator="Ctrl+I", command=lambda: self.file_treeview.selection_toggle(self.file_treeview.get_children()))
        self.actions_menu.menu.add_separator()
        self.actions_menu.menu.add_command(label="Refresh Files", accelerator="F5", command=self.update_file_tree_view)
        # Presets
        self.presets_menu = ttk.Menubutton(self.frame_bottom_row, text="Presets")
        self.presets_menu.pack(side="left", fill="x", padx=2, pady=2)
        self.presets_menu.menu = tk.Menu(self.presets_menu, tearoff=0)
        self.presets_menu["menu"] = self.presets_menu.menu
        self.presets_menu.menu.add_radiobutton(label="Numbering", variable=self.rename_preset_var, value="Numbering", command=self.update_rename_preview)
        self.presets_menu.menu.add_radiobutton(label="Auto-Date", variable=self.rename_preset_var, value="Auto-Date", command=self.update_rename_preview)
        # Rename
        self.rename_button = ttk.Button(self.frame_bottom_row, text="Rename Files", command=self.rename_files)
        self.rename_button.pack(side="left", fill="both", expand=True, padx=2, pady=2)


#endregion
################################################################################################################################################
#region -  Rename Process


    def rename_files(self):
        selected_items = self.file_treeview.selection()
        if not selected_items:
            messagebox.showinfo("No Selection", "No files selected for renaming.")
            return
        # Show warning if enabled
        if self.show_warning_var.get():
            msg = f"Are you sure you want to rename {len(selected_items)} files?\n\nThere is no undo for this operation."
            if not messagebox.askyesno("Confirm Rename", msg):
                return
        duplicate_option = self.handle_duplicates_var.get()
        if (duplicate_option == "Move to Folder"):
            renamed_folder = self.setup_renamed_folder()
        else:
            renamed_folder = None
        for item in selected_items:
            old_name = self.file_treeview.set(item, "Name")
            new_name = self.file_treeview.set(item, "New Name")
            if not new_name or new_name == old_name:
                continue
            old_path = os.path.join(self.working_dir, old_name)
            if renamed_folder:
                new_path = os.path.join(renamed_folder, new_name)
            else:
                new_path = os.path.join(self.working_dir, new_name)
            try:
                os.rename(old_path, new_path)
            except FileExistsError:
                # Overwrite or skip handled at preview, so just skip here if it still conflicts
                continue
            except Exception as e:
                messagebox.showerror("Rename Error", f"Failed to rename {old_name}: {e}")
        self.update_file_tree_view()



    def setup_renamed_folder(self):
        renamed_folder = os.path.join(self.working_dir, "Renamed Files")
        if not os.path.exists(renamed_folder):
            os.makedirs(renamed_folder)
        return renamed_folder


#endregion
################################################################################################################################################
#region -  Treeview Functions


    def on_selection_change(self, event=None):
        # Check if files still exist and refresh if needed
        for item in self.file_treeview.get_children():
            filename = self.file_treeview.set(item, "Name")
            if not os.path.exists(os.path.join(self.working_dir, filename)):
                self.update_file_tree_view()
                return
        self.selected_items = set(self.file_treeview.selection())
        self.update_rename_preview()
        self.update_info_label(filecount=True)


    def update_file_tree_view(self):
        # Clear selection tracking
        self.selected_items.clear()
        self.last_preview_count = 0
        # Get the sort key from the parent
        sort_key = self.parent.get_file_sort_key()
        # List all supported files in the working directory
        files = [f for f in os.listdir(self.working_dir) if f.lower().endswith(self.supported_filetypes)]
        # Sort files using the parent's sort key; prepend working_dir for full path if needed
        files = sorted(files, key=lambda f: sort_key(f))
        # Clear existing treeview items
        for item in self.file_treeview.get_children():
            self.file_treeview.delete(item)
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
            self.file_treeview.insert("", "end", values=(file, file, ext, size_kb, modified_time))


    def sort_treeview(self, column):
        items = [(self.file_treeview.set(item, column), item) for item in self.file_treeview.get_children("")]
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
            self.file_treeview.move(item, "", index)
        # Add or update sort indicator in column heading
        for col in self.file_treeview["columns"]:
            if col == column:
                self.file_treeview.heading(col, text=f"{col} {'↓' if self.sort_reverse else '↑'}")
            else:
                self.file_treeview.heading(col, text=col)


#endregion
################################################################################################################################################
#region -  Rename Preview


    def update_rename_preview(self):
        selected_count = len(self.selected_items)
        number_preset = True if self.rename_preset_var.get() == "Numbering" else False
        date_preset = True if self.rename_preset_var.get() == "Auto-Date" else False
        if selected_count == 0:
            for item in self.file_treeview.get_children():
                current_name = self.file_treeview.set(item, "Name")
                self.file_treeview.set(item, "New Name", current_name)
            self.last_preview_count = 0
            return
        pairs = self.get_file_pairs() if self.respect_img_txt_pairs_var.get() else {}
        processed_pairs = set()
        existing_files = set(os.listdir(self.working_dir))
        preview_files = set()  # Track files we're planning to rename to
        counter = 1
        self.generate_rename_preview(number_preset, date_preset, pairs, processed_pairs, existing_files, preview_files, counter)
        self.last_preview_count = selected_count


    def generate_rename_preview(self, number_preset, date_preset, pairs, processed_pairs, existing_files, preview_files, counter):
        for item in self.file_treeview.get_children():
            current_name = self.file_treeview.set(item, "Name")
            base, ext = os.path.splitext(current_name)
            if current_name in processed_pairs:
                continue
            if item in self.selected_items:
                if base in pairs and self.respect_img_txt_pairs_var.get():
                    img_file, txt_file = pairs[base]
                    new_base = f"{counter:05d}" if number_preset else base
                    if date_preset:
                        modified_time = self.file_treeview.set(item, "Modified")
                        date_str = time.strftime("%Y-%m-%d", time.strptime(modified_time, "%Y-%m-%d, %I:%M:%S %p"))
                        new_base = f"{date_str}_{counter:05d}"
                    # Handle both files in the pair
                    for tree_item in self.file_treeview.get_children():
                        tree_name = self.file_treeview.set(tree_item, "Name")
                        if tree_name in (img_file, txt_file):
                            _, tree_ext = os.path.splitext(tree_name)
                            new_name = f"{new_base}{tree_ext}"
                            # Handle potential duplicates
                            final_name = self.handle_duplicate_filename(new_name, existing_files | preview_files)
                            if final_name:  # Skip if None (skip option)
                                self.file_treeview.set(tree_item, "New Name", final_name)
                                preview_files.add(final_name)
                            else:
                                self.file_treeview.set(tree_item, "New Name", tree_name)
                            processed_pairs.add(tree_name)
                    counter += 1
                elif current_name not in processed_pairs:
                    if number_preset:
                        new_name = f"{counter:05d}{ext}"
                    elif date_preset:
                        modified_time = self.file_treeview.set(item, "Modified")
                        date_str = time.strftime("%Y-%m-%d", time.strptime(modified_time, "%Y-%m-%d, %I:%M:%S %p"))
                        new_name = f"{date_str}_{counter:05d}{ext}"
                    else:
                        new_name = current_name
                    # Handle potential duplicates
                    final_name = self.handle_duplicate_filename(new_name, existing_files | preview_files)
                    if final_name:  # Skip if None (skip option)
                        self.file_treeview.set(item, "New Name", final_name)
                        preview_files.add(final_name)
                    else:
                        self.file_treeview.set(item, "New Name", current_name)
                    counter += 1
            else:
                self.file_treeview.set(item, "New Name", current_name)


    def handle_duplicate_filename(self, new_name, existing_files):
        """Handle duplicate filenames based on user preference."""
        base, ext = os.path.splitext(new_name)
        duplicate_option = self.handle_duplicates_var.get()
        if duplicate_option == "Rename":
            counter = 1
            while new_name in existing_files:
                new_name = f"{base}_{counter}{ext}"
                counter += 1
            return new_name
        elif duplicate_option == "Move to Folder":
            renamed_folder = os.path.join(self.working_dir, "Renamed Files")
            new_path = os.path.join(renamed_folder, new_name)
            return new_name  # Just return the name for preview, actual move happens during rename
        elif duplicate_option == "Overwrite":
            return new_name  # Will be handled during actual rename with confirmation
        elif duplicate_option == "Skip":
            if new_name in existing_files:
                return None  # None indicates skip this file
            return new_name



    def get_file_pairs(self):
        """Returns a dictionary of paired files where key is the base name and value is tuple of (img_file, txt_file)"""
        pairs = {}
        files = {f for f in os.listdir(self.working_dir)}
        for file in files:
            base, ext = os.path.splitext(file)
            ext = ext.lower()
            # Skip if not a supported file
            if ext not in self.supported_filetypes:
                continue
            # Check for text pair
            txt_pair = f"{base}.txt"
            if ext != '.txt' and txt_pair in files:
                pairs[base] = (file, txt_pair)
        return pairs


#endregion
################################################################################################################################################
#region -  Other Functions


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
        self.update_file_tree_view()


    def update_info_label(self, filecount=None, text=None):
        if filecount:
            filecount = sum(1 for file in os.listdir(self.working_dir) if file.endswith(self.supported_filetypes))
            selection_count = self.last_preview_count
            digits = len(str(filecount))
            selection_str = str(selection_count).zfill(digits)
            self.info_label.config(text=f"{filecount} {'File' if filecount == 1 else 'Files'} Found | {selection_str} {'Selected' if selection_count == 1 else 'Selected'}")
        if text:
            self.info_label.config(text=text)


    def open_folder(self):
        path = self.working_dir
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Open Folder Error", f"Failed to open folder: {e}")


#endregion
################################################################################################################################################
#region -  Help


    def open_help_window(self):
        filetypes = ", ".join(self.supported_filetypes).replace(".", "")
        help_text = {
            "Batch Rename Help": "",
            "Supported Filetypes:": f"{filetypes}\n",
            "Instructions:": (
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
                "6. Confirm the operation if prompted.\n"
            ),
            "Note:": (
                "• There is no undo for this operation!\n"
                "• Use caution when renaming files.\n\n"
            ),
            "Hotkeys:": (
                "• Ctrl+Click: Select/Deselect\n"
                "• Ctrl+A: Select All\n"
                "• Ctrl+D: Deselect All\n"
                "• Ctrl+I: Invert Selection\n"
                "• F5: Refresh\n\n"
            ),
        }
        self.help_window.open_window(geometry="450x700", help_text=help_text)


#endregion
