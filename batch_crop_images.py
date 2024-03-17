"""
########################################
#                                      #
#           Batch Crop Images          #
#                                      #
#   Version : v1.00                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
Crop a folder of images by resizing (ensuring they are larger than the target) then cropping to the target resolution.

"""

####### Imports #############################################


import os
import shutil
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image


####### Class Setup #########################################


class BatchCrop:
    def __init__(self, master, filepath, window_x, window_y):
        self.top = Toplevel(master, borderwidth=2, relief="groove")
        self.top.overrideredirect("true")
        self.top.geometry("+{}+{}".format(window_x, window_y))
        self.top.grab_set()
        self.top.focus_force()
        self.top.bind("<Escape>", self.close_window)

        self.filepath = filepath
        self.supported_formats = {".jpg", ".jpeg", ".png", ".jfif", ".jpg_large", ".bmp", ".webp"}

        self.create_interface()


    def create_interface(self):

        self.frame_container = Frame(self.top)
        self.frame_container.pack(expand=True, fill="both")


        # Title
        title = Label(self.frame_container, cursor="size", text="Batch Crop Images", font=("", 16))
        title.pack(side="top", fill="x", padx=5, pady=5)
        title.bind("<ButtonPress-1>", self.start_drag)
        title.bind("<ButtonRelease-1>", self.stop_drag)
        title.bind("<B1-Motion>", self.dragging_window)

        self.button_close = Button(self.frame_container, text="X", overrelief="groove", relief="flat", command=self.close_window)
        self.button_close.place(anchor="nw", relx=0.92, height=40, width=40, x=-10, y=0)
        self.bind_widget_highlight(self.button_close, color='#ffcac9')

        separator = ttk.Separator(self.frame_container)
        separator.pack(side="top", fill="x")


        # Width and Height Entry
        self.frame_width_height = Frame(self.top)
        self.frame_width_height.pack(side="top", fill="x", padx=10, pady=10)

        self.frame_width = Frame(self.frame_width_height)
        self.frame_width.pack(side="left", fill="x", padx=10, pady=10)

        self.label_width = Label(self.frame_width, text="Width (px)")
        self.label_width.pack(anchor="w", side="top", padx=5, pady=5)
        self.entry_width_var = StringVar()
        self.entry_width = Entry(self.frame_width, textvariable=self.entry_width_var)
        self.entry_width.pack(side="top", padx=5, pady=5)
        self.entry_width.bind("<Return>", self.process_images)

        self.frame_height = Frame(self.frame_width_height)
        self.frame_height.pack(side="left", fill="x", padx=10, pady=10)

        self.label_height = Label(self.frame_height, text="Height (px)")
        self.label_height.pack(anchor="w", side="top", padx=5, pady=5)
        self.entry_height_var = StringVar()
        self.entry_height = Entry(self.frame_height, textvariable=self.entry_height_var)
        self.entry_height.pack(side="top", padx=5, pady=5)
        self.entry_height.bind("<Return>", self.process_images)


        # Primary Buttons
        self.frame_primary_buttons = Frame(self.top)
        self.frame_primary_buttons.pack(side="top", fill="x")

        self.button_crop = Button(self.frame_primary_buttons, overrelief="groove", text="Crop", command=self.process_images)
        self.button_crop.pack(side="left", expand=True, fill="x", padx=5, pady=5)

        self.button_cancel = Button(self.frame_primary_buttons, overrelief="groove", text="Cancel", command=self.close_window)
        self.button_cancel.pack(side="left", expand=True, fill="x", padx=5, pady=5)


####### Primary Functions #######################################


    def resize_image(self, image, resolution):
        width, height = image.size
        new_width, new_height = resolution
        if width < new_width or height < new_height:
            aspect_ratio = width / height
            if aspect_ratio > (new_width / new_height):
                new_width = int(new_height * aspect_ratio)
            else:
                new_height = int(new_width / aspect_ratio)
            image = image.resize((new_width, new_height), Image.LANCZOS)
        return image


    def crop_image(self, image, resolution):
        width, height = image.size
        new_width, new_height = resolution
        left = (width - new_width) / 2
        top = (height - new_height) / 2
        right = (width + new_width) / 2
        bottom = (height + new_height) / 2
        return image.crop((left, top, right, bottom))


    def rename_text_files(self):
        new_directory = os.path.join(self.filepath, 'cropped_images')
        for filename in os.listdir(self.filepath):
            if filename.endswith(".txt"):
                basename = os.path.splitext(filename)[0]
                for image_filename in os.listdir(new_directory):
                    if image_filename.startswith(basename):
                        new_basename = os.path.splitext(image_filename)[0]
                        new_txt_filename = f"{new_basename}.txt"
                        shutil.copy(os.path.join(self.filepath, filename), os.path.join(new_directory, new_txt_filename))


    def process_images(self, event=None):
        try:
            new_directory = os.path.join(self.filepath, 'cropped_images')
            os.makedirs(new_directory, exist_ok=True)
            for filename in os.listdir(self.filepath):
                if any(filename.endswith(format) for format in self.supported_formats):
                    image = Image.open(os.path.join(self.filepath, filename))
                    resolution = (int(self.entry_width_var.get()),
                                  int(self.entry_height_var.get()))
                    resized_image = self.resize_image(image, resolution)
                    cropped_image = self.crop_image(resized_image, resolution)
                    if cropped_image.mode == 'RGBA':
                        cropped_image = cropped_image.convert('RGB')
                    cropped_image.save(os.path.join(new_directory, f'{os.path.splitext(filename)[0]}_{resolution[0]}x{resolution[1]}.jpg'), quality=100)
            self.rename_text_files()
            self.close_window()
            result = messagebox.askyesno("Crop Successful", f"All images cropped successfuly.\n\nOutput path:\n{new_directory}\n\nOpen output path?")
            if result:
               os.startfile(new_directory)
        except ValueError:
            messagebox.showerror("Error", "Invalid values. Please enter valid digits.")
        except (PermissionError, IOError) as e:
            messagebox.showerror("Error", f"An error occurred.\n\n{e}")
            self.close_window()



####### Window drag bar setup #######################################


    def start_drag(self, event):
        self.x = event.x
        self.y = event.y


    def stop_drag(self, event):
        self.x = None
        self.y = None


    def dragging_window(self, event):
        dx = event.x - self.x
        dy = event.y - self.y
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


    def close_window(self, event=None):
        self.top.destroy()