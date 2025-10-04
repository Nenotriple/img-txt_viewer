#region Imports


# Standard Library
import os


# Standard Library - GUI
from tkinter import (
    ttk,
    IntVar,
    Frame, Canvas
)


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as Tip
from PIL import Image, ImageTk, ImageDraw, ImageFont


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region ImageGrid


class ImageGrid(ttk.Frame):
    image_cache = {1: {}, 2: {}, 3: {}}  # Cache for each thumbnail size
    text_file_cache = {}  # Cache to store text file pairs


    def __init__(self, master: 'Frame', parent: 'Main'):
        super().__init__(master)
        # Initialize ImgTxtViewer variables and methods
        self.parent = parent
        self.is_initialized = False
        self.canvas_window = None
        # Supported file types
        self.supported_filetypes = (".png", ".webp", ".jpg", ".jpeg", ".jpg_large", ".jfif", ".tif", ".tiff", ".bmp", ".gif", ".mp4")
        # Used keeping track of thumbnail buttons
        self.thumbnail_buttons = {}
        # Used for highlighting the selected thumbnail
        self.initial_selected_thumbnail = None
        self.prev_selected_thumbnail = None
        self.selected_thumbnail = None


    def _is_video_file(self, file_path: str) -> bool:
        """Check if the file is a video file by extension."""
        return file_path.lower().endswith('.mp4')


    def initialize(self):
        '''Initialize the ImageGrid widget. This must be called before using the widget.'''
        if self.is_initialized:
            return
        # Parent variables
        self.reverse_sort_direction_var = self.parent.reverse_load_order_var.get()
        self.working_folder = self.parent.image_dir.get()

        # Image grid configuration
        self.max_width = 80  # Thumbnail width
        self.max_height = 80  # Thumbnail height
        self.images_per_load = 250  # Num of images to load per set
        self.padding = 4  # Default padding between thumbnails
        self.rows = 0  # Num of rows in the grid
        self.columns = 0  # Num of columns in the grid

        # Image loading
        self.loaded_images = 0  # Num of images loaded to the UI
        # Get number of total images from parent
        self.num_total_images = len(self.parent.image_files)
        # Default thumbnail size. Range=(1,2,3). Set to 3 if total_images is less than 25.
        self.image_size = IntVar(value=3 if self.num_total_images < 25 else 2)
        # Image flag
        self.image_flag = self.create_image_flag()

        # Interface creation
        self.create_interface()
        self.load_images()
        self.is_initialized = True


#endregion
#region Create Interface


    # --- Build Interface ---
    def create_interface(self):
        self.configure_grid_structure()
        self.create_canvas()
        self.create_control_row()


    # --- Grid Setup ---
    def configure_grid_structure(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)


    # --- Canvas Setup ---
    def create_canvas(self):
        self.frame_main = ttk.Frame(self, padding=(10, 10, 10, 4))
        self.frame_main.grid(row=0, column=0, sticky="nsew")
        self.frame_main.columnconfigure(0, weight=1)
        self.frame_main.rowconfigure(0, weight=1)

        self.canvas_container = ttk.Frame(self.frame_main)
        self.canvas_container.grid(row=0, column=0, sticky="nsew")
        self.canvas_container.columnconfigure(0, weight=1)
        self.canvas_container.rowconfigure(0, weight=1)

        self.scrollbar = ttk.Scrollbar(self.canvas_container, orient="vertical")
        self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(4, 0))

        self.canvas_thumbnails = Canvas(self.canvas_container, takefocus=False, yscrollcommand=self.scrollbar.set, highlightthickness=0)
        self.canvas_thumbnails.grid(row=0, column=0, sticky="nsew")
        self.canvas_thumbnails.bind("<MouseWheel>", self.on_mousewheel)
        self.scrollbar.config(command=self.canvas_thumbnails.yview)

        self.frame_image_grid = ttk.Frame(self.canvas_thumbnails, padding=(self.padding, self.padding))
        self.frame_image_grid.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas_window = self.canvas_thumbnails.create_window((0, 0), window=self.frame_image_grid, anchor="nw")
        self.canvas_thumbnails.bind("<Configure>", self.on_canvas_configure)
        self.frame_image_grid.bind("<Configure>", self.on_frame_configure)


    # --- Controls ---
    def create_control_row(self):
        self.frame_bottom = ttk.LabelFrame(self, text="Grid Controls", padding=(10, 6))
        self.frame_bottom.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.frame_bottom.columnconfigure(1, weight=1)
        self.frame_bottom.columnconfigure(3, weight=1)

        self.label_size = ttk.Label(self.frame_bottom, text="Size:")
        self.label_size.grid(row=0, column=0, sticky="w", padx=(0, 8))
        Tip.create(widget=self.label_size, text="Adjust grid size")

        self.slider_image_size = ttk.Scale(self.frame_bottom, variable=self.image_size, orient="horizontal", from_=1, to=3, command=self.round_scale_input)
        self.slider_image_size.grid(row=0, column=1, sticky="ew")
        self.slider_image_size.bind("<ButtonRelease-1>", lambda event: self.reload_grid())
        Tip.create(widget=self.slider_image_size, text="Adjust grid size")

        self.label_size_value = ttk.Label(self.frame_bottom, textvariable=self.image_size, width=3)
        self.label_size_value.grid(row=0, column=2, padx=(8, 12))
        Tip.create(widget=self.label_size_value, text="Current grid size")

        self.label_image_info = ttk.Label(self.frame_bottom, width=16, anchor="e")
        self.label_image_info.grid(row=0, column=3, sticky="e")
        Tip.create(widget=self.label_image_info, text="Loaded images / total images")

        self.button_load_all = ttk.Button(self.frame_bottom, text="Load All", command=self.load_all_images)
        self.button_load_all.grid(row=0, column=4, padx=(12, 6))
        Tip.create(widget=self.button_load_all, text="Load all images in the folder (slower)")

        self.button_refresh = ttk.Button(self.frame_bottom, text="Refresh", command=self.reload_grid)
        self.button_refresh.grid(row=0, column=5)
        Tip.create(widget=self.button_refresh, text="Refresh the image grid")


    # --- Canvas Events ---
    def on_canvas_configure(self, event):
        if self.canvas_window is not None:
            self.canvas_thumbnails.itemconfigure(self.canvas_window, width=event.width)
            self.configure_scroll_region(reset_view=False)


    # --- Grid Events ---
    def on_frame_configure(self, _event):
        self.configure_scroll_region(reset_view=False)


#endregion
#region Primary Logic


    def reload_grid(self, event=None):
        self.clear_frame(self.frame_image_grid)
        self.set_size_settings()
        self.update_image_info_label()
        self.update_cache_and_grid()
        self.highlight_thumbnail(self.parent.current_index)


    def update_cache_and_grid(self):
        self.update_image_cache()
        self.create_image_grid()


    def update_image_cache(self):
        image_size_key = self.image_size.get()
        filtered_sorted_files = sorted(self.parent.image_files, key=self.parent.get_file_sort_key(), reverse=self.reverse_sort_direction_var)
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
        self.label_image_info.config(text=f"{self.loaded_images} / {self.num_total_images}")
        self.button_load_all.config(state="disabled" if self.loaded_images == self.num_total_images else "normal")


    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()


    def calculate_columns(self):
        frame_width = self.canvas_container.winfo_width()
        if frame_width <= 1:
            frame_width = self.canvas_container.winfo_reqwidth()
        available_width = frame_width - (2 * self.padding)
        thumbnail_width_with_padding = self.max_width + (2 * self.padding)
        columns = max(1, available_width // thumbnail_width_with_padding)
        self.columns = columns
        return int(columns)


    def set_size_settings(self):
        size_settings = {
            1: (45, 45, 13),
            2: (80, 80, 8),
            3: (170, 170, 4)
        }
        self.max_width, self.max_height, self.cols = size_settings.get(self.image_size.get(), (80, 80, 8))
        self.image_flag = self.create_image_flag()
        self.cols = self.calculate_columns()


    def create_image_grid(self):
        self.images = self.load_image_set()
        self.populate_image_grid()
        self.configure_scroll_region(reset_view=True)
        self.add_load_more_button()


    def populate_image_grid(self):
        self.thumbnail_buttons.clear()
        self.prev_selected_thumbnail = None
        self.initial_selected_thumbnail = None
        for column in range(self.cols):
            self.frame_image_grid.columnconfigure(column, weight=1)
        for index, (image, filepath, image_index) in enumerate(self.images):
            row, col = divmod(index, self.cols)
            button_style = "Highlighted.TButton" if index == self.parent.current_index else "TButton"
            thumbnail = ttk.Button(self.frame_image_grid, image=image, takefocus=False, style=button_style)
            thumbnail.configure(command=lambda idx=image_index: self.on_mouse_click(idx))
            thumbnail.image = image
            thumbnail.grid(row=row, column=col, sticky="nsew")
            thumbnail.bind("<MouseWheel>", self.on_mousewheel)
            self.thumbnail_buttons[image_index] = thumbnail
            if index == self.parent.current_index:
                self.initial_selected_thumbnail = thumbnail
            # Get file info (different approach for videos)
            filesize = os.path.getsize(filepath)
            filesize = f"{filesize / 1024:.2f} KB" if filesize < 1024 * 1024 else f"{filesize / 1024 / 1024:.2f} MB"
            if self._is_video_file(filepath):
                video_info = self.parent.update_videoinfo(filepath)
                resolution = f"({video_info['resolution']})" if 'resolution' in video_info else "(Video)"
                tooltip_text = f"#{image_index + 1}, {os.path.basename(filepath)}, {filesize}, {resolution}"
            else:
                with Image.open(filepath) as img:
                    width, height = img.size
                resolution = f"({width} x {height})"
                tooltip_text = f"#{image_index + 1}, {os.path.basename(filepath)}, {filesize}, {resolution}"
            Tip.create(widget=thumbnail, text=tooltip_text, follow_mouse=True)


    def load_images(self, all_images=False):
        self.loaded_images = self.num_total_images if all_images else min(self.loaded_images + self.images_per_load, self.num_total_images)
        self.update_image_info_label()
        self.reload_grid()


    def load_all_images(self):
        self.load_images(all_images=True)


    def load_image_set(self):
        images = []
        image_size_key = self.image_size.get()
        image_files = self.parent.image_files
        text_files = self.parent.text_files
        current_text_file_sizes = {
            text_file: os.path.getsize(text_file) if os.path.exists(text_file) else 0
            for text_file in text_files
        }
        for image_index, img_path in enumerate(image_files):
            if len(images) >= self.loaded_images:
                break
            if image_index < len(text_files):
                txt_path = text_files[image_index]
            else:
                txt_path = os.path.splitext(img_path)[0] + '.txt'
            current_text_file_size = current_text_file_sizes.get(txt_path, 0)
            if current_text_file_size == 0 and not os.path.exists(txt_path):
                current_text_file_size = 0
            cached_text_file_size = self.text_file_cache.get(txt_path, -1)
            if img_path not in self.image_cache[image_size_key] or current_text_file_size != cached_text_file_size:
                new_img = self.create_new_image(img_path, txt_path)
            else:
                new_img = self.image_cache[image_size_key][img_path]
            images.append((ImageTk.PhotoImage(new_img), img_path, image_index))
        return images


    def create_new_image(self, img_path, txt_path):
        new_img = Image.new("RGBA", (self.max_width, self.max_height))
        # Handle video files
        if self._is_video_file(img_path):
            # Check if we have a thumbnail in the video_thumb_dict
            if hasattr(self.parent, 'video_thumb_dict') and img_path in self.parent.video_thumb_dict:
                # Access the thumbnail from the nested dictionary
                thumb_data = self.parent.video_thumb_dict[img_path]['thumbnail']
                # Ensure thumbnail is the correct size
                thumb = thumb_data.copy()
                thumb = thumb.resize((self.max_width, self.max_height), Image.LANCZOS)
                position = (0, 0)
                new_img.paste(thumb, position)
            else:
                # Request thumbnail generation
                self.parent.update_video_thumbnails()
                # Create a temporary placeholder
                draw = ImageDraw.Draw(new_img)
                draw.rectangle([(0, 0), (self.max_width, self.max_height)], outline="gray", width=2)
                font = ImageFont.truetype("arial", 12)
                draw.text((self.max_width//2, self.max_height//2), "Video", fill="gray", font=font, anchor="mm")
        else:
            # Regular image handling
            with Image.open(img_path) as img:
                img.thumbnail((self.max_width, self.max_height))
                position = ((self.max_width - img.width) // 2, (self.max_height - img.height) // 2)
                new_img.paste(img, position)
        if txt_path is None or not os.path.exists(txt_path) or os.path.getsize(txt_path) == 0:
            flag_position = (self.max_width - self.image_flag.width, self.max_height - self.image_flag.height)
            new_img.paste(self.image_flag, flag_position, mask=self.image_flag)
        self.image_cache[self.image_size.get()][img_path] = new_img
        return new_img


    def get_image_and_text_paths(self, filename):
        img_path = os.path.join(self.working_folder, filename)
        txt_path = os.path.splitext(img_path)[0] + '.txt'
        return img_path, txt_path


    def create_image_flag(self):
        size = self.image_size.get() if isinstance(self.image_size, IntVar) else self.image_size
        diameter = {1: 14, 2: 20, 3: 28}.get(size, 20)
        margin = max(2, diameter // 5)
        scale = 4
        hr_width, hr_height = self.max_width * scale, self.max_height * scale
        img_flag_hr = Image.new("RGBA", (hr_width, hr_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img_flag_hr)
        hr_diameter = diameter * scale
        hr_margin = margin * scale
        center_x = hr_width - hr_diameter // 2 - hr_margin
        center_y = hr_height - hr_diameter // 2 - hr_margin
        radius = hr_diameter // 2
        circle_bbox = [
            (center_x - radius, center_y - radius),
            (center_x + radius, center_y + radius),
        ]
        draw.ellipse(circle_bbox, fill=(250, 80, 83, 230))
        ring_thickness = max(scale, (diameter // 10) * scale)
        inner_bbox = [
            (circle_bbox[0][0] + ring_thickness, circle_bbox[0][1] + ring_thickness),
            (circle_bbox[1][0] - ring_thickness, circle_bbox[1][1] - ring_thickness),
        ]
        draw.ellipse(inner_bbox, fill=(250, 80, 83, 160))
        bar_height = max(2, diameter // 6) * scale
        bar_width = int(hr_diameter / 1.6)
        bar_bbox = [
            (center_x - bar_width // 2, center_y - bar_height // 2),
            (center_x + bar_width // 2, center_y + bar_height // 2),
        ]
        draw.rounded_rectangle(bar_bbox, radius=bar_height // 2, fill="white")
        img_flag = img_flag_hr.resize((self.max_width, self.max_height), Image.LANCZOS)
        return img_flag


    def get_image_index(self, directory, filename):
        filename = os.path.basename(filename)
        try:
            return self.parent.image_files.index(os.path.join(directory, filename))
        except ValueError:
            return -1


#endregion
#region Interface Logic


    def configure_scroll_region(self, reset_view=True):
        if self.canvas_window is None:
            return
        self.frame_image_grid.update_idletasks()
        bbox = self.canvas_thumbnails.bbox(self.canvas_window)
        if bbox is None:
            return
        x0, y0, x1, y1 = bbox
        extra_height = self.max_height + (2 * self.padding) if self.loaded_images < self.num_total_images else 0
        self.canvas_thumbnails.config(scrollregion=(x0, y0, x1, y1 + extra_height))
        if reset_view:
            self.canvas_thumbnails.yview_moveto(0)


    def add_load_more_button(self):
        if self.loaded_images < self.num_total_images:
            total_items = len(self.thumbnail_buttons)
            final_row = (total_items - 1) // self.columns if total_items else 0
            self.load_more_button = ttk.Button(self.frame_image_grid, text="Load More", command=self.load_images)
            self.load_more_button.grid(row=final_row + 1, column=0, columnspan=self.columns, pady=(self.padding * 2), padx=self.padding, sticky="ew")
            Tip.create(widget=self.load_more_button, text=f"Load the next {self.images_per_load} images")


    def highlight_thumbnail(self, index):
        if self.prev_selected_thumbnail:
            self._reset_thumbnail(self.prev_selected_thumbnail)
        button = self.thumbnail_buttons.get(index)
        if not button:
            return
        img_path = None
        for _, path, idx in self.images:
            if idx == index:
                img_path = path
                break
        if not img_path:
            return
        self.prev_selected_thumbnail = button
        # Handle video files differently
        if self._is_video_file(img_path):
            if hasattr(self.parent, 'video_thumb_dict') and img_path in self.parent.video_thumb_dict:
                # Access the thumbnail from the nested dictionary
                img = self.parent.video_thumb_dict[img_path]['thumbnail'].copy()
                img = img.resize((self.max_width, self.max_height), Image.LANCZOS)
                highlighted_thumbnail = self.apply_highlight(img)
                bordered_thumb = ImageTk.PhotoImage(highlighted_thumbnail)
                button.configure(image=bordered_thumb, style="Highlighted.TButton")
                button.image = bordered_thumb
        else:
            with Image.open(img_path) as img:
                img.thumbnail((self.max_width, self.max_height))
                highlighted_thumbnail = self.apply_highlight(img)
                bordered_thumb = ImageTk.PhotoImage(highlighted_thumbnail)
                button.configure(image=bordered_thumb, style="Highlighted.TButton")
                button.image = bordered_thumb
        self.ensure_thumbnail_visible(button)
        self.parent.update_imageinfo()


    def _reset_thumbnail(self, button):
        if not button:
            return
        for index, btn in self.thumbnail_buttons.items():
            if btn == button:
                for img_tk, path, idx in self.images:
                    if idx == index:
                        button.configure(image=img_tk, style="TButton")
                        button.image = img_tk
                        return
                break


    def apply_highlight(self, img):
        mask_color = (0, 93, 215, 96)
        base = img.copy().convert("RGBA")
        overlay = Image.new("RGBA", base.size, mask_color)
        return Image.alpha_composite(base, overlay)


    def reset_initial_thumbnail(self):
        if self.initial_selected_thumbnail:
            self.initial_selected_thumbnail.configure(style="TButton")
            self.initial_selected_thumbnail = None


    def ensure_thumbnail_visible(self, button):
        if not button:
            return
        button_index = list(self.thumbnail_buttons.values()).index(button)
        row, _ = divmod(button_index, self.cols)
        cell_height = self.max_height + 2 * self.padding
        button_y = row * cell_height
        canvas_height = self.canvas_thumbnails.winfo_height()
        total_height = self.frame_image_grid.winfo_height()
        center_pos = (button_y + cell_height / 2) - (canvas_height / 2)
        center_pos = max(0, min(center_pos, total_height - canvas_height))
        target_scroll = center_pos / total_height
        self.canvas_thumbnails.yview_moveto(target_scroll)


    def on_mouse_click(self, index):
        self.parent.jump_to_image(index)
        self.parent.update_imageinfo()


    def on_mousewheel(self, event):
        if self.canvas_thumbnails.winfo_exists():
            self.canvas_thumbnails.yview_scroll(int(-1*(event.delta/120)), "units")


    def round_scale_input(self, event=None):
        value = float(self.slider_image_size.get())
        if int(value) != value:
            self.slider_image_size.set(round(value))
