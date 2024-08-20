"""
########################################
#                                      #
#             Upscale Image            #
#                                      #
#   Version : v1.03                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
Upscale a single image using realesrgan-ncnn-vulkan.exe

"""

################################################################################################################################################
#region -  Imports


import os
import re
import time
import shutil
import threading
import subprocess
from tkinter import ttk, Toplevel, messagebox, Frame, Label, Button, TclError
from PIL import Image, ImageSequence


#endregion
################################################################################################################################################
#region - CLASS: Upscale


class Upscale:
    def __init__(self, master, img_txt_viewer, filepath, window_x, window_y, update_pair, jump_to_image):
        self.top = Toplevel(master, borderwidth=2, relief="groove")
        self.top.overrideredirect("true")
        self.top.geometry("+{}+{}".format(window_x, window_y))
        self.top.grab_set()
        self.top.focus_force()
        self.top.bind("<Escape>", self.close_window)

        self.supported_filetypes = (".png", ".webp", ".jpg", ".jpeg", ".jpg_large", ".jfif", ".tif", ".tiff", ".bmp", ".gif")

        self.img_txt_viewer = img_txt_viewer
        self.sort_key = self.img_txt_viewer.get_file_sort_key()
        self.ImgTxt_update_pair = update_pair
        self.ImgTxt_jump_to_image = jump_to_image

        self.process = None
        self.start_x = None
        self.start_y = None

        self.original_filepath = filepath
        self.converted_filepath = None

        self.total_gif_frames = None
        self.current_gif_frame = None

        self.is_window_closed = False


        self.get_image_info()
        self.create_interface()
        self.update_size_info_label()


#endregion
################################################################################################################################################
#region -  Setup Interface


    def create_interface(self):

        self.frame_container = Frame(self.top)
        self.frame_container.pack(expand=True, fill="both")


        title = Label(self.frame_container, cursor="size", text="Upscale Image", font=("", 16))
        title.pack(side="top", fill="x", padx=5, pady=5)
        title.bind("<ButtonPress-1>", self.start_drag)
        title.bind("<ButtonRelease-1>", self.stop_drag)
        title.bind("<B1-Motion>", self.dragging_window)


        self.button_close = Button(self.frame_container, text="X", overrelief="groove", relief="flat", command=self.close_window)
        self.button_close.place(anchor="nw", relx=0.92, height=40, width=40, x=-15, y=0)
        self.bind_widget_highlight(self.button_close, color='#ffcac9')


        separator = ttk.Separator(self.frame_container)
        separator.pack(side="top", fill="x")


####### Options ##################################################
        frame_comboboxes = Frame(self.frame_container)
        frame_comboboxes.pack(side="left", fill="x", padx=10, pady=10)


        frame_model = Frame(frame_comboboxes)
        frame_model.pack(side="left", fill="x", padx=10, pady=10)


        self.label_upscale_model = Label(frame_model, text="Upscale Model")
        self.label_upscale_model.pack(anchor="w", side="top", padx=5, pady=5)
        self.combobox_upscale_model = ttk.Combobox(frame_model, width=25, state="readonly", values=["realesr-animevideov3-x4", "RealESRGAN_General_x4_v3", "realesrgan-x4plus", "realesrgan-x4plus-anime"])
        self.combobox_upscale_model.pack(side="top", fill="x", padx=5, pady=5)
        self.combobox_upscale_model.set("realesr-animevideov3-x4")


        frame_size = Frame(frame_comboboxes)
        frame_size.pack(side="left", fill="x", padx=10, pady=10)


        self.label_size = Label(frame_model, text="Upscale Factor")
        self.label_size.pack(anchor="w", side="top", padx=5, pady=5)
        self.entry_size = ttk.Combobox(frame_model, width=5, state="readonly", values=["1x", "2x", "3x", "4x"])
        self.entry_size.pack(side="top", anchor="w", padx=5, pady=5)
        self.entry_size.bind("<<ComboboxSelected>>", self.update_size_info_label)
        self.entry_size.set("2x")


####### Info ##################################################
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
        if self.original_filepath.lower().endswith(".gif"):
            label_frames = Label(self.frame_labels, text="Frames:")
            label_frames.pack(anchor="w", side="top", padx=5, pady=5)


        self.frame_dimensions = Frame(self.frame_info)
        self.frame_dimensions.pack(side="left", expand=True, fill="x", padx=10, pady=10)


        self.label_current_dimensions = Label(self.frame_dimensions, text=f"{self.original_image_width} x {self.original_image_height}", width=20)
        self.label_current_dimensions.pack(anchor="w", side="top", padx=5, pady=5)
        self.label_new_dimensions = Label(self.frame_dimensions, text="0 x 0", width=20)
        self.label_new_dimensions.pack(anchor="w", side="top", padx=5, pady=5)
        if self.original_filepath.lower().endswith(".gif"):
            self.label_framecount = Label(self.frame_dimensions, text=f"{self.current_gif_frame} of {self.total_gif_frames}", width=20)
            self.label_framecount.pack(anchor="w", side="top", padx=5, pady=5)



####### Primary Buttons ##################################################
        self.frame_primary_buttons = Frame(self.top)
        self.frame_primary_buttons.pack(side="top", fill="x")


        self.progress_bar = ttk.Progressbar(self.frame_primary_buttons, maximum=100)
        self.progress_bar.pack(side="top", expand=True, fill="x", padx=10, pady=10)


        self.button_upscale = Button(self.frame_primary_buttons, overrelief="groove", text="Upscale", command=self.determine_image_type)
        self.button_upscale.pack(side="left", expand=True, fill="x", padx=5, pady=5)


        self.button_cancel = Button(self.frame_primary_buttons, overrelief="groove", text="Cancel", command=self.close_window)
        self.button_cancel.pack(side="left", expand=True, fill="x", padx=5, pady=5)


#endregion
################################################################################################################################################
#region -  Primary Functions


    def determine_image_type(self):
        directory, filename = os.path.split(self.original_filepath)
        filename, extension = os.path.splitext(filename)
        gif_path = self.original_filepath
        if extension.lower() == '.gif':
            self.upscale_gif(gif_path)
        else:
            self.upscale_image()


    def upscale_gif(self, gif_path):
        upscale_thread = threading.Thread(target=self._upscale_gif, args=(gif_path,))
        upscale_thread.start()


    def _upscale_gif(self, gif_path):
        try:
            self.button_upscale.config(state="disabled")
            gif = Image.open(gif_path)
            frames = [(frame.copy().convert("RGB"), frame.info['duration']) for frame in ImageSequence.Iterator(gif)]
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
                subprocess.run(["main/bin/resrgan/realesrgan-ncnn-vulkan.exe",
                                "-i", temp_frame_path,
                                "-o", upscaled_frame_path,
                                "-n", model,
                                "-s", "4",
                                "-f", "jpg"],
                                creationflags=subprocess.CREATE_NO_WINDOW)
                self.resize_image(upscaled_frame_path)
                if os.path.exists(upscaled_frame_path):
                    upscaled_frame = Image.open(upscaled_frame_path).convert("RGB")
                    upscaled_frames.append((upscaled_frame, duration))
                self.update_progress((i+1)/total_frames*90)
                padded_frame_number = str(i+1).zfill(len(str(total_frames)))
                self.label_framecount.config(text=f"{padded_frame_number} of {total_frames}")
            directory, filename = os.path.split(gif_path)
            filename, extension = os.path.splitext(filename)
            upscaled_gif_path = os.path.join(directory, f"{filename}_upscaled{extension}")
            upscaled_frames[0][0].save(upscaled_gif_path, save_all=True, append_images=[frame for frame, _ in upscaled_frames[1:]], loop=0, duration=[duration for _, duration in upscaled_frames])
            shutil.rmtree(temp_dir)
            self.update_progress(99)
            time.sleep(0.1)
            self.close_window(self.get_image_index(directory, f"{filename}_upscaled{extension}"))
            result = messagebox.askyesno("Upscale Successful", f"Output path:\n{upscaled_gif_path}\n\nOpen image?")
            if result:
                os.startfile(upscaled_gif_path)
        except (PermissionError, FileNotFoundError, TclError):
            return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred.\n\n{e}")
            self.close_window()


    def upscale_image(self):
        try:
            self.button_upscale.config(state="disabled")
            self.update_progress(25)
            directory, filename = os.path.split(self.original_filepath)
            filename, extension = os.path.splitext(filename)
            if extension.lower() == '.webp':
                extension = self.convert_webp_to_jpg(directory, filename)
            output_image_path = os.path.join(directory, f"{filename}_up{extension}")
            model = str(self.combobox_upscale_model.get())
            upscale_process = subprocess.Popen(["main/bin/resrgan/realesrgan-ncnn-vulkan.exe",
                              "-i", self.original_filepath,
                              "-o", output_image_path,
                              "-n", model,
                              "-s", "4",
                              "-f", "jpg"],
                              creationflags=subprocess.CREATE_NO_WINDOW)
            self.update_progress(40)
            upscale_process.wait()
            self.update_progress(75)
            self.resize_image(output_image_path)
            self.update_progress(99)
            time.sleep(0.1)
            self.delete_converted_image()
            index = self.get_image_index(directory, output_image_path)
            self.close_window(index)
            result = messagebox.askyesno("Upscale Successful", f"Output path:\n{output_image_path}\n\nOpen image?")
            if result:
               os.startfile(output_image_path)
        except (Exception) as e:
            messagebox.showerror("Error", f"An error occurred.\n\n{e}")
            self.close_window()


    def get_image_index(self, directory, filename):
        filename = os.path.basename(filename)
        image_files = sorted((file for file in os.listdir(directory) if file.lower().endswith(self.supported_filetypes)), key=self.sort_key)
        return image_files.index(filename) if filename in image_files else -1


    def delete_converted_image(self):
        if self.converted_filepath and os.path.exists(self.converted_filepath):
            os.remove(self.converted_filepath)
            self.converted_filepath = None


    def resize_image(self, output_image_path):
        if not self.top.winfo_exists():
            return
        selected_scaling_factor = int(self.entry_size.get().strip("x"))
        if selected_scaling_factor == 4:
            return
        with Image.open(output_image_path).convert("RGB") as img:
            new_width = self.original_image_width * selected_scaling_factor
            new_height = self.original_image_height * selected_scaling_factor
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
#region -  Image Info


    def get_image_info(self):
        try:
            image = Image.open(self.original_filepath)
            self.original_image_width, self.original_image_height = image.size
            if self.original_filepath.lower().endswith(".gif"):
                frames = [frame for frame in ImageSequence.Iterator(image)]
                self.total_gif_frames = len(frames)
                self.current_gif_frame = format(1, f'0{len(str(self.total_gif_frames))}d')
            else:
                self.total_gif_frames = None
                self.current_gif_frame = None
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while opening image.\n\n{e}")
            self.close_window()


    def update_size_info_label(self, event=None):
        selected_scaling_factor = int(self.entry_size.get().strip("x"))
        new_width = self.original_image_width * selected_scaling_factor
        new_height = self.original_image_height * selected_scaling_factor
        self.label_new_dimensions.config(text=f"{new_width} x {new_height}")
        return new_width, new_height


#endregion
################################################################################################################################################
#region -  Misc


    def convert_webp_to_jpg(self, directory, filename):
        img = Image.open(self.original_filepath)
        if img.mode == "RGBA":
            img = img.convert("RGB")
        jpg_filepath = os.path.join(directory, f"{filename}.jpg")
        img.save(jpg_filepath, 'JPEG', quality=100)
        self.converted_filepath = jpg_filepath
        self.original_filepath = jpg_filepath
        extension = '.jpg'
        return extension


    def update_progress(self, progress):
        if not self.top.winfo_exists():
            return
        self.progress_bar.config(value=progress)
        self.frame_primary_buttons.update_idletasks()


    def delete_temp_dir(self):
        try:
            temp_dir = os.path.join(os.path.dirname(self.original_filepath), "temp_upscale_img")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except (PermissionError, FileNotFoundError):
            return


    def close_window(self, index=None, event=None):
        self.is_window_closed = True
        self.delete_temp_dir()
        if index:
            self.ImgTxt_update_pair()
            self.ImgTxt_jump_to_image(index)
        self.top.destroy()


#endregion
################################################################################################################################################
#region -  Changelog

'''


v1.03 changes:


  - New:
    - Added more supported filetypes


<br>


  - Fixed:
    -


<br>


  - Other changes:
    - Update index logic to support new loading order options


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
