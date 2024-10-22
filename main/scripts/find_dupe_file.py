"""
########################################
#           Find Dupe files            #
#   Version : v1.02                    #
#   Author  : github.com/Nenotriple    #
########################################

Description:
-------------
Scan a folder for duplicate images and/or all files by comparing their MD5 or SHA-256 hash.

"""


#endregion
################################################################################################################################################
#region -  Imports



# Standard Library
import os
import shutil
import hashlib
import threading


# Standard Library - GUI
from tkinter import (ttk, messagebox, simpledialog, filedialog,
                     StringVar, BooleanVar,
                     Menu, Text,
                     )


# Custom Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip


#endregion
################################################################################################################################################
#region -  Duplicate Image Finder - Main class setup


class FindDupeFile:
    def __init__(self):
        self.parent = None
        self.root = None
        self.version = None
        self.menu = None
        self.working_dir = None

        self.is_closing = False
        self.duplicates_count = 0
        self.total_duplicates = 0
        self.total_images_checked = 0
        self.max_scan_size = 2048 # in MB
        self.scanned_files = None
        self.startup = True

        self.filetypes_to_scan = ['All']

        self.process_stopped = BooleanVar(value=True)
        self.process_stopped.trace_add('write', self.toggle_widgets)

        self.process_mode = StringVar(value="md5")
        self.dupe_handling_mode = StringVar(value="Single")
        self.scanning_mode = StringVar(value="Images")
        self.recursive_mode = BooleanVar(value=False)


#endregion
################################################################################################################################################
#region -  Interface


    def setup_window(self, parent, root, version, menu, path=None):
        self.parent = parent
        self.root = root
        self.version = version
        self.menu = menu
        self.working_dir = path

        self.root.minsize(750, 250) # Width x Height
        self.root.title(f"{self.version} - img-txt Viewer - Find Duplicate Files")
        self.menu.entryconfig("Find Duplicate Files...", command=self.close_find_dupe_files)
        self.setup_ui()

        if path:
            self.folder_entry.insert(0, path)

        self.all_widgets = [
                             self.file_menu_button,
                             self.options_menu_button,
                             self.folder_entry,
                             self.browse_button,
                             #self.open_button,
                             self.clear_button,
                             self.radio_single,
                             self.radio_both,
                             self.undo_button,
                             self.run_button,
                             #self.stop_button,
                             self.radio_images,
                             self.radio_all_files,
                             self.recursive_checkbutton,
                             #self.textlog,
                             #tray_label_status,
                             #self.tray_label_duplicates,
                             #self.progress,
                             ]


    def setup_ui(self):
        self.setup_primary_frame()
        self.setup_top_row()
        self.create_widgets()


    def setup_primary_frame(self):
        self.parent.hide_primary_paned_window()
        self.find_dupe_files_frame = ttk.Frame(self.root)
        self.find_dupe_files_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=(0,20))
        self.find_dupe_files_frame.grid_rowconfigure(1, weight=1)
        self.find_dupe_files_frame.grid_columnconfigure(1, weight=1)


# --------------------------------------
# Top Row / Menubar
# --------------------------------------
    def setup_top_row(self):
        self.top_frame = ttk.Frame(self.find_dupe_files_frame)
        self.top_frame.pack(fill="x", padx=2, pady=2)

        self.close_button = ttk.Button(self.top_frame, text="<---Close", width=15, command=self.close_find_dupe_files)
        self.close_button.pack(side="left", fill="x", padx=2, pady=2)

        self.create_menubar()

        self.help_button = ttk.Button(self.top_frame, text="?", width=2)
        self.help_button.pack(side="right", fill="x", padx=2, pady=2)
        ToolTip.create(self.help_button, "Show/Hide Help", 50, 6, 12)


    def create_menubar(self):
        # File Menu
        self.file_menu_button = ttk.Menubutton(self.top_frame, text="File")
        self.file_menu = Menu(self.file_menu_button, tearoff=0)
        self.file_menu_button.config(menu=self.file_menu)
        self.file_menu.add_command(label="Select Folder...", command=self.select_folder)
        self.file_menu.add_command(label="Open Folder...", command=self.open_folder)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Restore Moved Duplicates", command=self.undo_file_move)
        self.file_menu.add_command(label="Move All Duplicates Upfront", command=self.move_all_duplicates_to_root)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Delete All Duplicates", command=self.delete_all_duplicates)
        self.file_menu_button.pack(side="left")

        # Options Menu
        self.options_menu_button = ttk.Menubutton(self.top_frame, text="Options")
        self.options_menu = Menu(self.options_menu_button, tearoff=0)
        self.options_menu_button.config(menu=self.options_menu)
        self.options_menu_button.pack(side="left")

        # Process Mode Menu
        self.process_mode_menu = Menu(self.options_menu, tearoff=0)
        self.options_menu.add_cascade(label="Process Mode", menu=self.process_mode_menu)
        self.process_mode_menu.add_radiobutton(label="MD5 - Fast", variable=self.process_mode, value="md5")
        self.process_mode_menu.add_radiobutton(label="SHA-256 - Slow", variable=self.process_mode, value="sha-256")

        # Scanning Options Menu
        self.scan_options_menu = Menu(self.options_menu, tearoff=0)
        self.options_menu.add_cascade(label="Scanning Options", menu=self.scan_options_menu)
        self.scan_options_menu.add_command(label="Set Max Scan Size...", command=self.open_max_scan_size_dialog)
        self.scan_options_menu.add_command(label="Set Filetypes to Scan...", command=self.open_filetypes_dialog)
        self.scan_options_menu.add_separator()
        self.scan_options_menu.add_checkbutton(label="Use Recursive Scanning", variable=self.recursive_mode)
        self.scan_options_menu.add_separator()

        # Scanning Mode Menu
        self.scanning_mode_menu = Menu(self.scan_options_menu, tearoff=0)
        self.scan_options_menu.add_cascade(label="Set Scanning Mode", menu=self.scanning_mode_menu)
        self.scanning_mode_menu.add_radiobutton(label="Images", variable=self.scanning_mode, value="Images")
        self.scanning_mode_menu.add_radiobutton(label="All Files", variable=self.scanning_mode, value="All Files")

        # Duplication Handling Menu
        self.duplication_handling_menu = Menu(self.options_menu, tearoff=0)
        self.options_menu.add_cascade(label="Duplication Handling", menu=self.duplication_handling_menu)
        self.duplication_handling_menu.add_radiobutton(label="Single", variable=self.dupe_handling_mode, value="Single")
        self.duplication_handling_menu.add_radiobutton(label="Both", variable=self.dupe_handling_mode, value="Both")


# --------------------------------------
# General Widgets
# --------------------------------------
    def create_widgets(self):
        # Frame - Widget Frame
        self.widget_frame = ttk.Frame(self.find_dupe_files_frame)
        self.widget_frame.pack(side="top", fill="both", padx=4, pady=4)


        # Frame - Folder Frame
        self.folder_frame = ttk.Frame(self.widget_frame)
        self.folder_frame.pack(fill="both", expand=True)

        # Entry - Folder Entry
        self.folder_entry = ttk.Entry(self.folder_frame)
        self.folder_entry.pack(side="left", fill="x", expand=True)

        # Button - Browse
        self.browse_button = ttk.Button(self.folder_frame, text="Browse...", command=self.select_folder)
        ToolTip.create(self.browse_button, "Select a folder to analyze for duplicate files.", delay=150, padx=6, pady=6)
        self.browse_button.pack(side="left")

        # Button - Open
        self.open_button = ttk.Button(self.folder_frame, text="Open", command=self.open_folder)
        ToolTip.create(self.open_button, "Open path from folder entry.", delay=150, padx=6, pady=6)
        self.open_button.pack(side="left")

        # Button - Clear
        self.clear_button = ttk.Button(self.folder_frame, text="X", width=2, command=lambda: self.folder_entry.delete(0, 'end'))
        ToolTip.create(self.clear_button, "Clear folder entry.", delay=150, padx=6, pady=6)
        self.clear_button.pack(side="left")


        # Radio Buttons - Duplicate Handling Mode
        self.radio_single = ttk.Radiobutton(self.widget_frame, text="Single", variable=self.dupe_handling_mode, value="Single")
        ToolTip.create(self.radio_single, "Move extra duplicate files, leaving a copy behind.\nFiles will be stored in the '_Duplicate__Files' folder located in the parent folder.", delay=150, padx=6, pady=6)
        self.radio_single.pack(side="left")
        self.radio_both = ttk.Radiobutton(self.widget_frame, text="Both", variable=self.dupe_handling_mode, value="Both")
        ToolTip.create(self.radio_both, "Move all duplicate files, leaving no copy behind.\nFiles will be stored in the '_Duplicate__Files' folder located in the parent folder.\nDuplicates will be grouped into subfolders.", delay=150, padx=6, pady=6)
        self.radio_both.pack(side="left")

        # Button - Undo
        self.undo_button = ttk.Button(self.widget_frame, text="Undo", width=6, command=self.undo_file_move)
        ToolTip.create(self.undo_button, "Restore all files to their original path.\nEnable 'Recursive' To also restore all files within subfolders.", delay=150, padx=6, pady=6)
        self.undo_button.pack(side="left")

        # Button - Run
        self.run_button = ttk.Button(self.widget_frame, text="Find Duplicates", command=self.find_duplicates)
        ToolTip.create(self.run_button, "Process the selected folder.", delay=1000, padx=6, pady=6)
        self.run_button.pack(side="left", fill="x", expand=True)

        # Button - Stop
        self.stop_button = ttk.Button(self.widget_frame, text="Stop!", width=6, command=self.stop_process)
        ToolTip.create(self.stop_button, "Stop all running processes.", delay=150, padx=6, pady=6)
        self.stop_button.pack(side="left", fill="x")

        # Radio Buttons - Scanning Mode
        self.radio_images = ttk.Radiobutton(self.widget_frame, text="Images", variable=self.scanning_mode, value="Images")
        ToolTip.create(self.radio_images, "Scan only image filetypes.", delay=150, padx=6, pady=6)
        self.radio_images.pack(side="left")
        self.radio_all_files = ttk.Radiobutton(self.widget_frame, text="All Files", variable=self.scanning_mode, value="All Files")
        ToolTip.create(self.radio_all_files, "Scan all filetypes.", delay=150, padx=6, pady=6)
        self.radio_all_files.pack(side="left")

        # Checkbutton - Subfolder Scanning
        self.recursive_checkbutton = ttk.Checkbutton(self.widget_frame, text="Recursive", variable=self.recursive_mode, offvalue=False)
        ToolTip.create(self.recursive_checkbutton, "Enable to scan subfolders.\nNOTE: This only compares files within the same subfolder, not across all scanned folders.", delay=150, padx=6, pady=6)
        self.recursive_checkbutton.pack(side="left")


        # Textlog
        self.create_textlog()
        self.startup_text = ("This tool will find any duplicate files by matching file hash.\n\nDuplicate files will be moved to a '_Duplicate__Files' folder within the scanned directory.")
        self.insert_to_textlog(self.startup_text)


        # Label - Tray - Status
        self.tray_label_status = ttk.Label(self.find_dupe_files_frame, width=15, relief="groove", text=" Idle...")
        ToolTip.create(self.tray_label_status, "App status.", delay=150, padx=6, pady=6)
        self.tray_label_status.pack(side="left", padx=2, ipadx=2, ipady=2)

        # Label - Tray - Total Duplicates
        self.tray_label_duplicates = ttk.Label(self.find_dupe_files_frame, width=15, relief="groove", text="Duplicates: 00000")
        ToolTip.create(self.tray_label_duplicates, "Total number of duplicate files across all scanned folders.", delay=150, padx=6, pady=6)
        self.tray_label_duplicates.pack(side="left", padx=2, ipadx=2, ipady=2)

        # Label - Tray - Total Images Checked
        self.tray_label_total_files = ttk.Label(self.find_dupe_files_frame, width=19, relief="groove", text="Files Checked: 000000")
        ToolTip.create(self.tray_label_total_files, "Total number of files checked across all scanned folders.", delay=150, padx=6, pady=6)
        self.tray_label_total_files.pack(side="left", padx=2, ipadx=2, ipady=2)

        # Progressbar
        self.progress = ttk.Progressbar(self.find_dupe_files_frame, length=100, mode='determinate')
        ToolTip.create(self.progress, "Progressbar.", delay=150, padx=6, pady=6)
        self.progress.pack(side="left", fill="x", padx=2, expand=True)


# --------------------------------------
# Textlog
# --------------------------------------
    def create_textlog(self):
        separator = ttk.Separator(self.find_dupe_files_frame)
        separator.pack(fill="x")
        text_frame = ttk.Frame(self.find_dupe_files_frame)
        text_frame.pack(side="top", expand="yes", fill="both", padx="2", pady="2")
        vscrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        hscrollbar = ttk.Scrollbar(text_frame, orient="horizontal")
        self.textlog = Text(text_frame, height=1, wrap="none", state='disabled', yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set, font=("Consolas", 8))
        vscrollbar.grid(row=0, column=1, sticky="ns")
        hscrollbar.grid(row=1, column=0, sticky="we")
        self.textlog.grid(row=0, column=0, sticky="nsew")
        vscrollbar.config(command=self.textlog.yview)
        hscrollbar.config(command=self.textlog.xview)
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)


#endregion
################################################################################################################################################
#region -  Textlog Helpers


    def insert_to_textlog(self, text):
        try:
            self.textlog.config(state='normal')
            self.textlog.insert('end', text)
            self.textlog.see('end')
            self.textlog.config(state='disabled')
        except RuntimeError: pass


    def check_and_clear_textlog(self):
        if self.startup == False:
            return
        textlog_content = self.textlog.get("1.0", 'end-1c')
        if self.startup_text in textlog_content:
            self.textlog.config(state='normal')
            self.textlog.delete('1.0', 'end')
            self.textlog.config(state='disabled')
            self.startup = False


#endregion
################################################################################################################################################
#region -  Find Duplicates


    def find_duplicates(self):
        self.duplicates_count = 0
        self.total_duplicates = 0
        self.total_images_checked = 0
        self.tray_label_duplicates.config(text="Duplicates: 00000")
        self.tray_label_total_files.config(text="Files Checked: 000000")
        if not self.folder_entry.get():
            return
        self.check_and_clear_textlog()
        if self.process_stopped.get() == True:
            self.process_stopped.set(False)
            threading.Thread(target=self._find_duplicates).start()


    def _find_duplicates(self):
        folder_path = self.folder_entry.get()
        if os.path.isdir(folder_path):
            if self.recursive_mode.get():
                for root, dirs, files in os.walk(folder_path):
                    if self.process_stopped.get():
                        break
                    self.scan_folder(root)
            else:
                self.scan_folder(folder_path)
        self.process_stopped.set(True)


    def scan_folder(self, folder_path):
        hash_dict = {}
        displayed_folder_path = folder_path.replace("\\", "/")
        self.insert_to_textlog(f"\n\nScanning... \nFolder Path: {displayed_folder_path}")
        self.tray_label_status.config(text=" Scanning...")
        duplicates_folder = os.path.join(folder_path, '_Duplicate__Files')
        duplicates_found = False
        self.scanned_files = list(self.get_files(folder_path))
        self.insert_to_textlog(f"\nTotal files to check: {len(self.scanned_files)}")
        self.update_total_images()
        self.progress['maximum'] = len(self.scanned_files)
        self.duplicates_count = 0
        for i, filename in enumerate(self.scanned_files, start=1):
            if self.process_stopped.get():
                break
            file_path = os.path.join(folder_path, filename)
            if os.path.commonpath([file_path, duplicates_folder]) == duplicates_folder or filename.startswith('.'):
                continue
            try:
                file_hash = self.get_file_hash(file_path)
                if file_hash is None:
                    continue
                if file_hash in hash_dict:
                    self.insert_to_textlog(f"\nDuplicate found: {os.path.basename(file_path)} == {os.path.basename(hash_dict[file_hash])}")
                    self.duplicates_count += 1
                    if not duplicates_found:
                        os.makedirs(duplicates_folder, exist_ok=True)
                        duplicates_found = True
                    if self.dupe_handling_mode.get() == "Both":
                        group_folder = os.path.join(duplicates_folder, file_hash)
                        os.makedirs(group_folder, exist_ok=True)
                        shutil.move(file_path, group_folder)
                        if os.path.exists(hash_dict[file_hash]):
                            shutil.move(hash_dict[file_hash], group_folder)
                    else:
                        shutil.move(file_path, duplicates_folder)
                else:
                    hash_dict[file_hash] = file_path
                self.progress['value'] = i
                self.root.update()
            except Exception as e:
                self.insert_to_textlog(f"\nERROR - find_duplicates: Exception: {e}")
        self.update_total_duplicates()
        self.status_check()
        if self.process_stopped.get() == False:
            self.insert_to_textlog(f"\nTotal duplicates found: {self.duplicates_count}")


    def get_files(self, folder_path):
        try:
            self.tray_label_status.config(text=" Building Lists...")
            duplicates_folder = os.path.join(folder_path, '_Duplicate__Files')
            with os.scandir(folder_path) as entries:
                for entry in entries:
                    if entry.is_file() and entry.stat().st_size <= self.max_scan_size * 1024 * 1024:
                        if os.path.commonpath([entry.path, duplicates_folder]) == duplicates_folder:
                            continue
                        if self.filetypes_to_scan == ['All'] or entry.name.endswith(tuple(self.filetypes_to_scan)):
                            if self.scanning_mode.get() == "Images" and self.is_image(entry.path):
                                yield entry.name
                            elif self.scanning_mode.get() == "All Files":
                                yield entry.name
        except Exception as e:
            self.insert_to_textlog(f"ERROR - get_files: Exception: {str(e)}")


    def is_image(self, file_path):
        image_file_extensions = ['.blp', '.bmp', '.dds','.dib', '.eps',
                                 '.gif', '.icns', '.ico', '.im', '.jpg',
                                 '.jpeg', '.jfif', '.jp2', '.jpx', '.msp',
                                 '.pcx', '.png', '.apng', '.ppm', '.sgi',
                                 '.spider', '.tga', '.tif', '.tiff', '.webp',
                                 '.xbm', '.cur', '.dcx', '.fits', '.fli',
                                 '.flc', '.fpx', '.ftex', '.gbr', '.gd',
                                 '.imt', '.naa', '.mcidas', '.mic', '.mpo',
                                 '.pcd', '.pixar', '.psd', '.qoi', '.sun',
                                 '.wal', '.wmf', '.emf', '.xpm', '.palm', '.pdf', '.xv']
        _, file_extension = os.path.splitext(file_path)
        return file_extension.lower() in image_file_extensions


    def get_file_hash(self, file_path):
        try:
            self.tray_label_status.config(text=" Comparing...")
            with open(file_path, 'rb') as f:
                if self.process_mode.get() == "md5":
                    return hashlib.md5(f.read()).hexdigest()
                elif self.process_mode.get() == "sha-256":
                    return hashlib.sha256(f.read()).hexdigest()
        except IOError:
            self.insert_to_textlog(f"\nERROR - get_file_hash: Cannot open file at {file_path}")
            return None


    def stop_process(self):
        self.progress['value'] = 0
        if self.process_stopped.get() == False:
            self.insert_to_textlog("\n\nStopping...\n")
            self.process_stopped.set(True)
            self.undo_file_move()


#endregion
################################################################################################################################################
#region -  Undo


    def undo_file_move(self):
        self.file_count = 0
        self.progress['value'] = 0
        self.total_files = self.count_total_files()
        self.progress['maximum'] = self.total_files
        try:
            if self.recursive_mode.get():
                for root, dirs, files in os.walk(self.folder_entry.get()):
                    self.undo_folder(root)
            else:
                self.undo_folder(self.folder_entry.get())
        except Exception as e:
            self.insert_to_textlog(f"\nERROR - get_files_to_undo: Exception: {e}")
        finally:
            if self.file_count != 0:
                self.insert_to_textlog(f"\n\nRestoring {self.file_count} files")
                self.status_check()


    def count_total_files(self):
        try:
            total_files = 0
            duplicates_folder = os.path.join(self.folder_entry.get(), '_Duplicate__Files')
            if os.path.exists(duplicates_folder):
                for root, dirs, files in os.walk(duplicates_folder):
                    total_files += len(files)
            return total_files
        except Exception as e:
            self.insert_to_textlog(f"ERROR - count_total_files: Exception: {str(e)}")
            return None


    def undo_folder(self, folder_path):
        try:
            duplicates_folder = os.path.join(folder_path, '_Duplicate__Files')
            if not os.path.exists(duplicates_folder):
                return
            for filename in os.listdir(duplicates_folder):
                if os.path.isfile(os.path.join(duplicates_folder, filename)):
                    shutil.move(os.path.join(duplicates_folder, filename), folder_path)
                    self.file_count += 1
                    self.progress['value'] = self.file_count
                elif os.path.isdir(os.path.join(duplicates_folder, filename)):
                    for sub_filename in os.listdir(os.path.join(duplicates_folder, filename)):
                        shutil.move(os.path.join(duplicates_folder, filename, sub_filename), folder_path)
                        self.file_count += 1
                        self.progress['value'] = self.file_count
                    os.rmdir(os.path.join(duplicates_folder, filename))
            os.rmdir(duplicates_folder)
        except Exception as e:
            self.insert_to_textlog(f"\nERROR - undo_folder: Exception: {e}")


#endregion
################################################################################################################################################
#region -  Delete Duplicates


    def delete_all_duplicates(self):
        try:
            if not messagebox.askokcancel("Warning", "CAUTION!\n\nAll folders with the name '_Duplicate__Files' will be deleted along with all file in those folders.\n\nTHIS CANNOT BE UNDONE!!!"):
                return
            if not messagebox.askokcancel("Final Warning", "Are you sure you want to delete all duplicates?"):
                return
            if self.recursive_mode.get():
                for root, dirs, files in os.walk(self.folder_entry.get()):
                    self.delete_folder(root)
            else:
                self.delete_folder(self.folder_entry.get())
        except Exception as e:
            self.insert_to_textlog(f"\nERROR - delete_all_duplicates: Exception: {e}")


    def delete_folder(self, folder_path):
        try:
            duplicates_folder = os.path.join(folder_path, '_Duplicate__Files')
            if not os.path.exists(duplicates_folder):
                return
            self.insert_to_textlog(f"\n\nDeleting duplicates...\nDeleting: {os.path.normpath(duplicates_folder)}")
            for filename in os.listdir(duplicates_folder):
                file_path = os.path.join(duplicates_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            os.rmdir(duplicates_folder)
            self.insert_to_textlog(f"\nAll files deleted successfully!")
        except Exception as e:
            self.insert_to_textlog(f"\nERROR - delete_folder: Exception: {e}")


#endregion
################################################################################################################################################
#region -  Move Duplicate Upfront


    def move_all_duplicates_to_root(self):
        try:
            root_path = self.folder_entry.get()
            root_duplicates_folder = os.path.join(root_path, '_Duplicate__Files')
            if not os.path.exists(root_duplicates_folder):
                os.makedirs(root_duplicates_folder)
            if not messagebox.askyesno("Confirmation", "Are you sure you want to move all duplicates to the root '_Duplicate__Files' folder?\n\nYou cannot undo this action!"):
                return
            for folder_path, dirs, files in os.walk(root_path):
                if folder_path == root_duplicates_folder:
                    continue
                duplicates_folder = os.path.join(folder_path, '_Duplicate__Files')
                if os.path.exists(duplicates_folder):
                    for filename in os.listdir(duplicates_folder):
                        file_path = os.path.join(duplicates_folder, filename)
                        new_file_path = os.path.join(root_duplicates_folder, filename)
                        if os.path.isfile(file_path):
                            counter = 1
                            while os.path.exists(new_file_path):
                                base, ext = os.path.splitext(filename)
                                new_file_path = os.path.join(root_duplicates_folder, f"{base}_{counter}{ext}")
                                counter += 1
                            shutil.move(file_path, new_file_path)
                        elif os.path.isdir(file_path):
                            for sub_filename in os.listdir(file_path):
                                sub_file_path = os.path.join(file_path, sub_filename)
                                new_sub_file_path = os.path.join(root_duplicates_folder, sub_filename)
                                counter = 1
                                while os.path.exists(new_sub_file_path):
                                    base, ext = os.path.splitext(sub_filename)
                                    new_sub_file_path = os.path.join(root_duplicates_folder, f"{base}_{counter}{ext}")
                                    counter += 1
                                shutil.move(sub_file_path, new_sub_file_path)
                            if not os.listdir(file_path):
                                os.rmdir(file_path)
                    if not os.listdir(duplicates_folder):
                        os.rmdir(duplicates_folder)
        except Exception as e:
            self.insert_to_textlog(f"\nERROR - move_all_duplicates_to_root: Exception: {e}")


#endregion
################################################################################################################################################
#region -  Settings Dialog


    # Set max image scanning size
    def open_max_scan_size_dialog(self):
        temp = simpledialog.askinteger("Input", f"Current Max Scan Size: {self.max_scan_size} MB\n\nEnter Max Scan Size in megabytes (MB)\nExample (1GB): 1024")
        if temp is not None:
            self.max_scan_size = temp


    # Set filetypes to scan
    def open_filetypes_dialog(self):
        current_filetypes = ', '.join(self.filetypes_to_scan)
        new_filetypes = simpledialog.askstring("Input", f"Current filetypes: {current_filetypes}\n\nEnter filetypes you want to scan. Unlisted filetypes will be skipped.\n\nEnter: 'All' to return to default.\n\nExample: .jpg, .png, .txt", parent=self.root)
        if new_filetypes is not None and new_filetypes.strip() != '':
            self.filetypes_to_scan = [ftype.strip() for ftype in new_filetypes.split(',')]


#endregion
################################################################################################################################################
#region -  Handle Widget States


    def disable_all(self):
        widgets_to_disable = self.all_widgets
        for widgets in widgets_to_disable:
            widgets.config(state="disabled")
        #for menu_item in ["File", "Options"]:
        #    self.menubar.entryconfig(menu_item, state="disabled")


    def enable_all(self):
        widgets_to_disable = self.all_widgets
        for widgets in widgets_to_disable:
            widgets.config(state="normal")
        #for menu_item in ["File", "Options"]:
        #    self.menubar.entryconfig(menu_item, state="normal")


    def toggle_widgets(self, *args):
        if self.process_stopped.get():
            self.enable_all()
        else:
            self.disable_all()


#endregion
################################################################################################################################################
#region -  Misc


    def select_folder(self):
        new_folder_path = filedialog.askdirectory()
        if new_folder_path:
            self.tray_label_duplicates.config(text="Duplicates: 00000")
            self.tray_label_total_files.config(text="Files Checked: 000000")
            self.progress['value'] = 0
            self.working_dir = new_folder_path
            self.folder_entry.delete(0, 'end')
            self.folder_entry.insert(0, self.working_dir)


    def open_folder(self):
        folder_path = self.folder_entry.get()
        if os.path.exists(folder_path):
            os.startfile(folder_path)
        else:
            messagebox.showinfo("Invalid Path", "The folder path is invalid or does not exist.")


    def status_check(self):
        if self.is_closing == False:
            self.tray_label_status.config(text=" Idle...")
        else:
            self.tray_label_status.config(text=" Closing...")


    def update_total_images(self):
        self.total_images_checked += len(self.scanned_files)
        self.tray_label_total_files.config(text=f"Files Checked: {self.total_images_checked:06d}")


    def update_total_duplicates(self):
        self.total_duplicates += self.duplicates_count
        self.tray_label_duplicates.config(text=f"Duplicates: {self.total_duplicates:05d}")


#endregion
################################################################################################################################################
#region -  Framework


    def close_find_dupe_files(self):
        self.is_closing = True
        self.stop_process()
        self.status_check()
        self.root.after(1000, self._close_find_dupe_files)


    def _close_find_dupe_files(self):
        self.root.minsize(545, 200) # Width x Height
        self.root.title(f"{self.version} - img-txt Viewer")
        self.find_dupe_files_frame.grid_remove()
        self.menu.entryconfig("Find Duplicate Files...", command=self.parent.show_find_dupe_file)
        self.parent.show_primary_paned_window()


#endregion

'''

v1.02 changes:

  - New:
    -


<br>

  - Fixed:
    -

<br>

  - Other changes:
    - Refactored to be a built-in tool.

<br>

  - To fix:
    -

'''