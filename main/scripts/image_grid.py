"""
########################################
#                                      #
#              Image Grid              #
#                                      #
#   Version : v1.02                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
Display a grid of images, clicking an image returns the index as defined in 'natural_sort'.
Images without a text pair have a red flag placed over them.

"""


################################################################################################################################################
#region -  Imports


import os
import re
from tkinter import ttk, Toplevel, IntVar, StringVar, BooleanVar, Frame, Label, Button, Radiobutton, Checkbutton, Scale, Scrollbar, Canvas
from PIL import Image, ImageTk, ImageDraw, ImageFont

from main.scripts.TkToolTip import TkToolTip as ToolTip # type: ignore


#endregion
################################################################################################################################################
#region - CLASS: ImageGrid


class ImageGrid:
    def __init__(self, master, filepath, window_x, window_y, jump_to_image):

        # Window configuration
        self.create_window(master, window_x, window_y)

        # Image navigation function
        self.ImgTxt_jump_to_image = jump_to_image

        # Image directory and supported file types
        self.folder = filepath
        self.supported_filetypes = (".png", ".webp", ".jpg", ".jpeg", ".jpg_large", ".jfif", ".tif", ".tiff", ".bmp", ".gif")

        # Image grid configuration
        self.max_width = 85  # Thumbnail width
        self.max_height = 85  # Thumbnail height
        self.rows = 500  # Max rows
        self.cols = 8  # Max columns
        self.images_per_load = 150  # Num of images to load per set

        # Image loading and filtering
        self.loaded_images = 0  # Num of images loaded to the UI
        self.filtered_images = 0  # Num of images displayed after filtering

        # Image flag and cache
        self.image_flag = self.create_image_flag()
        self.image_cache = {1: {}, 2: {}, 3: {}}  # Cache for each thumbnail size

        # Image files in the folder
        self.all_file_list = self.get_all_files()
        self.image_file_list = self.get_image_files()
        self.num_total_images = len(self.image_file_list)  # Number of images in the folder

        # Default thumbnail size. Range=(1,2,3). Set to 3 if total_images is less than 25.
        self.image_size = IntVar(value=3) if self.num_total_images < 25 else IntVar(value=2)

        # Toggle window auto-close when selecting an image
        self.auto_close = BooleanVar(value=True)

        # Interface creation
        self.create_interface()
        self.load_images()


#endregion
################################################################################################################################################
#region -  Create Interface


    def create_interface(self):
        self.create_top_handle()
        self.create_canvas()
        self.create_control_row()


    def create_top_handle(self):
        self.frame_top_Handle = Frame(self.top)
        self.frame_top_Handle.pack(fill="both")

        title = Label(self.frame_top_Handle, cursor="size", text="Image Grid", font=("", 16))
        title.pack(side="top", fill="x", padx=5, pady=5)
        title.bind("<ButtonPress-1>", self.start_drag)
        title.bind("<ButtonRelease-1>", self.stop_drag)
        title.bind("<B1-Motion>", self.dragging_window)

        self.button_close = Button(self.frame_top_Handle, text="X", overrelief="groove", relief="flat", command=self.close_window)
        self.button_close.place(anchor="nw", relx=0.945, height=40, width=40)
        self.bind_widget_highlight(self.button_close, color='#ffcac9')
        ToolTip.create(self.button_close, "Close", 500, 6, 12)

        separator = ttk.Separator(self.frame_top_Handle)
        separator.pack(side="top", fill="x")


    def create_canvas(self):
        self.frame_main = Frame(self.top)
        self.frame_main.pack(fill="both", expand=True)

        self.scrollbar = Scrollbar(self.frame_main)
        self.scrollbar.pack(side="right", fill="y")

        self.frame_thumbnails = Frame(self.frame_main)
        self.frame_thumbnails.pack(side="left", fill="both", expand=True)

        self.canvas_thumbnails = Canvas(self.frame_thumbnails, yscrollcommand=self.scrollbar.set)
        self.canvas_thumbnails.pack(side="top", fill="both", expand=True)
        self.canvas_thumbnails.bind("<MouseWheel>", self.on_mousewheel)

        self.scrollbar.config(command=self.canvas_thumbnails.yview)

        self.frame_image_grid = Frame(self.canvas_thumbnails)
        self.frame_image_grid.bind("<MouseWheel>", self.on_mousewheel)


    def create_control_row(self):
        self.frame_bottom = Frame(self.frame_thumbnails)
        self.frame_bottom.pack(side="bottom", fill="x", padx=5)

        self.label_image_info = Label(self.frame_bottom, text="Size:")
        self.label_image_info.pack(side="left", padx=5)
        ToolTip.create(self.label_image_info, "Adjust grid size", 500, 6, 12)

        self.slider_image_size = Scale(self.frame_bottom, variable=self.image_size, orient="horizontal", from_=1, to=3, showvalue=False)
        self.slider_image_size.bind("<ButtonRelease-1>", lambda event: self.reload_grid())
        self.slider_image_size.pack(side="left")
        ToolTip.create(self.slider_image_size, "Adjust grid size", 500, 6, 12)

        self.grip_window_size = ttk.Sizegrip(self.frame_bottom)
        self.grip_window_size.pack(side="right", padx=(5,0))
        ToolTip.create(self.grip_window_size, "Adjust window size", 500, 6, 12)

        self.button_load_all = Button(self.frame_bottom, text="Load All", overrelief="groove", command=lambda: self.load_images(all_images=True))
        self.button_load_all.pack(side="right", padx=5)
        ToolTip.create(self.button_load_all, "Load all images in the folder (Slow)", 500, 6, 12)

        self.label_image_info = Label(self.frame_bottom)
        self.label_image_info.pack(side="right", padx=5)
        ToolTip.create(self.label_image_info, "Filtered Images : Loaded Images, Total Images", 500, 6, 12)

        self.image_filter = StringVar(value="All")
        self.radiobutton_all = Radiobutton(self.frame_bottom, text="All", variable=self.image_filter, value="All", command=self.reload_grid)
        self.radiobutton_all.pack(side="left", padx=5)
        ToolTip.create(self.radiobutton_all, "Display all LOADED images", 500, 6, 12)

        self.radiobutton_paired = Radiobutton(self.frame_bottom, text="Paired", variable=self.image_filter, value="Paired", command=self.reload_grid)
        self.radiobutton_paired.pack(side="left", padx=5)
        ToolTip.create(self.radiobutton_paired, "Display images with text pairs", 500, 6, 12)

        self.radiobutton_unpaired = Radiobutton(self.frame_bottom, text="Unpaired", variable=self.image_filter, value="Unpaired", command=self.reload_grid)
        self.radiobutton_unpaired.pack(side="left", padx=5)
        ToolTip.create(self.radiobutton_unpaired, "Display images without text pairs", 500, 6, 12)

        self.checkbutton_auto_close = Checkbutton(self.frame_bottom, text="Auto-Close", variable=self.auto_close, command=self.toggle_auto_close)
        self.checkbutton_auto_close.pack(side="left", padx=5)
        ToolTip.create(self.checkbutton_auto_close, "Uncheck this to keep the window open after selecting an image", 500, 6, 12)


#endregion
################################################################################################################################################
#region -  Interface Logic


    def update_image_info_label(self):
        self.update_filtered_images()
        self.update_shown_images()
        self.update_button_state()


    def update_shown_images(self):
        shown_images = min(self.filtered_images, self.loaded_images)
        self.label_image_info.config(text=f"{shown_images} : {self.loaded_images}, of {self.num_total_images}")


    def update_button_state(self):
        if self.loaded_images == self.num_total_images:
            self.button_load_all.config(state="disabled")


    def reload_grid(self):
        for widget in self.frame_image_grid.winfo_children():
            widget.destroy()
        size_settings = {
            1: (50, 50, 13),
            2: (85, 85, 8),
            3: (175, 175, 4)
            }
        self.max_width, self.max_height, self.cols = size_settings.get(self.image_size.get(), (85, 85, 8))
        self.update_image_info_label()
        self.create_image_grid()


    def create_image_grid(self):
        self.canvas_thumbnails.create_window((0,0), window=self.frame_image_grid, anchor='nw')
        self.images = self.load_image_set()
        for row_index in range(self.rows):
            for col_index in range(self.cols):
                if self.images and row_index * self.cols + col_index < self.loaded_images:
                    image, filepath, image_index = self.images.pop(0)
                    thumbnail = Button(self.frame_image_grid, relief="flat", overrelief="groove", image=image, command=lambda  path=filepath: self.on_mouse_click(path))
                    thumbnail.image = image
                    thumbnail.grid(row=row_index, column=col_index)
                    thumbnail.bind("<MouseWheel>", self.on_mousewheel)
                    ToolTip.create(thumbnail, f"#{image_index + 1}, {os.path.basename(filepath)}", 200, 6, 12)
        scroll_index = self.loaded_images / self.cols
        scroll_index *= 1.2
        scrollregion_height = scroll_index * self.max_height
        self.canvas_thumbnails.config(scrollregion=(0, 0, 750, scrollregion_height))
        if self.image_filter.get() == "All":
            if self.loaded_images < self.num_total_images:
                load_more_button = Button(self.frame_image_grid, text="Load More...", height=2, command=self.load_images)
                load_more_button.grid(row=self.rows, column=0, columnspan=self.cols, sticky="ew", pady=5)
                ToolTip.create(load_more_button, "Load the next 150 images", 500, 6, 12)


    def on_mouse_click(self, path):
        index = self.get_image_index(self.folder, path)
        self.ImgTxt_jump_to_image(index)
        if self.auto_close.get() == True:
            self.close_window()


    def on_mousewheel(self, event):
        if self.canvas_thumbnails.winfo_exists():
            self.canvas_thumbnails.yview_scroll(int(-1*(event.delta/120)), "units")


    def toggle_auto_close(self):
        if self.auto_close.get():
            self.top.grab_set()
        else:
            self.top.grab_release()


#endregion
################################################################################################################################################
#region -  Primary Functions


    def load_images(self, all_images=False):
        self.loaded_images = self.num_total_images if all_images else min(self.loaded_images + self.images_per_load, self.num_total_images)
        self.update_image_info_label()
        self.reload_grid()


    def load_image_set(self):
        images = []
        image_count = 0
        for image_index, filename in enumerate(sorted(self.image_file_list, key=self.natural_sort)):
            if not self.filter_images(filename):
                continue
            img_path = os.path.join(self.folder, filename)
            txt_path = os.path.splitext(img_path)[0] + '.txt'
            new_img = self.image_cache[self.image_size.get()].get(img_path)
            if new_img is None:
                new_img = Image.new("RGBA", (self.max_width, self.max_height))
                new_img = self.paste_image_flag(new_img, img_path, txt_path)
            images.append((ImageTk.PhotoImage(new_img), img_path, image_index))
            image_count += 1
            if image_count >= self.loaded_images:
                break
        return images


    def filter_images(self, filename):
        if not filename.lower().endswith(self.supported_filetypes):
            return False
        img_path = os.path.join(self.folder, filename)
        txt_path = os.path.splitext(img_path)[0] + '.txt'
        try:
            file_info = os.stat(txt_path)
            file_size = file_info.st_size
        except FileNotFoundError:
            file_size = 0
        if self.image_filter.get() == "All":
            return True
        elif self.image_filter.get() == "Paired" and file_size != 0:
            return True
        elif self.image_filter.get() == "Unpaired" and file_size == 0:
            return True
        return False


    def update_filtered_images(self):
        self.filtered_images = sum(1 for filename in filter(self.filter_images, sorted(self.image_file_list, key=self.natural_sort)))


    def paste_image_flag(self, new_img, img_path, txt_path):
        img = Image.open(img_path)
        img.thumbnail((self.max_width, self.max_height))
        position = ((self.max_width - img.width) // 2, (self.max_height - img.height) // 2)
        new_img.paste(img, position)
        if not os.path.exists(txt_path) or os.path.getsize(txt_path) == 0:
            image_flag_position = (self.max_width - self.image_flag.width, self.max_height - self.image_flag.height)
            new_img.paste(self.image_flag, image_flag_position, mask=self.image_flag)
        self.image_cache[self.image_size.get()][img_path] = new_img
        return new_img


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
#region -  Misc


    def create_image_flag(self):
        flag_size = 15
        outline_width = 1
        left, top = [dim - flag_size - outline_width for dim in (self.max_width, self.max_height)]
        right, bottom = self.max_width, self.max_height
        image_flag = Image.new('RGBA', (self.max_width, self.max_height))
        draw = ImageDraw.Draw(image_flag)
        draw.rectangle(((left, top), (right, bottom)), fill="black")
        left += outline_width
        top += outline_width
        draw.rectangle(((left, top), (right - outline_width, bottom - outline_width)), fill="red")
        corner_size = flag_size // 2
        triangle_points = [(left - outline_width, top - outline_width), (left + corner_size, top - outline_width), (left - outline_width, top + corner_size)]
        draw.polygon(triangle_points, fill=(0, 0, 0, 0))
        draw.polygon([(left, top), (left + corner_size, top), (left, top + corner_size)], fill=(0, 0, 0, 0))
        center = ((left + right) // 2, (top + bottom) // 2)
        font = ImageFont.truetype("arial", 15)
        draw.text(center, " -", fill="white", font=font, anchor="mm")
        return image_flag


    def get_image_index(self, directory, filename):
        filename = os.path.basename(filename)
        files = os.listdir(directory)
        image_files = [file for file in files if file.lower().endswith(self.supported_filetypes)]
        image_files.sort(key=self.natural_sort)
        indexed_files = list(enumerate(image_files))
        for index, file in indexed_files:
            if file == filename:
                return index


    def get_all_files(self):
        try:
            return os.listdir(self.folder)
        except (FileNotFoundError, NotADirectoryError):
            return


    def get_image_files(self):
        return [name for name in self.all_file_list if os.path.isfile(os.path.join(self.folder, name)) and name.lower().endswith(self.supported_filetypes)]


    def natural_sort(self, string):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', string)]


#endregion
################################################################################################################################################
#region - Framework


    def create_window(self, master, window_x, window_y):
        # Create a new top-level widget and configure its properties
        self.top = Toplevel(master, borderwidth=2, relief="groove")
        self.top.overrideredirect(True)

        # Set the geometry (size and position) of the window
        window_size = "750x600"
        window_position = f"+{window_x}+{window_y}"
        self.top.geometry(f"{window_size}{window_position}")

        # Set the minimum and maximum size of the window
        self.top.minsize(750, 300)
        self.top.maxsize(750, 6000)

        # Make the window modal and set focus to it
        self.top.grab_set()
        self.top.focus_force()

        # Bind the Escape key to the close_window method
        self.top.bind("<Escape>", self.close_window)


    def close_window(self):
        self.top.destroy()


#endregion
################################################################################################################################################
#region - Changelog


'''

v1.02 changes:

  - New:
    -

<br>

  - Fixed:
    - Fixed issue where supported filetypes were case sensitive.

<br>

  - Other changes:
    -


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
