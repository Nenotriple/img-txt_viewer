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

        self._set_img_canvas_binds()


    def _set_img_canvas_binds(self):
        self.img_canvas.bind("<ButtonPress-1>", self._on_button_press)
        self.img_canvas.bind("<B1-Motion>", self._on_move_press, add="+")
        self.img_canvas.bind("<B1-Motion>", lambda event: self.parent.update_widget_values(), add="+")
        self.img_canvas.bind("<ButtonRelease-1>", self._on_button_release, add="+")
        self.img_canvas.bind("<ButtonRelease-1>", lambda event: self.parent.update_widget_values(), add="+")
        self.img_canvas.bind("<Motion>", self.handles_manager._update_cursor_icon)


    def _on_button_press(self, event):
        if not self.img_canvas.img_path:
            return
        x_off, y_off = self.img_canvas.x_off, self.img_canvas.y_off
        x_max = x_off + self.img_canvas.new_size[0]
        y_max = y_off + self.img_canvas.new_size[1]
        if self.rect:
            if self.handles_manager._is_handle_clicked(event):
                return
            x1, y1, x2, y2 = self.img_canvas.coords(self.rect)
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self._start_moving_rect(event, x1, y1, x2, y2)
                return
            else:
                self.clear_selection()
        if not (x_off <= event.x <= x_max and y_off <= event.y <= y_max):
            return
        self._start_selection(event, x_off, y_off, x_max, y_max)


    def _start_moving_rect(self, event, x1, y1, x2, y2):
        self.moving_rectangle = True
        self.move_offset_x = event.x - x1
        self.move_offset_y = event.y - y1
        self.rect_width = x2 - x1
        self.rect_height = y2 - y1
        self.handles_manager.hide_handles()


    def _start_selection(self, event, x_off, y_off, x_max, y_max):
        self.start_x = max(min(event.x, x_max), x_off)
        self.start_y = max(min(event.y, y_max), y_off)
        if self.parent.expand_from_center_var.get():
            self.center_x = self.start_x
            self.center_y = self.start_y
        self.rect = self.img_canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='white', tags='rect')


    def _on_move_press(self, event):
        if not self.img_canvas.img_path or not self.rect:
            return
        x_off, y_off = self.img_canvas.x_off, self.img_canvas.y_off
        x_max = x_off + self.img_canvas.new_size[0]
        y_max = y_off + self.img_canvas.new_size[1]
        if self.handles_manager._is_resizing():
            x1, y1, x2, y2 = self.handles_manager._resize(event)
        elif self.moving_rectangle:
            x1, y1, x2, y2 = self._calculate_moving_rect(event, x_off, y_off, x_max, y_max)
        else:
            x1, y1, x2, y2 = self._calculate_selection_rect(event, x_off, y_off, x_max, y_max)
        self.update_rectangle(x1, y1, x2, y2)


    def _calculate_moving_rect(self, event, x_off, y_off, x_max, y_max):
        x1 = max(x_off, min(event.x - self.move_offset_x, x_max - self.rect_width))
        y1 = max(y_off, min(event.y - self.move_offset_y, y_max - self.rect_height))
        x2 = x1 + self.rect_width
        y2 = y1 + self.rect_height
        return x1, y1, x2, y2


    def _calculate_selection_rect(self, event, x_off, y_off, x_max, y_max):
        curX = max(min(event.x, x_max), x_off)
        curY = max(min(event.y, y_max), y_off)
        if self.parent.expand_from_center_var.get():
            x1 = max(x_off, min(2 * self.center_x - curX, x_max))
            y1 = max(y_off, min(2 * self.center_y - curY, y_max))
            x2 = curX
            y2 = curY
        else:
            x1, y1 = self.start_x, self.start_y
            x2, y2 = curX, curY
        return x1, y1, x2, y2


    def update_rectangle(self, x1, y1, x2, y2):
        self.img_canvas.coords(self.rect, x1, y1, x2, y2)
        self.rect_width = x2 - x1
        self.rect_height = y2 - y1
        self._update_selection_coords(x1, y1, x2, y2)
        self.handles_manager.update_handles()
        self._update_overlay()


    def _on_button_release(self, event):
        if not self.img_canvas.img_path or not self.rect:
            return
        coords = self.img_canvas.coords(self.rect)
        if len(coords) != 4:
            return
        x1, y1, x2, y2 = coords
        if self.handles_manager._is_resizing():
            self.handles_manager._stop_resizing()
        elif self.moving_rectangle:
            self.moving_rectangle = False
        else:
            if x1 == x2 or y1 == y2:
                self.clear_selection()
                return
            self.handles_manager.update_handles(create=True)
            self._update_overlay()
        self._update_selection_coords(x1, y1, x2, y2)
        self.handles_manager.show_handles()


    def _update_selection_coords(self, x1, y1, x2, y2):
        cx_off, cy_off = self.img_canvas.x_off, self.img_canvas.y_off
        c_ns = self.img_canvas.new_size
        x1, x2 = sorted([max(cx_off, min(x1, cx_off + c_ns[0])), max(cx_off, min(x2, cx_off + c_ns[0]))])
        y1, y2 = sorted([max(cy_off, min(y1, cy_off + c_ns[1])), max(cy_off, min(y2, cy_off + c_ns[1]))])
        x1_adj, y1_adj = x1 - cx_off, y1 - cy_off
        x2_adj, y2_adj = x2 - cx_off, y2 - cy_off
        scale = self.img_canvas.img_scale_ratio
        x1_orig, y1_orig = int(x1_adj / scale), int(y1_adj / scale)
        x2_orig, y2_orig = int(x2_adj / scale), int(y2_adj / scale)
        orig_img_width, orig_img_height = self.img_canvas.original_img_width, self.img_canvas.original_img_height
        x1_orig, x2_orig = sorted([max(0, min(orig_img_width, x1_orig)), max(0, min(orig_img_width, x2_orig))])
        y1_orig, y2_orig = sorted([max(0, min(orig_img_height, y1_orig)), max(0, min(orig_img_height, y2_orig))])
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


    def _update_overlay(self):
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
            scale = self.img_canvas.img_scale_ratio
            x1 = self.coords[0] * scale + self.img_canvas.x_off
            y1 = self.coords[1] * scale + self.img_canvas.y_off
            x2 = self.coords[2] * scale + self.img_canvas.x_off
            y2 = self.coords[3] * scale + self.img_canvas.y_off
            self.rect = self.img_canvas.create_rectangle(x1, y1, x2, y2, outline='white', tags='rect')
            self.handles_manager.update_handles(create=True)
            self._update_overlay()


    def set_selection_dimensions(self, width=None, height=None, new_x=None, new_y=None):
        if not self.rect:
            return
        x1, y1, x2, y2 = self.img_canvas.coords(self.rect)
        cx_off, cy_off = self.img_canvas.x_off, self.img_canvas.y_off
        scale = self.img_canvas.img_scale_ratio
        c_size = self.img_canvas.new_size
        if new_x is not None:
            new_x = max(cx_off, min(new_x, cx_off + c_size[0] - (x2 - x1)))
            x2 = new_x + (x2 - x1)
            x1 = new_x
        if new_y is not None:
            new_y = max(cy_off, min(new_y, cy_off + c_size[1] - (y2 - y1)))
            y2 = new_y + (y2 - y1)
            y1 = new_y
        if width is not None:
            width = min(width * scale, c_size[0])
            x2 = x1 + width
            if x2 > cx_off + c_size[0]:
                x2 = cx_off + c_size[0]
                x1 = x2 - width
        if height is not None:
            height = min(height * scale, c_size[1])
            y2 = y1 + height
            if y2 > cy_off + c_size[1]:
                y2 = cy_off + c_size[1]
                y1 = y2 - height
        self.update_rectangle(x1, y1, x2, y2)


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
        size = self._calculate_handle_size(x1, y1, x2, y2)
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
                self.handles[key] = self.img_canvas.create_rectangle(cx - size, cy - size, cx + size, cy + size, fill=self.handle_color, tags='handle')
            elif key in self.handles:
                self.img_canvas.coords(self.handles[key], cx - size, cy - size, cx + size, cy + size)


    def _calculate_handle_size(self, x1, y1, x2, y2):
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


    def _hide_handles_except(self, active_handle):
        for key, handle in self.handles.items():
            if key != active_handle:
                self.img_canvas.itemconfigure(handle, state='hidden')


    def hide_handles(self):
        for handle in self.handles.values():
            self.img_canvas.itemconfigure(handle, state='hidden')


    def show_handles(self):
        for handle in self.handles.values():
            self.img_canvas.itemconfigure(handle, state='normal')


    def _is_handle_clicked(self, event):
        items = self.img_canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for key, handle in self.handles.items():
            if handle in items:
                self.resizing_handle = key
                self._hide_handles_except(key)
                return True
        return False


    def _update_cursor_icon(self, event):
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


    def _is_resizing(self):
        return self.resizing_handle is not None


    def _stop_resizing(self):
        self.resizing_handle = None
        self.show_handles()


    def _resize(self, event):
        x1, y1, x2, y2 = self.img_canvas.coords(self.crop_selection.rect)
        x_off, y_off = self.img_canvas.x_off, self.img_canvas.y_off
        x_max = x_off + self.img_canvas.new_size[0]
        y_max = y_off + self.img_canvas.new_size[1]
        handle_actions = {
            'n': lambda: (x1, max(y_off, min(event.y, y2 - 10)), x2, y2),
            'e': lambda: (x1, y1, min(x_max, max(event.x, x1 + 10)), y2),
            's': lambda: (x1, y1, x2, min(y_max, max(event.y, y1 + 10))),
            'w': lambda: (max(x_off, min(event.x, x2 - 10)), y1, x2, y2),
            'ne': lambda: (x1, max(y_off, min(event.y, y2 - 10)), min(x_max, max(event.x, x1 + 10)), y2),
            'nw': lambda: (max(x_off, min(event.x, x2 - 10)), max(y_off, min(event.y, y2 - 10)), x2, y2),
            'se': lambda: (x1, y1, min(x_max, max(event.x, x1 + 10)), min(y_max, max(event.y, y1 + 10))),
            'sw': lambda: (max(x_off, min(event.x, x2 - 10)), y1, x2, min(y_max, max(event.y, y1 + 10)))
            }
        x1_new, y1_new, x2_new, y2_new = handle_actions[self.resizing_handle]()
        return x1_new, y1_new, x2_new, y2_new


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
        self.x_off = 0
        self.y_off = 0
        self.img_thumbnail = None
        self.resize_after_id = None

        self.bind("<Configure>", self._resize_image)
        self.bind("<Button-3>", lambda event: self.parent.crop_selection.clear_selection())


    def _display_image(self, img_path):
        self.img_path = img_path
        with Image.open(img_path) as img:
            self.original_img = img.copy()
        self.original_img_width, self.original_img_height = self.original_img.size
        self._resize_image(None)


    def _resize_image(self, event):
        if not self.img_path:
            return
        new_width, new_height = self.winfo_width(), self.winfo_height()
        ratio = min(new_width / self.original_img_width, new_height / self.original_img_height)
        new_size = (int(self.original_img_width * ratio), int(self.original_img_height * ratio))
        if new_size != self.new_size:
            self.img_scale_ratio = ratio
            self.new_size = new_size
            self.img_resized = self.original_img.resize(self.new_size, Image.NEAREST)
            self.img_thumbnail = ImageTk.PhotoImage(self.img_resized)
            percent_scale = self.img_scale_ratio * 100
            self.parent.update_imageinfo(int(percent_scale))
        self.delete("all")
        self.x_off = (new_width - self.new_size[0]) // 2
        self.y_off = (new_height - self.new_size[1]) // 2
        self.create_image(self.x_off, self.y_off, anchor="nw", image=self.img_thumbnail)
        self.configure(scrollregion=self.bbox("all"))
        if self.resize_after_id:
            self.after_cancel(self.resize_after_id)
        self.resize_after_id = self.after(250, self.refresh_image)


    def refresh_image(self):
        if not self.img_path:
            return
        self.img_resized = self.original_img.resize(self.new_size, Image.LANCZOS)
        self.img_thumbnail = ImageTk.PhotoImage(self.img_resized)
        self.delete("all")
        self.create_image(self.x_off, self.y_off, anchor="nw", image=self.img_thumbnail)
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

        self.crop_selection = CropSelection(self, self.img_canvas)
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
        self.width_spinbox = ttk.Spinbox(self.size_frame, from_=1, to=9999, width=10, command=self.adjust_selection)
        self.width_spinbox.grid(row=0, column=1, columnspan=2, padx=self.padx, pady=self.pady)
        self.width_spinbox.set(0)
        self.width_spinbox.bind("<Return>", self.adjust_selection)

        # Height
        self.height_label = ttk.Label(self.size_frame, text="H (px):")
        self.height_label.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        self.height_spinbox = ttk.Spinbox(self.size_frame, from_=1, to=9999, width=10, command=self.adjust_selection)
        self.height_spinbox.grid(row=1, column=1, columnspan=2, padx=self.padx, pady=self.pady)
        self.height_spinbox.set(0)
        self.height_spinbox.bind("<Return>", self.adjust_selection)


    def create_position_widgets(self):
        self.position_frame = ttk.LabelFrame(self.control_panel, text="Position")
        self.position_frame.pack(pady=self.pady, padx=self.padx, fill="x")

        # X Position
        self.pos_x_label = ttk.Label(self.position_frame, text="X (px):")
        self.pos_x_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.pos_x_spinbox = ttk.Spinbox(self.position_frame, from_=0, to=9999, width=10, command=self.adjust_selection)
        self.pos_x_spinbox.grid(row=0, column=1, columnspan=2, padx=self.padx, pady=self.pady)
        self.pos_x_spinbox.set(0)
        self.pos_x_spinbox.bind("<Return>", self.adjust_selection)

        # Y Position
        self.pos_y_label = ttk.Label(self.position_frame, text="Y (px):")
        self.pos_y_label.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        self.pos_y_spinbox = ttk.Spinbox(self.position_frame, from_=0, to=9999, width=10, command=self.adjust_selection)
        self.pos_y_spinbox.grid(row=1, column=1, columnspan=2, padx=self.padx, pady=self.pady)
        self.pos_y_spinbox.set(0)
        self.pos_y_spinbox.bind("<Return>", self.adjust_selection)


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
        self.img_canvas._display_image(img_path)
        self.crop_selection.clear_selection()
        original_width, original_height = self.img_canvas.original_img.size
        displayed_width = self.img_canvas.winfo_width()
        percent_scale = int((displayed_width / original_width) * 100)
        self.update_imageinfo(percent_scale)
        self.width_spinbox.config(to=self.img_canvas.original_img_width)
        self.height_spinbox.config(to=self.img_canvas.original_img_height)


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
            self.root.after(100, self.crop_selection.clear_selection)


    def adjust_selection(self, event=None):
        if event is None:
            widget = self.root.focus_get()
        else:
            widget = event.widget
        try:
            value = int(widget.get())
        except (AttributeError, ValueError):
            return
        spinbox_map = {
            self.width_spinbox: 'width',
            self.height_spinbox: 'height',
            self.pos_x_spinbox: 'new_x',
            self.pos_y_spinbox: 'new_y'
            }
        kwargs = {spinbox_map[widget]: value}
        self.crop_selection.set_selection_dimensions(**kwargs)


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
            x, y, = x1, y1
            height, width = (y2 - y1), (x2 - x1)
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
