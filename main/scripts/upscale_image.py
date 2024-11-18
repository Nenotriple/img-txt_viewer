"""
########################################
#             Upscale Image            #
#   Version : v1.05                    #
#   Author  : github.com/Nenotriple    #
########################################

Description:
-------------
Upscale a single/batch image using realesrgan-ncnn-vulkan.exe

"""

################################################################################################################################################
#region -  Imports


# Standard Library
import os
import time
import shutil
import threading
import subprocess


# Standard Library - GUI
from tkinter import ttk, Toplevel, messagebox, filedialog, Frame, Label, Button, IntVar, DoubleVar, StringVar, TclError


# Third-Party Libraries
from PIL import Image, ImageSequence
from TkToolTip.TkToolTip import TkToolTip as ToolTip

#endregion
################################################################################################################################################
#region - CLASS: Upscale


class Upscale:
    def __init__(self, parent, root, filepath, batch, window_x, window_y):
        self.parent = parent
        self.root = root
        self.filepath = filepath
        self.batch_mode = batch

        # Other Filepaths
        self.executable_path = os.path.join(self.parent.application_path, "main/resrgan/realesrgan-ncnn-vulkan.exe")
        self.extra_models_path = os.path.join(self.parent.application_path, "ncnn_models".lower())
        self.batch_filepath = os.path.dirname(self.filepath)
        self.converted_filepath = None

        # Supported Filetypes
        self.supported_filetypes = (".png", ".webp", ".jpg", ".jpeg", ".jpg_large", ".jfif", ".tif", ".tiff", ".bmp", ".gif")

        # Included Models
        self.ncnn_models = ["realesr-animevideov3-x4", "RealESRGAN_General_x4_v3", "realesrgan-x4plus", "realesrgan-x4plus-anime", "AnimeSharp-4x", "UltraSharp-4x"]
        self.ncnn_models = self.find_additional_models()

        # Window Dragging
        self.start_x = None
        self.start_y = None

        # Other Variables
        self.batch_thread = False
        self.total_gif_frames = None
        self.current_gif_frame = None
        self.is_window_closed = False
        self.total_images = len([file for file in os.listdir(self.batch_filepath) if file.lower().endswith(self.supported_filetypes)])

        # Continue startup...
        self.get_image_info()
        self.create_window(window_x, window_y)
        self.create_interface()
        self.update_size_info_label()


#endregion
################################################################################################################################################
#region -  Setup Interface


    def create_window(self, window_x, window_y):
        self.top = Toplevel(self.root, borderwidth=2, relief="groove")
        self.top.overrideredirect("true")
        self.top.geometry("+{}+{}".format(window_x, window_y))
        self.top.grab_set()
        self.top.focus_force()
        self.top.bind("<Escape>", self.close_window)
        self.top.bind("<Return>", self.determine_image_type)


    def create_interface(self):
        self.frame_container = Frame(self.top)
        self.frame_container.pack(expand=True, fill="both")

        title_text = "Upscale Image" if not self.batch_mode else "Batch Upscale"
        title = Label(self.frame_container, cursor="size", text=title_text, font=("", 16))
        title.pack(side="top", fill="x", padx=5, pady=5)
        title.bind("<ButtonPress-1>", self.start_drag)
        title.bind("<ButtonRelease-1>", self.stop_drag)
        title.bind("<B1-Motion>", self.dragging_window)


        self.button_close = Button(self.frame_container, text="X", overrelief="groove", relief="flat", command=self.close_window)
        button_close_padding = 0.945 if self.batch_mode else 0.92
        self.button_close.place(anchor="nw", relx=button_close_padding, height=40, width=40, x=-15, y=0)
        self.bind_widget_highlight(self.button_close, color='#ffcac9')


        separator = ttk.Separator(self.frame_container)
        separator.pack(side="top", fill="x")


####### Options ##################################################
        frame_comboboxes = Frame(self.frame_container)
        frame_comboboxes.pack(side="top", fill="x", padx=10, pady=10)

        if self.batch_mode:
            frame_input_batch_directory = Frame(frame_comboboxes)
            frame_input_batch_directory.pack(side="top", fill="x", padx=10, pady=10)

            # Input
            self.label_batch_upscale_path = Label(frame_input_batch_directory, text="Upscale Path")
            self.label_batch_upscale_path.pack(anchor="w", side="top", padx=5, pady=5)
            self.batch_upscale_path = StringVar(value=self.batch_filepath)
            self.entry_batch_upscale_path = ttk.Entry(frame_input_batch_directory, width=50, textvariable=self.batch_upscale_path)
            self.entry_batch_upscale_path.pack(side="left", fill="x", padx=5, pady=5)
            self.entry_batch_upscale_path.config()
            self.input_tooltip = ToolTip.create(self.entry_batch_upscale_path, self.batch_upscale_path.get(), 250, 6, 12)

            self.button_browse_batch_input = ttk.Button(frame_input_batch_directory, text="Browse...", command=lambda: self.choose_directory(self.batch_upscale_path, self.input_tooltip))
            self.button_browse_batch_input.pack(side="left", fill="x", padx=2, pady=2)

            self.button_open_batch_input = ttk.Button(frame_input_batch_directory, text="Open", command=lambda: self.open_directory(self.batch_upscale_path.get()))
            self.button_open_batch_input.pack(side="left", fill="x", padx=2, pady=2)

            frame_output_batch_directory = Frame(frame_comboboxes)
            frame_output_batch_directory.pack(side="top", fill="x", padx=10, pady=10)

            # Output
            self.label_batch_output_path = Label(frame_output_batch_directory, text="Output Path")
            self.label_batch_output_path.pack(anchor="w", side="top", padx=5, pady=5)

            self.batch_output_path = StringVar(value=os.path.join(self.batch_upscale_path.get(), "Upscale_Output"))

            self.entry_batch_output_path = ttk.Entry(frame_output_batch_directory, width=50, textvariable=self.batch_output_path)
            self.entry_batch_output_path.pack(side="left", fill="x", padx=5, pady=5)
            self.output_tooltip = ToolTip.create(self.entry_batch_output_path, self.batch_output_path.get(), 250, 6, 12)

            self.browse_batch_output_button = ttk.Button(frame_output_batch_directory, text="Browse...", command=lambda: self.choose_directory(self.batch_output_path, self.output_tooltip))
            self.browse_batch_output_button.pack(side="left", fill="x", padx=2, pady=2)

            self.open_batch_output_button = ttk.Button(frame_output_batch_directory, text="Open", command=lambda: self.open_directory(self.batch_output_path.get()))
            self.open_batch_output_button.pack(side="left", fill="x", padx=2, pady=2)


        frame_model = Frame(frame_comboboxes)
        frame_model.pack(side="top", fill="x", padx=10, pady=10)

        self.label_upscale_model = Label(frame_model, text="Upscale Model")
        self.label_upscale_model.pack(anchor="w", side="top", padx=5, pady=5)
        self.combobox_upscale_model = ttk.Combobox(frame_model, width=25, state="readonly", values=self.ncnn_models)
        self.combobox_upscale_model.pack(side="top", fill="x", padx=5, pady=5)
        ToolTip.create(self.combobox_upscale_model, "Select the RESRGAN upscale model", 250, 6, 12)
        self.combobox_upscale_model.set("realesr-animevideov3-x4")


        frame_size = Frame(frame_comboboxes)
        frame_size.pack(side="top", fill="x", padx=10, pady=10)

        self.label_size = Label(frame_size, text="Upscale Factor")
        self.label_size.pack(anchor="w", side="top", padx=5, pady=5)
        self.upscale_factor_value = DoubleVar(value=2.00)
        self.slider_upscale_factor = ttk.Scale(frame_size, from_=0.25, to=8.00, orient="horizontal", variable=self.upscale_factor_value, command=self.update_upscale_factor_label)
        self.slider_upscale_factor.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ToolTip.create(self.slider_upscale_factor, "Determines the final size of the image.\n\nImages are first upscaled by 4x and then resized according to the selected upscale factor.\n\nThe final resolution is calculated as: (4 * original size) / upscale factor.", 250, 6, 12)
        self.label_upscale_factor_value = Label(frame_size, textvariable=self.upscale_factor_value, width=5)
        self.label_upscale_factor_value.pack(side="left", anchor="w", padx=5, pady=5)


        frame_slider = Frame(frame_comboboxes)
        frame_slider.pack(side="top", fill="x", padx=10, pady=10)

        self.label_upscale_strength = Label(frame_slider, text="Upscale Strength")
        self.label_upscale_strength.pack(anchor="w", side="top", padx=5, pady=5)
        self.upscale_strength_value = IntVar(value=100)
        self.slider_upscale_strength = ttk.Scale(frame_slider, from_=0, to=100, orient="horizontal", command=self.update_strength_label)
        self.slider_upscale_strength.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ToolTip.create(self.slider_upscale_strength, "Adjust the upscale strength to determine the final blending value of the output image.\n\n0% = Only original image, 100% = Only upscaled image.", 250, 6, 12)
        self.label_upscale_strength_percent = Label(frame_slider, width=5)
        self.label_upscale_strength_percent.pack(anchor="w", side="left", padx=5, pady=5)
        self.slider_upscale_strength.set(100)


####### Info ##################################################


        if self.batch_mode:
            self.frame_info = Frame(self.top)
            self.frame_info.pack(side="top", expand=True, fill="x", padx=10, pady=10)


            separator = ttk.Separator(self.frame_info)
            separator.pack(side="top", fill="x")


            self.frame_labels = Frame(self.frame_info)
            self.frame_labels.pack(side="left", expand=True, fill="x", padx=10, pady=10)

            label_num_images = Label(self.frame_labels, text="Upscaled:")
            label_num_images.pack(anchor="w", side="top", padx=5, pady=5)

            self.label_timer = Label(self.frame_labels, text="Timer: 00:00:00")
            self.label_timer.pack(anchor="w", side="top", padx=5, pady=5)


            self.frame_dimensions = Frame(self.frame_info)
            self.frame_dimensions.pack(side="left", expand=True, fill="x", padx=10, pady=10)

            self.label_number_of_images = Label(self.frame_dimensions, text=f"0 of {self.total_images}", width=20)
            self.label_number_of_images.pack(anchor="w", side="top", padx=5, pady=5)

            self.label_timer_eta = Label(self.frame_dimensions, text="ETA: 00:00:00", width=20)
            self.label_timer_eta.pack(anchor="w", side="top", padx=5, pady=5)


        else:
            self.frame_info = Frame(self.top)
            self.frame_info.pack(side="top", expand=True, fill="x", padx=10, pady=10)


            separator = ttk.Separator(self.frame_info)
            separator.pack(side="top", fill="x")


            self.frame_labels = Frame(self.frame_info)
            self.frame_labels.pack(side="left", expand=True, fill="x", padx=10, pady=10)

            label_current = Label(self.frame_labels, text="Current Size:")
            label_current.pack(anchor="w", side="top", padx=5, pady=5)
            label_new = Label(self.frame_labels, text="New Size:")
            label_new.pack(anchor="w", side="top", padx=5, pady=5)
            if self.filepath.lower().endswith(".gif"):
                label_frames = Label(self.frame_labels, text="Frames:")
                label_frames.pack(anchor="w", side="top", padx=5, pady=5)


            self.frame_dimensions = Frame(self.frame_info)
            self.frame_dimensions.pack(side="left", expand=True, fill="x", padx=10, pady=10)

            self.label_current_dimensions = Label(self.frame_dimensions, text=f"{self.original_image_width} x {self.original_image_height}", width=20)
            self.label_current_dimensions.pack(anchor="w", side="top", padx=5, pady=5)
            self.label_new_dimensions = Label(self.frame_dimensions, text="0 x 0", width=20)
            self.label_new_dimensions.pack(anchor="w", side="top", padx=5, pady=5)
            ToolTip.create(self.label_new_dimensions, " The final size of the image after upscaling ", 250, 6, 12)
            if self.filepath.lower().endswith(".gif"):
                self.label_framecount = Label(self.frame_dimensions, text=f"{self.current_gif_frame} of {self.total_gif_frames}", width=20)
                self.label_framecount.pack(anchor="w", side="top", padx=5, pady=5)


####### Primary Buttons ##################################################
        self.frame_primary_buttons = Frame(self.top)
        self.frame_primary_buttons.pack(side="top", fill="x")


        self.progress_bar = ttk.Progressbar(self.frame_primary_buttons, maximum=100)
        self.progress_bar.pack(side="top", expand=True, fill="x", padx=10, pady=10)


        button_command = self.determine_image_type
        self.button_upscale = ttk.Button(self.frame_primary_buttons, text="Upscale", command=button_command)
        self.button_upscale.pack(side="left", expand=True, fill="x", padx=5, pady=5)


        self.button_cancel = ttk.Button(self.frame_primary_buttons, text="Cancel", command=self.close_window)
        self.button_cancel.pack(side="left", expand=True, fill="x", padx=5, pady=5)

#endregion
################################################################################################################################################
#region -  Primary Functions


    def determine_image_type(self, event=None):
        if self.batch_mode:
            self.batch_upscale()
        else:
            directory, filename = os.path.split(self.filepath)
            filename, extension = os.path.splitext(filename)
            gif_path = self.filepath
            self.set_widget_state(state="disabled")
            if extension.lower() == '.gif':
                self._upscale_gif(gif_path)
            else:
                self.upscale_image()


    def batch_upscale(self):
        self.batch_thread = True
        thread = threading.Thread(target=self._batch_upscale)
        thread.start()
        self.set_widget_state(state="disabled")


    def batch_upscale_cancel_message(self, count):
        messagebox.showinfo("Batch Upscaled Canceled", f"Batch Upscaling canceled early.\n\n{count} of {self.total_images} images upscaled.")


    def _batch_upscale(self):
        input_path = self.batch_upscale_path.get()
        output_path = self.batch_output_path.get()
        count = 0
        start_time = time.time()
        try:
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            for filename in os.listdir(input_path):
                self.top.update()
                self.top.update_idletasks()
                if not self.batch_thread:
                    self.batch_upscale_cancel_message(count)
                    break
                file_path = os.path.join(input_path, filename)
                if os.path.isfile(file_path) and filename.lower().endswith(self.supported_filetypes):
                    self.filepath = file_path
                    if filename.lower().endswith('.gif'):
                        if not self.batch_thread:
                            self.batch_upscale_cancel_message(count)
                            break
                        self._upscale_gif(file_path, batch_mode=True, output_path=output_path)
                    else:
                        if not self.batch_thread:
                            self.batch_upscale_cancel_message(count)
                            break
                        self.upscale_image(batch_mode=True, output_path=output_path)
                    count += 1
                    elapsed_time = time.time() - start_time
                    avg_time_per_image = elapsed_time / count
                    remaining_images = self.total_images - count
                    eta = avg_time_per_image * remaining_images
                    self.top.update()
                    self.top.update_idletasks()
                    if not self.batch_thread:
                        self.batch_upscale_cancel_message(count)
                        break
                    self.label_timer.config(text=f"Timer: {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}")
                    if not self.batch_thread:
                        self.batch_upscale_cancel_message(count)
                        break
                    self.label_timer_eta.config(text=f"ETA: {time.strftime('%H:%M:%S', time.gmtime(eta))}")
                    if not self.batch_thread:
                        self.batch_upscale_cancel_message(count)
                        break
                    self.label_number_of_images.config(text=f"{count} of {self.total_images}")
            self.update_progress(100)
            if self.batch_thread:
                messagebox.showinfo("Success", f"Successfully upscaled {count} images!")
        except Exception as e:
            messagebox.showerror("Error: _batch_upscale()", f"An error occurred during batch upscaling.\n\n{e}")
        finally:
            self.close_window()


    def _upscale_gif(self, gif_path, batch_mode=None, output_path=None):
        try:
            self.button_upscale.config(state="disabled")
            with Image.open(gif_path) as gif:
                frames = [(frame.copy().convert("RGBA"), frame.info['duration']) for frame in ImageSequence.Iterator(gif)]
            temp_dir = os.path.join(os.path.dirname(gif_path), "temp_upscale_img")
            os.makedirs(temp_dir, exist_ok=True)
            upscaled_frames = []
            total_frames = len(frames)
            model = str(self.combobox_upscale_model.get())
            for i, (frame, duration) in enumerate(frames):
                if self.is_window_closed:
                    return
                temp_frame_path = os.path.join(temp_dir, f"frame_{i}.png")
                frame.save(temp_frame_path)
                upscaled_frame_path = os.path.join(temp_dir, f"frame_{i}_upscaled.png")
                self.top.update()
                upscale_command = [
                    self.executable_path,
                    "-i", temp_frame_path,
                    "-o", upscaled_frame_path,
                    "-n", model,
                    "-s", "4",
                    "-f", "jpg"]
                if model not in self.ncnn_models:
                    upscale_command.extend(["-m", self.extra_models_path])
                upscale_process = subprocess.Popen(upscale_command, creationflags=subprocess.CREATE_NO_WINDOW)
                upscale_process.wait()
                self.top.update()
                self.top.update_idletasks()
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
                self.close_window(self.get_image_index(directory, f"{filename}_upscaled{extension}"))
                result = messagebox.askyesno("Upscale Successful", f"Output path:\n{upscaled_gif_path}\n\nOpen image?")
                if result:
                    os.startfile(upscaled_gif_path)
        except (PermissionError, FileNotFoundError, TclError) as e:
            print(f"Error: {e}")
            return
        except Exception as e:
            messagebox.showerror("Error: _upscale_gif()", f"An error occurred.\n\n{e}")
            self.close_window()


    def upscale_image(self, batch_mode=False, output_path=None):
        try:
            self.button_upscale.config(state="disabled")
            self.update_progress(25)
            directory, filename = os.path.split(self.filepath)
            filename, extension = os.path.splitext(filename)
            if extension.lower() == '.webp':
                extension = self.convert_webp_to_jpg(directory, filename)
            output_image_path = os.path.join(output_path if batch_mode else directory, f"{filename}{extension}" if batch_mode else f"{filename}_up{extension}")
            model = str(self.combobox_upscale_model.get())
            upscale_command = [
                self.executable_path,
                "-i", self.filepath,
                "-o", output_image_path,
                "-n", model,
                "-s", "4",
                "-f", "jpg"]
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
                self.blend_images(self.filepath, output_image_path, extension)
            self.update_progress(99)
            if not batch_mode:
                time.sleep(0.1)
                index = self.get_image_index(directory, output_image_path)
                self.close_window(index)
                result = messagebox.askyesno("Upscale Successful", f"Output path:\n{output_image_path}\n\nOpen image?")
                if result:
                    os.startfile(output_image_path)
        except Exception as e:
            messagebox.showerror("Error: upscale_image()", f"An error occurred.\n\n{e}")
            self.close_window()


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
        if not self.top.winfo_exists():
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
#region -  Window drag


    def start_drag(self, event):
        self.start_x = event.x
        self.start_y = event.y


    def stop_drag(self, event):
        self.start_x = None
        self.start_y = None


    def dragging_window(self, event):
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        x = self.top.winfo_x() + dx
        y = self.top.winfo_y() + dy
        self.top.geometry(f"+{x}+{y}")


#endregion
################################################################################################################################################
#region -  Widget highlighting


    def bind_widget_highlight(self, widget, add=False, color=None):
        add = '+' if add else ''
        if color:
            widget.bind("<Enter>", lambda event: self.mouse_enter(event, color), add=add)
        else:
            widget.bind("<Enter>", self.mouse_enter, add=add)
        widget.bind("<Leave>", self.mouse_leave, add=add)


    def mouse_enter(self, event, color='#e5f3ff'):
        if event.widget['state'] == 'normal':
            event.widget['background'] = color


    def mouse_leave(self, event):
        event.widget['background'] = 'SystemButtonFace'


#endregion
################################################################################################################################################
#region -  Image Info / label


    def get_image_info(self):
        try:
            with Image.open(self.filepath) as image:
                self.original_image_width, self.original_image_height = image.size
                if self.filepath.lower().endswith(".gif"):
                    frames = [frame for frame in ImageSequence.Iterator(image)]
                    self.total_gif_frames = len(frames)
                    self.current_gif_frame = format(1, f'0{len(str(self.total_gif_frames))}d')
                else:
                    self.total_gif_frames = None
                    self.current_gif_frame = None
        except Exception as e:
            messagebox.showerror("Error: get_image_info()", f"Unexpected error while opening image.\n\n{e}")
            self.close_window()


    def update_size_info_label(self, event=None):
        if not self.batch_mode:
            selected_scaling_factor = float(self.upscale_factor_value.get())
            new_width = self.original_image_width * selected_scaling_factor
            new_height = self.original_image_height * selected_scaling_factor
            self.label_new_dimensions.config(text=f"{int(new_width)} x {int(new_height)}")
            return new_width, new_height


    def update_strength_label(self, value):
        value = int(float(value))
        self.upscale_strength_value.set(value)
        self.label_upscale_strength_percent.config(text=f"{value}%")


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
            "label_upscale_model",
            "combobox_upscale_model",
            "label_size",
            "entry_size",
            "label_upscale_strength",
            "slider_upscale_strength",
            "label_upscale_factor_value",
            "label_upscale_strength_percent"
        ]
        if self.batch_mode:
            widget_names.extend([
                "label_batch_upscale_path",
                "entry_batch_upscale_path",
                "button_browse_batch_input",
                "button_open_batch_input",
                "label_batch_output_path",
                "entry_batch_output_path",
                "browse_batch_output_button",
                "open_batch_output_button"
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
        with Image.open(self.filepath) as img:
            if img.mode == "RGBA":
                img = img.convert("RGB")
            jpg_filepath = os.path.join(directory, f"{filename}.jpg")
            img.save(jpg_filepath, 'JPEG', quality=100)
            self.converted_filepath = jpg_filepath
            extension = '.jpg'
            return extension


    def update_progress(self, progress):
        if not self.top.winfo_exists():
            return
        self.progress_bar.config(value=progress)
        self.frame_primary_buttons.update_idletasks()


    def delete_temp_dir(self):
        try:
            temp_dir = os.path.join(os.path.dirname(self.filepath), "temp_upscale_img")
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


    def close_window(self, index=None, event=None):
        self.batch_thread = False
        self.is_window_closed = True
        self.delete_temp_dir()
        if index:
            self.parent.update_pair()
            self.parent.jump_to_image(index)
        self.top.destroy()


#endregion
################################################################################################################################################
#region -  Changelog

'''


v1.05 changes:


  - New:
    - Batch Upscale: Added a label to display the number of images upscaled and the total number of images.
    - Batch Upscale: Added a timer and ETA label to show the total time taken and the estimated time remaining.

<br>


  - Fixed:
    - Prevent the app from hanging while upscaling a GIF.


<br>


  - Other changes:
    - Batch Upscale: Entry path ToolTips are now updated when the path is changed.
    - Widgets are now made with ttk (when appropriate) for better styling on Windows 11.


'''

#endregion
################################################################################################################################################
#region - Todo


'''

- Todo
  -

- Tofix
  -

'''

#endregion

