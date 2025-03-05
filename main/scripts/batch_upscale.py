#region -  Imports


# Standard Library
import os
import time
import shutil
import threading
import subprocess


# Standard Library - GUI
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# Third-Party Libraries
from PIL import Image, ImageSequence
from TkToolTip.TkToolTip import TkToolTip as ToolTip


# Custom Libraries
from main.scripts import HelpText
from main.scripts.help_window import HelpWindow
import main.scripts.entry_helper as entry_helper


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
################################################################################################################################################
#region - CLS BatchUpscale


class BatchUpscale:
    def __init__(self):
        self.parent: 'Main' = None
        self.root: 'tk.Tk' = None
        self.working_dir = None
        self.help_window = None
        self.entry_helper = entry_helper

        # Other Filepaths
        self.executable_path = None
        self.converted_filepath = None
        self.working_img_path = None

        # Supported Filetypes
        self.supported_filetypes = (".png", ".webp", ".jpg", ".jpeg", ".jpg_large", ".jfif", ".tif", ".tiff", ".bmp", ".gif")

        # Included Models
        self.ncnn_models = ["realesr-animevideov3-x4", "RealESRGAN_General_x4_v3", "realesrgan-x4plus", "realesrgan-x4plus-anime", "AnimeSharp-4x", "UltraSharp-4x"]
        self.extra_models_path = None

        # Batch Mode
        self.batch_thread_var = False
        self.batch_mode_var = tk.BooleanVar(value=True)
        self.input_path_var = tk.StringVar(value="")
        self.output_path_var = tk.StringVar(value="")

        # Other Variables
        self.total_images = 0
        self.auto_output_var = tk.BooleanVar(value=True)


    def setup_window(self, parent, root):
        self.parent = parent
        self.root = root
        self.working_dir = self.parent.image_dir.get()
        self.help_window = HelpWindow(self.root)

        self.working_img_path = self.parent.image_files[self.parent.current_index]
        self.executable_path = os.path.join(self.parent.application_path, "main/resrgan/realesrgan-ncnn-vulkan.exe")
        self.extra_models_path = os.path.join(self.parent.application_path, "ncnn_models".lower())
        self.ncnn_models = self.find_additional_models()
        self.input_path_var.set(self.working_dir)
        self.output_path_var.set(value=os.path.join(self.input_path_var.get(), "Upscale_Output"))
        self.total_images = len([file for file in os.listdir(self.working_dir) if file.lower().endswith(self.supported_filetypes)])

        self.setup_ui()
        self.populate_file_tree()
        self.highlight_parent_image()


#endregion
################################################################################################################################################
#region -  Interface


    def setup_ui(self):
        self.setup_primary_frame()
        self.create_bottom_row()
        self.create_path_selection_widgets()
        self.create_file_tree()
        self.create_upscale_settings_widgets()


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


    def create_bottom_row(self):
        self.frame_bottom_row = tk.Frame(self.batch_upscale_frame)
        self.frame_bottom_row.pack(side="bottom", fill="both")
        button_fame = tk.Frame(self.frame_bottom_row)
        button_fame.pack(side="top", fill="x")
        # Upscale
        self.button_upscale = ttk.Button(button_fame, text="Upscale", command=self.determine_image_type)
        self.button_upscale.pack(side="left", fill="x", expand=True)
        # Refresh
        self.button_refresh = ttk.Button(button_fame, text="Refresh", command=self.refresh_files)
        self.button_refresh.pack(side="left", fill="x")
        # Cancel
        self.button_cancel = ttk.Button(button_fame, text="Cancel", command=self.process_end)
        self.button_cancel.pack(side="left", fill="x")
        # Help
        self.button_help = ttk.Button(button_fame, text="?", width=2, command=self.open_help_window)
        self.button_help.pack(side="left", fill="x")
        # Info Row
        self.info_row = tk.Frame(self.frame_bottom_row)
        self.info_row.pack(side="top", fill="x")
        # Info Labels
        self.create_info_widgets()
        # Progressbar
        self.progressbar = ttk.Progressbar(self.info_row, maximum=100)
        self.progressbar.pack(side="left", fill="both", expand=True)


    def create_info_widgets(self):
        self.info_frame = tk.Frame(self.info_row)
        self.info_frame.pack(side="left", fill="both")
        self.info_frame.grid_rowconfigure(0, weight=1)
        # Total Count
        self.label_total_count = tk.Label(self.info_frame, text=f"Total: {self.total_images}", relief="groove", width=15, anchor="w")
        self.label_total_count.grid(row=0, column=0, padx=2)
        # Processed
        self.label_upscaled_count = tk.Label(self.info_frame, text=f"Processed: 0", relief="groove", width=15, anchor="w")
        self.label_upscaled_count.grid(row=0, column=5, padx=2)
        # Elapsed
        self.label_timer = tk.Label(self.info_frame, text="Elapsed: 00:00:00", relief="groove", width=15, anchor="w")
        self.label_timer.grid(row=0, column=10, padx=2)
        # ETA
        self.label_timer_eta = tk.Label(self.info_frame, text="ETA: 00:00:00", relief="groove", width=15, anchor="w")
        self.label_timer_eta.grid(row=0, column=15, padx=2)
        # Misc
        self.new_size_label = tk.Label(self.info_frame, text="New Size: 0x0", relief="groove", width=21, anchor="w")


    def create_path_selection_widgets(self):
        path_selection_frame = ttk.Labelframe(self.batch_upscale_frame, text="Path Selection")
        path_selection_frame.pack(side="top", fill="x")

        # Input Path
        input_frame = tk.Frame(path_selection_frame)
        input_frame.pack(side="top", fill="x")
        # Label
        tk.Label(input_frame, text="Input:", width=10).pack(side="left")
        # Entry
        self.entry_input_path = ttk.Entry(input_frame, textvariable=self.input_path_var)
        self.entry_input_path.pack(side="left", fill="x", expand=True)
        self.entry_helper.setup_entry_binds(self.entry_input_path)
        # Batch Mode
        self.batch_mode_checkbox = ttk.Checkbutton(input_frame, text="Batch Mode", variable=self.batch_mode_var, width=12, takefocus=False, command=self.toggle_batch_mode)
        self.batch_mode_checkbox.pack(side="left", fill="x")
        ToolTip.create(self.batch_mode_checkbox, "Enable or disable batch processing", delay=250, padx=6, pady=12)
        # Browse
        self.browse_input_button = ttk.Button(input_frame, text="Browse...", command=lambda: self.set_upscale_paths(path="input"))
        self.browse_input_button.pack(side="left", fill="x")
        # Open
        ttk.Button(input_frame, text="Open", command=lambda: self.open_directory(self.input_path_var.get())).pack(side="left", fill="x")

        # Output Path
        batch_output_frame = tk.Frame(path_selection_frame)
        batch_output_frame.pack(side="top", fill="x")
        # Label
        tk.Label(batch_output_frame, text="Output:", width=10).pack(side="left")
        # Entry
        self.entry_output_path = ttk.Entry(batch_output_frame, textvariable=self.output_path_var)
        self.entry_output_path.pack(side="left", fill="x", expand=True)
        self.entry_helper.setup_entry_binds(self.entry_output_path)
        # Auto
        self.auto_output_checkbox = ttk.Checkbutton(batch_output_frame, text="Auto Name", variable=self.auto_output_var, width=12, takefocus=False, command=self.toggle_batch_mode)
        self.auto_output_checkbox.pack(side="left", fill="x")
        ToolTip.create(self.auto_output_checkbox, "Automatically set a unique output path relative to the input path", delay=250, padx=6, pady=12)
        # Browse
        self.browse_output_button = ttk.Button(batch_output_frame, text="Browse...", command=lambda: self.set_upscale_paths(path="output"))
        self.browse_output_button.pack(side="left", fill="x")
        # Open
        ttk.Button(batch_output_frame, text="Open", command=lambda: self.open_directory(self.output_path_var.get())).pack(side="left", fill="x")


    def create_file_tree(self):
        tree_frame = tk.Frame(self.batch_upscale_frame)
        tree_frame.pack(side="top", fill="both", expand=True)
        self.file_tree = ttk.Treeview(tree_frame, columns=("Name", "Dimensions", "New Dimensions", "Type"), show="headings", selectmode="browse", height=1)
        self.file_tree.heading("Name", text="Name")
        self.file_tree.heading("Dimensions", text="Dimensions")
        self.file_tree.heading("New Dimensions", text="New Dimensions")
        self.file_tree.heading("Type", text="Type")
        self.file_tree.column("Name", stretch=True)
        self.file_tree.column("Dimensions", width=180, stretch=False)
        self.file_tree.column("New Dimensions", width=180, stretch=False)
        self.file_tree.column("Type", width=100, stretch=False)
        self.file_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.file_tree.yview)
        v_scrollbar.pack(side="right", fill="y")
        self.file_tree.configure(yscrollcommand=v_scrollbar.set)
        self.file_tree.bind("<<TreeviewSelect>>", self.handle_file_tree_selection)


    def create_upscale_settings_widgets(self):
        settings_frame = ttk.Labelframe(self.batch_upscale_frame, text="Settings")
        settings_frame.pack(side="bottom", fill="x")

        # Upscale Model
        frame_model = tk.Frame(settings_frame)
        frame_model.pack(side="top", fill="both", pady=(0, 5))
        # Label
        self.label_upscale_model = tk.Label(frame_model, text="Upscale Model:", width=20)
        self.label_upscale_model.pack(side="left")
        ToolTip.create(self.label_upscale_model, "Select the RESRGAN upscale model", delay=250, padx=6, pady=12)
        # Combobox
        self.combobox_upscale_model = ttk.Combobox(frame_model, width=25, state="readonly", values=self.ncnn_models)
        self.combobox_upscale_model.pack(side="top", fill="x")
        self.combobox_upscale_model.set("realesr-animevideov3-x4")

        # Upscale Factor
        frame_size = tk.Frame(settings_frame)
        frame_size.pack(side="top", fill="both")
        # Label
        label_upscale_factor = tk.Label(frame_size, text="Upscale Factor:", width=20)
        label_upscale_factor.pack(side="left")
        ToolTip.create(label_upscale_factor, "Determines the final size of the image.\n\nImages are first upscaled by 4x and then resized according to the selected upscale factor.\n\nThe final resolution is calculated as: (4 * original size) / upscale factor.", delay=250, padx=6, pady=12)
        # Slider
        self.upscale_factor_value = tk.DoubleVar(value=2.00)
        self.slider_upscale_factor = ttk.Scale(frame_size, from_=0.25, to=8.00, orient="horizontal", variable=self.upscale_factor_value, command=self.update_upscale_factor_label)
        self.slider_upscale_factor.pack(side="left", fill="x", expand=True)
        # Label
        self.label_upscale_factor_value = tk.Label(frame_size, textvariable=self.upscale_factor_value, width=5)
        self.label_upscale_factor_value.pack(side="left", anchor="w")

        # Upscale Strength
        frame_strength = tk.Frame(settings_frame)
        frame_strength.pack(side="top", fill="both")
        # Label
        self.label_upscale_strength = tk.Label(frame_strength, text="Upscale Strength:", width=20)
        self.label_upscale_strength.pack(side="left")
        ToolTip.create(self.label_upscale_strength, "Adjust the upscale strength to determine the final blending value of the output image.\n\n0% = Only original image, 100% = Only upscaled image.", delay=250, padx=6, pady=12)
        # Slider
        self.upscale_strength_value = tk.IntVar(value=100)
        self.slider_upscale_strength = ttk.Scale(frame_strength, from_=0, to=100, orient="horizontal", variable=self.upscale_strength_value, command=self.update_strength_label)
        self.slider_upscale_strength.pack(side="left", fill="x", expand=True)
        self.slider_upscale_strength.set(100)
        # Label
        self.label_upscale_strength_percent = tk.Label(frame_strength, width=5, text="100%")
        self.label_upscale_strength_percent.pack(anchor="w", side="left")


#endregion
################################################################################################################################################
#region -  Treeview Logic


    def populate_file_tree(self):
        self.file_tree.delete(*self.file_tree.get_children())
        scaling_factor = float(self.upscale_factor_value.get())
        input_path = self.input_path_var.get()
        if not os.path.isdir(input_path):
            input_path = os.path.dirname(input_path)
        for file in os.listdir(input_path):
            if file.lower().endswith(self.supported_filetypes):
                filepath = os.path.join(input_path, file)
                try:
                    with Image.open(filepath) as img:
                        width, height = img.size
                        dimensions = f"{width}x{height}"
                        new_width = int(width * scaling_factor)
                        new_height = int(height * scaling_factor)
                        new_dimensions = f"{new_width}x{new_height}"
                except Exception:
                    dimensions = "0x0"
                    new_dimensions = "0x0"
                ext = os.path.splitext(file)[1]
                self.file_tree.insert("", "end", values=(file, dimensions, new_dimensions, ext))


    def get_selection_details(self):
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            values = self.file_tree.item(item, "values")
            if values:
                filename = values[0]
                directory = self.working_dir
                name, extension = os.path.splitext(filename)
                filepath = os.path.join(directory, filename)
                return item, directory, filename, extension, filepath
        return None, None, None, None, None


    def handle_file_tree_selection(self, event=None):
        if self.batch_thread_var:
            return
        item, directory, filename, extension, filepath = self.get_selection_details()
        if not self.verify_selected_file(filepath):
            return
        if self.batch_mode_var.get():
            if self.auto_output_var.get():
                self.output_path_var.set(os.path.join(directory, "Upscale_Output"))
            return
        if filename:
            self.working_img_path = os.path.join(directory, filename)
            norm_path = os.path.normpath(self.working_img_path)
            self.input_path_var.set(norm_path)
            base = os.path.splitext(filename)[0]
            if self.auto_output_var.get():
                self.output_path_var.set(os.path.join(directory, f"{base}_up{extension}"))
            else:
                self.output_path_var.set(norm_path)
        self.update_new_dimensions_in_file_tree()


    def update_new_dimensions_in_file_tree(self):
        scaling_factor = float(self.upscale_factor_value.get())
        all_items = self.file_tree.get_children()
        selected_items = self.file_tree.selection() if not self.batch_mode_var.get() else all_items
        for item in all_items:
            values = self.file_tree.item(item, "values")
            if len(values) < 3:
                continue
            dimensions = values[1]
            if item in selected_items:
                try:
                    width_str, height_str = dimensions.split("x")
                    width = int(width_str)
                    height = int(height_str)
                    new_width = int(width * scaling_factor)
                    new_height = int(height * scaling_factor)
                    new_dimensions = f"{new_width}x{new_height}"
                except Exception:
                    new_dimensions = "-x-"
            else:
                new_dimensions = "-x-"
            new_values = (values[0], dimensions, new_dimensions, values[3])
            self.file_tree.item(item, values=new_values)


    def highlight_upscale_item(self, filename):
        for item in self.file_tree.get_children():
            values = self.file_tree.item(item, "values")
            if values and values[0] == filename:
                self.file_tree.selection_set(item)
                self.file_tree.see(item)
                break


    def highlight_parent_image(self):
        if not self.batch_mode_var.get():
            parent_img_path = self.parent.image_files[self.parent.current_index]
            self.highlight_upscale_item(os.path.basename(parent_img_path))


#endregion
################################################################################################################################################
#region -  UI Functions


    def set_widget_state(self, state):
        widget_list = [
            # Upscale
            self.button_upscale,
            # Input
            self.entry_input_path,
            self.batch_mode_checkbox,
            self.browse_input_button,
            # Output
            self.entry_output_path,
            self.auto_output_checkbox,
            self.browse_output_button,
            #Settings
            self.combobox_upscale_model,
            self.slider_upscale_factor,
            self.slider_upscale_strength,
        ]
        for widget in widget_list:
                widget.config(state=state)


    def toggle_batch_mode(self):
        input_path = self.input_path_var.get()
        output_path = self.output_path_var.get()
        if self.batch_mode_var:
            if not os.path.isdir(input_path):
                self.input_path_var.set(os.path.dirname(input_path))
            if not os.path.isdir(output_path):
                self.output_path_var.set(os.path.dirname(output_path))
        self.handle_file_tree_selection()
        self.update_new_dimensions_in_file_tree()


    def set_upscale_paths(self, path=None):
        if path is None:
            return
        if path == "input":
            if self.batch_mode_var.get():
                result = filedialog.askdirectory(initialdir=self.input_path_var.get())
                if not result:
                    return
                self.input_path_var.set(os.path.normpath(result))
            else:
                result = filedialog.askopenfilename(initialdir=self.input_path_var.get())
                if not result:
                    return
                self.input_path_var.set(os.path.normpath(result))
                self.working_img_path = self.input_path_var.get()
            self.populate_file_tree()
            self.clear_process_labels()
        elif path == "output":
            if self.batch_mode_var.get():
                result = filedialog.askdirectory(initialdir=self.output_path_var.get())
                if not result:
                    return
                self.output_path_var.set(os.path.normpath(result))
            else:
                result = filedialog.asksaveasfilename(initialdir=self.output_path_var.get())
                if not result:
                    return
                self.output_path_var.set(os.path.normpath(result))
        if self.auto_output_var.get():
            if self.batch_mode_var.get():
                self.output_path_var.set(os.path.join(self.input_path_var.get(), "Upscale_Output"))
            else:
                directory, filename = os.path.split(self.input_path_var.get())
                filename, extension = os.path.splitext(filename)
                self.output_path_var.set(os.path.join(directory, f"{filename}_up{extension}"))
        if not self.batch_mode_var.get():
            self.highlight_upscale_item(os.path.basename(self.working_img_path))
        self.determine_working_directory()
        self.entry_input_path.xview_moveto(1)
        self.entry_output_path.xview_moveto(1)


    def update_strength_label(self, event=None):
        try:
            value = int(self.upscale_strength_value.get())
            self.label_upscale_strength_percent.config(text=f"{value}%")
        except Exception:
            pass


    def update_upscale_factor_label(self, event):
        try:
            value = round(float(self.upscale_factor_value.get()) * 4) / 4
            self.upscale_factor_value.set(value)
            self.label_upscale_factor_value.config(text=f"{value:.2f}x")
            self.update_new_dimensions_in_file_tree()
        except Exception:
            pass


    def update_progress(self, progress):
        if not self.batch_upscale_frame.winfo_exists():
            return
        self.progressbar.config(value=progress)
        self.frame_bottom_row.update_idletasks()


    def clear_process_labels(self):
        self.label_upscaled_count.config(text="Processed: 0")
        self.label_timer.config(text="Elapsed: 00:00:00")
        self.label_timer_eta.config(text="ETA: 00:00:00")
        self.progressbar.config(value=0)


    def update_image_count(self):
        self.total_images = len([file for file in os.listdir(self.working_dir) if file.lower().endswith(self.supported_filetypes)])
        self.label_total_count.config(text=f"Total: {self.total_images}")


    def open_help_window(self):
        help_text = HelpText.BATCH_UPSCALE_HELP
        self.help_window.open_window(geometry="550x700", help_text=help_text)


#endregion
################################################################################################################################################
#region -  Primary Functions


    def determine_image_type(self, event=None):
        if self.batch_mode_var.get():
            self.batch_upscale()
        else:
            directory, filename = os.path.split(self.working_img_path)
            filename, extension = os.path.splitext(filename)
            gif_path = self.working_img_path
            self.set_widget_state(state="disabled")
            if extension.lower() == '.gif':
                self._upscale_gif(gif_path)
            else:
                self._upscale_image()
            self.set_widget_state(state="normal")
            self.populate_file_tree()


    def batch_upscale(self):
        self.batch_thread_var = True
        thread = threading.Thread(target=self._batch_upscale)
        thread.start()
        self.set_widget_state(state="disabled")


    def batch_upscale_cancel_message(self, count):
        messagebox.showinfo("Batch Upscaled Canceled", f"Batch Upscaling canceled early.\n\n{count} of {self.total_images} images upscaled.")


    def _batch_upscale(self):
        input_path = self.input_path_var.get()
        output_path = self.output_path_var.get()
        count = 0
        start_time = time.time()
        try:
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            for filename in os.listdir(input_path):
                self.batch_upscale_frame.update()
                self.batch_upscale_frame.update_idletasks()
                if not self.batch_thread_var:
                    self.batch_upscale_cancel_message(count)
                    break
                file_path = os.path.join(input_path, filename)
                if os.path.isfile(file_path) and filename.lower().endswith(self.supported_filetypes):
                    self.working_img_path = file_path
                    self.highlight_upscale_item(filename)
                    if filename.lower().endswith('.gif'):
                        if not self.batch_thread_var:
                            self.batch_upscale_cancel_message(count)
                            break
                        self._upscale_gif(file_path, batch_mode=True, output_path=output_path)
                    else:
                        if not self.batch_thread_var:
                            self.batch_upscale_cancel_message(count)
                            break
                        self._upscale_image(batch_mode=True, output_path=output_path)
                    count += 1
                    elapsed_time = time.time() - start_time
                    avg_time_per_image = elapsed_time / count
                    remaining_images = self.total_images - count
                    eta = avg_time_per_image * remaining_images
                    self.batch_upscale_frame.update()
                    self.batch_upscale_frame.update_idletasks()
                    if not self.batch_thread_var:
                        self.batch_upscale_cancel_message(count)
                        break
                    self.label_timer.config(text=f"Elapsed: {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}")
                    if not self.batch_thread_var:
                        self.batch_upscale_cancel_message(count)
                        break
                    self.label_timer_eta.config(text=f"ETA: {time.strftime('%H:%M:%S', time.gmtime(eta))}")
                    if not self.batch_thread_var:
                        self.batch_upscale_cancel_message(count)
                        break
                    self.label_upscaled_count.config(text=f"Processed: {count}")
            self.update_progress(100)
            if self.batch_thread_var:
                messagebox.showinfo("Success", f"Successfully upscaled {count} images!")
        except Exception as e:
            messagebox.showerror("Error: _batch_upscale()", f"An error occurred during batch upscaling.\n\n{e}")
        finally:
            self.set_widget_state(state="normal")
            self.batch_thread_var = False


    def _build_output_path(self, input_filepath, batch_mode, suffix="", ext_override=None):
        directory, filename = os.path.split(input_filepath)
        name, ext = os.path.splitext(filename)
        if ext_override is not None:
            ext = ext_override
        if batch_mode:
            output_dir = self.output_path_var.get()
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            return os.path.join(output_dir, f"{name}{suffix}{ext}")
        else:
            return self.output_path_var.get()


    def _build_upscale_command(self, input_path, output_path):
        model = str(self.combobox_upscale_model.get())
        upscale_command = [
            self.executable_path,
            "-i", input_path,
            "-o", output_path,
            "-n", model,
            "-s", "4",
            "-f", "jpg"
        ]
        if model not in self.ncnn_models:
            upscale_command.extend(["-m", self.extra_models_path])
        return upscale_command


    def _upscale_gif(self, gif_path, batch_mode=None, output_path=None):
        try:
            with Image.open(gif_path) as gif:
                frames = [(frame.copy().convert("RGBA"), frame.info['duration']) for frame in ImageSequence.Iterator(gif)]
            temp_dir = os.path.join(os.path.dirname(gif_path), "temp_upscale_dir")
            os.makedirs(temp_dir, exist_ok=True)
            upscaled_frames = []
            total_frames = len(frames)
            for i, (frame, duration) in enumerate(frames):
                temp_frame_path = os.path.join(temp_dir, f"frame_{i}.png")
                frame.save(temp_frame_path)
                upscaled_frame_path = os.path.join(temp_dir, f"frame_{i}_up.png")
                self.batch_upscale_frame.update()
                upscale_command = self._build_upscale_command(temp_frame_path, upscaled_frame_path)
                upscale_process = subprocess.Popen(upscale_command, creationflags=subprocess.CREATE_NO_WINDOW)
                upscale_process.wait()
                self.batch_upscale_frame.update()
                self.batch_upscale_frame.update_idletasks()
                self.resize_image(upscaled_frame_path)
                if os.path.exists(upscaled_frame_path):
                    if self.upscale_strength_value.get() != 100:
                        self.blend_images(temp_frame_path, upscaled_frame_path, '.png')
                    with Image.open(upscaled_frame_path) as upscaled_frame:
                        upscaled_frame = upscaled_frame.convert("RGBA")
                        upscaled_frames.append((upscaled_frame, duration))
                self.update_progress((i + 1) / total_frames * 90)
            upscaled_gif_path = self._build_output_path(gif_path, batch_mode, suffix="_up")
            upscaled_frames[0][0].save(upscaled_gif_path, save_all=True, append_images=[frame for frame, _ in upscaled_frames[1:]], loop=0, duration=[duration for _, duration in upscaled_frames])
            shutil.rmtree(temp_dir)
            self.update_progress(99)
            if not batch_mode:
                time.sleep(0.1)
                self.process_end()
                result = messagebox.askyesno("Upscale Successful", f"Output path:\n{upscaled_gif_path}\n\nOpen image?")
                if result:
                    os.startfile(upscaled_gif_path)
        except (PermissionError, FileNotFoundError, tk.TclError) as e:
            messagebox.showerror("Error: _upscale_gif()", f"An error occurred.\n\n{e}")
            self.process_end()
            return
        except Exception as e:
            messagebox.showerror("Error: _upscale_gif()", f"An error occurred.\n\n{e}")
            self.process_end()


    def _upscale_image(self, batch_mode=False, output_path=None):
        try:
            self.update_progress(25)
            directory, filename = os.path.split(self.working_img_path)
            name, extension = os.path.splitext(filename)
            if extension.lower() == '.webp':
                extension = self.convert_webp_to_jpg(directory, name)
            output_image_path = self._build_output_path(self.working_img_path, batch_mode, ext_override=extension)
            model = str(self.combobox_upscale_model.get())
            upscale_command = self._build_upscale_command(self.working_img_path, output_image_path)
            upscale_process = subprocess.Popen(upscale_command, creationflags=subprocess.CREATE_NO_WINDOW)
            self.update_progress(40)
            upscale_process.wait()
            self.update_progress(60)
            self.resize_image(output_image_path)
            self.update_progress(80)
            self.delete_converted_image()
            if self.upscale_strength_value.get() != 100:
                self.blend_images(self.working_img_path, output_image_path, extension)
            self.update_progress(99)
            if not batch_mode:
                time.sleep(0.1)
                self.process_end()
                result = messagebox.askyesno("Upscale Successful", f"Output path:\n{output_image_path}\n\nOpen image?")
                if result:
                    os.startfile(output_image_path)
        except Exception as e:
            messagebox.showerror("Error: _upscale_image()", f"An error occurred.\n\n{e}")
            self.process_end()


    def blend_images(self, original_image_path, upscaled_image_path, extension):
        with Image.open(original_image_path).convert("RGBA") as original_image:
            with Image.open(upscaled_image_path).convert("RGBA") as upscaled_image:
                original_image = original_image.resize(upscaled_image.size, Image.LANCZOS)
                alpha = self.upscale_strength_value.get() / 100.0
                blended_image = Image.blend(original_image, upscaled_image, alpha)
                if extension.lower() in ['.jpg', '.jpeg']:
                    blended_image = blended_image.convert("RGB")
                blended_image.save(upscaled_image_path)


    def get_image_index(self, directory, filename):
        filename = os.path.basename(filename)
        image_files = sorted((file for file in os.listdir(directory) if file.lower().endswith(self.supported_filetypes)), key=self.parent.get_file_sort_key(), reverse=self.parent.reverse_load_order_var.get())
        return image_files.index(filename) if filename in image_files else -1


    def delete_converted_image(self):
        if self.converted_filepath and os.path.exists(self.converted_filepath):
            os.remove(self.converted_filepath)
            self.converted_filepath = None


    def resize_image(self, output_image_path):
        if not self.batch_upscale_frame.winfo_exists():
            return
        selected_scaling_factor = float(self.upscale_factor_value.get())
        with Image.open(output_image_path) as img:
            current_width, current_height = img.size
            upscale_tool_factor = 4.0
            original_width = int(current_width / upscale_tool_factor)
            original_height = int(current_height / upscale_tool_factor)
            new_width = int(original_width * selected_scaling_factor)
            new_height = int(original_height * selected_scaling_factor)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            img.save(output_image_path, quality=100)


#endregion
################################################################################################################################################
#region -  Misc


    def set_working_directory(self, path=None, batch=None):
        if self.batch_thread_var:
            return
        if batch:
            self.batch_mode_var.set(True)
        else:
            self.batch_mode_var.set(False)
        if path:
            self.working_dir = path
        else:
            self.determine_working_directory()
        self.working_img_path = self.parent.image_files[self.parent.current_index]
        self.input_path_var.set(self.working_dir)
        self.output_path_var.set(value=os.path.join(self.input_path_var.get(), "Upscale_Output"))
        self.update_image_count()
        self.populate_file_tree()
        self.clear_process_labels()
        self.highlight_parent_image()


    def refresh_files(self):
        path = self.working_dir
        self.set_working_directory(path=path)


    def determine_working_directory(self):
        if not os.path.isdir(self.input_path_var.get()):
            self.working_dir = os.path.dirname(self.input_path_var.get())
        else:
            self.working_dir = self.input_path_var.get()


    def find_additional_models(self):
        if not os.path.exists(self.extra_models_path):
            return self.ncnn_models
        all_files = os.listdir(self.extra_models_path)
        bin_files = {os.path.splitext(f)[0] for f in all_files if f.endswith('.bin')}
        param_files = {os.path.splitext(f)[0] for f in all_files if f.endswith('.param')}
        paired_models = bin_files & param_files
        additional_models = {model for model in paired_models if model not in self.ncnn_models}
        combined_models = list(set(self.ncnn_models) | additional_models)
        return combined_models


    def convert_webp_to_jpg(self, directory, filename):
        with Image.open(self.working_img_path) as img:
            if img.mode == "RGBA":
                img = img.convert("RGB")
            jpg_filepath = os.path.join(directory, f"{filename}.jpg")
            img.save(jpg_filepath, 'JPEG', quality=100)
            self.converted_filepath = jpg_filepath
            extension = '.jpg'
            return extension


    def delete_temp_dir(self):
        try:
            temp_dir = os.path.join(os.path.dirname(self.working_img_path), "temp_upscale_dir")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except (PermissionError, FileNotFoundError):
            return


    def open_directory(self, directory):
        if os.path.exists(directory) and os.path.isfile(directory):
            directory = os.path.dirname(directory)
        current_dir = directory
        while current_dir and not os.path.isdir(current_dir):
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                break
            current_dir = parent_dir
        if os.path.isdir(current_dir):
            try:
                os.startfile(current_dir)
            except Exception:
                pass


    def process_end(self, event=None):
        self.batch_thread_var = False
        self.delete_temp_dir()
        self.set_widget_state(state="normal")


    def verify_selected_file(self, filepath):
        if filepath is None or not os.path.exists(filepath):
            self.populate_file_tree()
            return False
        else:
            return True
