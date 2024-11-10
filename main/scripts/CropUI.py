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
from PIL import Image, ImageTk, ImageSequence
from TkToolTip.TkToolTip import TkToolTip as ToolTip


#endregion
#########################################################################################################
#region CLS: CropSelection


class CropSelection:
    def __init__(self, parent, img_canvas):
        self.parent = parent
        self.img_canvas = img_canvas

        # Selection variables
        self.rect = None
        self.coords = None
        self.start_x = None
        self.start_y = None

        # Overlay variables
        self.overlay = None
        self.overlay_enabled = tk.BooleanVar(value=True)
        self.highlight_rect = None

        # Variables for moving and resizing
        self.moving_rectangle = False
        self.move_offset_x = 0
        self.move_offset_y = 0
        self.rect_width = 0
        self.rect_height = 0

        # Initialize handles manager
        self.handles_manager = CropSelHandles(self, img_canvas)

        # Bind events
        self.img_canvas.bind("<ButtonPress-1>", self._on_button_press)
        self.img_canvas.bind("<B1-Motion>", self._on_move_press, add="+")
        self.img_canvas.bind("<ButtonRelease-1>", self._on_button_release, add="+")
        self.img_canvas.bind("<Motion>", self.handles_manager._update_cursor_icon)
        self.img_canvas.bind("<Double-1>", self._on_double_click)
        # Bind mouse wheel events
        self.img_canvas.bind("<MouseWheel>", self._on_mousewheel, add="+")


# --------------------------------------
# Events
# --------------------------------------
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
        if not self.parent.fixed_sel_toggle_var.get():
            self._start_selection(event, x_off, y_off, x_max, y_max)
            return
        mode = self.parent.fixed_sel_mode_var.get()
        try:
            if mode == "Size":
                value = self.parent.fixed_sel_entry_var.get()
                if "x" in value:
                    value = value.split("x")
                else:
                    value = value.split(",")
                width = int(float(value[0].strip()) * self.img_canvas.img_scale_ratio)
                height = int(float(value[1].strip()) * self.img_canvas.img_scale_ratio)
                width = min(width, x_max - x_off)
                height = min(height, y_max - y_off)
                x1 = max(x_off, min(event.x - width / 2, x_max - width))
                y1 = max(y_off, min(event.y - height / 2, y_max - height))
                x2 = x1 + width
                y2 = y1 + height
            elif mode == "Width":
                width = int(float(self.parent.fixed_sel_entry_var.get()) * self.img_canvas.img_scale_ratio)
                width = min(width, x_max - x_off)
                x1 = max(x_off, min(event.x - width / 2, x_max - width))
                x2 = x1 + width
                y1 = y2 = event.y
                self.start_x, self.start_y = x1, y1
            elif mode == "Height":
                height = int(float(self.parent.fixed_sel_entry_var.get()) * self.img_canvas.img_scale_ratio)
                height = min(height, y_max - y_off)
                y1 = max(y_off, min(event.y - height / 2, y_max - height))
                y2 = y1 + height
                x1 = x2 = event.x
                self.start_x, self.start_y = x1, y1
            else:  # Aspect Ratio mode
                if self.parent.auto_aspect_var.get():
                    self.parent.determine_best_aspect_ratio()
                self._start_selection(event, x_off, y_off, x_max, y_max)
                return
            self.rect = self.img_canvas.create_rectangle(x1, y1, x2, y2, outline='white', tags='rect')
            self.update_overlay()
            if mode == "Size":
                self._start_moving_rect(event, x1, y1, x2, y2)
            return
        except (ValueError, IndexError):
            pass


    def _on_move_press(self, event):
        if not self.img_canvas.img_path or not self.rect:
            return
        x_off, y_off = self.img_canvas.x_off, self.img_canvas.y_off
        x_max = x_off + self.img_canvas.new_size[0]
        y_max = y_off + self.img_canvas.new_size[1]
        if self.handles_manager._is_resizing():
            x1, y1, x2, y2 = self.handles_manager._resize(event)
            self.parent.update_widget_values(resize=True)
        elif self.moving_rectangle:
            x1, y1, x2, y2 = self._calculate_moving_rect(event, x_off, y_off, x_max, y_max)
        else:
            x1, y1, x2, y2 = self._calculate_selection_rect(event, x_off, y_off, x_max, y_max)
            self.parent.update_widget_values(resize=True)
        self.update_rect(x1, y1, x2, y2)


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
            self.update_overlay()
        self._calculate_image_selection_coords(x1, y1, x2, y2)
        self.handles_manager.show_handles()
        self.parent.update_widget_values()
        self.handles_manager._hide_handles_based_on_mode()


    def _on_double_click(self, event):
        if self.rect:
            self.clear_selection()
            self.parent.update_widget_values()
            return
        if not self.img_canvas.img_path:
            return
        img_width, img_height = self.img_canvas.original_img_width, self.img_canvas.original_img_height
        half_width, half_height = img_width // 2, img_height // 2
        center_x, center_y = img_width // 2, img_height // 2
        x1, y1 = center_x - half_width // 2, center_y - half_height // 2
        x2, y2 = center_x + half_width // 2, center_y + half_height // 2
        scale = self.img_canvas.img_scale_ratio
        x1_scaled = self.img_canvas.x_off + int(x1 * scale)
        y1_scaled = self.img_canvas.y_off + int(y1 * scale)
        x2_scaled = self.img_canvas.x_off + int(x2 * scale)
        y2_scaled = self.img_canvas.y_off + int(y2 * scale)
        if self.rect:
            self.img_canvas.coords(self.rect, x1_scaled, y1_scaled, x2_scaled, y2_scaled)
        else:
            self.rect = self.img_canvas.create_rectangle(x1_scaled, y1_scaled, x2_scaled, y2_scaled, outline='white', tags='rect')
        self.coords = (x1, y1, x2, y2)
        self.rect_width = x2_scaled - x1_scaled
        self.rect_height = y2_scaled - y1_scaled
        self.handles_manager.update_handles()
        self.update_overlay()


    def _on_mousewheel(self, event):
        if not self.rect:
            return
        if event.delta:
            delta = event.delta
        else:
            return
        shift_pressed = event.state & 0x0001
        ctrl_pressed = event.state & 0x0004
        mode = self.parent.fixed_sel_mode_var.get()
        step = 10 if delta > 0 else -10

        if self.parent.fixed_sel_toggle_var.get():
            if mode == "Aspect Ratio":
                # Resize both width and height
                self._resize_selection_with_mousewheel(True, True, step)
            elif mode == "Width":
                # Only resize height
                self._resize_selection_with_mousewheel(False, True, step)
            elif mode == "Height":
                # Only resize width
                self._resize_selection_with_mousewheel(True, False, step)
            elif mode == "Size":
                # Do not allow resizing
                return
        else:
            if shift_pressed and ctrl_pressed: # Resize width and height
                self._resize_selection_with_mousewheel(True, True, step)
            elif shift_pressed: # Resize width
                self._resize_selection_with_mousewheel(True, False, step)
            else: # Resize height
                self._resize_selection_with_mousewheel(False, True, step)


# --------------------------------------
# Event Helpers
# --------------------------------------
    def _start_moving_rect(self, event, x1, y1, x2, y2):
        self.moving_rectangle = True
        if self.parent.fixed_sel_toggle_var.get() and self.parent.fixed_sel_mode_var.get() == "Size":
            self.move_offset_x = (x2 - x1) / 2
            self.move_offset_y = (y2 - y1) / 2
        else:
            self.move_offset_x = event.x - x1
            self.move_offset_y = event.y - y1
        self.rect_width = x2 - x1
        self.rect_height = y2 - y1
        self.handles_manager.hide_handles()


    def _start_selection(self, event, x_off, y_off, x_max, y_max):
        self.start_x = max(min(event.x, x_max), x_off)
        self.start_y = max(min(event.y, y_max), y_off)
        if self.parent.expand_center_toggle_var.get():
            self.center_x = self.start_x
            self.center_y = self.start_y
        if self.parent.fixed_sel_toggle_var.get() and self.parent.fixed_sel_mode_var.get() in ["Aspect Ratio", "Width", "Height"]:
            if self.parent.expand_center_toggle_var.get():
                self.center_x = (x_off + x_max) / 2
                self.center_y = (y_off + y_max) / 2
                self.start_x = self.center_x
                self.start_y = self.center_y
            else:
                self.start_x = max(min(event.x, x_max), x_off)
                self.start_y = max(min(event.y, y_max), y_off)
        self.rect = self.img_canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='white', tags='rect')


    def _resize_selection_with_mousewheel(self, delta_width, delta_height, step):
        x1, y1, x2, y2 = self.img_canvas.coords(self.rect)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        new_width = (x2 - x1) + (step if delta_width else 0)
        new_height = (y2 - y1) + (step if delta_height else 0)
        new_width = max(new_width, 10)
        new_height = max(new_height, 10)
        x1_new = cx - new_width / 2
        x2_new = cx + new_width / 2
        y1_new = cy - new_height / 2
        y2_new = cy + new_height / 2
        x_off, y_off = self.img_canvas.x_off, self.img_canvas.y_off
        x_max = x_off + self.img_canvas.new_size[0]
        y_max = y_off + self.img_canvas.new_size[1]
        x1_new = max(x_off, x1_new)
        y1_new = max(y_off, y1_new)
        x2_new = min(x_max, x2_new)
        y2_new = min(y_max, y2_new)
        self.update_rect(x1_new, y1_new, x2_new, y2_new)
        self.handles_manager.update_handles()
        self.parent.update_widget_values(resize=True)


# --------------------------------------
# Rectangle Calculations
# --------------------------------------
    def _calculate_image_selection_coords(self, x1, y1, x2, y2):
        # Retrieve canvas offsets and scale ratio
        cx_off, cy_off = self.img_canvas.x_off, self.img_canvas.y_off
        scale_ratio = self.img_canvas.img_scale_ratio
        c_ns = self.img_canvas.new_size
        # Clamp coordinates within image boundaries
        x1, x2 = sorted([
            max(cx_off, min(x1, cx_off + c_ns[0])),
            max(cx_off, min(x2, cx_off + c_ns[0]))
            ])
        y1, y2 = sorted([
            max(cy_off, min(y1, cy_off + c_ns[1])),
            max(cy_off, min(y2, cy_off + c_ns[1]))
            ])
        # Adjust coordinates relative to image
        x1_adj, y1_adj = x1 - cx_off, y1 - cy_off
        x2_adj, y2_adj = x2 - cx_off, y2 - cy_off
        # Scale back to original image coordinates
        x1_orig = int(x1_adj / scale_ratio)
        y1_orig = int(y1_adj / scale_ratio)
        x2_orig = int(x2_adj / scale_ratio)
        y2_orig = int(y2_adj / scale_ratio)
        # Get original image dimensions
        orig_img_width = self.img_canvas.original_img_width
        orig_img_height = self.img_canvas.original_img_height
        # Clamp to original image boundaries
        x1_orig, x2_orig = sorted([
            max(0, min(orig_img_width, x1_orig)),
            max(0, min(orig_img_width, x2_orig))
            ])
        y1_orig, y2_orig = sorted([
            max(0, min(orig_img_height, y1_orig)),
            max(0, min(orig_img_height, y2_orig))
            ])
        # Update coords if valid rectangle
        self.coords = (x1_orig, y1_orig, x2_orig, y2_orig) if x1_orig != x2_orig and y1_orig != y2_orig else None


    def _calculate_moving_rect(self, event, x_off, y_off, x_max, y_max):
        x1 = max(x_off, min(event.x - self.move_offset_x, x_max - self.rect_width))
        y1 = max(y_off, min(event.y - self.move_offset_y, y_max - self.rect_height))
        x2 = x1 + self.rect_width
        y2 = y1 + self.rect_height
        return x1, y1, x2, y2


    def _calculate_selection_rect(self, event, x_off, y_off, x_max, y_max):
        curX = max(min(event.x, x_max), x_off)
        curY = max(min(event.y, y_max), y_off)
        if self.parent.expand_center_toggle_var.get():
            if not hasattr(self, 'center_x') or not hasattr(self, 'center_y'):
                self.center_x = (x_off + x_max) / 2
                self.center_y = (y_off + y_max) / 2
            x1 = max(x_off, min(2 * self.center_x - curX, x_max))
            y1 = max(y_off, min(2 * self.center_y - curY, y_max))
            x2 = curX
            y2 = curY
        else:
            x1, y1 = self.start_x, self.start_y
            x2, y2 = curX, curY
        if self.parent.fixed_sel_toggle_var.get():
            x1, y1, x2, y2 = self._apply_fixed_selection(x1, y1, x2, y2, x_off, y_off, x_max, y_max)
        return x1, y1, x2, y2


# --------------------------------------
# Updates
# --------------------------------------
    def update_rect(self, x1, y1, x2, y2):
        if None in (x1, y1, x2, y2):
            return
        self.img_canvas.coords(self.rect, x1, y1, x2, y2)
        self.rect_width = x2 - x1
        self.rect_height = y2 - y1
        self._calculate_image_selection_coords(x1, y1, x2, y2)
        self.handles_manager.update_handles()
        self.update_overlay()


    def update_overlay(self):
        if not self.overlay_enabled.get():
            if self.highlight_rect:
                self.img_canvas.delete(self.highlight_rect)
            if self.rect:
                x1, y1, x2, y2 = self.img_canvas.coords(self.rect)
                self.highlight_rect = self.img_canvas.create_rectangle(x1-1, y1-1, x2+1, y2+1, outline='black', tags='highlight')
            return
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


    def clear_selection(self):
        if self.rect:
            self.img_canvas.delete(self.rect)
        if self.overlay:
            self.img_canvas.delete("overlay")
        if self.highlight_rect:
            self.img_canvas.delete(self.highlight_rect)
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


    def redraw_rect(self):
        if self.rect and self.coords:
            scale_ratio = self.img_canvas.img_scale_ratio
            x_off = self.img_canvas.x_off
            y_off = self.img_canvas.y_off
            x1 = self.coords[0] * scale_ratio + x_off
            y1 = self.coords[1] * scale_ratio + y_off
            x2 = self.coords[2] * scale_ratio + x_off
            y2 = self.coords[3] * scale_ratio + y_off
            self.rect = self.img_canvas.create_rectangle(x1, y1, x2, y2, outline='white', tags='rect')
            self.handles_manager.update_handles(create=True)
            self.update_overlay()


# --------------------------------------
# Fixed Selection
# --------------------------------------
    def _apply_fixed_selection(self, x1, y1, x2, y2, x_off, y_off, x_max, y_max):
        scale = self.img_canvas.img_scale_ratio
        mode = self.parent.fixed_sel_mode_var.get()
        value = self.parent.fixed_sel_entry_var.get()
        if mode == "Size":
            if "x" in value:
                value = value.split("x")
            else:
                value = value.split(",")
        elif mode == "Aspect Ratio":
            return self._apply_fixed_aspect_ratio(x1, y1, x2, y2, x_off, y_off, x_max, y_max, value)
        else:
            try:
                value = float(value)
            except ValueError:
                return x1, y1, x2, y2
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        if width == 0 or height == 0:
            width, height = 1, 1
        if mode == "Width":
            try:
                width = int(value * scale)
            except ValueError:
                return x1, y1, x2, y2
            if width == 0:
                return x1, y1, x2, y2
            height = width / (width / height)
        elif mode == "Height":
            try:
                height = int(value * scale)
            except ValueError:
                return x1, y1, x2, y2
            if height == 0:
                return x1, y1, x2, y2
            width = height * (width / height)
        elif mode == "Size":
            try:
                width_str, height_str = value
                width = int(width_str.strip()) * scale
                height = int(height_str.strip()) * scale
            except (ValueError, IndexError):
                return x1, y1, x2, y2
            if width == 0 or height == 0:
                return x1, y1, x2, y2
        if self.parent.expand_center_toggle_var.get() and self.parent.fixed_sel_toggle_var.get() and mode in ["Aspect Ratio", "Width", "Height"]:
            x1 = self.center_x - width / 2
            y1 = self.center_y - height / 2
            x2 = self.center_x + width / 2
            y2 = self.center_y + height / 2
        else:
            x2 = x1 + width if x2 >= x1 else x1 - width
            y2 = y1 + height if y2 >= y1 else y1 - height
        x2 = min(max(x2, x_off), x_max)
        y2 = min(max(y2, y_off), y_max)
        return x1, y1, x2, y2


    def _apply_fixed_aspect_ratio(self, x1, y1, x2, y2, x_off, y_off, x_max, y_max, value):
        try:
            if ":" in value:
                width_str, height_str = value.split(":")
                width_ratio = float(width_str.strip())
                height_ratio = float(height_str.strip())
                if width_ratio == 0 or height_ratio == 0:
                    return x1, y1, x2, y2
                ratio = width_ratio / height_ratio
            else:
                ratio = float(value)
            if ratio == 0:
                return x1, y1, x2, y2
        except (ValueError, ZeroDivisionError):
            return x1, y1, x2, y2
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        if self.parent.expand_center_toggle_var.get():
            if x2 != x1 and y2 != y1:  # Diagonal
                width = abs(x2 - x1)
                height = width / ratio
            elif x2 != x1:  # Horizontal
                width = abs(x2 - x1)
                height = width / ratio
            elif y2 != y1:  # Vertical
                height = abs(y2 - y1)
                width = height * ratio
            max_possible_width = min(2 * (self.center_x - x_off), 2 * (x_max - self.center_x))
            max_possible_height = min(2 * (self.center_y - y_off), 2 * (y_max - self.center_y))
            if width > max_possible_width:
                width = max_possible_width
                height = width / ratio
            if height > max_possible_height:
                height = max_possible_height
                width = height * ratio
            x1 = self.center_x - width / 2
            y1 = self.center_y - height / 2
            x2 = self.center_x + width / 2
            y2 = self.center_y + height / 2
        else:
            if x2 != x1 and y2 != y1:  # Diagonal
                width = abs(x2 - x1)
                height = width / ratio
                if y1 + height > y_max:
                    height = y_max - y1
                    width = height * ratio
                elif y1 + height < y_off:
                    height = y1 - y_off
                    width = height * ratio
                y2 = y1 + height if y2 >= y1 else y1 - height
                x2 = x1 + width if x2 >= x1 else x1 - width
            elif x2 != x1:  # Horizontal
                width = abs(x2 - x1)
                height = width / ratio
                if y1 + height > y_max:
                    height = y_max - y1
                    width = height * ratio
                y2 = y1 + height if y2 >= y1 else y1 - height
            elif y2 != y1:  # Vertical
                height = abs(y2 - y1)
                width = height * ratio
                if x1 + width > x_max:
                    width = x_max - x1
                    height = width / ratio
                x2 = x1 + width if x2 >= x1 else x1 - width
        # Final bounds check
        x1 = max(x_off, min(x_max, x1))
        x2 = max(x_off, min(x_max, x2))
        y1 = max(y_off, min(y_max, y1))
        y2 = max(y_off, min(y_max, y2))
        return x1, y1, x2, y2


# --------------------------------------
# Manual Adjustment
# --------------------------------------
    def set_selection_dimensions(self, width=None, height=None, new_x=None, new_y=None, original_value=None):
        if not self.rect:
            return
        x1, y1, x2, y2 = self.img_canvas.coords(self.rect)
        cx_off, cy_off = self.img_canvas.x_off, self.img_canvas.y_off
        c_size = self.img_canvas.new_size
        if new_x is not None:
            new_x += cx_off
            x2 = new_x + (x2 - x1)
            x1 = new_x
        if new_y is not None:
            new_y += cy_off
            y2 = new_y + (y2 - y1)
            y1 = new_y
        if self.parent.expand_center_toggle_var.get():
            x1, y1, x2, y2 = self._calculate_center_expansion(x1, y1, x2, y2, width, height, c_size)
        else:
            if width is not None:
                width = int(min(width, c_size[0]))
                x2 = x1 + width
            if height is not None:
                height = int(min(height, c_size[1]))
                y2 = y1 + height
        x1, y1, x2, y2 = self._clamp_coords_to_image(x1, y1, x2, y2, cx_off, cy_off, c_size)
        self.update_rect(round(x1), round(y1), round(x2), round(y2))


    def _calculate_center_expansion(self, x1, y1, x2, y2, width, height, c_size):
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        if width is not None:
            width = int(min(width, c_size[0]))
            x1 = center_x - width / 2
            x2 = center_x + width / 2
        if height is not None:
            height = int(min(height, c_size[1]))
            y1 = center_y - height / 2
            y2 = center_y + height / 2
        return x1, y1, x2, y2


    def _clamp_coords_to_image(self, x1, y1, x2, y2, cx_off, cy_off, c_size):
        if x1 < cx_off:
            x2 += cx_off - x1
            x1 = cx_off
        if y1 < cy_off:
            y2 += cy_off - y1
            y1 = cy_off
        if x2 > cx_off + c_size[0]:
            x1 -= x2 - (cx_off + c_size[0])
            x2 = cx_off + c_size[0]
        if y2 > cy_off + c_size[1]:
            y1 -= y2 - (cy_off + c_size[1])
            y2 = cy_off + c_size[1]
        return x1, y1, x2, y2


#endregion
#########################################################################################################
#region CLS: CropSelHandles


class CropSelHandles:
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


# --------------------------------------
# Handle Updates
# --------------------------------------
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


    def _hide_handles_based_on_mode(self):
        if self.crop_selection.parent.fixed_sel_toggle_var.get():
            mode = self.crop_selection.parent.fixed_sel_mode_var.get()
            hide_handles_dict = {
                "Aspect Ratio": ["n", "e", "s", "w"],
                "Width": ["e", "w", "ne", "nw", "se", "sw"],
                "Height": ["n", "s", "ne", "nw", "se", "sw"]
                }
            hide_handles = hide_handles_dict.get(mode, [])
            for key, handle in self.handles.items():
                if key in hide_handles:
                    self.img_canvas.itemconfigure(handle, state='hidden')
                else:
                    self.img_canvas.itemconfigure(handle, state='normal')


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


# --------------------------------------
# Handle Visibility
# --------------------------------------
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


    def delete_handles(self):
        for handle in self.handles.values():
            self.img_canvas.delete(handle)
        self.handles.clear()
        self.resizing_handle = None


# --------------------------------------
# Handle Events
# --------------------------------------
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


# --------------------------------------
# Handle Resizing
# --------------------------------------
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
        expand_from_center = self.crop_selection.parent.expand_center_toggle_var.get()
        handle = self.resizing_handle
        m_size = 10
        if self.crop_selection.parent.fixed_sel_toggle_var.get() and self.crop_selection.parent.fixed_sel_mode_var.get() == "Aspect Ratio":
            return self._resize_with_aspect_ratio(event, x1, y1, x2, y2, x_off, y_off, x_max, y_max, expand_from_center, m_size)
        if expand_from_center:
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            dx = max(m_size / 2, abs(event.x - cx))
            dy = max(m_size / 2, abs(event.y - cy))
            x1_new, y1_new, x2_new, y2_new = self._calculate_new_coords(x1, y1, x2, y2, cx, cy, dx, dy, x_off, y_off, x_max, y_max)
        else:
            x1_new, y1_new, x2_new, y2_new = x1, y1, x2, y2
            adjustments = {
                'n': lambda y: max(y_off, min(y, y2 - m_size)),
                's': lambda y: min(y_max, max(y, y1 + m_size)),
                'w': lambda x: max(x_off, min(x, x2 - m_size)),
                'e': lambda x: min(x_max, max(x, x1 + m_size))
                }
            for direction in handle:
                if direction in adjustments:
                    if direction in ['n', 's']:
                        y = adjustments[direction](event.y)
                        y1_new if direction == 'n' else y2_new
                        y1_new, y2_new = (y, y2_new) if direction == 'n' else (y1_new, y)
                    else:
                        x = adjustments[direction](event.x)
                        x1_new, x2_new = (x, x2_new) if direction == 'w' else (x1_new, x)
        return self._ensure_coords_in_bounds(x1_new, y1_new, x2_new, y2_new, x_off, y_off, x_max, y_max)


    def _resize_with_aspect_ratio(self, event, x1, y1, x2, y2, x_off, y_off, x_max, y_max, expand_from_center, m_size):
        handle = self.resizing_handle
        try:
            value = self.crop_selection.parent.fixed_sel_entry_var.get()
            if ':' in value:
                width_ratio, height_ratio = map(float, value.split(':'))
                target_ratio = width_ratio / height_ratio
            else:
                target_ratio = float(value)
        except (ValueError, ZeroDivisionError):
            target_ratio = (x2 - x1) / (y2 - y1) if y2 != y1 else 1
        orig_coords = (x1, y1, x2, y2)
        if expand_from_center:
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = abs(event.x - cx), abs(event.y - cy)
            if 'n' in handle or 's' in handle:
                dx = dy * target_ratio
            else:
                dy = dx / target_ratio
            x1_new, y1_new, x2_new, y2_new = self._calculate_new_coords(x1, y1, x2, y2, cx, cy, dx, dy, x_off, y_off, x_max, y_max)
        else:
            if 'n' in handle or 's' in handle:
                new_height = abs(y2 - event.y) if 'n' in handle else abs(event.y - y1)
                new_width = new_height * target_ratio
                y1_new = max(y_off, min(event.y, y2 - m_size)) if 'n' in handle else y1
                y2_new = y2 if 'n' in handle else min(y_max, max(event.y, y1 + m_size))
                x1_new = (x1 + x2 - new_width) / 2
                x2_new = x1_new + new_width
            else:
                new_width = abs(x2 - event.x) if 'w' in handle else abs(event.x - x1)
                new_height = new_width / target_ratio
                x1_new = max(x_off, min(event.x, x2 - m_size)) if 'w' in handle else x1
                x2_new = x2 if 'w' in handle else min(x_max, max(event.x, x1 + m_size))
                y1_new = (y1 + y2 - new_height) / 2
                y2_new = y1_new + new_height
        x1_new, y1_new, x2_new, y2_new = self._ensure_coords_in_bounds(x1_new, y1_new, x2_new, y2_new, x_off, y_off, x_max, y_max)
        new_width, new_height = x2_new - x1_new, y2_new - y1_new
        if new_height != 0:
            ratio_error = abs((new_width / new_height) - target_ratio) / target_ratio
            if ratio_error > 0.01:
                return orig_coords
        return x1_new, y1_new, x2_new, y2_new


    def _calculate_new_coords(self, x1, y1, x2, y2, cx, cy, dx, dy, x_off, y_off, x_max, y_max):
        handle = self.resizing_handle
        x1_new = max(x_off, cx - dx) if 'w' in handle or 'e' in handle else x1
        y1_new = max(y_off, cy - dy) if 'n' in handle or 's' in handle else y1
        x2_new = min(x_max, cx + dx) if 'e' in handle or 'w' in handle else x2
        y2_new = min(y_max, cy + dy) if 's' in handle or 'n' in handle else y2
        return x1_new, y1_new, x2_new, y2_new


    def _ensure_coords_in_bounds(self, x1, y1, x2, y2, x_off, y_off, x_max, y_max):
        x1 = max(x_off, min(x1, x_max))
        x2 = max(x_off, min(x2, x_max))
        y1 = max(y_off, min(y1, y_max))
        y2 = max(y_off, min(y2, y_max))
        return x1, y1, x2, y2


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
        self.img_scale_ratio = 1.0
        self.new_size = (0, 0)
        self.x_off = 0
        self.y_off = 0
        self.img_thumbnail = None
        self.resize_after_id = None
        self._resize_image(None)


    def _resize_image(self, event=None):
        if not self.img_path:
            return
        new_width, new_height = self.winfo_width(), self.winfo_height()
        ratio = min(new_width / self.original_img_width, new_height / self.original_img_height)
        new_size = (int(self.original_img_width * ratio), int(self.original_img_height * ratio))
        if new_size != self.new_size and new_size[0] > 0 and new_size[1] > 0:
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
        if hasattr(self, 'crop_selection'):
            self.crop_selection.redraw_rect()


#endregion
#########################################################################################################
#region CLS: CropInterface


class CropInterface:
    def __init__(self):
        # Primary variables
        self.parent = None
        self.root = None
        self.version = None
        self.menu = None
        self.image_path = None

        # Image Variables
        self.image_files = []
        self.image_info_cache = {}
        self.selection_aspect = 0
        self.current_index = 0

        # UI
        self.pady = 5
        self.padx = 10
        self.padxl = (5,2)
        self.padxr = (2,5)

        # Settings
        self.overlay_var = tk.BooleanVar(value=True)
        self.after_crop_var = tk.StringVar(value="Save & Close")
        self.expand_center_toggle_var = tk.BooleanVar(value=False)

        # Fixed Selection
        self.fixed_sel_toggle_var = tk.BooleanVar(value=False)
        self.fixed_sel_entry_var = tk.StringVar(value="1:1")
        self.fixed_sel_mode_var = tk.StringVar(value="Aspect Ratio")
        self.auto_aspect_var = tk.BooleanVar(value=False)
        self.auto_entry_var = tk.StringVar(value="1:1, 5:4, 4:5, 4:3, 3:4, 3:2, 2:3, 16:9, 9:16, 2:1, 1:2")


# --------------------------------------
# UI
# --------------------------------------
    def setup_window(self, parent, root, version, menu, path=None, image_paths=None):
        self.parent = parent
        self.root = root
        self.version = version
        self.menu = menu
        if os.path.exists(path):
            self.image_path = path
        self.image_files = image_paths
        self.root.minsize(530, 370)
        self.root.title(f"{self.version} - img-txt Viewer - Crop Image")
        self.menu.entryconfig("Crop...", command=self.close_crop_ui)
        self.create_main_frame()
        self.setup_top_frame()
        self.create_image_ui()
        self.create_control_panel()
        self.crop_selection = CropSelection(self, self.img_canvas)
        self.img_canvas.crop_selection = self.crop_selection
        if path:
            self.path_entry.insert(0, path)
            self.current_index = self.parent.current_index
            self.display_image(self.image_files[self.current_index])
        self.root.bind("<Configure>", lambda event: print(f"\rWindow size (W,H): {event.width},{event.height}    ", end='') if event.widget == self.root else None, add="+")


    def create_main_frame(self):
        self.parent.hide_primary_paned_window()
        self.crop_ui_frame = tk.Frame(self.root)
        self.crop_ui_frame.grid(row=0, column=0, sticky="nsew")
        self.crop_ui_frame.grid_rowconfigure(0, weight=0)
        self.crop_ui_frame.grid_rowconfigure(1, weight=0)
        self.crop_ui_frame.grid_rowconfigure(2, weight=1)
        self.crop_ui_frame.grid_columnconfigure(0, weight=1)
        self.crop_ui_frame.grid_columnconfigure(1, weight=0)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)


    def setup_top_frame(self):
        top_frame = tk.Frame(self.crop_ui_frame)
        top_frame.grid(row=0, column=0, columnspan=99, padx=self.padx, pady=(5,0), sticky="nsew")
        top_frame.grid_columnconfigure(3, weight=1)
        # Close
        ttk.Button(top_frame, text="<---Close", width=15, command=self.close_crop_ui).grid(row=0, column=0, sticky="w")
        # Crop Info
        self.crop_info_label = ttk.Label(top_frame, text="Crop to: 0x0 (0:0)", anchor="w")
        self.crop_info_label.grid(row=0, column=2, padx=self.padx, sticky="ew")
        # Directory
        directory_frame = tk.Frame(top_frame)
        directory_frame.grid(row=0, column=3, padx=(self.padx, 0), sticky="ew")
        self.path_entry = ttk.Entry(directory_frame)
        self.path_entry.pack(side="left", fill="x", expand=True)
        self.parent.bind_entry_functions(self.path_entry)
        browse_button = ttk.Button(directory_frame, text="Browse...", width=9, command=self.open_directory_dialog)
        browse_button.pack(side="left")
        open_button = ttk.Button(directory_frame, text="Open", width=9, command=lambda: self.parent.open_directory(self.path_entry.get()))
        open_button.pack(side="left")
        # Help
        help_button = ttk.Button(top_frame, text="?", width=2, command=self.show_help)
        help_button.grid(row=0, column=4, padx=2, sticky="e")
        ToolTip.create(help_button, "Show/Hide Help", 50, 6, 12)


    def create_image_ui(self):
        # Image Stats
        stats_frame = tk.Frame(self.crop_ui_frame)
        stats_frame.grid(row=1, column=0, sticky="ew", pady=self.pady)
        self.img_stats_label = ttk.Label(stats_frame)
        self.img_stats_label.pack(fill="x")
        # Image Canvas
        canvas_frame = tk.Frame(self.crop_ui_frame)
        canvas_frame.grid(row=2, column=0, sticky="nsew")
        self.img_canvas = ImageCanvas(self, canvas_frame)
        self.img_canvas.pack(fill="both", expand=True)


    def create_control_panel(self):
        self.control_panel = tk.Frame(self.crop_ui_frame, relief="sunken", borderwidth=1)
        self.control_panel.grid(row=1, column=1, sticky="nsew", rowspan=2, padx=self.padx, pady=self.pady)
        self.create_nav_and_crop_widgets()
        self.spinbox_frame = tk.Frame(self.control_panel)
        self.spinbox_frame.pack(pady=self.pady, padx=self.padx, fill="x")
        self.create_size_widgets()
        self.create_position_widgets()
        self.create_selection_widgets()
        self.create_option_widgets()
        self.create_transform_widgets()


    def create_nav_and_crop_widgets(self):
        top_frame = tk.Frame(self.control_panel)
        top_frame.pack(pady=self.pady, padx=self.padx, fill="x")
        # After Crop
        after_crop_menu = ttk.Menubutton(top_frame, text="After Crop")
        after_crop_menu.pack(side="left", padx=(2,0), pady=self.pady, fill="x", expand=True)
        after_crop_menu.menu = tk.Menu(after_crop_menu, tearoff=0)
        after_crop_menu["menu"] = after_crop_menu.menu
        after_crop_menu.menu.add_radiobutton(label="Save & Close", variable=self.after_crop_var, value="Save & Close")
        after_crop_menu.menu.add_radiobutton(label="Save & Next", variable=self.after_crop_var, value="Save & Next")
        after_crop_menu.menu.add_radiobutton(label="Save As...", variable=self.after_crop_var, value="Save As...")
        after_crop_menu.menu.add_radiobutton(label="Save", variable=self.after_crop_var, value="Save")
        after_crop_menu.menu.add_separator()
        after_crop_menu.menu.add_radiobutton(label="Overwrite", variable=self.after_crop_var, value="Overwrite")
        # Index
        index_frame = tk.Frame(top_frame)
        index_frame.pack(side="left", padx=5, pady=self.pady, fill="x", expand=True)
        self.image_index_spinbox = ttk.Spinbox(index_frame, from_=1, to=len(self.image_files), width=5, command=self.image_index_changed)
        self.image_index_spinbox.pack(side="left", fill="x", expand=True)
        self.image_index_spinbox.bind("<Return>", self.image_index_changed)
        self.parent.bind_entry_functions(self.image_index_spinbox)
        ttk.Label(index_frame, text=f"of {len(self.image_files)}").pack(side="left")
        # Nav Buttons
        nav_button_frame = tk.Frame(self.control_panel)
        nav_button_frame.pack(pady=self.pady, padx=self.padx, fill="x")
        self.prev_button = ttk.Button(nav_button_frame, text="<---Previous", command=self.show_previous_image)
        self.prev_button.pack(side="left", fill="x", expand=True)
        self.next_button = ttk.Button(nav_button_frame, text="Next--->", command=self.show_next_image)
        self.next_button.pack(side="left", fill="x", expand=True)
        # Crop Button
        self.crop_button = ttk.Button(self.control_panel, text="Crop Selection", command=self.crop_image)
        self.crop_button.pack(fill="x", pady=self.pady, padx=self.padx)


    def create_size_widgets(self):
        size_frame = ttk.LabelFrame(self.spinbox_frame, text="Size")
        size_frame.pack(side="left", fill="x", padx=(0,2), expand=True)
        size_frame.columnconfigure(1, weight=1)
        # Width
        self.width_label = ttk.Label(size_frame, text="W (px):")
        self.width_label.grid(row=0, column=0, padx=self.padxl, pady=self.pady, sticky='w')
        ToolTip(self.width_label, "Width of selection in pixels", 200, 6, 12)
        self.width_spinbox = ttk.Spinbox(size_frame, from_=1, to=9999, width=7, command=self.adjust_selection)
        self.width_spinbox.grid(row=0, column=1, padx=self.padxr, pady=self.pady, sticky='e')
        self.width_spinbox.set(0)
        self.width_spinbox.bind("<Return>", self.adjust_selection)
        self.width_spinbox.bind("<MouseWheel>", self.focus_widget_and_adjust_selection)
        self.parent.bind_entry_functions(self.width_spinbox)
        # Height
        self.height_label = ttk.Label(size_frame, text="H (px):")
        self.height_label.grid(row=1, column=0, padx=self.padxl, pady=self.pady, sticky='w')
        ToolTip(self.height_label, "Height of selection in pixels", 200, 6, 12)
        self.height_spinbox = ttk.Spinbox(size_frame, from_=1, to=9999, width=7, command=self.adjust_selection)
        self.height_spinbox.grid(row=1, column=1, padx=self.padxr, pady=self.pady, sticky='e')
        self.height_spinbox.set(0)
        self.height_spinbox.bind("<Return>", self.adjust_selection)
        self.height_spinbox.bind("<MouseWheel>", self.focus_widget_and_adjust_selection)
        self.parent.bind_entry_functions(self.height_spinbox)


    def create_position_widgets(self):
        position_frame = ttk.LabelFrame(self.spinbox_frame, text="Position")
        position_frame.pack(side="left", fill="x", padx=(2,0), expand=True)
        position_frame.columnconfigure(1, weight=1)
        # X Position
        self.pos_x_label = ttk.Label(position_frame, text="X (px):")
        self.pos_x_label.grid(row=0, column=0, padx=self.padxl, pady=self.pady, sticky='w')
        ToolTip(self.pos_x_label, "X coordinate of selection in pixels (From top left corner)", 200, 6, 12)
        self.pos_x_spinbox = ttk.Spinbox(position_frame, from_=0, to=9999, width=7, command=self.adjust_selection)
        self.pos_x_spinbox.grid(row=0, column=1, padx=self.padxr, pady=self.pady, sticky='e')
        self.pos_x_spinbox.set(0)
        self.pos_x_spinbox.bind("<Return>", self.adjust_selection)
        self.pos_x_spinbox.bind("<MouseWheel>", self.focus_widget_and_adjust_selection)
        self.parent.bind_entry_functions(self.pos_x_spinbox)
        # Y Position
        self.pos_y_label = ttk.Label(position_frame, text="Y (px):")
        self.pos_y_label.grid(row=1, column=0, padx=self.padxl, pady=self.pady, sticky='w')
        ToolTip(self.pos_y_label, "Y coordinate of selection in pixels (From top left corner)", 200, 6, 12)
        self.pos_y_spinbox = ttk.Spinbox(position_frame, from_=0, to=9999, width=7, command=self.adjust_selection)
        self.pos_y_spinbox.grid(row=1, column=1, padx=self.padxr, pady=self.pady, sticky='e')
        self.pos_y_spinbox.set(0)
        self.pos_y_spinbox.bind("<Return>", self.adjust_selection)
        self.pos_y_spinbox.bind("<MouseWheel>", self.focus_widget_and_adjust_selection)
        self.parent.bind_entry_functions(self.pos_y_spinbox)


    def create_selection_widgets(self):
        fixed_selection_frame = ttk.LabelFrame(self.control_panel, text="Fixed Selection")
        fixed_selection_frame.pack(pady=self.pady, padx=self.padx, fill="x")
        fixed_selection_frame.columnconfigure(1, weight=1)
        # Fixed selection
        self.fixed_selection_checkbutton = ttk.Checkbutton(fixed_selection_frame, variable=self.fixed_sel_toggle_var, text="Fixed", command=self.toggle_widgets_by_mode)
        self.fixed_selection_checkbutton.grid(row=0, column=0, padx=self.padxl, pady=self.pady, sticky="w")
        ToolTip(self.fixed_selection_checkbutton, "Enable fixed aspect ratio, width, height, or size", 200, 6, 12)
        # Fixed selection Combobox
        self.fixed_selection_option_combobox = ttk.Combobox(fixed_selection_frame, values=["Aspect Ratio", "Width", "Height", "Size"], state="readonly", textvariable=self.fixed_sel_mode_var, width=16)
        self.fixed_selection_option_combobox.grid(row=0, column=1, columnspan=99, sticky="e", padx=self.pady, pady=self.pady)
        self.fixed_selection_option_combobox.bind("<<ComboboxSelected>>", self.toggle_widgets_by_mode)
        self.fixed_selection_option_combobox.bind("<MouseWheel>", self.toggle_widgets_by_mode)
        ToolTip(self.fixed_selection_option_combobox, "Choose what to be fixed", 200, 6, 12)
        # Auto Mode
        self.auto_aspect_checkbutton = ttk.Checkbutton(fixed_selection_frame, text="Auto", variable=self.auto_aspect_var, command=self.update_auto_entry_state, state="disabled")
        self.auto_aspect_checkbutton.grid(row=1, column=0, padx=self.padxl, pady=self.pady, sticky="w")
        ToolTip(self.auto_aspect_checkbutton, "Automatically select the best aspect ratio for the selection based on the predefined ratios and the aspect ratio of the displayed image.\n\n'Fixed' and 'Aspect Ratio' must be enabled!", 200, 6, 12, wraplength=240)
        # Error Pip
        self.selection_error_pip = tk.Label(fixed_selection_frame)
        self.selection_error_pip.grid(row=1, column=1, pady=self.pady, sticky="w")
        self.selection_error_pip_tooltip = ToolTip(self.selection_error_pip, 100, 6, 12, state="disabled")
        # Selection Entry
        self.fixed_selection_entry = ttk.Entry(fixed_selection_frame, textvariable=self.fixed_sel_entry_var, width=12)
        self.fixed_selection_entry.grid(row=1, column=2, padx=self.pady, pady=self.pady, sticky="ew")
        self.fixed_selection_entry_tooltip = ToolTip(self.fixed_selection_entry, "Enter a ratio 'W:H' or a decimal '1.0'", 200, 6, 12)
        self.fixed_selection_entry.bind("<KeyRelease>", lambda event: self.update_widget_values(resize=True))
        self.parent.bind_entry_functions(self.fixed_selection_entry)
        # Insert Button
        self.insert_button = ttk.Button(fixed_selection_frame, text="<", width=1, command=self.insert_selection_dimension)
        self.insert_button.grid(row=1, column=3, padx=self.pady, pady=self.pady, sticky="e")
        ToolTip(self.insert_button, "Insert current selection dimensions relative to the selected mode", 200, 6, 12)
        # Auto Entry
        self.auto_entry = ttk.Entry(fixed_selection_frame, textvariable=self.auto_entry_var, width=12, state="disabled")
        self.auto_entry.grid(row=3, column=0, columnspan=99, sticky="ew", padx=self.pady, pady=self.pady)
        self.parent.bind_entry_functions(self.auto_entry)
        ToolTip(self.auto_entry, "Enter aspect ratios separated by commas. As a ratio: 'W:H', or a decimal: '1.0'", 200, 6, 12)


    def create_option_widgets(self):
        options_frame = ttk.LabelFrame(self.control_panel, text="Options")
        options_frame.pack(pady=self.pady, padx=self.padx, fill="x")
        options_frame.columnconfigure(0, weight=1)
        # Expand From Center
        self.expand_from_center_checkbutton = ttk.Checkbutton(options_frame, variable=self.expand_center_toggle_var, text="Expand Center")
        self.expand_from_center_checkbutton.grid(row=0, column=0, padx=self.padxl, pady=self.pady, sticky="w")
        ToolTip(self.expand_from_center_checkbutton, "Expand selection from center outwards", 200, 6, 12)
        # Highlight
        self.overlay_checkbutton = ttk.Checkbutton(options_frame, variable=self.overlay_var, text="Highlight", command=self.toggle_overlay)
        self.overlay_checkbutton.grid(row=0, column=1, padx=self.padxl, pady=self.pady, sticky="e")
        ToolTip(self.overlay_checkbutton, "Toggle the overlay/highlight that darkens the background during selection", 200, 6, 12)


    def create_transform_widgets(self):
        transform_frame = ttk.LabelFrame(self.control_panel, text="Transform")
        transform_frame.pack(pady=self.pady, padx=self.padx, fill="x")
        # Rotate
        rotate_button = ttk.Button(transform_frame, text="Rotate", command=lambda: self.transform_image("rotate_270"))
        rotate_button.pack(side="left", fill="x", pady=self.pady, padx=2)
        # Flip
        flipx_button = ttk.Button(transform_frame, text="Flip X", command=lambda: self.transform_image("flip_x"))
        flipx_button.pack(side="left", fill="x", pady=self.pady, padx=2)
        flipy_button = ttk.Button(transform_frame, text="Flip Y", command=lambda: self.transform_image("flip_y"))
        flipy_button.pack(side="left", fill="x", pady=self.pady, padx=2)


# --------------------------------------
# UI Helpers
# --------------------------------------
    def update_widget_values(self, label=False, resize=False):
        def update_label(aspect_ratio):
            width = int(self.width_spinbox.get())
            height = int(self.height_spinbox.get())
            max_width = self.img_canvas.original_img_width
            max_height = self.img_canvas.original_img_height
            display_width = min(width, max_width)
            display_height = min(height, max_height)
            self.crop_info_label.config(text=f"Crop to: {display_width}x{display_height} ({aspect_ratio:.2f})")
            self.selection_aspect = round(aspect_ratio, 2)
            self.pos_x_spinbox.config(to=max_width - display_width)
            self.pos_y_spinbox.config(to=max_height - display_height)

        def set_spinbox_values(width, height, aspect_ratio):
            self.width_spinbox.set(width)
            self.height_spinbox.set(height)
            self.set_error_pip_color("normal")
            update_label(aspect_ratio)

        def handle_fixed_selection(value, width, height):
            option = self.fixed_sel_mode_var.get()
            try:
                if option == "Width":
                    width = int(value)
                elif option == "Height":
                    height = int(value)
                elif option == "Size":
                    if 'x' in value:
                        width, height = map(int, value.split("x"))
                    elif ',' in value:
                        width, height = map(int, value.split(","))
                    else:
                        raise ValueError
                elif option == "Aspect Ratio":
                    if ':' in value:
                        ratio_width, ratio_height = map(int, value.split(':'))
                        aspect_ratio = ratio_width / ratio_height
                    else:
                        aspect_ratio = float(value)
                    width = int(height * aspect_ratio)
                set_spinbox_values(width, height, width / height if height != 0 else 0)
            except ValueError:
                self.width_spinbox.set(0)
                self.height_spinbox.set(0)
                error_message = {
                    "Width": "Expected whole number (Integer)",
                    "Height": "Expected whole number (Integer)",
                    "Size": "Expected 'W x H' OR 'W , H' (Integer x Integer OR Integer , Integer)",
                    "Aspect Ratio": "Expected ratio: 'W:H' (Integer:Integer); or a float '1.0'"
                    }[option]
                self.set_error_pip_color("error", error_message)
        try:
            x1, y1, x2, y2 = self.crop_selection.coords
            x, y = x1, y1
            height, width = (y2 - y1), (x2 - x1)
            aspect_ratio = width / height if height != 0 else 0
        except TypeError:
            x = y = height = width = aspect_ratio = 0
        try:
            if label:
                update_label(aspect_ratio)
                return
            self.pos_x_spinbox.set(x)
            self.pos_y_spinbox.set(y)
            if resize:
                if self.fixed_sel_toggle_var.get():
                    handle_fixed_selection(self.fixed_sel_entry_var.get(), width, height)
                else:
                    set_spinbox_values(width, height, aspect_ratio)
            else:
                update_label(aspect_ratio)
        except UnboundLocalError:
            pass


    def insert_selection_dimension(self):
        mode = self.fixed_sel_mode_var.get()
        entry = self.fixed_sel_entry_var
        if mode == "Aspect Ratio":
            entry.set(self.selection_aspect)
        elif mode == "Width":
            entry.set(self.width_spinbox.get())
        elif mode == "Height":
            entry.set(self.height_spinbox.get())
        elif mode == "Size":
            entry.set(f"{self.width_spinbox.get()} x {self.height_spinbox.get()}")


    def focus_widget_and_adjust_selection(self, event):
        event.widget.focus_set()
        self.adjust_selection(event)


    def toggle_widgets_by_mode(self, event=None):
        width = self.width_spinbox
        height = self.height_spinbox
        message_map = {
            "Aspect Ratio": "Enter a ratio 'W:H' or a decimal '1.0'",
            "Width": "Enter a whole number",
            "Height": "Enter a whole number",
            "Size": "Enter 'W x H' OR 'W , H'"
            }
        if self.fixed_sel_toggle_var.get():
            state_map = {# Mode: {Widget: State}
                "Aspect Ratio": {width: "disabled", height: "disabled"},
                "Width": {width: "disabled", height: "normal"},
                "Height": {width: "normal", height: "disabled"},
                "Size": {width: "disabled", height: "disabled"}
                }
            mode = self.fixed_sel_mode_var.get()
            for widget, widget_state in state_map.get(mode, {}).items():
                widget.config(state=widget_state)
        else:
            width.config(state="normal")
            height.config(state="normal")
        if self.fixed_sel_toggle_var.get() and self.fixed_sel_mode_var.get() == "Aspect Ratio":
            self.auto_aspect_checkbutton.config(state="normal")
            self.update_auto_entry_state()
        else:
            self.auto_aspect_checkbutton.config(state="disabled")
            self.auto_aspect_var.set(False)
            self.update_auto_entry_state()
        self.fixed_selection_entry_tooltip.config(text=message_map.get(self.fixed_sel_mode_var.get(), ""))


    def set_error_pip_color(self, state=None, message=None, event=None):
        if state == "error":
            self.selection_error_pip.config(bg="#fd8a8a")
            self.selection_error_pip_tooltip.config(state="normal", text=message)
        if state == "normal":
            self.selection_error_pip.config(bg="SystemButtonFace")
            self.selection_error_pip_tooltip.config(state="disabled")


    def update_auto_entry_state(self):
        if self.fixed_sel_toggle_var.get() and self.fixed_sel_mode_var.get() == "Aspect Ratio":
            if self.auto_aspect_var.get():
                self.auto_entry.config(state="normal")
                self.fixed_selection_entry.config(state="disabled")
            else:
                self.auto_entry.config(state="disabled")
                self.fixed_selection_entry.config(state="normal")
        else:
            self.auto_entry.config(state="disabled")
            self.fixed_selection_entry.config(state="normal")


    def determine_best_aspect_ratio(self, event=None):
        def convert_to_float(ratio):
            if ':' in ratio:
                width, height = map(float, ratio.split(':'))
                return round(width / height, 2)
            return round(float(ratio), 2)

        ratio_list = [input.strip() for input in self.auto_entry_var.get().split(",")]
        ratio_list = list(set(convert_to_float(r) for r in ratio_list))
        width = self.img_canvas.original_img_width
        height = self.img_canvas.original_img_height
        image_ratio = round(width / height, 2)
        closest_ratio = min(ratio_list, key=lambda x: abs(x - image_ratio))
        self.fixed_selection_entry.config(state="normal")
        self.fixed_selection_entry.delete(0, 'end')
        self.fixed_selection_entry.insert(0, str(closest_ratio))
        self.fixed_selection_entry.config(state="disabled")


    def image_index_changed(self, event=None):
        try:
            index = int(self.image_index_spinbox.get()) - 1
            if 0 <= index < len(self.image_files):
                self.current_index = index
                self.display_image(self.image_files[self.current_index])
        except ValueError:
            pass


    def show_help(self):
        help_message = ("Not Implemented!")
        messagebox.showinfo("CropUI Help", help_message)


    def toggle_overlay(self):
        self.crop_selection.overlay_enabled.set(self.overlay_var.get())
        self.crop_selection.update_overlay()


# --------------------------------------
# Main
# --------------------------------------
    def open_directory_dialog(self):
        dir_path = filedialog.askdirectory()
        if (dir_path and os.path.exists(dir_path)):
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
        self.image_index_spinbox.config(from_=1, to=len(self.image_files))
        self.image_index_spinbox.set(self.current_index + 1)


    def show_previous_image(self):
        if self.image_files:
            self.current_index = (self.current_index - 1) % len(self.image_files)
            self.display_image(self.image_files[self.current_index])


    def show_next_image(self):
        if self.image_files:
            self.current_index = (self.current_index + 1) % len(self.image_files)
            self.display_image(self.image_files[self.current_index])


    def crop_image(self):
        if not (self.img_canvas.img_path and self.crop_selection.coords):
            return
        width = int(self.width_spinbox.get())
        height = int(self.height_spinbox.get())
        pos_x = int(self.pos_x_spinbox.get())
        pos_y = int(self.pos_y_spinbox.get())
        max_width = self.img_canvas.original_img_width
        max_height = self.img_canvas.original_img_height
        display_width = min(width, max_width)
        display_height = min(height, max_height)
        coords = (pos_x, pos_y, pos_x + display_width, pos_y + display_height)
        cropped_img = self.img_canvas.original_img.crop(coords)
        self.after_crop_option(cropped_img)


    def after_crop_option(self, cropped_img):
        after_crop_option = self.after_crop_var.get()
        if after_crop_option == "Save & Close":
            save_path = self.generate_unique_filename(self.img_canvas.img_path)
            cropped_img.save(save_path)
            self.close_crop_ui()
        elif after_crop_option == "Save & Next":
            save_path = self.generate_unique_filename(self.img_canvas.img_path)
            cropped_img.save(save_path)
            self.show_next_image()
        elif after_crop_option == "Save As...":
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if save_path:
                cropped_img.save(save_path)
        elif after_crop_option == "Save":
            save_path = self.generate_unique_filename(self.img_canvas.img_path)
            cropped_img.save(save_path)
        elif after_crop_option == "Overwrite":
            confirm = messagebox.askyesno("Confirm Overwrite", "Are you sure you want to overwrite the original image?")
            if confirm:
                cropped_img.save(self.img_canvas.img_path)
                self.img_canvas._display_image(self.img_canvas.img_path)
                self.crop_selection.clear_selection()


    def generate_unique_filename(self, original_path):
        directory, filename = os.path.split(original_path)
        name, ext = os.path.splitext(filename)
        counter = 1
        while True:
            new_filename = f"{name}_crop_{counter}{ext}"
            new_filepath = os.path.join(directory, new_filename)
            if not os.path.exists(new_filepath):
                return new_filepath
            counter += 1


# --------------------------------------
# Selection
# --------------------------------------
    def adjust_selection(self, event=None):
        if event is None:
            widget = self.root.focus_get()
        else:
            widget = event.widget
        try:
            original_value = int(widget.get())
        except (AttributeError, ValueError):
            return
        spinbox_map = {
            self.width_spinbox: 'width',
            self.height_spinbox: 'height',
            self.pos_x_spinbox: 'new_x',
            self.pos_y_spinbox: 'new_y'
            }
        scale = self.img_canvas.img_scale_ratio
        scaled_value = int(original_value * scale)
        kwargs = {spinbox_map[widget]: scaled_value, 'original_value': original_value}
        self.crop_selection.set_selection_dimensions(**kwargs)
        self.update_widget_values(label=True)


# --------------------------------------
# Transform Image
# --------------------------------------
    def transform_image(self, mode):
        path = self.image_files[self.current_index]
        img = self.img_canvas.original_img
        if mode == "flip_x":
            transform = Image.FLIP_LEFT_RIGHT
        elif mode == "flip_y":
            transform = Image.FLIP_TOP_BOTTOM
        elif mode == "rotate_270":
            transform = Image.ROTATE_270
        else:
            raise ValueError(f"Unsupported transformation mode: {mode}")
        if path.lower().endswith('.gif'):
            self.process_gif_frames(img, path, lambda frame: frame.transpose(transform))
        else:
            transformed_img = img.transpose(transform)
            transformed_img.save(path)
        self.img_canvas._display_image(self.img_canvas.img_path)
        self.crop_selection.clear_selection()


    def process_gif_frames(self, img, path, transform_function):
        frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
        transformed_frames = [transform_function(frame) for frame in frames]
        durations = [frame.info.get('duration', 34) for frame in frames]
        first_frame = transformed_frames[0]
        rest_frames = transformed_frames[1:]
        first_frame.save(path, append_images=rest_frames, save_all=True, duration=durations, loop=0)


# --------------------------------------
# Image Info
# --------------------------------------
    def update_imageinfo(self, percent_scale=0):
        if self.image_files:
            self.image_file = self.image_files[self.current_index]
            if self.image_file not in self.image_info_cache:
                self.image_info_cache[self.image_file] = self.get_image_info(self.image_file)
            image_info = self.image_info_cache[self.image_file]
            self.img_stats_label.config(text=f"{image_info['filename']}  |  {image_info['resolution']}  |  {percent_scale}%  |  {image_info['size']}  |  {image_info['color_mode']}", anchor="w")


    def get_image_info(self, image_file):
        image = self.img_canvas.original_img
        width, height = image.size
        color_mode = image.mode
        size = os.path.getsize(image_file)
        size_kb = size / 1024
        size_str = f"{round(size_kb)} KB" if size_kb < 1024 else f"{round(size_kb / 1024, 2)} MB"
        filename = os.path.basename(image_file)
        filename = (filename[:61] + '(...)') if len(filename) > 64 else filename
        return {"filename": filename, "resolution": f"{width}x{height}", "size": size_str, "color_mode": color_mode}


# --------------------------------------
# Close CropUI
# --------------------------------------
    def close_crop_ui(self, event=None):
        self.root.minsize(545, 200) # Width x Height
        self.parent.sync_title_with_content()
        self.crop_ui_frame.grid_remove()
        self.menu.entryconfig("Crop...", command=self.parent.show_crop_ui)
        self.parent.show_primary_paned_window()
        self.parent.refresh_text_box()
        self.parent.refresh_file_lists()
        self.parent.update_thumbnail_panel()


#endregion
