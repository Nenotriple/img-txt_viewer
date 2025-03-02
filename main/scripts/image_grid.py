#region -  Imports


# Standard Library
import os


# Standard Library - GUI
from tkinter import (
    ttk,
    IntVar,
    Frame, Label, Scrollbar, Canvas
)


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip
from PIL import Image, ImageTk, ImageDraw, ImageFont


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
################################################################################################################################################
#region - CLASS: ImageGrid


class ImageGrid(ttk.Frame):
    image_cache = {1: {}, 2: {}, 3: {}}  # Cache for each thumbnail size
    image_size_cache = {}  # Cache to store image sizes
    text_file_cache = {}  # Cache to store text file pairs


    def __init__(self, master: 'Frame', parent: 'Main'):
        super().__init__(master)
        # Initialize ImgTxtViewer variables and methods
        self.parent = parent
        self.is_initialized = False
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
        # Image flag
        self.image_flag = self.create_image_flag()
        # Get number of total images from parent
        self.num_total_images = len(self.parent.image_files)
        # Default thumbnail size. Range=(1,2,3). Set to 3 if total_images is less than 25.
        self.image_size = IntVar(value=2) if self.num_total_images < 25 else IntVar(value=2)

        # Interface creation
        self.create_interface()
        self.load_images()
        self.is_initialized = True


#endregion
################################################################################################################################################
#region -  Create Interface


    def create_interface(self):
        self.create_canvas()
        self.create_control_row()


    def create_canvas(self):
        self.frame_main = Frame(self)
        self.frame_main.pack(fill="both", expand=True)
        self.scrollbar = Scrollbar(self.frame_main)
        self.scrollbar.pack(side="right", fill="y")
        self.frame_thumbnails = Frame(self.frame_main, takefocus=False)
        self.frame_thumbnails.pack(side="left", fill="both", expand=True)
        self.canvas_thumbnails = Canvas(self.frame_thumbnails, takefocus=False, yscrollcommand=self.scrollbar.set)
        self.canvas_thumbnails.pack(side="top", fill="both", expand=True)
        self.canvas_thumbnails.bind("<MouseWheel>", self.on_mousewheel)
        self.scrollbar.config(command=self.canvas_thumbnails.yview)
        self.frame_image_grid = Frame(self.canvas_thumbnails, takefocus=False)
        self.frame_image_grid.bind("<MouseWheel>", self.on_mousewheel)


    def create_control_row(self):
        self.frame_bottom = Frame(self.frame_thumbnails)
        self.frame_bottom.pack(side="bottom", fill="x", padx=5)
        # Size slider
        self.label_size = Label(self.frame_bottom, text="Size:")
        self.label_size.pack(side="left", padx=5)
        ToolTip.create(self.label_size, "Adjust grid size", 500, 6, 12)
        self.slider_image_size = ttk.Scale(self.frame_bottom, variable=self.image_size, orient="horizontal", from_=1, to=3, command=self.round_scale_input)
        self.slider_image_size.bind("<ButtonRelease-1>", lambda event: self.reload_grid())
        self.slider_image_size.pack(side="left")
        ToolTip.create(self.slider_image_size, "Adjust grid size", 500, 6, 12)
        # Refresh
        self.button_refresh = ttk.Button(self.frame_bottom, text="Refresh", command=self.reload_grid)
        self.button_refresh.pack(side="right", padx=5)
        ToolTip.create(self.button_refresh, "Refresh the image grid", 500, 6, 12)
        # Load All
        self.button_load_all = ttk.Button(self.frame_bottom, text="Load All", command=lambda: self.load_images(all_images=True))
        self.button_load_all.pack(side="right", padx=5)
        ToolTip.create(self.button_load_all, "Load all images in the folder (Slow)", 500, 6, 12)
        # Image Info
        self.label_image_info = Label(self.frame_bottom, width=14)
        self.label_image_info.pack(side="right", padx=5)
        ToolTip.create(self.label_image_info, "Loaded Images / Total Images", 500, 6, 12)


#endregion
################################################################################################################################################
#region -  Primary Logic


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
        frame_width = self.frame_thumbnails.winfo_width()
        if frame_width <= 1:
            frame_width = self.frame_thumbnails.winfo_reqwidth()
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
        self.cols = self.calculate_columns()


    def create_image_grid(self):
        self.canvas_thumbnails.create_window((0, 0), window=self.frame_image_grid, anchor='nw')
        self.images = self.load_image_set()
        self.populate_image_grid()
        self.configure_scroll_region()
        self.add_load_more_button()


    def populate_image_grid(self):
        for index, (image, filepath, image_index) in enumerate(self.images):
            row, col = divmod(index, self.cols)
            button_style = "Highlighted.TButton" if index == self.parent.current_index else "TButton"
            thumbnail = ttk.Button(self.frame_image_grid, image=image, takefocus=False, style=button_style)
            thumbnail.configure(command=lambda idx=image_index: self.on_mouse_click(idx))
            thumbnail.image = image
            thumbnail.grid(row=row, column=col)
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

            ToolTip.create(thumbnail, tooltip_text, 200, 6, 12)


    def load_images(self, all_images=False):
        self.loaded_images = self.num_total_images if all_images else min(self.loaded_images + self.images_per_load, self.num_total_images)
        self.update_image_info_label()
        self.reload_grid()


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
            txt_path = text_files[image_index]
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
        # Handle video files
        if self._is_video_file(img_path):
            # Check if we have a thumbnail in the video_thumb_dict
            if hasattr(self.parent, 'video_thumb_dict') and img_path in self.parent.video_thumb_dict:
                img = self.parent.video_thumb_dict[img_path]
                img.thumbnail((self.max_width, self.max_height))
                position = ((self.max_width - img.width) // 2, (self.max_height - img.height) // 2)
                new_img.paste(img, position)
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


    def paste_image_flag(self, new_img, img_path, txt_path, current_text_file_size=None):
        # Handle video files
        if self._is_video_file(img_path):
            if hasattr(self.parent, 'video_thumb_dict') and img_path in self.parent.video_thumb_dict:
                img = self.parent.video_thumb_dict[img_path]
                img.thumbnail((self.max_width, self.max_height))
                position = ((self.max_width - img.width) // 2, (self.max_height - img.height) // 2)
                new_img.paste(img, position)
        else:
            # Regular image handling
            with Image.open(img_path) as img:
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
        try:
            return self.parent.image_files.index(os.path.join(directory, filename))
        except ValueError:
            return -1


#endregion
################################################################################################################################################
#region -  Interface Logic


    def configure_scroll_region(self):
        total_filtered_images = len(self.thumbnail_buttons)
        total_rows = (total_filtered_images + self.cols - 1) // self.cols
        cell_height = self.max_height + (2 * self.padding)
        base_height = total_rows * cell_height
        extra_height = cell_height if (self.loaded_images < self.num_total_images) else 0
        scrollregion_height = base_height + extra_height
        self.canvas_thumbnails.config(scrollregion=(0, 0, 750, scrollregion_height))
        self.canvas_thumbnails.yview_moveto(0)


    def add_load_more_button(self):
        if self.loaded_images < self.num_total_images:
            total_items = len(self.thumbnail_buttons)
            final_row = (total_items - 1) // self.columns
            self.load_more_button = ttk.Button(self.frame_image_grid, text="Load More", command=self.load_images)
            self.load_more_button.grid(row=final_row + 1, column=0, columnspan=self.columns, pady=10, sticky='ew')
            ToolTip.create(self.load_more_button, "Load the next 150 images", 500, 6, 12)


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
                img = self.parent.video_thumb_dict[img_path].copy()
                img.thumbnail((self.max_width, self.max_height))
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
