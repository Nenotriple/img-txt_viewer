"""
########################################
#                                      #
#             Upscale Image            #
#                                      #
#   Version : v1.00                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
Upscale a single image using realesrgan-ncnn-vulkan.exe

"""

####### Imports #############################################


import os
import time
import subprocess
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image


####### Class Setup #########################################

class Upscale:
    def __init__(self, master, filepath, window_x, window_y, update_pair):
        self.top = Toplevel(master, borderwidth=2, relief="groove")
        self.top.overrideredirect("true")
        self.top.geometry("+{}+{}".format(window_x, window_y))
        self.top.grab_set()
        self.top.focus_force()
        self.top.bind("<Escape>", self.close_window)

        self.ImgTxt_update_pair = update_pair

        self.process = None
        self.start_x = None
        self.start_y = None

        self.original_filepath = filepath
        self.converted_filepath = None

        self.get_image_info()
        self.create_interface()
        self.update_info_label()


####### Setup Interface ##################################################
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


        self.label_size = Label(frame_model, text="Upscale Model")
        self.label_size.pack(anchor="w", side="top", padx=5, pady=5)
        self.entry_size = ttk.Combobox(frame_model, width=25, state="readonly", values=["1x", "2x", "3x", "4x"])
        self.entry_size.pack(side="top", fill="x", padx=5, pady=5)
        self.entry_size.bind("<<ComboboxSelected>>", self.update_info_label)
        self.entry_size.set("2x")


####### Info ##################################################
        self.frame_info = Frame(self.top)
        self.frame_info.pack(side="top", expand=True, fill="x", padx=10, pady=10)


        separator = ttk.Separator(self.frame_info)
        separator.pack(side="top", fill="x")


        self.frame_labels = Frame(self.frame_info)
        self.frame_labels.pack(side="left", expand=True, fill="x", padx=10, pady=10)


        label_current = Label(self.frame_labels, text="Current:")
        label_current.pack(anchor="w", side="top", padx=5, pady=5)
        label_new = Label(self.frame_labels, text="New:")
        label_new.pack(anchor="w", side="top", padx=5, pady=5)


        self.frame_dimensions = Frame(self.frame_info)
        self.frame_dimensions.pack(side="left", expand=True, fill="x", padx=10, pady=10)


        self.label_current_dimensions = Label(self.frame_dimensions, text=f"{self.original_image_width} x {self.original_image_height}", width=20)
        self.label_current_dimensions.pack(anchor="w", side="top", padx=5, pady=5)
        self.label_new_dimensions = Label(self.frame_dimensions, text="0 x 0", width=20)
        self.label_new_dimensions.pack(anchor="w", side="top", padx=5, pady=5)




####### Primary Buttons ##################################################
        self.frame_primary_buttons = Frame(self.top)
        self.frame_primary_buttons.pack(side="top", fill="x")


        self.progress_bar = ttk.Progressbar(self.frame_primary_buttons, maximum=100)
        self.progress_bar.pack(side="top", expand=True, fill="x", padx=10, pady=10)


        self.button_upscale = Button(self.frame_primary_buttons, overrelief="groove", text="Upscale", command=self.upscale_image)
        self.button_upscale.pack(side="left", expand=True, fill="x", padx=5, pady=5)


        self.button_cancel = Button(self.frame_primary_buttons, overrelief="groove", text="Cancel", command=self.close_window)
        self.button_cancel.pack(side="left", expand=True, fill="x", padx=5, pady=5)


####### Primary Functions #######################################


    def get_image_info(self):
        try:
            image = Image.open(self.original_filepath)
            self.original_image_width, self.original_image_height = image.size
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while opening image.\n\n{e}")
            self.close_window()


    def update_info_label(self, event=None):
        selected_scaling_factor = int(self.entry_size.get().strip("x"))
        new_width = self.original_image_width * selected_scaling_factor
        new_height = self.original_image_height * selected_scaling_factor
        self.label_new_dimensions.config(text=f"{new_width} x {new_height}")
        return new_width, new_height


    def upscale_image(self):
        try:
            self.update_progress(25)
            directory, filename = os.path.split(self.original_filepath)
            filename, extension = os.path.splitext(filename)
            if extension.lower() == '.webp':
                img = Image.open(self.original_filepath)
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                jpg_filepath = os.path.join(directory, f"{filename}.jpg")
                img.save(jpg_filepath, 'JPEG', quality=100)
                self.converted_filepath = jpg_filepath
                self.original_filepath = jpg_filepath
                extension = '.jpg'
            index = 0
            while os.path.exists(os.path.join(directory, f"{filename}_up{index}{extension}")):
                index += 1
            output_image_path = os.path.join(directory, f"{filename}_up{index}{extension}")
            model = str(self.combobox_upscale_model.get())
            self.process = subprocess.Popen(["resrgan/realesrgan-ncnn-vulkan.exe",
                                             "-i", self.original_filepath,
                                             "-o", output_image_path,
                                             "-n", model,
                                             "-s", "4",
                                             "-f", "jpg"],
                                             creationflags=subprocess.CREATE_NO_WINDOW)
            self.update_progress(40)
            self.process.wait()
            self.update_progress(75)
            self.resize_image(output_image_path)
            self.update_progress(99)
            time.sleep(0.1)
            self.delete_converted_image()
            self.close_window()
            result = messagebox.askyesno("Upscale Successful", f"Output path:\n{output_image_path}\n\nOpen image?")
            if result:
               os.startfile(output_image_path)
        except (Exception) as e:
            messagebox.showerror("Error", f"An error occurred.\n\n{e}")
            self.close_window()

    def delete_converted_image(self):
        if self.converted_filepath and os.path.exists(self.converted_filepath):
            os.remove(self.converted_filepath)
            self.converted_filepath = None


    def resize_image(self, output_image_path):
        selected_scaling_factor = int(self.entry_size.get().strip("x"))
        if selected_scaling_factor == 4:
            return
        with Image.open(output_image_path) as img:
            new_width = self.original_image_width * selected_scaling_factor
            new_height = self.original_image_height * selected_scaling_factor
            img = img.resize((new_width, new_height), Image.LANCZOS)
            img.save(output_image_path, quality=100)


####### Window drag bar setup #######################################


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


####### Widget highlighting setup #######################################


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


####### Misc #######################################


    def update_progress(self, progress):
        self.progress_bar.config(value=progress)
        self.frame_primary_buttons.update_idletasks()


    def close_window(self, event=None):
        self.ImgTxt_update_pair()
        self.top.destroy()