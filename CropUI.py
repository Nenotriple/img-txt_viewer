"""
########################################
#                CropUI                #
#   Version : v1.00                    #
#   Author  : github.com/Nenotriple    #
########################################

Description:
-------------
Create a UI that allows the user to open an image file and crop a selection from the image.

"""

#endregion
#########################################################################################################
#region - Imports


# Standard Library
import os


# Standard Library GUI
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# Third Party Library
from PIL import Image, ImageTk


#endregion
#########################################################################################################
#region CLS: CropSelection


class CropSelection:
    def __init__(self, parent, img_canvas):
        self.parent = parent
        self.img_canvas = img_canvas

        # Selection variables
        self.rect = None
        self.overlay = None
        self.coords = None
        self.start_x = None
        self.start_y = None

        # Variables for moving and resizing
        self.moving_rectangle = False
        self.move_offset_x = 0
        self.move_offset_y = 0
        self.rect_width = 0
        self.rect_height = 0

        # Initialize handles manager
        self.handles_manager = CropSelectionHandles(self, img_canvas)

        self.setup_img_canvas_binds()


    def setup_img_canvas_binds(self):
        self.img_canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.img_canvas.bind("<B1-Motion>", lambda event: self.on_move_press(event), add="+")
        self.img_canvas.bind("<B1-Motion>", lambda event: self.parent.update_widget_values(), add="+")
        self.img_canvas.bind("<ButtonRelease-1>", self.on_button_release, add="+")
        self.img_canvas.bind("<ButtonRelease-1>", lambda event: self.parent.update_widget_values(), add="+")
        self.img_canvas.bind("<Motion>", self.handles_manager.update_cursor_icon)


    def on_button_press(self, event):
        if not self.img_canvas.img_path:
            return
        x_offset, y_offset = self.img_canvas.x_offset, self.img_canvas.y_offset
        x_max = x_offset + self.img_canvas.new_size[0]
        y_max = y_offset + self.img_canvas.new_size[1]
        if self.rect:
            if self.handles_manager.is_handle_clicked(event):
                return
            x1, y1, x2, y2 = self.img_canvas.coords(self.rect)
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.moving_rectangle = True
                self.move_offset_x = event.x - x1
                self.move_offset_y = event.y - y1
                self.rect_width = x2 - x1
                self.rect_height = y2 - y1
                self.handles_manager.hide_handles()
                return
            else:
                self.clear_selection()
        if not (x_offset <= event.x <= x_max and y_offset <= event.y <= y_max):
            return
        self.start_x = max(min(event.x, x_max), x_offset)
        self.start_y = max(min(event.y, y_max), y_offset)
        if self.parent.expand_from_center_var.get():
            self.center_x = self.start_x
            self.center_y = self.start_y
        self.rect = self.img_canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='white', tags='rect')


    def on_move_press(self, event):
        if not self.img_canvas.img_path or not self.rect:
            return
        x_offset, y_offset = self.img_canvas.x_offset, self.img_canvas.y_offset
        x_max = x_offset + self.img_canvas.new_size[0]
        y_max = y_offset + self.img_canvas.new_size[1]

        def update_rectangle(x1, y1, x2, y2):
            self.img_canvas.coords(self.rect, x1, y1, x2, y2)
            self.rect_width = x2 - x1
            self.rect_height = y2 - y1
            self.update_selection_coords(x1, y1, x2, y2)
            self.handles_manager.update_handles()
            self.update_overlay()

        if self.handles_manager.is_resizing():
            x1, y1, x2, y2 = self.handles_manager.resize(event)
            update_rectangle(x1, y1, x2, y2)
        elif self.moving_rectangle:
            x1 = max(x_offset, min(event.x - self.move_offset_x, x_max - self.rect_width))
            y1 = max(y_offset, min(event.y - self.move_offset_y, y_max - self.rect_height))
            x2 = x1 + self.rect_width
            y2 = y1 + self.rect_height
            update_rectangle(x1, y1, x2, y2)
        else:
            if self.parent.expand_from_center_var.get():
                curX = max(min(event.x, x_max), x_offset)
                curY = max(min(event.y, y_max), y_offset)
                x1 = max(x_offset, min(2 * self.center_x - curX, x_max))
                y1 = max(y_offset, min(2 * self.center_y - curY, y_max))
                x2 = curX
                y2 = curY
                update_rectangle(x1, y1, x2, y2)
            else:
                curX = max(min(event.x, x_max), x_offset)
                curY = max(min(event.y, y_max), y_offset)
                update_rectangle(self.start_x, self.start_y, curX, curY)


    def on_button_release(self, event):
        if not self.img_canvas.img_path or not self.rect:
            return
        coords = self.img_canvas.coords(self.rect)
        if len(coords) != 4:
            return
        x1, y1, x2, y2 = coords
        if self.handles_manager.is_resizing():
            self.handles_manager.stop_resizing()
        elif self.moving_rectangle:
            self.moving_rectangle = False
        else:
            if x1 == x2 or y1 == y2:
                self.clear_selection()
                return
            self.handles_manager.create_handles()
            self.update_overlay()
        self.update_selection_coords(x1, y1, x2, y2)
        self.handles_manager.show_handles()


    def update_selection_coords(self, x1, y1, x2, y2):
        """
        Updates the selection coordinates based on user input and adjusts them according to the image canvas offsets and scale ratio.

        Parameters:
            x1 (int): The x-coordinate of the first selection point.
            y1 (int): The y-coordinate of the first selection point.
            x2 (int): The x-coordinate of the second selection point.
            y2 (int): The y-coordinate of the second selection point.

        Sets:
            self.coords (tuple or None): The adjusted original coordinates as a tuple (x1_orig, y1_orig, x2_orig, y2_orig). Set to None if the selection has zero area.
        """
        # Convert canvas coordinates to original image coordinates
        x_offset, y_offset = self.img_canvas.x_offset, self.img_canvas.y_offset
        x_max = x_offset + self.img_canvas.new_size[0]
        y_max = y_offset + self.img_canvas.new_size[1]
        # Ensure coordinates are within canvas bounds
        x1, x2 = sorted([max(x_offset, min(x1, x_max)), max(x_offset, min(x2, x_max))])
        y1, y2 = sorted([max(y_offset, min(y1, y_max)), max(y_offset, min(y2, y_max))])
        # Adjust coordinates based on image scale ratio and offsets
        x1_adj = x1 - x_offset
        y1_adj = y1 - y_offset
        x2_adj = x2 - x_offset
        y2_adj = y2 - y_offset
        # Convert adjusted coordinates to original image coordinates
        img_scale_ratio = self.img_canvas.img_scale_ratio
        x1_orig = int(x1_adj / img_scale_ratio)
        y1_orig = int(y1_adj / img_scale_ratio)
        x2_orig = int(x2_adj / img_scale_ratio)
        y2_orig = int(y2_adj / img_scale_ratio)
        # Ensure coordinates are within original image bounds
        original_img_width = self.img_canvas.original_img_width
        original_img_height = self.img_canvas.original_img_height
        x1_orig, x2_orig = sorted([max(0, min(original_img_width, x1_orig)), max(0, min(original_img_width, x2_orig))])
        y1_orig, y2_orig = sorted([max(0, min(original_img_height, y1_orig)), max(0, min(original_img_height, y2_orig))])
        # Set coordinates
        self.coords = (x1_orig, y1_orig, x2_orig, y2_orig) if x1_orig != x2_orig and y1_orig != y2_orig else None


    def clear_selection(self):
        if self.rect:
            self.img_canvas.delete(self.rect)
        if self.overlay:
            self.img_canvas.delete("overlay")
        self.handles_manager.delete_handles()
        self.rect = None
        self.coords = None
        self.start_x = None
        self.start_y = None
        self.moving_rectangle = False
        self.move_offset_x = 0
        self.move_offset_y = 0
        self.rect_width = 0
        self.rect_height = 0
        self.parent.update_widget_values()


    def update_overlay(self):
        if self.overlay:
            self.img_canvas.delete("overlay")
        self.overlay = []
        if self.rect:
            x1, y1, x2, y2 = self.img_canvas.coords(self.rect)
            canvas_width = self.img_canvas.winfo_width()
            canvas_height = self.img_canvas.winfo_height()
            overlay_coords = [
                (0, 0, canvas_width, y1),
                (0, y1, x1, y2),
                (x2, y1, canvas_width, y2),
                (0, y2, canvas_width, canvas_height)
                ]
            self.overlay = [self.img_canvas.create_rectangle(*coords, fill="black", stipple="gray50", outline="", tags="overlay") for coords in overlay_coords]
            self.img_canvas.tag_lower("overlay", 'rect')


    def redraw(self):
        if self.rect and self.coords:
            x1 = self.coords[0] * self.img_canvas.img_scale_ratio + self.img_canvas.x_offset
            y1 = self.coords[1] * self.img_canvas.img_scale_ratio + self.img_canvas.y_offset
            x2 = self.coords[2] * self.img_canvas.img_scale_ratio + self.img_canvas.x_offset
            y2 = self.coords[3] * self.img_canvas.img_scale_ratio + self.img_canvas.y_offset
            self.rect = self.img_canvas.create_rectangle(x1, y1, x2, y2, outline='white', tags='rect')
            self.handles_manager.update_handles(create=True)
            self.update_overlay()


    def update_selection_size(self, width=None, height=None, x=None, y=None):
        if not self.rect:
            return
        # Get current rectangle coordinates
        x1_canvas, y1_canvas, x2_canvas, y2_canvas = self.img_canvas.coords(self.rect)
        # Convert canvas coordinates to original image coordinates
        x_offset, y_offset = self.img_canvas.x_offset, self.img_canvas.y_offset
        img_scale_ratio = self.img_canvas.img_scale_ratio
        x1_orig = (x1_canvas - x_offset) / img_scale_ratio
        y1_orig = (y1_canvas - y_offset) / img_scale_ratio
        x2_orig = (x2_canvas - x_offset) / img_scale_ratio
        y2_orig = (y2_canvas - y_offset) / img_scale_ratio
        current_width = x2_orig - x1_orig
        current_height = y2_orig - y1_orig
        updated = False
        if x is not None and x != x1_orig:
            x1_orig = x
            updated = True
        if y is not None and y != y1_orig:
            y1_orig = y
            updated = True
        if width is not None and width != current_width:
            x2_orig = x1_orig + width
            updated = True
        else:
            x2_orig = x1_orig + current_width
        if height is not None and height != current_height:
            y2_orig = y1_orig + height
            updated = True
        else:
            y2_orig = y1_orig + current_height
        if updated:
            # Convert back to canvas coordinates
            x1_canvas = x1_orig * img_scale_ratio + x_offset
            y1_canvas = y1_orig * img_scale_ratio + y_offset
            x2_canvas = x2_orig * img_scale_ratio + x_offset
            y2_canvas = y2_orig * img_scale_ratio + y_offset
            # Ensure coordinates are within canvas bounds
            x_max = x_offset + self.img_canvas.new_size[0]
            y_max = y_offset + self.img_canvas.new_size[1]
            x1_canvas = max(x_offset, min(x1_canvas, x_max))
            y1_canvas = max(y_offset, min(y1_canvas, y_max))
            x2_canvas = max(x_offset, min(x2_canvas, x_max))
            y2_canvas = max(y_offset, min(y2_canvas, y_max))
            if x2_canvas < x1_canvas:
                x1_canvas, x2_canvas = x2_canvas, x1_canvas
            if y2_canvas < y1_canvas:
                y1_canvas, y2_canvas = y2_canvas, y1_canvas
            # Update rectangle on canvas
            self.img_canvas.coords(self.rect, x1_canvas, y1_canvas, x2_canvas, y2_canvas)
            self.rect_width = x2_canvas - x1_canvas
            self.rect_height = y2_canvas - y1_canvas
            self.update_selection_coords(x1_canvas, y1_canvas, x2_canvas, y2_canvas)
            self.handles_manager.update_handles()
            self.update_overlay()


#endregion
#########################################################################################################
#region CLS: CropSelHandles


class CropSelectionHandles:
    def __init__(self, crop_selection, img_canvas):
        self.crop_selection = crop_selection
        self.img_canvas = img_canvas

        # Handles
        self.handles = {}
        self.handle_size = 6
        self.handle_color = 'white'
        self.resizing_handle = None

        # Cursor mapping for handles
        self.cursor_mapping = {
            'n': 'top_side',
            'e': 'right_side',
            's': 'bottom_side',
            'w': 'left_side',
            'ne': 'top_right_corner',
            'nw': 'top_left_corner',
            'se': 'bottom_right_corner',
            'sw': 'bottom_left_corner'
            }


    def update_handles(self, create=False):
        if not self.crop_selection.rect:
            return
        x1, y1, x2, y2 = self.img_canvas.coords(self.crop_selection.rect)
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        size = self.calculate_handle_size(x1, y1, x2, y2)
        positions = {
            'n': (mid_x, y1),
            'e': (x2, mid_y),
            's': (mid_x, y2),
            'w': (x1, mid_y),
            'ne': (x2, y1),
            'nw': (x1, y1),
            'se': (x2, y2),
            'sw': (x1, y2)
            }
        for key, (cx, cy) in positions.items():
            if create:
                self.handles[key] = self.img_canvas.create_rectangle(
                    cx - size, cy - size, cx + size, cy + size,
                    fill=self.handle_color, tags='handle'
                    )
            elif key in self.handles:
                self.img_canvas.coords(self.handles[key], cx - size, cy - size, cx + size, cy + size)


    def calculate_handle_size(self, x1, y1, x2, y2):
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        if width < 50 or height < 50:
            return self.handle_size - 4
        elif width < 100 or height < 100:
            return self.handle_size - 3
        elif width < 150 or height < 150:
            return self.handle_size - 2
        else:
            return self.handle_size


    def hide_handles_except(self, active_handle):
        for key, handle in self.handles.items():
            if key != active_handle:
                self.img_canvas.itemconfigure(handle, state='hidden')


    def hide_handles(self):
        for handle in self.handles.values():
            self.img_canvas.itemconfigure(handle, state='hidden')


    def show_handles(self):
        for handle in self.handles.values():
            self.img_canvas.itemconfigure(handle, state='normal')


    def is_handle_clicked(self, event):
        items = self.img_canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for key, handle in self.handles.items():
            if handle in items:
                self.resizing_handle = key
                self.hide_handles_except(key)
                return True
        return False


    def update_cursor_icon(self, event):
        if not self.img_canvas.img_path:
            return
        items = self.img_canvas.find_overlapping(event.x, event.y, event.x, event.y)
        cursor = "cross"
        for key, handle in self.handles.items():
            if handle in items:
                cursor = self.cursor_mapping.get(key, "cross")
                break
        self.img_canvas.config(cursor=cursor)


    def delete_handles(self):
        for handle in self.handles.values():
            self.img_canvas.delete(handle)
        self.handles.clear()
        self.resizing_handle = None


    def is_resizing(self):
        return self.resizing_handle is not None


    def stop_resizing(self):
        self.resizing_handle = None
        self.show_handles()


    def resize(self, event):
        x1, y1, x2, y2 = self.img_canvas.coords(self.crop_selection.rect)
        x_offset, y_offset = self.img_canvas.x_offset, self.img_canvas.y_offset
        x_max = x_offset + self.img_canvas.new_size[0]
        y_max = y_offset + self.img_canvas.new_size[1]
        handle_actions = {
            'n': lambda: (x1, max(y_offset, min(event.y, y2 - 10)), x2, y2),
            'e': lambda: (x1, y1, min(x_max, max(event.x, x1 + 10)), y2),
            's': lambda: (x1, y1, x2, min(y_max, max(event.y, y1 + 10))),
            'w': lambda: (max(x_offset, min(event.x, x2 - 10)), y1, x2, y2),
            'ne': lambda: (x1, max(y_offset, min(event.y, y2 - 10)), min(x_max, max(event.x, x1 + 10)), y2),
            'nw': lambda: (max(x_offset, min(event.x, x2 - 10)), max(y_offset, min(event.y, y2 - 10)), x2, y2),
            'se': lambda: (x1, y1, min(x_max, max(event.x, x1 + 10)), min(y_max, max(event.y, y1 + 10))),
            'sw': lambda: (max(x_offset, min(event.x, x2 - 10)), y1, x2, min(y_max, max(event.y, y1 + 10)))
            }
        x1_new, y1_new, x2_new, y2_new = handle_actions[self.resizing_handle]()
        return x1_new, y1_new, x2_new, y2_new


    def create_handles(self):
        self.update_handles(create=True)


#endregion
#########################################################################################################
#region CLS: ImageCanvas


class ImageCanvas(tk.Canvas):
    def __init__(self, parent, frame):
        super().__init__(frame, cursor="cross")
        self.parent = parent
        self.img_path = None
        self.original_img = None
        self.original_img_width = 0
        self.original_img_height = 0
        self.img_scale_ratio = 1.0
        self.new_size = (0, 0)
        self.x_offset = 0
        self.y_offset = 0
        self.img_thumbnail = None
        self.resize_after_id = None

        self.bind("<Configure>", self.resize_image)
        self.bind("<Button-3>", lambda event: self.parent.crop_selection.clear_selection())


    def display_image(self, img_path):
        self.img_path = img_path
        with Image.open(img_path) as img:
            self.original_img = img.copy()
        self.original_img_width, self.original_img_height = self.original_img.size
        self.resize_image(None)


    def resize_image(self, event):
        if not self.img_path:
            return
        # Calculate new dimensions while maintaining aspect ratio
        new_width, new_height = self.winfo_width(), self.winfo_height()
        ratio = min(new_width / self.original_img_width, new_height / self.original_img_height)
        new_size = (int(self.original_img_width * ratio), int(self.original_img_height * ratio))
        # Resize if new size is different
        if new_size != self.new_size:
            self.img_scale_ratio = ratio
            self.new_size = new_size
            # Resize the image
            self.img_resized = self.original_img.resize(self.new_size, Image.NEAREST)
            # Convert resized image for Tkinter
            self.img_thumbnail = ImageTk.PhotoImage(self.img_resized)
            # Update image info
            percent_scale = self.img_scale_ratio * 100
            self.parent.update_imageinfo(int(percent_scale))
        self.delete("all")
        # Center and Create image image on canvas
        self.x_offset = (new_width - self.new_size[0]) // 2
        self.y_offset = (new_height - self.new_size[1]) // 2
        self.create_image(self.x_offset, self.y_offset, anchor="nw", image=self.img_thumbnail)
        self.configure(scrollregion=self.bbox("all"))
        # Schedule HQ resize after 250ms
        if self.resize_after_id:
            self.after_cancel(self.resize_after_id)
        self.resize_after_id = self.after(250, self.refresh_image)


    def refresh_image(self):
        if not self.img_path:
            return
        self.img_resized = self.original_img.resize(self.new_size, Image.LANCZOS)
        self.img_thumbnail = ImageTk.PhotoImage(self.img_resized)
        self.delete("all")
        self.create_image(self.x_offset, self.y_offset, anchor="nw", image=self.img_thumbnail)
        self.configure(scrollregion=self.bbox("all"))
        if hasattr(self, 'crop_selection'):
            self.crop_selection.redraw()


#endregion
#########################################################################################################
#region CLS: ImageCropper


class ImageCropper:
    def __init__(self):
        self.image_files = []
        self.current_index = 0
        self.image_info_cache = {}
        self.pady = 5
        self.padx = 10
        self.setup_window()

        # Create crop selection object
        self.crop_selection = CropSelection(self, self.img_canvas)
        # Bind crop selection to image canvas
        self.img_canvas.crop_selection = self.crop_selection


    def setup_window(self):
        self.root = tk.Tk()
        self.root.minsize(590, 440)
        self.root.title("Image Cropper")
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.create_image_ui()
        self.create_control_panel()
        # Display window size on resize:
        #self.root.bind("<Configure>", lambda event: print(f"\rWindow size (W,H): {event.width},{event.height}    ", end='') if event.widget == self.root else None, add="+")


    def create_image_ui(self):
        # Image Stats
        stats_frame = tk.Frame(self.main_frame, relief="sunken", borderwidth=1)
        stats_frame.grid(row=0, column=0, sticky="ew", pady=self.pady)
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.stats_label = ttk.Label(stats_frame)
        self.stats_label.pack(fill="x")

        # Image Canvas
        canvas_frame = tk.Frame(self.main_frame)
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.img_canvas = ImageCanvas(self, canvas_frame)
        self.img_canvas.pack(fill="both", expand=True)


    def create_control_panel(self):
        self.create_directory_and_navigation_widgets()
        self.create_size_widgets()
        self.create_position_widgets()
        self.create_aspect_ratio_widgets()


    def create_directory_and_navigation_widgets(self):
        self.control_panel = tk.Frame(self.main_frame, relief="sunken", borderwidth=1)
        self.control_panel.grid(row=0, column=1, sticky="nsew", rowspan=2, padx=self.padx, pady=self.pady)
        self.main_frame.grid_columnconfigure(1, weight=0)

        # Directory
        self.directory_frame = tk.Frame(self.control_panel)
        self.directory_frame.pack(pady=self.pady, padx=self.padx, fill="x")
        self.path_entry = ttk.Entry(self.directory_frame)
        self.path_entry.pack(side="left", fill="x")
        self.open_button = ttk.Button(self.directory_frame, text="Browse...", width=9, command=self.open_directory_dialog)
        self.open_button.pack(side="left", fill="x")

        # Navigation
        self.nav_frame = tk.Frame(self.control_panel)
        self.nav_frame.pack(pady=self.pady, padx=self.padx, fill="x")
        self.prev_button = ttk.Button(self.nav_frame, text="<---Previous", width=12, command=self.show_previous_image)
        self.prev_button.pack(side="left", fill="x", expand=True)
        self.next_button = ttk.Button(self.nav_frame, text="Next--->", width=12, command=self.show_next_image)
        self.next_button.pack(side="left", fill="x", expand=True)

        # Crop Button
        self.crop_button = ttk.Button(self.control_panel, text="Crop Selection", command=self.crop_image)
        self.crop_button.pack(fill="x", pady=self.pady, padx=self.padx)


    def create_size_widgets(self):
        self.size_frame = ttk.LabelFrame(self.control_panel, text="Size")
        self.size_frame.pack(pady=self.pady, padx=self.padx, fill="x")

        # Width
        self.width_label = ttk.Label(self.size_frame, text="W (px):")
        self.width_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.width_spinbox = ttk.Spinbox(self.size_frame, from_=1, to=99999, width=10)
        self.width_spinbox.grid(row=0, column=1, columnspan=2, padx=self.padx, pady=self.pady)
        self.width_spinbox.bind("<Return>", lambda event: self.crop_selection.update_selection_size(width=int(self.width_spinbox.get())))

        # Height
        self.height_label = ttk.Label(self.size_frame, text="H (px):")
        self.height_label.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        self.height_spinbox = ttk.Spinbox(self.size_frame, from_=1, to=99999, width=10)
        self.height_spinbox.grid(row=1, column=1, columnspan=2, padx=self.padx, pady=self.pady)
        self.height_spinbox.bind("<Return>", lambda event: self.crop_selection.update_selection_size(height=int(self.width_spinbox.get())))


    def create_position_widgets(self):
        self.position_frame = ttk.LabelFrame(self.control_panel, text="Position")
        self.position_frame.pack(pady=self.pady, padx=self.padx, fill="x")

        # X Position
        self.pos_x_label = ttk.Label(self.position_frame, text="X (px):")
        self.pos_x_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.pos_x_spinbox = ttk.Spinbox(self.position_frame, from_=0, to=99999, width=10)
        self.pos_x_spinbox.grid(row=0, column=1, columnspan=2, padx=self.padx, pady=self.pady)
        self.pos_x_spinbox.bind("<Return>", lambda event: self.crop_selection.update_selection_size(x=int(self.pos_x_spinbox.get())))

        # Y Position
        self.pos_y_label = ttk.Label(self.position_frame, text="Y (px):")
        self.pos_y_label.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        self.pos_y_spinbox = ttk.Spinbox(self.position_frame, from_=0, to=99999, width=10)
        self.pos_y_spinbox.grid(row=1, column=1, columnspan=2, padx=self.padx, pady=self.pady)
        self.pos_y_spinbox.bind("<Return>", lambda event: self.crop_selection.update_selection_size(y=int(self.pos_y_spinbox.get())))


    def create_aspect_ratio_widgets(self):
        self.aspect_ratio_frame = ttk.LabelFrame(self.control_panel, text="Aspect Ratio")
        self.aspect_ratio_frame.pack(pady=self.pady, padx=self.padx, fill="x")

        # Expand From Center
        self.expand_from_center_var = tk.BooleanVar(value=False)
        self.expand_from_center_checkbutton = ttk.Checkbutton(self.aspect_ratio_frame, variable=self.expand_from_center_var, text="Expand From Center")
        self.expand_from_center_checkbutton.grid(row=0, column=0, columnspan=3, padx=self.padx, pady=self.pady, sticky="w")

        # Fixed Aspect Ratio
        self.fixed_selection_var = tk.BooleanVar(value=False)
        self.fixed_selection_checkbutton = ttk.Checkbutton(self.aspect_ratio_frame, variable=self.fixed_selection_var, text="Fixed", width=5)
        self.fixed_selection_checkbutton.grid(row=1, column=0, padx=self.padx, pady=self.pady)

        # Aspect Ratio Combobox
        self.fixed_selection_option_var = tk.StringVar(value="Aspect Ratio")
        self.fixed_selection_option_combobox = ttk.Combobox(self.aspect_ratio_frame, values=["Aspect Ratio", "Width", "Height", "Size"], state="readonly", textvariable=self.fixed_selection_option_var, width=12)
        self.fixed_selection_option_combobox.grid(row=1, column=1, columnspan=2, sticky="ew", padx=self.padx, pady=self.pady)

        # Aspect Entry Frame
        self.aspect_entry_frame = tk.Frame(self.aspect_ratio_frame)
        self.aspect_entry_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=self.padx, pady=self.pady)

        # Clear Button
        self.clear_button = ttk.Button(self.aspect_entry_frame, text="Clear", width=5)
        self.clear_button.pack(side="right")

        # Aspect Ratio Entry
        self.fixed_selection_entry_var = tk.StringVar(value="1:1")
        self.fixed_selection_entry = ttk.Entry(self.aspect_entry_frame, textvariable=self.fixed_selection_entry_var, width=12)
        self.fixed_selection_entry.pack(side="right")


    def open_directory_dialog(self):
        dir_path = filedialog.askdirectory()
        if dir_path and os.path.exists(dir_path):
            self.image_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"))]
            self.current_index = 0
            if self.image_files:
                self.display_image(self.image_files[self.current_index])
                self.path_entry.delete(0, "end")
                self.path_entry.insert(0, dir_path)
            else:
                messagebox.showerror("Error", "No image files found in the selected directory.")


    def display_image(self, img_path):
        self.img_canvas.display_image(img_path)
        self.crop_selection.clear_selection()
        original_width, original_height = self.img_canvas.original_img.size
        displayed_width = self.img_canvas.winfo_width()
        percent_scale = int((displayed_width / original_width) * 100)
        self.update_imageinfo(percent_scale)


    def show_previous_image(self):
        if self.image_files:
            self.current_index = (self.current_index - 1) % len(self.image_files)
            self.display_image(self.image_files[self.current_index])


    def show_next_image(self):
        if self.image_files:
            self.current_index = (self.current_index + 1) % len(self.image_files)
            self.display_image(self.image_files[self.current_index])


    def crop_image(self):
        if not self.img_canvas.img_path:
            return
        if self.crop_selection.coords:
            cropped = self.img_canvas.original_img.crop(self.crop_selection.coords)
            cropped.show()
            self.root.after(750, self.crop_selection.clear_selection)


    def update_imageinfo(self, percent_scale=0):
        if self.image_files:
            self.image_file = self.image_files[self.current_index]
            if self.image_file not in self.image_info_cache:
                self.image_info_cache[self.image_file] = self.get_image_info(self.image_file)
            image_info = self.image_info_cache[self.image_file]
            self.stats_label.config(text=f"{image_info['filename']}  |  {image_info['resolution']}  |  {percent_scale}%  |  {image_info['size']}  |  {image_info['color_mode']}", anchor="w")


    def get_image_info(self, image_file):
        image = self.img_canvas.original_img
        width, height = image.size
        color_mode = image.mode
        size = os.path.getsize(image_file)
        size_kb = size / 1024
        size_str = f"{round(size_kb)} KB" if size_kb < 1024 else f"{round(size_kb / 1024, 2)} MB"
        filename = os.path.basename(image_file)
        filename = (filename[:61] + '(...)') if len(filename) > 64 else filename
        return {"filename": filename, "resolution": f"{width} x {height}", "size": size_str, "color_mode": color_mode}


    def update_widget_values(self):
        try:
            x1, y1, x2, y2 = self.crop_selection.coords
            x = x1
            y = y1
            height = y2 - y1
            width = x2 - x1
        except TypeError:
            x = y = height = width = 0
        self.pos_x_spinbox.set(x)
        self.pos_y_spinbox.set(y)
        self.width_spinbox.set(width)
        self.height_spinbox.set(height)


    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    cropper = ImageCropper()
    cropper.run()

#endregion
