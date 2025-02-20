
################################################################################################################################################
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


#endregion
################################################################################################################################################
#region - CLS BatchUpscale


class BatchUpscale:
    def __init__(self):
        self.parent = None
        self.root = None
        self.working_dir = None

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
        self.batch_mode_var = True
        self.batch_thread_var = False
        self.batch_input_path_var = tk.StringVar(value="")
        self.batch_output_path_var = tk.StringVar(value="")

        # Other Variables
        self.total_gif_frames = 0
        self.current_gif_frame = 0
        self.total_images = 0
        self.original_image_width = 0
        self.original_image_height = 0


    def setup_window(self, parent, root):
        self.parent = parent
        self.root = root
        self.working_dir = self.parent.image_dir.get()
        self.working_img_path = self.parent.image_files[self.parent.current_index]

        self.executable_path = os.path.join(self.parent.application_path, "main/resrgan/realesrgan-ncnn-vulkan.exe")
        self.extra_models_path = os.path.join(self.parent.application_path, "ncnn_models".lower())
        self.ncnn_models = self.find_additional_models()

        if self.batch_mode_var:
            self.batch_input_path_var.set(self.working_dir)
            self.batch_output_path_var.set(value=os.path.join(self.batch_input_path_var.get(), "Upscale_Output"))
        self.total_images = len([file for file in os.listdir(self.working_dir) if file.lower().endswith(self.supported_filetypes)])

        self.get_image_info()
        self.setup_ui()
        self.set_working_directory(self.working_dir)
        self.create_interface()
        self.update_size_info_label()


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
        #self.info_label.pack(side="left", fill="x", padx=2)
        # Directory
        self.entry_directory = ttk.Entry(self.top_frame)
        self.entry_directory.insert(0, os.path.normpath(self.working_dir) if self.working_dir else "...")
        #self.entry_directory.pack(side="left", fill="x", expand=True, padx=2)
        self.entry_directory.bind("<Return>", lambda event: self.set_working_directory(self.entry_directory.get()))
        self.entry_directory.bind("<Button-1>", lambda event: self.entry_directory.delete(0, "end") if self.entry_directory.get() == "..." else None)
        # Browse
        self.browse_button = ttk.Button(self.top_frame, width=8, text="Browse...", command=self.set_working_directory)
        #self.browse_button.pack(side="left", padx=2)
        # Open
        self.open_button = ttk.Button(self.top_frame, width=8, text="Open", command=self.open_folder)
        #self.open_button.pack(side="left", padx=2)
        # Help
        self.help_button = ttk.Button(self.top_frame, text="?", width=2, command=self.show_help)
        #self.help_button.pack(side="right", fill="x", padx=2)


    def create_control_row(self):
        self.frame_control_row = tk.Frame(self.batch_upscale_frame, borderwidth=2)
        self.frame_control_row.pack(side="top", fill="x", padx=2, pady=2)


    def create_bottom_row(self):
        self.frame_bottom_row = tk.Frame(self.batch_upscale_frame)
        self.frame_bottom_row.pack(side="bottom", fill="both")
        button_fame = tk.Frame(self.frame_bottom_row)
        button_fame.pack(side="top", fill="x")
        # Upscale Button
        self.button_upscale = ttk.Button(button_fame, text="Upscale", command=self.determine_image_type)
        self.button_upscale.pack(side="left", fill="x", expand=True)
        # Cancel Button
        self.button_cancel = ttk.Button(button_fame, text="Cancel", command=self.close_tab)
        self.button_cancel.pack(side="left", fill="x")
        # Progress Bar
        self.progress_bar = ttk.Progressbar(self.frame_bottom_row, maximum=100)
        self.progress_bar.pack(side="top", fill="x")


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
            print(f"Error opening folder: {e}")


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







#endregion
################################################################################################################################################
#region -  Setup Interface


    def create_interface(self):
        self.create_upscale_model_selection_widgets()
        self.create_info_widgets()
        self.create_upscale_settings_widgets()


    def create_upscale_model_selection_widgets(self):
        self.batch_path_selection_frame = ttk.Labelframe(self.batch_upscale_frame, text="Batch Paths")
        self.batch_path_selection_frame.pack(side="top", fill="x")

        # Input Path
        batch_input_frame = tk.Frame(self.batch_path_selection_frame)
        batch_input_frame.pack(side="top", fill="x")

        tk.Label(batch_input_frame, text="Input:", width=10).pack(side="left")

        self.entry_batch_input_path = ttk.Entry(batch_input_frame, textvariable=self.batch_input_path_var)
        self.entry_batch_input_path.pack(side="left", fill="x", expand=True)
        self.input_tooltip = ToolTip.create(self.entry_batch_input_path, self.batch_input_path_var.get(), delay=250, padx=6, pady=12)

        self.button_browse_batch_input = ttk.Button(batch_input_frame, text="Browse...")
        self.button_browse_batch_input.pack(side="left", fill="x")

        self.button_open_batch_input = ttk.Button(batch_input_frame, text="Open", command=lambda: self.open_directory(self.batch_input_path_var.get()))
        self.button_open_batch_input.pack(side="left", fill="x")

        # Output Path
        batch_output_frame = tk.Frame(self.batch_path_selection_frame)
        batch_output_frame.pack(side="top", fill="x")

        tk.Label(batch_output_frame, text="Output:", width=10).pack(side="left")

        self.entry_batch_output_path = ttk.Entry(batch_output_frame, textvariable=self.batch_output_path_var)
        self.entry_batch_output_path.pack(side="left", fill="x", expand=True)
        self.output_tooltip = ToolTip.create(self.entry_batch_output_path, self.batch_output_path_var.get(), delay=250, padx=6, pady=12)

        self.browse_batch_output_button = ttk.Button(batch_output_frame, text="Browse...")
        self.browse_batch_output_button.pack(side="left", fill="x")

        self.open_batch_output_button = ttk.Button(batch_output_frame, text="Open", command=lambda: self.open_directory(self.batch_output_path_var.get()))
        self.open_batch_output_button.pack(side="left", fill="x")



    def create_upscale_settings_widgets(self):
        settings_frame = ttk.Labelframe(self.batch_upscale_frame, text="Settings")
        settings_frame.pack(side="bottom", fill="x")
        # Upscale Model
        frame_model = tk.Frame(settings_frame)
        frame_model.pack(side="top", fill="both", pady=(0, 5))

        self.label_upscale_model = tk.Label(frame_model, text="Upscale Model:", width=20)
        self.label_upscale_model.pack(side="left")
        ToolTip.create(self.label_upscale_model, "Select the RESRGAN upscale model", delay=250, padx=6, pady=12)

        self.combobox_upscale_model = ttk.Combobox(frame_model, width=25, state="readonly", values=self.ncnn_models)
        self.combobox_upscale_model.pack(side="top", fill="x")
        self.combobox_upscale_model.set("realesr-animevideov3-x4")

        # Upscale Factor
        frame_size = tk.Frame(settings_frame)
        frame_size.pack(side="top", fill="both")

        label_size = tk.Label(frame_size, text="Upscale Factor:", width=20)
        label_size.pack(side="left")
        ToolTip.create(label_size, "Determines the final size of the image.\n\nImages are first upscaled by 4x and then resized according to the selected upscale factor.\n\nThe final resolution is calculated as: (4 * original size) / upscale factor.", delay=250, padx=6, pady=12)

        self.upscale_factor_value = tk.DoubleVar(value=2.00)
        self.slider_upscale_factor = ttk.Scale(frame_size, from_=0.25, to=8.00, orient="horizontal", variable=self.upscale_factor_value, command=self.update_upscale_factor_label)
        self.slider_upscale_factor.pack(side="left", fill="x", expand=True)

        self.label_upscale_factor_value = tk.Label(frame_size, textvariable=self.upscale_factor_value, width=5)
        self.label_upscale_factor_value.pack(side="left", anchor="w")

        # Upscale Strength
        frame_strength = tk.Frame(settings_frame)
        frame_strength.pack(side="top", fill="both")

        self.label_upscale_strength = tk.Label(frame_strength, text="Upscale Strength:", width=20)
        self.label_upscale_strength.pack(side="left")
        ToolTip.create(self.label_upscale_strength, "Adjust the upscale strength to determine the final blending value of the output image.\n\n0% = Only original image, 100% = Only upscaled image.", delay=250, padx=6, pady=12)

        self.upscale_strength_value = tk.IntVar(value=100)
        self.slider_upscale_strength = ttk.Scale(frame_strength, from_=0, to=100, orient="horizontal", variable=self.upscale_strength_value, command=self.update_strength_label)
        self.slider_upscale_strength.pack(side="left", fill="x", expand=True)
        self.slider_upscale_strength.set(100)

        self.label_upscale_strength_percent = tk.Label(frame_strength, width=5, text="100%")
        self.label_upscale_strength_percent.pack(anchor="w", side="left")


    def create_info_widgets(self):
        if self.batch_mode_var:
            self.frame_info = ttk.Labelframe(self.batch_upscale_frame, text="Image Info")
            self.frame_info.pack(side="bottom", fill="both")
            # Output info
            self.frame_labels = tk.Frame(self.frame_info)
            self.frame_labels.pack(side="left", expand=True, fill="x")
            tk.Label(self.frame_labels, text="Upscaled:").pack(anchor="w", side="top")
            # Timer
            self.label_timer = tk.Label(self.frame_labels, text="Timer: 00:00:00")
            self.label_timer.pack(anchor="w", side="top")
            # Output info
            self.frame_dimensions = tk.Frame(self.frame_info)
            self.frame_dimensions.pack(side="left", expand=True, fill="x")
            # Number of images
            self.label_number_of_images = tk.Label(self.frame_dimensions, text=f"0 of {self.total_images}", width=20)
            self.label_number_of_images.pack(anchor="w", side="top")
            # ETA
            self.label_timer_eta = tk.Label(self.frame_dimensions, text="ETA: 00:00:00", width=20)
            self.label_timer_eta.pack(anchor="w", side="top")
        else:
            self.frame_info = ttk.Labelframe(self.batch_upscale_frame, text="Image Info")
            self.frame_info.pack(side="bottom", fill="both")
            # Output info
            self.frame_labels = tk.Frame(self.frame_info)
            self.frame_labels.pack(side="left", expand=True, fill="x")
            # Current Size
            label_current = tk.Label(self.frame_labels, text="Current Size:")
            label_current.pack(anchor="w", side="top")
            # New Size
            label_new = tk.Label(self.frame_labels, text="New Size:")
            label_new.pack(anchor="w", side="top")
            # GIF Frames
            if self.working_img_path.lower().endswith(".gif"):
                label_frames = tk.Label(self.frame_labels, text="Frames:")
                label_frames.pack(anchor="w", side="top")
            # Output info
            self.frame_dimensions = tk.Frame(self.frame_info)
            self.frame_dimensions.pack(side="left", expand=True, fill="x")
            # Current Size
            self.label_current_dimensions = tk.Label(self.frame_dimensions, text=f"{self.original_image_width} x {self.original_image_height}", width=20)
            self.label_current_dimensions.pack(anchor="w", side="top")
            # New Size
            self.label_new_dimensions = tk.Label(self.frame_dimensions, text="0 x 0", width=20)
            self.label_new_dimensions.pack(anchor="w", side="top")
            ToolTip.create(self.label_new_dimensions, " The final size of the image after upscaling ", delay=250, padx=6, pady=12)
            # GIF Frames
            if self.working_img_path.lower().endswith(".gif"):
                self.label_framecount = tk.Label(self.frame_dimensions, text=f"{self.current_gif_frame} of {self.total_gif_frames}", width=20)
                self.label_framecount.pack(anchor="w", side="top")


#endregion
################################################################################################################################################
#region -  Primary Functions


    def determine_image_type(self, event=None):
        if self.batch_mode_var:
            self.batch_upscale()
        else:
            directory, filename = os.path.split(self.working_img_path)
            filename, extension = os.path.splitext(filename)
            gif_path = self.working_img_path
            self.set_widget_state(state="disabled")
            if extension.lower() == '.gif':
                self._upscale_gif(gif_path)
            else:
                self.upscale_image()
            self.set_widget_state(state="normal")


    def batch_upscale(self):
        self.batch_thread_var = True
        thread = threading.Thread(target=self._batch_upscale)
        thread.start()
        self.set_widget_state(state="disabled")


    def batch_upscale_cancel_message(self, count):
        messagebox.showinfo("Batch Upscaled Canceled", f"Batch Upscaling canceled early.\n\n{count} of {self.total_images} images upscaled.")


    def _batch_upscale(self):
        input_path = self.batch_input_path_var.get()
        output_path = self.batch_output_path_var.get()
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
                    if filename.lower().endswith('.gif'):
                        if not self.batch_thread_var:
                            self.batch_upscale_cancel_message(count)
                            break
                        self._upscale_gif(file_path, batch_mode=True, output_path=output_path)
                    else:
                        if not self.batch_thread_var:
                            self.batch_upscale_cancel_message(count)
                            break
                        self.upscale_image(batch_mode=True, output_path=output_path)
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
                    self.label_timer.config(text=f"Timer: {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}")
                    if not self.batch_thread_var:
                        self.batch_upscale_cancel_message(count)
                        break
                    self.label_timer_eta.config(text=f"ETA: {time.strftime('%H:%M:%S', time.gmtime(eta))}")
                    if not self.batch_thread_var:
                        self.batch_upscale_cancel_message(count)
                        break
                    self.label_number_of_images.config(text=f"{count} of {self.total_images}")
            self.update_progress(100)
            if self.batch_thread_var:
                messagebox.showinfo("Success", f"Successfully upscaled {count} images!")
        except Exception as e:
            messagebox.showerror("Error: _batch_upscale()", f"An error occurred during batch upscaling.\n\n{e}")


    def _upscale_gif(self, gif_path, batch_mode=None, output_path=None):
        try:
            with Image.open(gif_path) as gif:
                frames = [(frame.copy().convert("RGBA"), frame.info['duration']) for frame in ImageSequence.Iterator(gif)]
            temp_dir = os.path.join(os.path.dirname(gif_path), "temp_upscale_img")
            os.makedirs(temp_dir, exist_ok=True)
            upscaled_frames = []
            total_frames = len(frames)
            model = str(self.combobox_upscale_model.get())
            for i, (frame, duration) in enumerate(frames):
                temp_frame_path = os.path.join(temp_dir, f"frame_{i}.png")
                frame.save(temp_frame_path)
                upscaled_frame_path = os.path.join(temp_dir, f"frame_{i}_upscaled.png")
                self.batch_upscale_frame.update()
                upscale_command = [
                    self.executable_path,
                    "-i", temp_frame_path,
                    "-o", upscaled_frame_path,
                    "-n", model,
                    "-s", "4",
                    "-f", "jpg"
                ]
                if model not in self.ncnn_models:
                    upscale_command.extend(["-m", self.extra_models_path])
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
                self.update_progress((i+1)/total_frames*90)
                if not batch_mode:
                    padded_frame_number = str(i+1).zfill(len(str(total_frames)))
                    self.label_framecount.config(text=f"{padded_frame_number} of {total_frames}")
            directory, filename = os.path.split(gif_path)
            filename, extension = os.path.splitext(filename)
            upscaled_gif_path = os.path.join(output_path if batch_mode else directory, f"{filename}_upscaled{extension}")
            upscaled_frames[0][0].save(upscaled_gif_path, save_all=True, append_images=[frame for frame, _ in upscaled_frames[1:]], loop=0, duration=[duration for _, duration in upscaled_frames])
            shutil.rmtree(temp_dir)
            self.update_progress(99)
            if not batch_mode:
                time.sleep(0.1)
                self.close_tab(self.get_image_index(directory, f"{filename}_upscaled{extension}"))
                result = messagebox.askyesno("Upscale Successful", f"Output path:\n{upscaled_gif_path}\n\nOpen image?")
                if result:
                    os.startfile(upscaled_gif_path)
        except (PermissionError, FileNotFoundError, tk.TclError) as e:
            print(f"Error: {e}")
            return
        except Exception as e:
            messagebox.showerror("Error: _upscale_gif()", f"An error occurred.\n\n{e}")
            self.close_tab()


    def upscale_image(self, batch_mode=False, output_path=None):
        try:
            self.update_progress(25)
            directory, filename = os.path.split(self.working_img_path)
            filename, extension = os.path.splitext(filename)
            if extension.lower() == '.webp':
                extension = self.convert_webp_to_jpg(directory, filename)
            output_image_path = os.path.join(output_path if batch_mode else directory, f"{filename}{extension}" if batch_mode else f"{filename}_up{extension}")
            model = str(self.combobox_upscale_model.get())
            upscale_command = [
                self.executable_path,
                "-i", self.working_img_path,
                "-o", output_image_path,
                "-n", model,
                "-s", "4",
                "-f", "jpg"
            ]
            if model not in self.ncnn_models:
                upscale_command.extend(["-m", self.extra_models_path])
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
                index = self.get_image_index(directory, output_image_path)
                self.close_tab(index)
                result = messagebox.askyesno("Upscale Successful", f"Output path:\n{output_image_path}\n\nOpen image?")
                if result:
                    os.startfile(output_image_path)
        except Exception as e:
            messagebox.showerror("Error: upscale_image()", f"An error occurred.\n\n{e}")
            self.close_tab()


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
#region -  Image Info / label


    def get_image_info(self):
        try:
            with Image.open(self.working_img_path) as image:
                self.original_image_width, self.original_image_height = image.size
                if self.working_img_path.lower().endswith(".gif"):
                    frames = [frame for frame in ImageSequence.Iterator(image)]
                    self.total_gif_frames = len(frames)
                    self.current_gif_frame = format(1, f'0{len(str(self.total_gif_frames))}d')
                else:
                    self.total_gif_frames = 0
                    self.current_gif_frame = 0
        except Exception as e:
            messagebox.showerror("Error: get_image_info()", f"Unexpected error while opening image.\n\n{e}")
            self.close_tab()


    def update_size_info_label(self, event=None):
        if not self.batch_mode_var:
            selected_scaling_factor = float(self.upscale_factor_value.get())
            new_width = self.original_image_width * selected_scaling_factor
            new_height = self.original_image_height * selected_scaling_factor
            self.label_new_dimensions.config(text=f"{int(new_width)} x {int(new_height)}")
            return new_width, new_height


    def update_strength_label(self, event=None):
        try:
            value = int(self.upscale_strength_value.get())
            self.label_upscale_strength_percent.config(text=f"{value}%")
        except Exception:
            pass


    def update_upscale_factor_label(self, event):
        value = round(float(self.upscale_factor_value.get()) * 4) / 4
        self.upscale_factor_value.set(value)
        self.label_upscale_factor_value.config(text=f"{value:.2f}x")
        self.update_size_info_label()


#endregion
################################################################################################################################################
#region -  Misc


    def set_widget_state(self, state):
        widget_names = [
            "combobox_upscale_model",
            "entry_size",
            "slider_upscale_strength",
            "button_upscale",
        ]
        if self.batch_mode_var:
            widget_names.extend([
                "entry_batch_input_path",
                "button_browse_batch_input",
                "entry_batch_output_path",
                "browse_batch_output_button",
                "button_upscale",
            ])
        for widget_name in widget_names:
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.config(state=state)


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


    def update_progress(self, progress):
        if not self.batch_upscale_frame.winfo_exists():
            return
        self.progress_bar.config(value=progress)
        self.frame_bottom_row.update_idletasks()


    def delete_temp_dir(self):
        try:
            temp_dir = os.path.join(os.path.dirname(self.working_img_path), "temp_upscale_img")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except (PermissionError, FileNotFoundError):
            return


    def choose_directory(self, entry_path_var, tooltip):
        directory = os.path.normpath(filedialog.askdirectory())
        if directory:
            entry_path_var.set(directory)
            tooltip.config(text=directory)


    def open_directory(self, directory):
        try:
            if os.path.isdir(directory):
                os.startfile(directory)
        except Exception: return


    def close_tab(self, index=None, event=None):
        self.batch_thread_var = False
        self.delete_temp_dir()
        self.set_widget_state(state="normal")
        if index:
            self.parent.update_pair()
            self.parent.jump_to_image(index)
