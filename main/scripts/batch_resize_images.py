#region -  Imports


# Standard Library
import os
import time
import threading
import subprocess


# Standard Library - GUI
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# Third-Party Libraries
from PIL import Image, PngImagePlugin
from TkToolTip.TkToolTip import TkToolTip as ToolTip


# Local
from main.scripts import HelpText
from main.scripts.help_window import HelpWindow


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
################################################################################################################################################
#region - CLASS: ResizeImages


class BatchResizeImages:
    def __init__(self):
        self.parent: 'Main' = None
        self.root: 'tk.Tk' = None
        self.working_dir = None
        self.help_window = None

        self.resize_thread = None
        self.files_processed = 0
        self.supported_filetypes = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")


#endregion
################################################################################################################################################
#region -  Interface


    def setup_window(self, parent, root, path=None):
        self.parent = parent
        self.root = root
        self.working_dir = path
        self.help_window = HelpWindow(self.root)
        self.setup_ui()
        self.set_working_directory(path)


    def setup_ui(self):
        self.setup_primary_frame()
        self.setup_top_row()
        self.create_control_row()
        self.create_bottom_row()


        #self.additional_setup()


    def setup_primary_frame(self):
        # Configure the tab to expand properly
        self.parent.batch_resize_images_tab.grid_rowconfigure(0, weight=1)
        self.parent.batch_resize_images_tab.grid_columnconfigure(0, weight=1)
        # Create and configure the main frame
        self.batch_resize_images_frame = tk.Frame(self.parent.batch_resize_images_tab)
        self.batch_resize_images_frame.grid(row=0, column=0, sticky="nsew")
        # Configure the main frame's grid
        self.batch_resize_images_frame.grid_rowconfigure(1, weight=1)
        self.batch_resize_images_frame.grid_columnconfigure(0, weight=1)


    def setup_top_row(self):
        self.top_frame = tk.Frame(self.batch_resize_images_frame)
        self.top_frame.pack(fill="x", padx=2, pady=2)
        # Directory
        self.create_directory_row()
        # Help
        self.help_button = ttk.Button(self.top_frame, text="?", width=2, command=self.open_help_window)
        self.help_button.pack(side="left", fill="x", padx=2)
        ToolTip.create(self.help_button, "Show/Hide Help", delay=50, padx=6, pady=12)


    def create_directory_row(self):
        self.frame_top_row = tk.Frame(self.top_frame)
        self.frame_top_row.pack(side="left", fill="both", expand=True, padx=2)
        # Directory Entry
        self.entry_directory = ttk.Entry(self.frame_top_row)
        self.entry_directory.insert(0, os.path.normpath(self.working_dir) if self.working_dir else "...")
        self.entry_directory.pack(side="left", fill="x", expand=True, padx=2)
        self.entry_directory.bind("<Return>", lambda event: self.set_working_directory(self.entry_directory.get()))
        self.entry_directory.bind("<Button-1>", lambda event: self.entry_directory.delete(0, "end") if self.entry_directory.get() == "..." else None)
        # Browse
        self.browse_button = ttk.Button(self.frame_top_row, width=8, text="Browse...", command=self.set_working_directory)
        self.browse_button.pack(side="left", padx=2)
        # Open
        self.open_button = ttk.Button(self.frame_top_row, width=8, text="Open", command=self.open_folder)
        self.open_button.pack(side="left", padx=2)
        # Filetree
        self.file_tree_frame = ttk.Frame(self.batch_resize_images_frame)
        self.file_tree_frame.pack(side="top", fill="both", expand=True, padx=2, pady=2)
        self.file_tree = ttk.Treeview(self.file_tree_frame, columns=("Name", "Dimensions", "New Dimensions", "Type", "New Type"), show="headings", height=1)
        self.file_tree.heading("Name", text="Name")
        self.file_tree.heading("Dimensions", text="Dimensions")
        self.file_tree.heading("New Dimensions", text="New Dimensions")
        self.file_tree.heading("Type", text="Type")
        self.file_tree.heading("New Type", text="New Type")
        self.file_tree.column("Name", stretch=True)
        self.file_tree.column("Dimensions", width=160, stretch=False)
        self.file_tree.column("New Dimensions", width=160, stretch=False)
        self.file_tree.column("Type", width=100, stretch=False)
        self.file_tree.column("New Type", width=100, stretch=False)
        self.file_tree.pack(side="left", fill="both", expand=True)
        self.tree_scrollbar = ttk.Scrollbar(self.file_tree_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=self.tree_scrollbar.set)
        self.tree_scrollbar.pack(side="right", fill="y")


    def create_control_row(self):
        self.frame_control_row = ttk.Frame(self.batch_resize_images_frame)
        self.frame_control_row.pack(side="top", fill="x", padx=2, pady=2)
        self.create_resize_settings_frame()
        self.create_size_input_frame()
        self.create_options_frame()


    def create_resize_settings_frame(self):
        self.frame_resize_settings = ttk.LabelFrame(self.frame_control_row, text="Resize Settings")
        self.frame_resize_settings.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        # Resize Mode
        self.frame_resize_mode = tk.Frame(self.frame_resize_settings)
        self.frame_resize_mode.pack(side="top", anchor="w", padx=2, pady=2)
        self.resize_mode_label = tk.Label(self.frame_resize_mode, width=10, text="Resize To:")
        self.resize_mode_label.pack(side="left", padx=2, pady=2)
        self.resize_mode_var = tk.StringVar()
        self.resize_mode = ttk.Combobox(self.frame_resize_mode, width=21, textvariable=self.resize_mode_var, values=["Resolution", "Percentage", "Width", "Height", "Shorter Side", "Longer Side"], state="readonly")
        self.resize_mode.set("Resolution")
        self.resize_mode.pack(side="left", padx=2, pady=2)
        self.resize_mode.bind("<<ComboboxSelected>>", self.handle_combo_selection)
        # Resize Condition
        self.frame_resize_condition = tk.Frame(self.frame_resize_settings)
        self.frame_resize_condition.pack(side="top", anchor="w", padx=2, pady=2)
        self.resize_condition_label = tk.Label(self.frame_resize_condition, width=10, text="Condition:")
        self.resize_condition_label.pack(side="left", padx=2, pady=2)
        self.resize_condition_var = tk.StringVar()
        self.resize_condition = ttk.Combobox(self.frame_resize_condition, width=21, textvariable=self.resize_condition_var, values=["Upscale and Downscale", "Upscale Only", "Downscale Only"], state="readonly")
        self.resize_condition.set("Upscale and Downscale")
        self.resize_condition.pack(side="left", padx=2, pady=2)
        self.resize_condition.bind("<<ComboboxSelected>>", self.handle_combo_selection)
        # Filetype
        self.frame_filetype = tk.Frame(self.frame_resize_settings)
        self.frame_filetype.pack(side="top", anchor="w", padx=2, pady=2)
        self.filetype_label = tk.Label(self.frame_filetype, width=10, text="Filetype:")
        self.filetype_label.pack(side="left", padx=2, pady=2)
        self.filetype_var = tk.StringVar()
        self.filetype = ttk.Combobox(self.frame_filetype, width=6, textvariable=self.filetype_var, values=["AUTO", "JPEG", "PNG", "WEBP"], state="readonly")
        self.filetype.set("AUTO")
        self.filetype.pack(side="left", padx=2, pady=2)
        self.filetype.bind("<<ComboboxSelected>>", self.handle_combo_selection)


    def create_size_input_frame(self):
        self.frame_sizes = ttk.LabelFrame(self.frame_control_row, text="Size/Quality")
        self.frame_sizes.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        # Width Frame
        self.width_frame = tk.Frame(self.frame_sizes)
        self.width_frame.pack(side="top", anchor="w")
        self.width_label = tk.Label(self.width_frame, width=10, text="Width:")
        self.width_label.pack(side="left", padx=2, pady=2)
        self.width_entry = ttk.Entry(self.width_frame, width=20)
        self.width_entry.pack(side="left", padx=2, pady=2)
        self.width_entry.bind("<KeyRelease>", self.update_file_tree_info)
        # Height Frame
        self.height_frame = tk.Frame(self.frame_sizes)
        self.height_frame.pack(side="top", anchor="w")
        self.height_label = tk.Label(self.height_frame, width=10, text="Height:")
        self.height_label.pack(side="left", padx=2, pady=2)
        self.height_entry = ttk.Entry(self.height_frame, width=20)
        self.height_entry.pack(side="left", padx=2, pady=2)
        self.height_entry.bind("<KeyRelease>", self.update_file_tree_info)
        # Quality Frame
        self.frame_quality = tk.Frame(self.frame_sizes)
        self.frame_quality.pack(fill="x")
        self.quality_label = tk.Label(self.frame_quality, width=10, text="Quality:")
        self.quality_label.pack(side="left", padx=2, pady=2)
        self.quality_var = tk.IntVar(value=100)
        self.original_quality = self.quality_var.get()
        self.quality_scale = ttk.Scale(self.frame_quality, length=1, variable=self.quality_var, orient="horizontal", from_=20, to=100, command=lambda val: self.quality_var.set(int(float(val))))
        self.quality_scale.pack(side="left", fill="x", expand=True)
        self.quality_value_label = tk.Label(self.frame_quality, textvariable=self.quality_var, width=3)
        self.quality_value_label.pack(side="left", padx=2, pady=2)


    def create_options_frame(self):
        self.frame_checkbuttons = ttk.LabelFrame(self.frame_control_row, text="Options")
        self.frame_checkbuttons.pack(side="top", fill="both", expand=True, padx=2, pady=2)
        # Configure grid
        self.frame_checkbuttons.grid_columnconfigure(0, weight=1)
        self.frame_checkbuttons.grid_columnconfigure(1, weight=1)
        self.frame_checkbuttons.grid_rowconfigure(0, weight=1)
        self.frame_checkbuttons.grid_rowconfigure(1, weight=1)
        # Use output folder
        self.use_output_folder_var = tk.BooleanVar(value=True)
        self.use_output_folder_checkbutton = ttk.Checkbutton(self.frame_checkbuttons, text="Use Output Folder", variable=self.use_output_folder_var)
        self.use_output_folder_checkbutton.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        ToolTip.create(self.use_output_folder_checkbutton, "A new folder will be created in the selected directory called 'Resize Output' where images will be saved.", delay=250, padx=6, pady=12, wraplength=200)
        # Overwrite files
        self.overwrite_files_var = tk.BooleanVar(value=False)
        self.overwrite_files_checkbutton = ttk.Checkbutton(self.frame_checkbuttons, text="Overwrite Output", variable=self.overwrite_files_var)
        self.overwrite_files_checkbutton.grid(row=0, column=1, sticky="w", padx=2, pady=2)
        ToolTip.create(self.overwrite_files_checkbutton, "If enabled: Conflicting files will be overwritten.\nIf Disabled: Conflicting files will have '_#' appended to the filename.", delay=250, padx=6, pady=12, wraplength=200)
        # Save Chunk Info
        self.save_png_info_var = tk.BooleanVar(value=False)
        self.save_png_info_checkbutton = ttk.Checkbutton(self.frame_checkbuttons, text="Save PNG Info", variable=self.save_png_info_var)
        self.save_png_info_checkbutton.grid(row=1, column=0, sticky="w", padx=2, pady=2)
        ToolTip.create(self.save_png_info_checkbutton, "Auto-save PNG chunk info or create a text file on conversion.", delay=250, padx=6, pady=12, wraplength=200)
        # Convert Only
        self.convert_only_var = tk.BooleanVar(value=False)
        self.convert_only_checkbutton = ttk.Checkbutton(self.frame_checkbuttons, text="Convert Only", variable=self.convert_only_var, command=self.toggle_convert_only_mode)
        self.convert_only_checkbutton.grid(row=1, column=1, sticky="w", padx=2, pady=2)
        ToolTip.create(self.convert_only_checkbutton, "Ignore resize options and convert the images only.", delay=250, padx=6, pady=12, wraplength=200)


    def create_bottom_row(self):
        self.frame_bottom_row = tk.Frame(self.batch_resize_images_frame)
        self.frame_bottom_row.pack(side="bottom", fill="x")
        self.frame_buttons = tk.Frame(self.frame_bottom_row)
        self.frame_buttons.pack(fill="x")
        # Resize Button
        self.button_resize = ttk.Button(self.frame_buttons, text="Resize!", command=self.start_resize_process)
        self.button_resize.pack(side="left", fill="x", expand=True, padx=2, pady=2)
        # Cancel Button
        self.button_cancel = ttk.Button(self.frame_buttons, width=8, state="disabled", text="Cancel", command=lambda: setattr(self, 'stop', True))
        self.button_cancel.pack(side="left", fill="x", padx=2, pady=2)
        # Info Frame
        self.info_frame = tk.Frame(self.frame_bottom_row)
        self.info_frame.pack(fill="x")
        # Info Label
        self.info_label_total = tk.Label(self.info_frame, anchor="w", text="Total: 0", relief="groove", width=15)
        self.info_label_total.pack(side="left", fill="both", padx=2)
        self.info_label_processed = tk.Label(self.info_frame, anchor="w", text="Processed: 0", relief="groove", width=15)
        self.info_label_processed.pack(side="left", fill="both", padx=2)
        self.info_label_elapsed = tk.Label(self.info_frame, anchor="w", text="Elapsed: ..", relief="groove", width=15)
        self.info_label_elapsed.pack(side="left", fill="both", padx=2)
        self.info_label_eta = tk.Label(self.info_frame, anchor="w", text="ETA: ...", relief="groove", width=15)
        self.info_label_eta.pack(side="left", fill="both", padx=2)
        # Progress Bar
        self.percent_complete = tk.StringVar()
        self.percent_bar = ttk.Progressbar(self.info_frame, value=0, length=100, variable=self.percent_complete)
        self.percent_bar.pack(side="left", fill="both", expand=True, padx=2)


#endregion
################################################################################################################################################
#region -  UI Functions


    def handle_combo_selection(self, event=None):
        widget = event.widget
        if widget == self.filetype:
            self.update_quality_widgets()
        elif widget == self.resize_mode:
            self.update_entries()
        self.update_file_tree_info()



    def toggle_widgets(self, state):
            if state == "disabled":
                self.help_button.config(state=state)
                self.browse_button.config(state=state)
                #self.open_button.config(state=state)
                self.entry_directory.config(state=state)
                self.resize_mode.config(state=state)
                self.resize_condition.config(state=state)
                self.filetype.config(state=state)
                self.width_entry.config(state=state)
                self.height_entry.config(state=state)
                self.quality_scale.config(state=state)
                self.use_output_folder_checkbutton.config(state=state)
                self.overwrite_files_checkbutton.config(state=state)
                self.save_png_info_checkbutton.config(state=state)
                self.convert_only_checkbutton.config(state=state)
                self.button_resize.config(state=state)
            else:
                self.help_button.config(state=state)
                self.browse_button.config(state=state)
                #self.open_button.config(state=state)
                self.entry_directory.config(state=state)
                self.resize_mode.config(state="readonly")
                self.filetype.config(state="readonly")
                self.update_entries()
                self.update_quality_widgets()
                self.use_output_folder_checkbutton.config(state=state)
                self.overwrite_files_checkbutton.config(state=state)
                self.save_png_info_checkbutton.config(state=state)
                self.convert_only_checkbutton.config(state=state)
                self.button_resize.config(state=state)


    def update_quality_widgets(self, *args):
        if self.filetype_var.get() == "PNG":
            self.original_quality = self.quality_var.get()
            self.quality_scale.config(state="disabled")
            self.quality_label.config(state="disabled")
            self.quality_value_label.config(state="disabled")
            self.quality_var.set(100)
        else:
            self.quality_scale.config(state="normal")
            self.quality_label.config(state="normal")
            self.quality_value_label.config(state="normal")
            self.quality_var.set(self.original_quality)


    def update_entries(self, *args):
        mode = self.resize_mode_var.get()
        if mode == "Resolution":
            self.width_entry.config(state="normal")
            self.width_label.config(state="normal")
            self.height_entry.config(state="normal")
            self.height_label.config(state="normal")
            self.resize_condition_label.config(state="normal")
            self.resize_condition.config(state="readonly")
            self.width_label.config(text="Width:")
            self.height_label.config(text="Height:")
        elif mode == "Percentage":
            self.width_entry.config(state="normal")
            self.width_label.config(state="normal")
            self.height_entry.delete(0, 'end')
            self.height_entry.config(state="disabled")
            self.height_label.config(state="disabled")
            self.resize_condition_label.config(state="normal")
            self.resize_condition.config(state="disabled")
            self.width_label.config(text="%")
            self.height_label.config(text="-")
        elif mode in ["Width", "Shorter Side", "Longer Side"]:
            self.width_entry.config(state="normal")
            self.width_label.config(state="normal")
            self.height_entry.delete(0, 'end')
            self.height_entry.config(state="disabled")
            self.height_label.config(state="disabled")
            self.resize_condition_label.config(state="normal")
            self.resize_condition.config(state="readonly")
            if mode == "Width":
                self.width_label.config(text="Width:")
            else:
                self.width_label.config(text="Size")
            self.height_label.config(text="-")
        elif mode in ["Height"]:
            self.width_entry.delete(0, 'end')
            self.width_entry.config(state="disabled")
            self.width_label.config(state="disabled")
            self.height_entry.config(state="normal")
            self.height_label.config(state="normal")
            self.resize_condition_label.config(state="normal")
            self.resize_condition.config(state="readonly")
            self.width_label.config(text="-")
            self.height_label.config(text="Height:")


    def update_message_text(self, filecount=None, processed=None, elapsed=None, eta=None):
        if filecount:
            count = sum(1 for file in os.listdir(self.working_dir) if file.endswith(self.supported_filetypes))
            self.info_label_total.config(text=f"Total: {count}")
        if processed:
            self.info_label_processed.config(text=f"Processed: {processed}")
        if elapsed:
            self.info_label_elapsed.config(text=f"Elapsed: {elapsed}")
        if eta:
            self.info_label_eta.config(text=f"ETA: {eta}")


    def toggle_convert_only_mode(self):
        if self.convert_only_var.get():
            state = "disabled"
            self.resize_mode.config(state=state)
            self.resize_condition.config(state=state)
            self.width_entry.config(state=state)
            self.height_entry.config(state=state)
            self.update_file_tree_info()
            self.button_resize.config(text="Convert!")
        else:
            state = "normal"
            self.resize_mode.config(state="readonly")
            self.resize_condition.config(state=state)
            self.width_entry.config(state=state)
            self.height_entry.config(state=state)
            self.update_file_tree_info()
            self.update_quality_widgets()
            self.update_entries()
            self.button_resize.config(text="Resize!")


#endregion
################################################################################################################################################
#region -  Misc


    def set_working_directory(self, path=None):
        if self.is_resizing():
            return
        try:
            if path:
                new_folder_path = path
            else:
                new_folder_path = filedialog.askdirectory()
            if new_folder_path:
                self.working_dir = new_folder_path
                self.entry_directory.delete(0, "end")
                self.entry_directory.insert(0, new_folder_path)
                self.update_message_text(filecount=True)
                self.button_resize.config(state="normal")
                self.percent_complete.set(0)
                self.percent_bar['value'] = self.percent_complete.get()
                self.populate_file_tree()
                self.update_file_tree_info()
        except FileNotFoundError:
            messagebox.showinfo("Error", "The system cannot find the path specified.")
        except Exception as e:
            messagebox.showinfo("Error", str(e))


    def open_folder(self):
        try:
            os.startfile(self.working_dir)
        except FileNotFoundError:
            messagebox.showinfo("Error", "The system cannot find the path specified.")
        except Exception as e:
            messagebox.showinfo("Error", str(e))


    def get_output_folder_path(self):
        if self.use_output_folder_var.get() == 1:
            output_folder_path = os.path.join(self.working_dir, "Resize Output")
            if not os.path.exists(output_folder_path):
                os.makedirs(output_folder_path)
        else:
            output_folder_path = self.working_dir
        return output_folder_path


    def open_help_window(self):
        help_text = HelpText.BATCH_RESIZE_IMAGES_HELP
        self.help_window.open_window(geometry="450x700", help_text=help_text)


#endregion
################################################################################################################################################
#region -  Filetree Functions


    def populate_file_tree(self):
        self.file_tree.delete(*self.file_tree.get_children())
        if self.working_dir:
            files = [f for f in os.listdir(self.working_dir) if f.lower().endswith(self.supported_filetypes)]
            for file in files:
                filepath = os.path.join(self.working_dir, file)
                try:
                    with Image.open(filepath) as img:
                        width, height = img.size
                        dimensions = f"{width}x{height}"
                        file_ext = os.path.splitext(file)[1].lower()
                except:
                    dimensions = "-"
                    file_ext = "-"
                self.file_tree.insert("", "end", values=(file, dimensions, "-", file_ext, "-"))


    def update_file_tree_info(self, event=None):
        resize_mode = self.resize_mode_var.get()
        width_str = self.width_entry.get().strip()
        height_str = self.height_entry.get().strip()
        try:
            width = int(width_str) if width_str else None
        except ValueError:
            width = None
        try:
            height = int(height_str) if height_str else None
        except ValueError:
            height = None
        filetype_choice = self.filetype_var.get() if self.filetype_var.get() != "AUTO" else ""
        for child in self.file_tree.get_children():
            file_values = list(self.file_tree.item(child, "values"))
            orig_dim = file_values[1]
            if orig_dim == "-":
                continue
            w_orig, h_orig = [int(i) for i in orig_dim.split("x")]
            img_size = (w_orig, h_orig)
            if self.convert_only_var.get():
                file_values[2] = orig_dim
            else:
                new_size = self.simulate_new_size(img_size, resize_mode, width, height)
                if new_size:
                    new_w, new_h = new_size
                    file_values[2] = f"{new_w}x{new_h}"
            new_type = filetype_choice.upper() if filetype_choice else file_values[3]
            file_values[4] = new_type
            self.file_tree.item(child, values=file_values)


    def simulate_new_size(self, original_size, mode, w, h):
        try:
            if mode == "Resolution":
                new_w = w if w is not None else "-"
                new_h = h if h is not None else "-"
                new_size = (new_w, new_h)
            elif mode == "Percentage":
                if w is None:
                    new_size = ("-", "-")
                else:
                    ratio = w / 100.0
                    new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
            elif mode == "Width":
                if w is None:
                    new_size = ("-", "-")
                else:
                    ratio = w / float(original_size[0])
                    new_size = (w, int(original_size[1] * ratio))
            elif mode == "Height":
                if h is None:
                    new_size = ("-", "-")
                else:
                    ratio = h / float(original_size[1])
                    new_size = (int(original_size[0] * ratio), h)
            elif mode == "Shorter Side":
                if w is None:
                    new_size = ("-", "-")
                else:
                    if original_size[0] < original_size[1]:
                        ratio = w / float(original_size[0])
                        new_size = (w, int(original_size[1] * ratio))
                    else:
                        ratio = w / float(original_size[1])
                        new_size = (int(original_size[0] * ratio), w)
            elif mode == "Longer Side":
                if w is None:
                    new_size = ("-", "-")
                else:
                    if original_size[0] > original_size[1]:
                        ratio = w / float(original_size[0])
                        new_size = (w, int(original_size[1] * ratio))
                    else:
                        ratio = w / float(original_size[1])
                        new_size = (int(original_size[0] * ratio), w)
            else:
                new_size = ("-", "-")
            if (isinstance(new_size[0], int) and isinstance(new_size[1], int) and
                not self.should_resize(original_size, new_size)):
                return original_size
            return new_size
        except Exception:
            return None


#endregion
################################################################################################################################################
#region -  Resize


# --------------------------------------
# Input Validation
# --------------------------------------
    def validate_dimensions(self, width, height):
        if width is None or height is None:
            messagebox.showinfo("Error", "Please enter a valid width and height.")
            return False
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError("Width and height must be integers.")
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be greater than 0.")
        return True


    def validate_dimension(self, dimension):
        if dimension is None:
            messagebox.showinfo("Error", "Please enter a valid size.")
            return False
        if not isinstance(dimension, int):
            raise TypeError("Size must be an integer.")
        if dimension <= 0:
            raise ValueError("Size must be greater than 0.")
        return True


    def validate_percentage(self, percentage):
        if percentage is None:
            messagebox.showinfo("Error", "Please enter a valid percentage.")
            return False
        if not isinstance(percentage, (int, float)):
            raise TypeError("Percentage must be a number.")
        if percentage <= 0:
            raise ValueError("Percentage must be greater than 0.")
        return True


# --------------------------------------
# Resize Functions
# --------------------------------------
    def resize_to_resolution(self, img, width, height):
        if not self.validate_dimensions(width, height):
            return
        img = img.resize((width, height), Image.LANCZOS)
        return img


    def resize_to_percentage(self, img, percentage):
        if not self.validate_percentage(percentage):
            return
        width = int(img.size[0] * percentage)
        height = int(img.size[1] * percentage)
        img = img.resize((width, height), Image.LANCZOS)
        return img


    def resize_to_width(self, img, width):
        if not self.validate_dimension(width):
            return
        wpercent = (width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((width, hsize), Image.LANCZOS)
        return img


    def resize_to_height(self, img, height):
        if not self.validate_dimension(height):
            return
        hpercent = (height / float(img.size[1]))
        wsize = int((float(img.size[0]) * float(hpercent)))
        img = img.resize((wsize, height), Image.LANCZOS)
        return img


    def resize_to_shorter_side(self, img, size):
        if not self.validate_dimension(size):
            return
        if img.size[0] < img.size[1]:
            wpercent = (size / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((size, hsize), Image.LANCZOS)
        else:
            hpercent = (size / float(img.size[1]))
            wsize = int((float(img.size[0]) * float(hpercent)))
            img = img.resize((wsize, size), Image.LANCZOS)
        return img


    def resize_to_longer_side(self, img, size):
        if not self.validate_dimension(size):
            return
        if img.size[0] > img.size[1]:
            wpercent = (size / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((size, hsize), Image.LANCZOS)
        else:
            hpercent = (size / float(img.size[1]))
            wsize = int((float(img.size[0]) * float(hpercent)))
            img = img.resize((wsize, size), Image.LANCZOS)
        return img


# --------------------------------------
# Resize Conditions
# --------------------------------------
    def should_resize(self, original_size, new_size):
        if original_size == new_size:
            return False
        resize_condition = self.resize_condition_var.get()
        if resize_condition == "Upscale Only":
            return new_size > original_size
        elif resize_condition == "Downscale Only":
            return new_size < original_size
        elif resize_condition == "Percentage":
            return True
        else:  # "Upscale and Downscale"
            return True


    def calculate_resize_mode(self, img, resize_mode, width, height):
        original_size = img.size
        if resize_mode == "Resolution":
            new_size = (width, height)
            if self.should_resize(original_size, new_size):
                img = self.resize_to_resolution(img, width, height)
        elif resize_mode == "Percentage":
            percentage = width / 100
            new_size = (int(original_size[0] * percentage), int(original_size[1] * percentage))
            if self.should_resize(original_size, new_size):
                img = self.resize_to_percentage(img, percentage)
        elif resize_mode == "Width":
            new_size = (width, original_size[1])
            if self.should_resize(original_size, new_size):
                img = self.resize_to_width(img, width)
        elif resize_mode == "Height":
            new_size = (original_size[0], height)
            if self.should_resize(original_size, new_size):
                img = self.resize_to_height(img, height)
        elif resize_mode == "Shorter Side":
            new_size = (width, width)
            if self.should_resize(original_size, new_size):
                img = self.resize_to_shorter_side(img, width)
        elif resize_mode == "Longer Side":
            new_size = (height, height)
            if self.should_resize(original_size, new_size):
                img = self.resize_to_longer_side(img, width)
        return img


    def get_resize_confirmation(self, output_folder_path):
        output_folder_message = f"Images will be saved to:\n{os.path.normpath(output_folder_path)}"
        default_message = "Are you sure you want to continue?"
        confirm_message = output_folder_message if self.use_output_folder_var.get() == 1 else default_message
        return confirm_message


    def get_entry_values(self, silent=False):
        resize_mode = self.resize_mode_var.get()
        width_entry = self.width_entry.get()
        height_entry = self.height_entry.get()
        width = int(width_entry) if width_entry else None
        height = int(height_entry) if height_entry else None
        if resize_mode == "Resolution" and (width is None or height is None):
            if not silent:
                messagebox.showinfo("Error", "Please enter a valid width and height.")
            return None
        elif resize_mode == "Percentage" and width is None:
            if not silent:
                messagebox.showinfo("Error", "Please enter a valid percentage.")
            return None
        elif resize_mode in ["Width", "Shorter Side", "Longer Side"] and width is None:
            if not silent:
                messagebox.showinfo("Error", "Please enter a valid width.")
            return None
        elif resize_mode == "Height" and height is None:
            if not silent:
                messagebox.showinfo("Error", "Please enter a valid height.")
            return None
        return resize_mode, width, height


# --------------------------------------
# Primary Resize process
# --------------------------------------
    def start_resize_process(self):
        self.resize_thread = threading.Thread(target=self._resize_thread)
        self.resize_thread.start()


    def _resize_thread(self):
        self.percent_complete.set(0)
        self.stop = False
        self.files_processed = 0
        start_time = time.time()
        if self.working_dir is not None:
            if not self.stop:
                self.toggle_widgets(state="disabled")
                self.button_cancel.config(state="normal")
            try:
                # If not in convert-only mode, retrieve resize settings.
                if not self.convert_only_var.get():
                    result = self.get_entry_values()
                    if result is None:
                        return
                    resize_mode, width, height = result
                else:
                    # In convert-only mode we ignore resize settings.
                    resize_mode = None
                    width = None
                    height = None

                image_files = [file for file in os.listdir(self.working_dir) if file.endswith(self.supported_filetypes)]
                total_images = len(image_files)
                output_folder_path = self.get_output_folder_path()
                confirm_message = self.get_resize_confirmation(output_folder_path)
                if messagebox.askokcancel("Confirmation", confirm_message):
                    self.root.focus_force()
                    for image_index, filename in enumerate(image_files):
                        if self.stop:
                            self.button_cancel.config(state="disabled")
                            break
                        try:
                            img = Image.open(os.path.join(self.working_dir, filename))
                            if img is None:
                                return
                            img = img.convert('RGB')
                            # Only apply resizing if not in convert-only mode.
                            if not self.convert_only_var.get():
                                img = self.calculate_resize_mode(img, resize_mode, width, height)
                            dest_image_path = self.save_image(img, output_folder_path, filename, total_images)
                            src_image_path = os.path.join(self.working_dir, filename)
                            self.handle_metadata(filename, src_image_path, dest_image_path)
                            self.files_processed += 1
                            self.percent_complete.set((image_index + 1) / total_images * 100)
                            self.percent_bar['value'] = self.percent_complete.get()
                            self.percent_bar.update()
                            elapsed_time = time.time() - start_time
                            eta = (elapsed_time / (image_index + 1)) * (total_images - (image_index + 1))
                            elapsed_time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
                            eta_str = time.strftime('%H:%M:%S', time.gmtime(eta))
                            self.update_message_text(processed=self.files_processed, elapsed=elapsed_time_str, eta=eta_str)
                        except Exception as e:
                            messagebox.showerror("ERROR - _resize_thread()", str(e))
                    if not self.stop:
                        messagebox.showinfo("Done!", "Resizing finished." if not self.convert_only_var.get() else "Conversion finished.")
                        self.root.focus_force()
            except Exception as e:
                messagebox.showerror("ERROR - _resize_thread()", str(e))
            finally:
                self.button_resize.config(state="normal")
                self.toggle_widgets(state="normal")


    def is_resizing(self):
        return self.resize_thread is not None and self.resize_thread.is_alive()


    def save_image(self, img, output_folder_path, filename, total_images):
        if 'icc_profile' in img.info:
            del img.info['icc_profile']
        filetype = self.filetype_var.get().lower()
        base_filename, original_extension = os.path.splitext(filename)
        if filetype == "auto":
            filetype = original_extension[1:]
        filename_with_new_extension = f"{base_filename}.{filetype}"
        counter = 1
        if not self.overwrite_files_var.get():
            while os.path.exists(os.path.join(output_folder_path, filename_with_new_extension)):
                filename_with_new_extension = f"{base_filename}_{counter}.{filetype}"
                counter += 1
        img.save(os.path.join(output_folder_path, filename_with_new_extension), quality=self.quality_var.get(), optimize=True)
        return os.path.join(output_folder_path, filename_with_new_extension)


#endregion
################################################################################################################################################
#region -  Handle Metadata


    def handle_metadata(self, filename, src_image_path, output_image_path):
        if self.save_png_info_var.get():
            if filename.lower().endswith(".png"):
                if output_image_path.lower().endswith(".webp"):
                    self.copy_png_to_webp(src_image_path, output_image_path)
                else:
                    self.copy_png_metadata(src_image_path, output_image_path)
            if filename.lower().endswith(".webp"):
                self.copy_webp_metadata(src_image_path, output_image_path)


# --------------------------------------
# PNG
# --------------------------------------
    def read_png_metadata(self, src_image_path):
        src_image = Image.open(src_image_path)
        metadata = src_image.info
        metadata_text = ""
        pnginfo = PngImagePlugin.PngInfo()
        for key in metadata:
            if isinstance(metadata[key], bytes):
                value = metadata[key].decode('utf-8')
                pnginfo.add_text(key, value, 0)
            else:
                value = str(metadata[key])
                pnginfo.add_text(key, value, 0)
            metadata_text += f"{key}: {value}\n"
        return pnginfo, metadata_text


    def write_png_metadata(self, pnginfo, metadata_text, dest_image_path):
        dest_image = Image.open(dest_image_path)
        dest_image.save(dest_image_path, pnginfo=pnginfo)
        base_filename = os.path.basename(dest_image_path)
        dir_path = os.path.dirname(dest_image_path)
        if not base_filename.endswith('.png'):
            with open(os.path.join(dir_path, f"{base_filename}.txt"), "w", encoding="utf-8") as f:
                f.write(metadata_text)


    def copy_png_metadata(self, src_image_path, dest_image_path):
        pnginfo, metadata_text = self.read_png_metadata(src_image_path)
        self.write_png_metadata(pnginfo, metadata_text, dest_image_path)


    def copy_png_to_webp(self, src_image_path, dest_image_path):
        exiftool_path = "exiftool.exe"
        if os.path.exists(exiftool_path):
            src_image = Image.open(src_image_path)
            metadata = src_image.info
            metadata_str = ', '.join(f'{key}: {value}' for key, value in metadata.items())
            subprocess.run([exiftool_path, '-overwrite_original', f'-UserComment={metadata_str}', dest_image_path], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            self.stop = True
            messagebox.showerror("Error!",
                "Could not copy metadata from PNG-to-WEBP."
                "\n\nexiftool.exe does not exist in the root path. (Check spelling)"
                "\n\nDownload the Windows executable from exiftool.org and place in the same folder as batch_resize_images.exe, restart the program and try again."
                "\n\nThe resize operation will now stop."
            )


# --------------------------------------
# WEBP
# --------------------------------------
    def read_webp_metadata(self, src_image_path):
        process = subprocess.run(["exiftool.exe", '-UserComment', '-b', src_image_path], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        user_comment = process.stdout.strip()
        return user_comment


    def write_webp_metadata(self, user_comment, dest_image_path):
        base_filename = os.path.basename(dest_image_path)
        subprocess.run(["exiftool.exe", '-overwrite_original', f'-UserComment={user_comment}', dest_image_path], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if not base_filename.endswith('.webp'):
            with open(f"{base_filename}.txt", "w", encoding="utf-8") as f:
                f.write(user_comment)


    def copy_webp_metadata(self, src_image_path, dest_image_path):
        if os.path.exists("exiftool.exe"):
            user_comment = self.read_webp_metadata(src_image_path)
            self.write_webp_metadata(user_comment, dest_image_path)
        else:
            self.stop = True
            messagebox.showerror("Error!",
                "Could not copy metadata from WEBP-to-WEBP."
                "\n\nexiftool.exe does not exist in the root path. (Check spelling)"
                "\n\nDownload the Windows executable from exiftool.org and place in the same folder as batch_resize_images.exe, restart the program and try again."
                "\n\nThe resize operation will now stop."
            )
