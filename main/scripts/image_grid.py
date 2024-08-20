"""
########################################
#                                      #
#              Image Grid              #
#                                      #
#   Version : v1.03                    #
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
import configparser
from tkinter import ttk, Toplevel, IntVar, StringVar, BooleanVar, Frame, Label, Button, Scale, Radiobutton, Checkbutton, Menu, Menubutton, Entry, Scale, Scrollbar, Canvas, messagebox, END
from PIL import Image, ImageTk, ImageDraw, ImageFont

from main.scripts.TkToolTip import TkToolTip as ToolTip


#endregion
################################################################################################################################################
#region - CLASS: ImageGrid


class ImageGrid:
    image_cache = {1: {}, 2: {}, 3: {}}  # Cache for each thumbnail size
    image_size_cache = {}  # Cache to store image sizes
    text_file_cache = {}  # Cache to store text file pairs


    def __init__(self, master, img_txt_viewer, window_x, window_y, jump_to_image):

        # Window configuration
        self.create_window(master, window_x, window_y)

        # Initilize ImgTxtViewer variables and methods
        self.img_txt_viewer = img_txt_viewer
        self.sort_key = self.img_txt_viewer.get_file_sort_key()
        self.working_folder = self.img_txt_viewer.image_dir.get()

        # Setup configparser and settings file
        self.config = configparser.ConfigParser()
        self.settings_file = "settings.cfg"

        # Image navigation function
        self.ImgTxt_jump_to_image = jump_to_image

        # Supported file types
        self.supported_filetypes = (".png", ".webp", ".jpg", ".jpeg", ".jpg_large", ".jfif", ".tif", ".tiff", ".bmp", ".gif")

        # Image grid configuration
        self.max_width = 85  # Thumbnail width
        self.max_height = 85  # Thumbnail height
        self.rows = 500  # Max rows
        self.cols = 8  # Max columns
        self.images_per_load = 250  # Num of images to load per set

        # Image loading and filtering
        self.loaded_images = 0  # Num of images loaded to the UI
        self.filtered_images = 0  # Num of images displayed after filtering

        # Image flag
        self.image_flag = self.create_image_flag()

        # Image files in the folder
        self.all_file_list = self.get_all_files()
        self.image_file_list = self.get_image_files()
        self.num_total_images = len(self.image_file_list)  # Number of images in the folder

        # Default thumbnail size. Range=(1,2,3). Set to 3 if total_images is less than 25.
        self.image_size = IntVar(value=3) if self.num_total_images < 25 else IntVar(value=2)

        # Toggle window auto-close when selecting an image
        self.auto_close = BooleanVar()

        # Read and set settings
        self.read_settings()

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
        self.create_filtering_row()


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
        self.grip_window_size.pack(side="right", padx=(5, 0))
        ToolTip.create(self.grip_window_size, "Adjust window size", 500, 6, 12)

        self.button_refresh = Button(self.frame_bottom, text="Refresh", overrelief="groove", command=self.reload_grid)
        self.button_refresh.pack(side="right", padx=5)
        ToolTip.create(self.button_refresh, "Refresh the image grid. Useful when you've added or removed images, or altered the text pairs.", 500, 6, 12)

        self.button_load_all = Button(self.frame_bottom, text="Load All", overrelief="groove", command=lambda: self.load_images(all_images=True))
        self.button_load_all.pack(side="right", padx=5)
        ToolTip.create(self.button_load_all, "Load all images in the folder (Slow)", 500, 6, 12)

        self.label_image_info = Label(self.frame_bottom, width=14)
        self.label_image_info.pack(side="right", padx=5)
        ToolTip.create(self.label_image_info, "Filtered Images : Loaded Images, Total Images", 500, 6, 12)

        self.checkbutton_auto_close = Checkbutton(self.frame_bottom, text="Auto-Close", overrelief="groove", variable=self.auto_close)
        self.checkbutton_auto_close.pack(side="right", padx=5)
        ToolTip.create(self.checkbutton_auto_close, "Uncheck this to keep the window open after selecting an image", 500, 6, 12)


    def create_filtering_row(self):
        self.button_toggle_frame = Button(self.frame_bottom, text="Filtering", overrelief="groove", command=self.toggle_filterframe_visibility)
        self.button_toggle_frame.pack(side="left", padx=5)
        ToolTip.create(self.button_toggle_frame, "Show or hide the filtering options", 500, 6, 12)

        self.frame_filtering = Frame(self.frame_thumbnails)
        self.filterframe_visible = False

        hori_separator = ttk.Separator(self.frame_filtering)
        hori_separator.pack(side="top", fill="x")

        vert_separator = ttk.Separator(self.frame_filtering, orient="vertical")
        vert_separator.pack(side="left", fill="y")

        self.pair_filter_var = StringVar(value="All")
        self.radiobutton_all = Radiobutton(self.frame_filtering, text="All", variable=self.pair_filter_var, value="All", overrelief="groove", command=self.reload_grid)
        self.radiobutton_all.pack(side="left", padx=1)
        ToolTip.create(self.radiobutton_all, "Display all LOADED images", 500, 6, 12)

        self.radiobutton_paired = Radiobutton(self.frame_filtering, text="Paired", variable=self.pair_filter_var, value="Paired", overrelief="groove", command=self.reload_grid)
        self.radiobutton_paired.pack(side="left", padx=1)
        ToolTip.create(self.radiobutton_paired, "Display images with text pairs", 500, 6, 12)

        self.radiobutton_unpaired = Radiobutton(self.frame_filtering, text="Unpaired", variable=self.pair_filter_var, value="Unpaired", overrelief="groove", command=self.reload_grid)
        self.radiobutton_unpaired.pack(side="left", padx=1)
        ToolTip.create(self.radiobutton_unpaired, "Display images without text pairs", 500, 6, 12)

        vert_separator = ttk.Separator(self.frame_filtering, orient="vertical")
        vert_separator.pack(side="left", fill="y")

        self.enable_extra_filter_var = BooleanVar(value=0)
        self.checkbutton_enable_extra_filter = Checkbutton(self.frame_filtering, variable=self.enable_extra_filter_var, overrelief="groove", command=self.toggle_filter_widgets)
        self.checkbutton_enable_extra_filter.pack(side="left")

        self.filter_options = ["Resolution", "Aspect Ratio", "Filesize", "Filename", "Filetype", "Tags"]
        self.filter_var = StringVar(value=self.filter_options[0])
        self.combobox_filter = ttk.Combobox(self.frame_filtering, textvariable=self.filter_var, values=self.filter_options, width=12, state="disabled")
        self.combobox_filter.pack(side="left", padx=5)
        self.combobox_filter.bind('<<ComboboxSelected>>', lambda event: self.handle_filter_options())
        ToolTip.create(self.combobox_filter, "Filter images by the selected option", 500, 6, 12)

        self.operator_var = StringVar(value="=")
        self.operator_options = ["=", "<", ">", "*"]
        self.menu_button_operator = Menubutton(self.frame_filtering, textvariable=self.operator_var, indicatoron=False, relief="raised", state="disabled")
        self.menu_button_operator.menu = Menu(self.menu_button_operator, tearoff=0)
        self.menu_button_operator["menu"] = self.menu_button_operator.menu
        self.menu_button_operator.config(width=2)
        for option in self.operator_options:
            self.menu_button_operator.menu.add_radiobutton(label=option, variable=self.operator_var, value=option, command=self.reload_grid)
        self.menu_button_operator.pack(side="left", padx=5)
        ToolTip.create(self.menu_button_operator, "Select a filter operator", 500, 6, 12)

        self.filter_entry = Entry(self.frame_filtering, state="disabled", width=15)
        self.filter_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.filter_entry.bind("<KeyRelease>", lambda event: self.reload_grid())
        self.filter_entry_tooltiptext_resolution = "Enter an appropriate filter value for: Resolution\n\nEnter a full resolution like 100x100 (WxH), or enter a single value like 100w, 100h"
        self.filter_entry_tooltiptext_aspectratio = "Enter an appropriate filter value for: Aspect Ratio\n\nEnter as a single number decimal like 1.0, 1.78, or as a ratio like 1:1, 16:9"
        self.filter_entry_tooltiptext_filesize = "Enter an appropriate filter value for: Filesize\n\nEnter a value in MB like 1, 2, 3, 0.5, 0.25, etc."
        self.filter_entry_tooltiptext_filename = "Enter an appropriate filter value for: Filename\n\nEnter a filename. Do not enter the file extension. Not case sensitive."
        self.filter_entry_tooltiptext_filetype = "Enter an appropriate filter value for: Filetype\n\nEnter a file extension. Not case sensitive."
        self.filter_entry_tooltiptext_tags = "Enter an appropriate filter value for: Tags\n\nEnter a tag or string of text."
        self.filter_entry_tooltip = ToolTip.create(self.filter_entry, self.filter_entry_tooltiptext_resolution, 500, 6, 12)

        self.label_filtertext = Label(self.frame_filtering, state="disabled", text="WxH", width=3)
        self.label_filtertext.pack(side="left", padx=5)

        self.filter_extra_options = {
            "Resolution": ["256x256", "640x360", "512x512", "800x600", "768x768", "1024x768", "1280x720", "1360x768", "1024x1024", "1400x900", "1600x900", "1920x1080", "1536x1536", "2560x1440", "2048x2048", "2560x2560", "3840x2160", "3072x3072", "3582x3582", "4096x4096"],
            "Aspect Ratio": ["1:3", "1:2", "9:16", "2:3", "5:7", "3:4", "4:5", "1:1", "5:4", "4:3", "3:2", "16:10", "16:9", "1.85:1", "21:9", "2.35:1"],
            "Filesize": ["0.5", "1", "2", "5", "10", "15", "20"],
            "Filename": [],
            "Filetype": ["PNG", "WEBP", "JPG", "JPEG", "JPG_LARGE", "JFIF", "TIF", "TIFF", "BMP", "GIF"],
            "Tags": []
        }
        self.filter_extra_var = StringVar(value=self.filter_extra_options["Resolution"][0])
        self.combobox_filterinput = ttk.Combobox(self.frame_filtering, textvariable=self.filter_extra_var, values=self.filter_extra_options["Resolution"], state="disabled")
        self.combobox_filterinput.pack(side="left", padx=5)
        self.combobox_filterinput.bind("<<ComboboxSelected>>", self.update_filter_entry)

    def update_filter_entry(self, event):
        selected_value = self.combobox_filterinput.get()
        self.filter_entry.delete(0, END)
        self.filter_entry.insert(0, selected_value)
        self.reload_grid()

#endregion
################################################################################################################################################
#region -  Primary Logic


    def reload_grid(self, event=None):
        self.clear_frame(self.frame_image_grid)
        self.set_size_settings()
        self.update_image_info_label()
        self.update_cache_and_grid()


    def update_cache_and_grid(self):
        self.update_filtered_images()
        self.update_image_cache()
        self.create_image_grid()


    def update_image_cache(self):
        image_size_key = self.image_size.get()
        filtered_sorted_files = list(filter(self.filter_images, sorted(self.image_file_list, key=self.sort_key)))
        current_text_file_sizes = {
            os.path.splitext(os.path.join(self.working_folder, filename))[0] + '.txt': os.path.getsize(os.path.splitext(os.path.join(self.working_folder, filename))[0] + '.txt') if os.path.exists(os.path.splitext(os.path.join(self.working_folder, filename))[0] + '.txt') else 0
            for filename in filtered_sorted_files}
        for filename in filtered_sorted_files:
            img_path, txt_path = self.get_image_and_text_paths(filename)
            current_text_file_size = current_text_file_sizes[txt_path]
            cached_text_file_size = self.text_file_cache.get(txt_path, -1)
            if img_path not in self.image_cache[image_size_key] or current_text_file_size != cached_text_file_size:
                self.create_new_image(img_path, txt_path)
                self.text_file_cache[txt_path] = current_text_file_size


    def update_image_info_label(self):
        self.update_filtered_images()
        self.update_shown_images()
        self.update_button_state()


    def update_shown_images(self):
        shown_images = min(self.filtered_images, self.loaded_images)
        self.label_image_info.config(text=f"{shown_images} : {self.loaded_images}, of {self.num_total_images}")


    def update_button_state(self):
        self.button_load_all.config(state="disabled" if self.loaded_images == self.num_total_images else "normal")


    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()


    def set_size_settings(self):
        size_settings = {1: (50, 50, 13),
                         2: (85, 85, 8),
                         3: (175, 175, 4)}
        self.max_width, self.max_height, self.cols = size_settings.get(self.image_size.get(), (85, 85, 8))


    def create_image_grid(self):
        self.canvas_thumbnails.create_window((0, 0), window=self.frame_image_grid, anchor='nw')
        self.images = self.load_image_set()
        self.populate_image_grid()
        self.configure_scroll_region()
        self.add_load_more_button()


    def populate_image_grid(self):
        for index, (image, filepath, image_index) in enumerate(self.images):
            row, col = divmod(index, self.cols)
            thumbnail = Button(self.frame_image_grid, relief="flat", overrelief="groove", image=image, command=lambda path=filepath: self.on_mouse_click(path))
            thumbnail.image = image
            thumbnail.grid(row=row, column=col)
            thumbnail.bind("<MouseWheel>", self.on_mousewheel)
            filesize = os.path.getsize(filepath)
            filesize = f"{filesize / 1024:.2f} KB" if filesize < 1024 * 1024 else f"{filesize / 1024 / 1024:.2f} MB"
            width, height = Image.open(filepath).size
            resolution = f"({width} x {height})"
            ToolTip.create(thumbnail, f"#{image_index + 1}, {os.path.basename(filepath)}, {filesize}, {resolution}", 200, 6, 12)


    def load_images(self, all_images=False):
        self.loaded_images = self.num_total_images if all_images else min(self.loaded_images + self.images_per_load, self.num_total_images)
        self.update_image_info_label()
        self.reload_grid()


    def load_image_set(self):
        images = []
        image_size_key = self.image_size.get()
        filtered_sorted_files = list(filter(self.filter_images, sorted(self.image_file_list, key=self.sort_key)))
        current_text_file_sizes = {
            os.path.splitext(os.path.join(self.working_folder, filename))[0] + '.txt': os.path.getsize(os.path.splitext(os.path.join(self.working_folder, filename))[0] + '.txt') if os.path.exists(os.path.splitext(os.path.join(self.working_folder, filename))[0] + '.txt') else 0
            for filename in filtered_sorted_files}
        for image_index, filename in enumerate(filtered_sorted_files):
            if len(images) >= self.loaded_images:
                break
            img_path, txt_path = self.get_image_and_text_paths(filename)
            current_text_file_size = current_text_file_sizes[txt_path]
            cached_text_file_size = self.text_file_cache.get(txt_path, -1)
            if img_path not in self.image_cache[image_size_key] or current_text_file_size != cached_text_file_size:
                new_img = self.create_new_image(img_path, txt_path)
            else:
                new_img = self.image_cache[image_size_key][img_path]
            images.append((ImageTk.PhotoImage(new_img), img_path, image_index))
        return images


    def create_new_image(self, img_path, txt_path):
        new_img = Image.new("RGBA", (self.max_width, self.max_height))
        img = Image.open(img_path)
        img.thumbnail((self.max_width, self.max_height))
        position = ((self.max_width - img.width) // 2, (self.max_height - img.height) // 2)
        new_img.paste(img, position)
        if not os.path.exists(txt_path) or os.path.getsize(txt_path) == 0:
            flag_position = (self.max_width - self.image_flag.width, self.max_height - self.image_flag.height)
            new_img.paste(self.image_flag, flag_position, mask=self.image_flag)
        self.image_cache[self.image_size.get()][img_path] = new_img
        return new_img


    def filter_images(self, filename):
        if not filename.lower().endswith(self.supported_filetypes):
            return False
        txt_path = os.path.splitext(os.path.join(self.working_folder, filename))[0] + '.txt'
        file_size = os.path.getsize(txt_path) if os.path.exists(txt_path) else 0
        filter_dict = {"All": True, "Paired": file_size != 0, "Unpaired": file_size == 0}
        if not filter_dict.get(self.pair_filter_var.get(), False):
            return False
        if not self.enable_extra_filter_var.get():
            return True
        current_filter = self.filter_var.get()
        operator = self.operator_var.get()
        filter_value = self.filter_entry.get().strip()
        if not filter_value:
            return True

        def check_resolution(img_width, img_height):
            lower_limit = 0.90
            higher_limit = 1.10
            try:
                if 'x' in filter_value:
                    width, height = map(int, filter_value.split('x'))
                    checks = {
                        '=': (img_width == width and img_height == height),
                        '<': (img_width < width and img_height < height),
                        '>': (img_width > width and img_height > height),
                        '*': (lower_limit * width <= img_width <= higher_limit * width and lower_limit * height <= img_height <= higher_limit * height)
                    }
                elif 'w' in filter_value:
                    width = int(filter_value.rstrip('w'))
                    checks = {
                        '=': (img_width == width),
                        '<': (img_width < width),
                        '>': (img_width > width),
                        '*': (lower_limit * width <= img_width <= higher_limit * width)
                    }
                elif 'h' in filter_value:
                    height = int(filter_value.rstrip('h'))
                    checks = {
                        '=': (img_height == height),
                        '<': (img_height < height),
                        '>': (img_height > height),
                        '*': (lower_limit * height <= img_height <= higher_limit * height)
                    }
                else:
                    width = int(filter_value)
                    checks = {
                        '=': (img_width == width),
                        '<': (img_width < width),
                        '>': (img_width > width),
                        '*': (lower_limit * width <= img_width <= higher_limit * width)
                    }
                return checks.get(operator, False)
            except ValueError:
                return False

        def check_aspect_ratio(img_width, img_height):
            try:
                if ':' in filter_value:
                    num, denom = map(int, filter_value.split(':'))
                    target_aspect_ratio = num / denom
                else:
                    target_aspect_ratio = float(filter_value)

                aspect_ratio = img_width / img_height
                checks = {
                    '=': abs(aspect_ratio - target_aspect_ratio) < 0.01,
                    '<': aspect_ratio < target_aspect_ratio,
                    '>': aspect_ratio > target_aspect_ratio,
                    '*': 0.90 * target_aspect_ratio <= aspect_ratio <= 1.10 * target_aspect_ratio
                }
                return checks.get(operator, False)
            except ValueError:
                return False

        def check_filesize(actual_size, target_size):
            lower_limit = target_size * 0.75
            upper_limit = target_size * 1.25
            tolerance = 0.01

            if operator == "=":
                return lower_limit * (1 - tolerance) <= actual_size <= upper_limit * (1 + tolerance)
            elif operator == "<":
                return actual_size < target_size
            elif operator == ">":
                return actual_size > target_size
            elif operator == "*":
                return lower_limit <= actual_size <= upper_limit

        def check_filename(base_filename):
            filter_value_lower = filter_value.lower()
            if operator == "=":
                return base_filename.startswith(filter_value_lower)
            elif operator == "<":
                return len(base_filename) < len(filter_value_lower)
            elif operator == ">":
                return len(base_filename) > len(filter_value_lower)
            elif operator == "*":
                return any(filter_value_lower in sub for sub in base_filename.split('_'))

        def check_filetype(filetype):
            return filename.lower().endswith(filetype)

        def check_tags(tags):
            if operator == "=":
                return filter_value == tags
            elif operator == "<":
                return len(tags) < len(filter_value)
            elif operator == ">":
                return len(tags) > len(filter_value)
            elif operator == "*":
                return filter_value in tags

        try:
            if current_filter == "Resolution" or current_filter == "Aspect Ratio":
                if filename not in self.image_size_cache:
                    with Image.open(os.path.join(self.working_folder, filename)) as img:
                        self.image_size_cache[filename] = img.size
                img_width, img_height = self.image_size_cache[filename]

                if current_filter == "Resolution" and not check_resolution(img_width, img_height):
                    return False
                if current_filter == "Aspect Ratio" and not check_aspect_ratio(img_width, img_height):
                    return False
            elif current_filter == "Filesize":
                target_size = float(filter_value) * 1024 * 1024
                actual_size = os.path.getsize(os.path.join(self.working_folder, filename))
                if not check_filesize(actual_size, target_size):
                    return False
            elif current_filter == "Filename":
                base_filename = os.path.splitext(filename)[0].lower()
                if not check_filename(base_filename):
                    return False
            elif current_filter == "Filetype":
                if not check_filetype(filter_value.strip(".").lower()):
                    return False
            elif current_filter == "Tags":
                if os.path.exists(txt_path):
                    with open(txt_path, 'r') as file:
                        tags = file.read()
                        if not check_tags(tags):
                            return False
                else:
                    return False
        except Exception:
            return False
        return True



    def update_filtered_images(self):
        self.filtered_images = sum(1 for _ in filter(self.filter_images, sorted(self.image_file_list, key=self.sort_key)))


    def get_image_and_text_paths(self, filename):
        img_path = os.path.join(self.working_folder, filename)
        txt_path = os.path.splitext(img_path)[0] + '.txt'
        return img_path, txt_path


    def paste_image_flag(self, new_img, img_path, txt_path, current_text_file_size=None):
        img = Image.open(img_path)
        img.thumbnail((self.max_width, self.max_height))
        position = ((self.max_width - img.width) // 2, (self.max_height - img.height) // 2)
        new_img.paste(img, position)
        if current_text_file_size is None:
            current_text_file_size = os.path.getsize(txt_path) if os.path.exists(txt_path) else 0
        if current_text_file_size == 0:
            flag_position = (self.max_width - self.image_flag.width, self.max_height - self.image_flag.height)
            new_img.paste(self.image_flag, flag_position, mask=self.image_flag)
        self.image_cache[self.image_size.get()][img_path] = new_img
        return new_img


    def create_image_flag(self):
        flag_size = 15
        outline_width = 1
        left, top = [dim - flag_size - outline_width for dim in (self.max_width, self.max_height)]
        right, bottom = self.max_width, self.max_height
        image_flag = Image.new('RGBA', (self.max_width, self.max_height))
        draw = ImageDraw.Draw(image_flag)
        draw.rectangle(((left, top), (right, bottom)), fill="black")
        draw.rectangle(((left + outline_width, top + outline_width), (right - outline_width, bottom - outline_width)), fill="red")
        corner_size = flag_size // 2
        triangle_points = [
            (left - outline_width, top - outline_width),
            (left + corner_size, top - outline_width),
            (left - outline_width, top + corner_size)]
        draw.polygon(triangle_points, fill=(0, 0, 0, 0))
        center = ((left + right) // 2, (top + bottom) // 2)
        font = ImageFont.truetype("arial", 15)
        draw.text(center, " -", fill="white", font=font, anchor="mm")
        return image_flag


    def get_image_index(self, directory, filename):
        filename = os.path.basename(filename)
        image_files = sorted((file for file in os.listdir(directory) if file.lower().endswith(self.supported_filetypes)), key=self.sort_key)
        return image_files.index(filename) if filename in image_files else -1


#endregion
################################################################################################################################################
#region -  Interface Logic


    def configure_scroll_region(self):
        scroll_index = self.loaded_images / self.cols * 1.2
        scrollregion_height = scroll_index * self.max_height
        self.canvas_thumbnails.config(scrollregion=(0, 0, 750, scrollregion_height))


    def add_load_more_button(self):
        if self.pair_filter_var.get() == "All" and self.loaded_images < self.num_total_images:
            load_more_button = Button(self.frame_image_grid, text="Load More...", height=2, command=self.load_images)
            load_more_button.grid(row=self.rows, column=0, columnspan=self.cols, sticky="ew", pady=5)
            ToolTip.create(load_more_button, "Load the next 150 images", 500, 6, 12)


    def on_mouse_click(self, path):
        index = self.get_image_index(self.working_folder, path)
        self.ImgTxt_jump_to_image(index)
        if self.auto_close.get():
            self.close_window()


    def on_mousewheel(self, event):
        if self.canvas_thumbnails.winfo_exists():
            self.canvas_thumbnails.yview_scroll(int(-1*(event.delta/120)), "units")


    def handle_filter_options(self):
        filter = self.filter_var.get()
        operator_menu = self.menu_button_operator.menu
        equal_index = self.operator_options.index("=")
        new_options = self.filter_extra_options.get(filter, [])
        self.combobox_filterinput.config(values=new_options)
        if new_options:
            self.filter_extra_var.set(new_options[0])
            self.combobox_filterinput.config(state="readonly")
        else:
            self.filter_extra_var.set('')
            self.combobox_filterinput.config(state="disabled")
        if filter == "Resolution":
            self.label_filtertext.config(text="WxH")
            operator_menu.entryconfig(equal_index, state="normal")
            self.filter_entry_tooltip.config(text=self.filter_entry_tooltiptext_resolution)
        elif filter == "Aspect Ratio":
            self.label_filtertext.config(text="1:1")
            operator_menu.entryconfig(equal_index, state="normal")
            self.filter_entry_tooltip.config(text=self.filter_entry_tooltiptext_aspectratio)
        elif filter == "Filesize":
            self.label_filtertext.config(text="MB")
            operator_menu.entryconfig(equal_index, state="normal")
            self.filter_entry_tooltip.config(text=self.filter_entry_tooltiptext_filesize)
        elif filter == "Filename":
            operator_menu.entryconfig(equal_index, state="normal")
            self.label_filtertext.config(text="")
            self.filter_entry_tooltip.config(text=self.filter_entry_tooltiptext_filename)
        elif filter == "Filetype":
            operator_menu.entryconfig(equal_index, state="normal")
            self.label_filtertext.config(text="")
            self.filter_entry_tooltip.config(text=self.filter_entry_tooltiptext_filetype)
        elif filter == "Tags":
            self.operator_var.set("*")
            operator_menu.entryconfig(equal_index, state="disabled")
            self.label_filtertext.config(text="")
            self.filter_entry_tooltip.config(text=self.filter_entry_tooltiptext_tags)
        else:
            self.label_filtertext.config(text="")
            operator_menu.entryconfig(equal_index, state="normal")


    def toggle_filter_widgets(self):
        state = "normal" if self.enable_extra_filter_var.get() else "disabled"
        combostate = "readonly" if state == "normal" else "disabled"
        self.combobox_filter.config(state=combostate)
        self.combobox_filterinput.config(state=combostate)
        self.menu_button_operator.config(state=state)
        self.filter_entry.config(state=state)
        self.label_filtertext.config(state=state)
        self.reload_grid()


    def toggle_filterframe_visibility(self):
        if self.filterframe_visible:
            self.frame_filtering.pack_forget()
            self.button_toggle_frame.config(relief="raised")
        else:
            self.frame_filtering.pack(side="bottom", fill="x", padx=5, pady=(0, 5))
            self.button_toggle_frame.config(relief="sunken")
        self.filterframe_visible = not self.filterframe_visible


#endregion
################################################################################################################################################
#region -  Misc


    def get_all_files(self):
        try:
            return os.listdir(self.working_folder)
        except (FileNotFoundError, NotADirectoryError):
            return


    def get_image_files(self):
        return [name for name in self.all_file_list if os.path.isfile(os.path.join(self.working_folder, name)) and name.lower().endswith(self.supported_filetypes)]


#    def natural_sort(self, string):
#        return [int(text) if text.isdigit() else text.lower()
#                for text in re.split(r'(\d+)', string)]


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
#region -  Save / Read Settings


    def save_settings(self):
        try:
            # Read existing settings
            if os.path.exists(self.settings_file):
                self.config.read(self.settings_file)

            # Auto-Close
            if not self.config.has_section("Other"):
                self.config.add_section("Other")
            self.config.set("Other", "auto_close", str(self.auto_close.get()))

            # Write updated settings back to file
            with open(self.settings_file, "w", encoding="utf-8") as f:
                self.config.write(f)
        except (PermissionError, IOError) as e:
            messagebox.showerror("Error", f"Error: An error occurred while saving the user settings.\n\n{e}")


    def read_settings(self):
         try:
             # Read existing settings
             if os.path.exists(self.settings_file):
                 self.config.read(self.settings_file)

                 # Auto-Close
                 self.auto_close.set(value=self.config.getboolean("Other", "auto_close", fallback=False))

         except Exception as e:
             messagebox.showerror("Error", f"Error: An unexpected error occurred.\n\n{e}")

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
#region - Framework


    def create_window(self, master, window_x, window_y):
        # Create a new transparent top-level widget that will appear in the taskbar
        self.transparent_top = Toplevel(master)
        self.transparent_top.attributes('-alpha', 0.0)
        self.transparent_top.iconify()
        self.transparent_top.title("Image Grid")

        # Redirect focus to the top-level window when the transparent window is focused
        self.transparent_top.bind("<FocusIn>", lambda event: self.top.focus_force())

        # Create a new top-level widget without window decorations
        self.top = Toplevel(master, borderwidth=2, relief="groove")
        self.top.overrideredirect(True)

        # Set the geometry (size and position) of the window
        window_size = "750x600"
        window_position = f"+{window_x}+{window_y}"
        self.top.geometry(f"{window_size}{window_position}")

        # Set the minimum and maximum size of the window
        self.top.minsize(750, 300)
        self.top.maxsize(750, 6000)

        # Make the window modal, set focus to it, set always on top
        self.top.focus_force()

        # Bind the Escape and F2 keys to the close_window method
        self.top.bind("<Escape>", lambda event: self.close_window(event))
        self.top.bind('<F2>', lambda event: self.close_window(event))

        # When the undecorated window is closed, also destroy the transparent window
        self.top.protocol('WM_DELETE_WINDOW', self.close_window)


    def close_window(self, event=None):
        self.save_settings()
        self.transparent_top.destroy()
        self.top.destroy()


#endregion
################################################################################################################################################
#region - Changelog


'''

v1.03 changes:

  - New:
    - Filtering options are now moved to a new menu.
    - You can now filter images by `Resolution`, `Aspect Ratio`, `Filesize`, `Filename`, `Filetype`, and `Tags`.
      - Along with these operators, `=`, `<`, `>`, `*`
    - Resolution and Filesize are now displayed in the image tooltip.
    - `Auto-Close`: This setting is now saved to the `settings.cfg` file.

<br>

  - Fixed:
    - Fixed the issue of not being able to focus on the image grid window when selecting the it from the taskbar.

<br>

  - Other changes:
    - Increased the default number of images loaded from 150 to 250.
    - Improved image and text cache.
    - Update index logic to support new loading order options.

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
