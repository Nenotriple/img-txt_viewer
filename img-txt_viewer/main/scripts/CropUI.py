#region Imports


# Standard Library
import os


# Standard Library GUI
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# Third Party Library
from PIL import Image, ImageTk, ImageSequence
from TkToolTip.TkToolTip import TkToolTip as ToolTip


# Local
from main.scripts import HelpText
from main.scripts.help_window import HelpWindow
import main.scripts.entry_helper as entry_helper

# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region CropSelection


class CropSelection:
    def __init__(self, crop_ui: 'CropInterface', img_canvas: 'ImageCanvas'):
        self.crop_ui = crop_ui
        self.img_canvas = img_canvas

        # Selection variables
        self.rect = None
        self.coords = None
        self.start_x = None
        self.start_y = None

        # Overlay variables
        self.overlay = None
        self.overlay_enabled = True
        self.overlay_rect = None

        # Variables for moving and resizing
        self.moving_rect = False
        self.move_offset_x = 0
        self.move_offset_y = 0
        self.rect_width = 0
        self.rect_height = 0

        # Handle manager
        self.handle_manager = CropSelHandles(self, img_canvas)

        # Guideline manager
        self.guideline_manager = CropSelGuidelines(self, img_canvas)

        # Bind events
        self.img_canvas.bind("<ButtonPress-1>", self._on_button_press)
        self.img_canvas.bind("<B1-Motion>", self._on_move_press, add="+")
        self.img_canvas.bind("<ButtonRelease-1>", self._on_button_release, add="+")
        self.img_canvas.bind("<Motion>", self.handle_manager._update_cursor_img)
        self.img_canvas.bind("<Double-1>", self._on_double_click)
        # Bind mouse wheel events
        self.img_canvas.bind("<MouseWheel>", self._on_mousewheel, add="+")


# ----------------------------
# Events
# ----------------------------
    def _on_button_press(self, event):
        if not self.img_canvas.img_path:
            return
        x_off, y_off = self.img_canvas.x_off, self.img_canvas.y_off
        x_max = x_off + self.img_canvas.new_size[0]
        y_max = y_off + self.img_canvas.new_size[1]
        if self.rect:
            if self.handle_manager._is_handle_clicked(event):
                return
            x1, y1, x2, y2 = self.img_canvas.coords(self.rect)
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self._start_moving_rect(event, x1, y1, x2, y2)
                return
            else:
                self.clear_selection()
        if not (x_off <= event.x <= x_max and y_off <= event.x <= y_max):
            return
        if not self.crop_ui.fixed_sel_toggle_var.get():
            self._start_selection(event, x_off, y_off, x_max, y_max)
            return
        mode = self.crop_ui.fixed_sel_mode_var.get()
        try:
            if mode == "Size":
                value = self.crop_ui.fixed_sel_entry_var.get()
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
                width = int(float(self.crop_ui.fixed_sel_entry_var.get()) * self.img_canvas.img_scale_ratio)
                width = min(width, x_max - x_off)
                x1 = max(x_off, min(event.x - width / 2, x_max - width))
                x2 = x1 + width
                y1 = y2 = event.y
                self.start_x, self.start_y = x1, y1
            elif mode == "Height":
                height = int(float(self.crop_ui.fixed_sel_entry_var.get()) * self.img_canvas.img_scale_ratio)
                height = min(height, y_max - y_off)
                y1 = max(y_off, min(event.y - height / 2, y_max - height))
                y2 = y1 + height
                x1 = x2 = event.x
                self.start_x, self.start_y = x1, y1
            else:  # Aspect Ratio mode
                if self.crop_ui.auto_aspect_var.get():
                    self.crop_ui.determine_best_aspect_ratio()
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
        if self.handle_manager._is_resizing():
            x1, y1, x2, y2 = self.handle_manager._resize(event)
            self.crop_ui.update_widget_values(resize=True)
        elif self.moving_rect:
            x1, y1, x2, y2 = self._calc_moving_rect(event, x_off, y_off, x_max, y_max)
        else:
            x1, y1, x2, y2 = self._calc_selection_rect(event, x_off, y_off, x_max, y_max)
            self.crop_ui.update_widget_values(resize=True)
        self.update_rect(x1, y1, x2, y2)


    def _on_button_release(self, event):
        if not self.img_canvas.img_path or not self.rect:
            return
        coords = self.img_canvas.coords(self.rect)
        if len(coords) != 4:
            return
        x1, y1, x2, y2 = coords
        if self.handle_manager._is_resizing():
            self.handle_manager._stop_resizing()
        elif self.moving_rect:
            self.moving_rect = False
        else:
            if x1 == x2 or y1 == y2:
                self.clear_selection()
                return
            self.handle_manager.update_handles(create=True)
            self.update_overlay()
        self._calc_img_sel_coords(x1, y1, x2, y2)
        self.handle_manager.show_handles()
        self.crop_ui.update_widget_values()
        self.handle_manager._hide_handles_on_mode()


    def _on_double_click(self, event):
        if self.rect:
            self.clear_selection()
            self.crop_ui.update_widget_values()
            return
        if not self.img_canvas.img_path:
            return
        img_width, img_height = self.img_canvas.original_img_width, self.img_canvas.original_img_height
        center_x, center_y = img_width // 2, img_height // 2
        # Handle fixed selection if enabled
        if self.crop_ui.fixed_sel_toggle_var.get():
            mode = self.crop_ui.fixed_sel_mode_var.get()
            value = self.crop_ui.fixed_sel_entry_var.get()
            if mode == "Aspect Ratio":
                try:
                    if ":" in value:
                        width_ratio, height_ratio = map(float, value.split(":"))
                        aspect_ratio = width_ratio / height_ratio
                    else:
                        aspect_ratio = float(value)
                    if aspect_ratio >= 1:  # Wider than tall
                        half_width = min(img_width // 2, int(img_height * aspect_ratio) // 2)
                        half_height = int(half_width / aspect_ratio)
                    else:  # Taller than wide
                        half_height = min(img_height // 2, int(img_width / aspect_ratio) // 2)
                        half_width = int(half_height * aspect_ratio)
                except (ValueError, ZeroDivisionError):
                    half_width, half_height = img_width // 4, img_height // 4
            elif mode == "Width":
                try:
                    fixed_width = int(float(value))
                    half_width = min(img_width, fixed_width) // 2
                    half_height = img_height // 4
                except ValueError:
                    half_width, half_height = img_width // 4, img_height // 4
            elif mode == "Height":
                try:
                    fixed_height = int(float(value))
                    half_width = img_width // 4
                    half_height = min(img_height, fixed_height) // 2
                except ValueError:
                    half_width, half_height = img_width // 4, img_height // 4
            elif mode == "Size":
                try:
                    if "x" in value:
                        width, height = map(int, value.split("x"))
                    else:
                        width, height = map(int, value.split(","))
                    half_width = min(img_width, width) // 2
                    half_height = min(img_height, height) // 2
                except (ValueError, IndexError):
                    half_width, half_height = img_width // 4, img_height // 4
        else:
            half_width, half_height = img_width // 4, img_height // 4
        x1, y1 = center_x - half_width, center_y - half_height
        x2, y2 = center_x + half_width, center_y + half_height
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
        self.handle_manager.update_handles()
        self.update_overlay()
        self.crop_ui.update_widget_values(resize=True)
        self.guideline_manager.update_guidelines(self.crop_ui.guideline_combo.get())


    def _on_mousewheel(self, event):
        if not self.rect:
            return
        if event.delta:
            delta = event.delta
        else:
            return
        shift_pressed = event.state & 0x0001
        ctrl_pressed = event.state & 0x0004
        mode = self.crop_ui.fixed_sel_mode_var.get()
        step = 10 if delta > 0 else -10
        if self.crop_ui.fixed_sel_toggle_var.get():
            if mode == "Aspect Ratio":
                # Resize both width and height while maintaining aspect ratio
                self._resize_sel_on_mousewheel(True, True, step, maintain_aspect_ratio=True)
            elif mode == "Width":
                # Only resize height
                self._resize_sel_on_mousewheel(False, True, step)
            elif mode == "Height":
                # Only resize width
                self._resize_sel_on_mousewheel(True, False, step)
            elif mode == "Size":
                # Do not allow resizing
                return
        else:
            if shift_pressed and ctrl_pressed: # Resize width and height
                self._resize_sel_on_mousewheel(True, True, step)
            elif shift_pressed: # Resize width
                self._resize_sel_on_mousewheel(True, False, step)
            else: # Resize height
                self._resize_sel_on_mousewheel(False, True, step)


# ----------------------------
# Event Helpers
# ----------------------------
    def _start_moving_rect(self, event, x1, y1, x2, y2):
        self.moving_rect = True
        if self.crop_ui.fixed_sel_toggle_var.get() and self.crop_ui.fixed_sel_mode_var.get() == "Size":
            self.move_offset_x = (x2 - x1) / 2
            self.move_offset_y = (y2 - y1) / 2
        else:
            self.move_offset_x = event.x - x1
            self.move_offset_y = event.y - y1
        self.rect_width = x2 - x1
        self.rect_height = y2 - y1
        self.handle_manager.hide_handles()


    def _start_selection(self, event, x_off, y_off, x_max, y_max):
        self.start_x = max(min(event.x, x_max), x_off)
        self.start_y = max(min(event.y, y_max), y_off)
        if self.crop_ui.expand_center_var.get():
            self.center_x = self.start_x
            self.center_y = self.start_y
        if self.crop_ui.fixed_sel_toggle_var.get() and self.crop_ui.fixed_sel_mode_var.get() in ["Aspect Ratio", "Width", "Height"]:
            if self.crop_ui.expand_center_var.get():
                self.center_x = (x_off + x_max) / 2
                self.center_y = (y_off + y_max) / 2
                self.start_x = self.center_x
                self.start_y = self.center_y
            else:
                self.start_x = max(min(event.x, x_max), x_off)
                self.start_y = max(min(event.y, y_max), y_off)
        self.rect = self.img_canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='white', tags='rect')


    def _resize_sel_on_mousewheel(self, delta_width, delta_height, step, maintain_aspect_ratio=False):
        x1, y1, x2, y2 = self.img_canvas.coords(self.rect)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        x_off, y_off = self.img_canvas.x_off, self.img_canvas.y_off
        img_width = self.img_canvas.new_size[0]
        img_height = self.img_canvas.new_size[1]
        new_width = (x2 - x1) + (step if delta_width else 0)
        new_height = (y2 - y1) + (step if delta_height else 0)
        if maintain_aspect_ratio:
            aspect_ratio_str = self.crop_ui.fixed_sel_entry_var.get()
            if ':' in aspect_ratio_str:
                width_ratio, height_ratio = map(float, aspect_ratio_str.split(':'))
                aspect_ratio = width_ratio / height_ratio
            else:
                aspect_ratio = float(aspect_ratio_str)
            if delta_width:
                new_height = new_width / aspect_ratio
            elif delta_height:
                new_width = new_height * aspect_ratio
            max_width = img_width
            max_height = img_height
            if new_width > max_width:
                new_width = max_width
                new_height = new_width / aspect_ratio
            if new_height > max_height:
                new_height = max_height
                new_width = new_height * aspect_ratio
        new_width = max(new_width, 10)
        new_height = max(new_height, 10)
        x1_new = cx - new_width / 2
        x2_new = cx + new_width / 2
        y1_new = cy - new_height / 2
        y2_new = cy + new_height / 2
        x1_new = max(x_off, x1_new)
        y1_new = max(y_off, y1_new)
        x2_new = min(x_off + img_width, x2_new)
        y2_new = min(y_off + img_height, y2_new)
        self.update_rect(x1_new, y1_new, x2_new, y2_new)
        self.handle_manager.update_handles()
        self.crop_ui.update_widget_values(resize=True)


# ----------------------------
# Rectangle Calculations
# ----------------------------
    def _calc_img_sel_coords(self, x1, y1, x2, y2):
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


    def _calc_moving_rect(self, event, x_off, y_off, x_max, y_max):
        x1 = max(x_off, min(event.x - self.move_offset_x, x_max - self.rect_width))
        y1 = max(y_off, min(event.y - self.move_offset_y, y_max - self.rect_height))
        x2 = x1 + self.rect_width
        y2 = y1 + self.rect_height
        return x1, y1, x2, y2


    def _calc_selection_rect(self, event, x_off, y_off, x_max, y_max):
        curX = max(min(event.x, x_max), x_off)
        curY = max(min(event.y, y_max), y_off)
        if self.crop_ui.expand_center_var.get():
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
        if self.crop_ui.fixed_sel_toggle_var.get():
            x1, y1, x2, y2 = self._apply_fixed_selection(x1, y1, x2, y2, x_off, y_off, x_max, y_max)
        return x1, y1, x2, y2


# ----------------------------
# Updates
# ----------------------------
    def update_rect(self, x1, y1, x2, y2):
        if None in (x1, y1, x2, y2):
            return
        self.img_canvas.coords(self.rect, x1, y1, x2, y2)
        self.rect_width = x2 - x1
        self.rect_height = y2 - y1
        self._calc_img_sel_coords(x1, y1, x2, y2)
        self.handle_manager.update_handles()
        self.update_overlay()
        self.guideline_manager.update_guidelines(self.crop_ui.guideline_combo.get())


    def update_overlay(self):
        if not self.overlay_enabled:
            if self.overlay_rect:
                self.img_canvas.delete(self.overlay_rect)
            if self.rect:
                x1, y1, x2, y2 = self.img_canvas.coords(self.rect)
                self.overlay_rect = self.img_canvas.create_rectangle(x1-1, y1-1, x2+1, y2+1, outline='black', tags='highlight')
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
        if self.overlay_rect:
            self.img_canvas.delete(self.overlay_rect)
        self.handle_manager.clear_handles()
        self.guideline_manager.clear_guidelines()
        self.rect = None
        self.coords = None
        self.start_x = None
        self.start_y = None
        self.moving_rect = False
        self.move_offset_x = 0
        self.move_offset_y = 0
        self.rect_width = 0
        self.rect_height = 0
        self.crop_ui.update_widget_values()


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
            self.handle_manager.update_handles(create=True)
            self.update_overlay()


# ----------------------------
# Fixed Selection
# ----------------------------
    def _apply_fixed_selection(self, x1, y1, x2, y2, x_off, y_off, x_max, y_max):
        scale = self.img_canvas.img_scale_ratio
        mode = self.crop_ui.fixed_sel_mode_var.get()
        value = self.crop_ui.fixed_sel_entry_var.get()
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
        if self.crop_ui.expand_center_var.get() and self.crop_ui.fixed_sel_toggle_var.get() and mode in ["Aspect Ratio", "Width", "Height"]:
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
            ratio = float(value.split(":")[0]) / float(value.split(":")[1]) if ":" in value else float(value)
            if ratio <= 0:
                return x1, y1, x2, y2
        except (ValueError, ZeroDivisionError):
            return x1, y1, x2, y2
        width = abs(x2 - x1)
        height = width / ratio if width != 0 else abs(y2 - y1) * ratio
        if self.crop_ui.expand_center_var.get():
            max_width = min(2 * (self.center_x - x_off), 2 * (x_max - self.center_x))
            max_height = min(2 * (self.center_y - y_off), 2 * (y_max - self.center_y))
            if width > max_width:
                width = max_width
                height = width / ratio
            if height > max_height:
                height = max_height
                width = height * ratio
            half_width = width / 2
            half_height = height / 2
            x1 = self.center_x - half_width
            x2 = self.center_x + half_width
            y1 = self.center_y - half_height
            y2 = self.center_y + half_height
        else:
            if width != 0 or abs(y2 - y1) != 0:
                is_horizontal = width != 0
                is_dragging_right = x2 > x1
                is_dragging_down = y2 > y1
                if is_horizontal:
                    height = width / ratio
                    max_height = y_max - y1 if is_dragging_down else y1 - y_off
                    if height > max_height:
                        height = max_height
                        width = height * ratio
                    x2 = x1 + (width if is_dragging_right else -width)
                    y2 = y1 + (height if is_dragging_down else -height)
                else:
                    height = abs(y2 - y1)
                    width = height * ratio
                    max_width = x_max - x1 if is_dragging_right else x1 - x_off
                    if width > max_width:
                        width = max_width
                        height = width / ratio
                    x2 = x1 + (width if is_dragging_right else -width)
                    y2 = y1 + (height if is_dragging_down else -height)
        return (
            max(x_off, min(x_max, x1)),
            max(y_off, min(y_max, y1)),
            max(x_off, min(x_max, x2)),
            max(y_off, min(y_max, y2))
        )


# ----------------------------
# Manual Adjustment
# ----------------------------
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
        if self.crop_ui.expand_center_var.get():
            x1, y1, x2, y2 = self._calc_center_expansion(x1, y1, x2, y2, width, height, c_size)
        else:
            if width is not None:
                width = int(min(width, c_size[0]))
                x2 = x1 + width
            if height is not None:
                height = int(min(height, c_size[1]))
                y2 = y1 + height
        x1, y1, x2, y2 = self._clamp_coords_to_img(x1, y1, x2, y2, cx_off, cy_off, c_size)
        self.update_rect(round(x1), round(y1), round(x2), round(y2))


    def _calc_center_expansion(self, x1, y1, x2, y2, width, height, c_size):
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


    def _clamp_coords_to_img(self, x1, y1, x2, y2, cx_off, cy_off, c_size):
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
#region CropSelHandles


class CropSelHandles:
    def __init__(self, crop_selection: 'CropSelection', img_canvas: 'ImageCanvas'):
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


# ----------------------------
# Handle Updates
# ----------------------------
    def update_handles(self, create=False):
        if not self.crop_selection.rect:
            return
        x1, y1, x2, y2 = self.img_canvas.coords(self.crop_selection.rect)
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        size = self._calc_handle_size(x1, y1, x2, y2)
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


    def _hide_handles_on_mode(self):
        if self.crop_selection.crop_ui.fixed_sel_toggle_var.get():
            mode = self.crop_selection.crop_ui.fixed_sel_mode_var.get()
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


    def _calc_handle_size(self, x1, y1, x2, y2):
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


# ----------------------------
# Handle Visibility
# ----------------------------
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


    def clear_handles(self):
        for handle in self.handles.values():
            self.img_canvas.delete(handle)
        self.handles.clear()
        self.resizing_handle = None


# ----------------------------
# Handle Events
# ----------------------------
    def _is_handle_clicked(self, event):
        items = self.img_canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for key, handle in self.handles.items():
            if handle in items:
                self.resizing_handle = key
                self._hide_handles_except(key)
                return True
        return False


    def _update_cursor_img(self, event):
        if not self.img_canvas.img_path:
            return
        items = self.img_canvas.find_overlapping(event.x, event.y, event.x, event.y)
        cursor = "cross"
        for key, handle in self.handles.items():
            if handle in items:
                cursor = self.cursor_mapping.get(key, "cross")
                break
        self.img_canvas.config(cursor=cursor)


# ----------------------------
# Handle Resizing
# ----------------------------
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
        expand_from_center = self.crop_selection.crop_ui.expand_center_var.get()
        handle = self.resizing_handle
        m_size = 10
        if self.crop_selection.crop_ui.fixed_sel_toggle_var.get() and self.crop_selection.crop_ui.fixed_sel_mode_var.get() == "Aspect Ratio":
            return self._resize_with_aspect_ratio(event, x1, y1, x2, y2, x_off, y_off, x_max, y_max, expand_from_center, m_size)
        if expand_from_center:
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            dx = max(m_size / 2, abs(event.x - cx))
            dy = max(m_size / 2, abs(event.y - cy))
            x1_new, y1_new, x2_new, y2_new = self._calc_new_coords(x1, y1, x2, y2, cx, cy, dx, dy, x_off, y_off, x_max, y_max)
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
            value = self.crop_selection.crop_ui.fixed_sel_entry_var.get()
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
            x1_new, y1_new, x2_new, y2_new = self._calc_new_coords(x1, y1, x2, y2, cx, cy, dx, dy, x_off, y_off, x_max, y_max)
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


    def _calc_new_coords(self, x1, y1, x2, y2, cx, cy, dx, dy, x_off, y_off, x_max, y_max):
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
#region CropSelGuidelines


class CropSelGuidelines:
    def __init__(self, crop_selection: 'CropSelection', img_canvas: 'ImageCanvas'):
        self.crop_selection = crop_selection
        self.img_canvas = img_canvas
        self.guidelines = []
        self.mode = None


    def update_guidelines(self, mode=None, event=None):
        self.clear_guidelines()
        if not self.crop_selection.rect or mode in (None, 'None'):
            return
        self.mode = mode
        x1, y1, x2, y2 = self.img_canvas.coords(self.crop_selection.rect)
        if self.mode == "Crosshair":
            self._draw_crosshair(x1, y1, x2, y2)
        elif self.mode == 'Center Lines':
            self._draw_center_line(x1, y1, x2, y2)
        elif self.mode == 'Rule of Thirds':
            self._draw_rule_of_thirds(x1, y1, x2, y2)
        elif self.mode == 'Diagonal Lines':
            self._draw_diagonal_lines(x1, y1, x2, y2)


    def draw_guideline(self, x1, y1, x2, y2, offset=1):
        # Draw main guideline in white
        line_white = self.img_canvas.create_line(x1, y1, x2, y2, fill='white', dash=(2, 2))
        # Draw offset line in black
        x1_off, y1_off, x2_off, y2_off = self.offset_line(x1, y1, x2, y2, offset)
        line_black = self.img_canvas.create_line(x1_off, y1_off, x2_off, y2_off, fill='black', dash=(2, 2))
        # Add lines to guidelines list
        self.guidelines.extend([line_white, line_black])


    def _draw_center_line(self, x1, y1, x2, y2):
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        self.draw_guideline(cx, y1, cx, y2)
        self.draw_guideline(x1, cy, x2, cy)


    def _draw_rule_of_thirds(self, x1, y1, x2, y2):
        third_x = (x2 - x1) / 3
        third_y = (y2 - y1) / 3
        x_positions = [x1 + third_x, x1 + 2 * third_x]
        y_positions = [y1 + third_y, y1 + 2 * third_y]
        for x in x_positions:
            self.draw_guideline(x, y1, x, y2)
        for y in y_positions:
            self.draw_guideline(x1, y, x2, y)


    def _draw_diagonal_lines(self, x1, y1, x2, y2):
        # Calculate the length of the diagonal
        diagonal_length = min(x2 - x1, y2 - y1)
        offset = 1  # px
        # Define diagonal lines coordinates
        diagonals = [
            (x1, y1, x1 + diagonal_length, y1 + diagonal_length),
            (x2, y1, x2 - diagonal_length, y1 + diagonal_length),
            (x1, y2, x1 + diagonal_length, y2 - diagonal_length),
            (x2, y2, x2 - diagonal_length, y2 - diagonal_length)
        ]
        # Draw diagonal guidelines
        for x1, y1, x2, y2 in diagonals:
            self.draw_guideline(x1, y1, x2, y2, offset)


    def _draw_crosshair(self, x1, y1, x2, y2):
        # Calculate center point
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        black_text = self.img_canvas.create_text(cx+1, cy+1, text="X", font=("", 5), fill="black")
        white_text = self.img_canvas.create_text(cx, cy, text="X", font=("", 5), fill="white")
        self.guidelines.extend([black_text, white_text])


    def clear_guidelines(self):
        for line in self.guidelines:
            self.img_canvas.delete(line)
        self.guidelines.clear()


    def offset_line(self, x1, y1, x2, y2, offset):
        # Compute direction vector
        dx = x2 - x1
        dy = y2 - y1
        length = (dx**2 + dy**2)**0.5
        if length == 0:
            return x1, y1, x2, y2  # Can't offset zero-length line
        # Compute perpendicular vector
        px = -dy / length
        py = dx / length
        # Offset points
        x1_off = x1 + px * offset
        y1_off = y1 + py * offset
        x2_off = x2 + px * offset
        y2_off = y2 + py * offset
        return x1_off, y1_off, x2_off, y2_off



#endregion
#region ImageCanvas


class ImageCanvas(tk.Canvas):
    def __init__(self, parent: 'CropInterface', frame):
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
        self.img_thumb = None
        self.resize_after_id = None

        self.bind("<Configure>", self._resize_img)
        self.bind("<Button-3>", lambda event: self.parent.crop_selection.clear_selection())


    def _display_img(self, img_path):
        self.img_path = img_path
        if img_path.lower().endswith('.mp4'):
            self.original_img = Image.new("RGB", (32, 32), "white")
        else:
            with Image.open(img_path) as img:
                self.original_img = img.copy()
        self.original_img_width, self.original_img_height = self.original_img.size
        self.img_scale_ratio = 1.0
        self.new_size = (0, 0)
        self.x_off = 0
        self.y_off = 0
        self.img_thumb = None
        self.resize_after_id = None
        self._resize_img(None)


    def _resize_img(self, event=None):
        if not self.img_path:
            return
        new_width, new_height = self.winfo_width(), self.winfo_height()
        ratio = min(new_width / self.original_img_width, new_height / self.original_img_height)
        new_size = (int(self.original_img_width * ratio), int(self.original_img_height * ratio))
        filter_type = Image.NEAREST
        if new_size != self.new_size and new_size[0] > 0 and new_size[1] > 0:
            self.img_scale_ratio = ratio
            self.new_size = new_size
            max_size = max(self.original_img_width, self.original_img_height)
            if max_size > 768:
                filter_type = Image.NEAREST
            elif 480 < max_size <= 768:
                filter_type = Image.BILINEAR
            else:
                filter_type = Image.LANCZOS
            self.img_resized = self.original_img.resize(self.new_size, filter_type)
            self.img_thumb = ImageTk.PhotoImage(self.img_resized)
            percent_scale = self.img_scale_ratio * 100
            self.parent.update_imginfo(int(percent_scale))
        self.delete("all")
        self.x_off = (new_width - self.new_size[0]) // 2
        self.y_off = (new_height - self.new_size[1]) // 2
        self.create_image(self.x_off, self.y_off, anchor="nw", image=self.img_thumb)
        if self.resize_after_id:
            self.after_cancel(self.resize_after_id)
        if filter_type != Image.LANCZOS:
            self.resize_after_id = self.after(250, self.refresh_img)


    def refresh_img(self):
        if not self.img_path or not all(self.new_size):
            return
        try:
            self.img_resized = self.original_img.resize(self.new_size, Image.LANCZOS)
            self.img_thumb = ImageTk.PhotoImage(self.img_resized)
            self.delete("all")
            self.create_image(self.x_off, self.y_off, anchor="nw", image=self.img_thumb)
            if hasattr(self, 'crop_selection'):
                self.parent.crop_selection.redraw_rect()
        except ValueError:
            pass


#endregion
#region CropInterface


class CropInterface:
    def __init__(self):
        # Primary variables
        self.parent: 'Main' = None
        self.root: 'tk.Tk' = None
        self.text_controller = None
        self.working_dir = None
        self.entry_helper = entry_helper

        # Source image path independent of temp display
        self.current_source_path = None

        # Image Variables
        self.gif_frames = []
        self.img_info_cache = {}
        self.selection_aspect = 0
        self.current_index = 0

        # UI
        self.pady = 5
        self.padx = 10
        self.padxl = (5,2)
        self.padxr = (2,5)

        # Settings
        self.dir_entry_var = tk.StringVar()
        self.overlay_var = tk.BooleanVar(value=True)
        self.after_crop_var = tk.StringVar(value="Save & Close")
        self.expand_center_var = tk.BooleanVar(value=False)
        self.guidelines_var = tk.StringVar(value="Crosshair")

        # Fixed Selection
        self.fixed_sel_toggle_var = tk.BooleanVar(value=False)
        self.fixed_sel_entry_var = tk.StringVar(value="1:1")
        self.fixed_sel_mode_var = tk.StringVar(value="Aspect Ratio")
        self.auto_aspect_var = tk.BooleanVar(value=False)
        self.auto_entry_var = tk.StringVar(value="1:1, 5:4, 4:5, 4:3, 3:4, 3:2, 2:3, 16:9, 9:16, 2:1, 1:2")

        # Label vars
        self.crop_info_label_var = tk.StringVar(value="Crop to: 0x0 (0:0)")
        self.img_stats_label_var = tk.StringVar(value="")
        self.thumb_time_label_var = tk.StringVar(value="0/0")
        self.img_index_label_var = tk.StringVar(value="0/0")


# ----------------------------
# UI
# ----------------------------
    def setup_window(self, parent, root):
        self.parent = parent
        self.root = root
        self.img_files = self.parent.image_files
        self.text_controller = self.parent.text_controller
        self.help_window = HelpWindow(self.root)
        # Window
        self.create_main_frame()
        self.setup_top_frame()
        self.create_img_ui()
        self.create_control_panel()
        self.crop_selection = CropSelection(self, self.img_canvas)
        self.img_canvas.crop_selection = self.crop_selection
        self.set_working_directory


    def create_main_frame(self):
        self.parent.crop_ui_tab.columnconfigure(0, weight=1)
        self.parent.crop_ui_tab.rowconfigure(0, weight=1)
        self.crop_ui_frame = tk.Frame(self.parent.crop_ui_tab)
        self.crop_ui_frame.grid(row=0, column=0, sticky="nsew")
        self.crop_ui_frame.grid_rowconfigure(0, weight=0)
        self.crop_ui_frame.grid_rowconfigure(1, weight=0)
        self.crop_ui_frame.grid_rowconfigure(2, weight=1)
        self.crop_ui_frame.grid_columnconfigure(0, weight=1)
        self.crop_ui_frame.grid_columnconfigure(1, weight=0)


    def setup_top_frame(self):
        frame = tk.Frame(self.crop_ui_frame)
        frame.grid(row=0, column=0, columnspan=99, sticky="nsew")
        frame.grid_columnconfigure(3, weight=1)
        # Crop Info
        ttk.Label(frame, textvariable=self.crop_info_label_var, anchor="w", width=25).grid(row=0, column=2, sticky="ew")
        # Directory
        dir_frame = tk.Frame(frame)
        dir_frame.grid(row=0, column=3, padx=(self.padx, 0), sticky="ew")
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_entry_var)
        dir_entry.pack(side="left", fill="x", expand=True)
        dir_entry
        self.entry_helper.setup_entry_binds(dir_entry)
        ttk.Button(dir_frame, text="Open", width=9, command=lambda: self.parent.open_directory(self.dir_entry_var.get())).pack(side="left")
        ttk.Button(dir_frame, text="Refresh", width=9, command=self.refresh_files).pack(side="left")
        # Help
        help_btn = ttk.Button(frame, text="?", width=2, command=self.open_help_window)
        help_btn.grid(row=0, column=4, padx=2, sticky="e")
        ToolTip.create(help_btn, "Show/Hide Help", 50, 6, 12)


    def create_img_ui(self):
        # Image Stats
        frame = tk.Frame(self.crop_ui_frame)
        frame.grid(row=1, column=0, sticky="ew", pady=self.pady)
        ttk.Label(frame, textvariable=self.img_stats_label_var, anchor="w").grid(row=0, column=0, sticky="ew")
        # Image Canvas
        img_frame = tk.Frame(self.crop_ui_frame)
        img_frame.grid(row=2, column=0, sticky="nsew")
        img_frame.grid_rowconfigure(0, weight=1)
        img_frame.grid_columnconfigure(0, weight=1)
        self.img_canvas = ImageCanvas(self, img_frame)
        self.img_canvas.grid(row=0, column=0, sticky="nsew")
        # GIF Thumbnails
        self.thumb_frame = tk.Frame(img_frame)
        self.thumb_frame.grid(row=1, column=0, sticky="ew")
        self.thumb_frame.columnconfigure(0, weight=1)
        self.thumb_frame.columnconfigure(1, weight=0)
        self.thumb_canvas = tk.Canvas(self.thumb_frame, height=72)
        self.thumb_canvas.grid(row=0, column=0, columnspan=99, sticky="ew")
        thumb_scroll = ttk.Scrollbar(self.thumb_frame, orient="horizontal", command=self.thumb_canvas.xview)
        thumb_scroll.grid(row=1, column=0, columnspan=99, sticky="ew")
        self.thumb_canvas.configure(xscrollcommand=thumb_scroll.set)
        self.thumbnail_frame = tk.Frame(self.thumb_canvas)
        self.thumb_canvas.create_window((0, 0), window=self.thumbnail_frame, anchor='nw')
        self.thumbnail_frame.bind("<Configure>", lambda event: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))
        thumb_scroll.bind("<MouseWheel>", lambda event: self.thumb_canvas.xview_scroll(-1 * (event.delta // 120), "units"))
        self.thumb_timeline = ttk.Scale(self.thumb_frame, from_=0, to=0, orient="horizontal", command=self.thumbnail_timeline_changed)
        self.thumb_timeline.grid(row=2, column=0, sticky="ew", padx=self.padx)
        ttk.Label(self.thumb_frame, textvariable=self.thumb_time_label_var).grid(row=2, column=1, sticky="e")
        self.thumb_frame.grid_remove()


    def create_control_panel(self):
        self.control_frame = tk.Frame(self.crop_ui_frame, relief="sunken", borderwidth=1)
        self.control_frame.grid(row=1, column=1, sticky="nsew", rowspan=2, pady=self.pady)
        self.create_nav_and_crop_widgets()
        self.spin_frame = tk.Frame(self.control_frame)
        self.spin_frame.pack(pady=self.pady, padx=self.padx, fill="x")
        self.create_size_widgets()
        self.create_position_widgets()
        self.create_selection_widgets()
        self.create_option_widgets()
        self.create_transform_widgets()


    def create_nav_and_crop_widgets(self):
        frame = tk.Frame(self.control_frame)
        frame.pack(pady=self.pady, padx=self.padx, fill="x")
        # After Crop menu
        menubutton = ttk.Menubutton(frame, text="After Crop")
        menubutton.pack(side="left", padx=(2,0), pady=self.pady, fill="x", expand=True)
        menu = tk.Menu(menubutton, tearoff=0)
        menubutton.config(menu=menu)
        menu.add_radiobutton(label="Save & Close", variable=self.after_crop_var, value="Save & Close")
        menu.add_radiobutton(label="Save & Next", variable=self.after_crop_var, value="Save & Next")
        menu.add_radiobutton(label="Save As...", variable=self.after_crop_var, value="Save As...")
        menu.add_radiobutton(label="Save", variable=self.after_crop_var, value="Save")
        menu.add_separator()
        menu.add_radiobutton(label="Overwrite", variable=self.after_crop_var, value="Overwrite")
        # Index
        index_frame = tk.Frame(frame)
        index_frame.pack(side="left", padx=5, pady=self.pady, fill="x", expand=True)
        self.img_index_spin = ttk.Spinbox(index_frame, from_=1, to=len(self.img_files), width=5, command=self.img_index_changed)
        self.img_index_spin.pack(side="left", fill="x", expand=True)
        self.img_index_spin.bind("<Return>", self.img_index_changed)
        self.entry_helper.setup_entry_binds(self.img_index_spin)
        ttk.Label(index_frame, textvariable=self.img_index_label_var).pack(side="left")
        # Nav Buttons
        nav_btn_frame = tk.Frame(self.control_frame)
        nav_btn_frame.pack(pady=self.pady, padx=self.padx, fill="x")
        ttk.Button(nav_btn_frame, text="<---Previous", command=self.show_previous_img).pack(side="left", fill="x", expand=True)
        ttk.Button(nav_btn_frame, text="Next--->", command=self.show_next_img).pack(side="left", fill="x", expand=True)
        # Crop Button
        ttk.Button(self.control_frame, text="Crop Selection", command=self.crop_img).pack(fill="x", pady=self.pady, padx=self.padx)


    def create_size_widgets(self):
        frame = ttk.LabelFrame(self.spin_frame, text="Size")
        frame.pack(side="left", fill="x", padx=(0,2), expand=True)
        frame.columnconfigure(1, weight=1)
        # Width
        width_label = ttk.Label(frame, text="W (px):")
        width_label.grid(row=0, column=0, padx=self.padxl, pady=self.pady, sticky='w')
        ToolTip(width_label, "Width of selection in pixels", 200, 6, 12)
        self.width_spin = ttk.Spinbox(frame, from_=1, to=9999, width=7, command=self.adjust_selection)
        self.width_spin.grid(row=0, column=1, padx=self.padxr, pady=self.pady, sticky='e')
        self.width_spin.set(0)
        self.width_spin.bind("<Return>", self.adjust_selection)
        self.width_spin.bind("<MouseWheel>", self.focus_widget_and_adjust_selection)
        self.entry_helper.setup_entry_binds(self.width_spin)
        # Height
        height_label = ttk.Label(frame, text="H (px):")
        height_label.grid(row=1, column=0, padx=self.padxl, pady=self.pady, sticky='w')
        ToolTip(height_label, "Height of selection in pixels", 200, 6, 12)
        self.height_spin = ttk.Spinbox(frame, from_=1, to=9999, width=7, command=self.adjust_selection)
        self.height_spin.grid(row=1, column=1, padx=self.padxr, pady=self.pady, sticky='e')
        self.height_spin.set(0)
        self.height_spin.bind("<Return>", self.adjust_selection)
        self.height_spin.bind("<MouseWheel>", self.focus_widget_and_adjust_selection)
        self.entry_helper.setup_entry_binds(self.height_spin)


    def create_position_widgets(self):
        frame = ttk.LabelFrame(self.spin_frame, text="Position")
        frame.pack(side="left", fill="x", padx=(2,0), expand=True)
        frame.columnconfigure(1, weight=1)
        # X Position
        pos_x_label = ttk.Label(frame, text="X (px):")
        pos_x_label.grid(row=0, column=0, padx=self.padxl, pady=self.pady, sticky='w')
        ToolTip(pos_x_label, "X coordinate of selection in pixels (From top left corner)", 200, 6, 12)
        self.pos_x_spin = ttk.Spinbox(frame, from_=0, to=9999, width=7, command=self.adjust_selection)
        self.pos_x_spin.grid(row=0, column=1, padx=self.padxr, pady=self.pady, sticky='e')
        self.pos_x_spin.set(0)
        self.pos_x_spin.bind("<Return>", self.adjust_selection)
        self.pos_x_spin.bind("<MouseWheel>", self.focus_widget_and_adjust_selection)
        self.entry_helper.setup_entry_binds(self.pos_x_spin)
        # Y Position
        pos_y_label = ttk.Label(frame, text="Y (px):")
        pos_y_label.grid(row=1, column=0, padx=self.padxl, pady=self.pady, sticky='w')
        ToolTip(pos_y_label, "Y coordinate of selection in pixels (From top left corner)", 200, 6, 12)
        self.pos_y_spin = ttk.Spinbox(frame, from_=0, to=9999, width=7, command=self.adjust_selection)
        self.pos_y_spin.grid(row=1, column=1, padx=self.padxr, pady=self.pady, sticky='e')
        self.pos_y_spin.set(0)
        self.pos_y_spin.bind("<Return>", self.adjust_selection)
        self.pos_y_spin.bind("<MouseWheel>", self.focus_widget_and_adjust_selection)
        self.entry_helper.setup_entry_binds(self.pos_y_spin)


    def create_selection_widgets(self):
        frame = ttk.LabelFrame(self.control_frame, text="Fixed Selection")
        frame.pack(pady=self.pady, padx=self.padx, fill="x")
        frame.columnconfigure(1, weight=1)
        # Fixed selection
        fixed_sel_check = ttk.Checkbutton(frame, variable=self.fixed_sel_toggle_var, text="Fixed", command=self.toggle_widgets_by_mode)
        fixed_sel_check.grid(row=0, column=0, padx=self.padxl, pady=self.pady, sticky="w")
        ToolTip(fixed_sel_check, "Enable fixed aspect ratio, width, height, or size", 200, 6, 12)
        # Fixed selection Combobox
        fixed_sel_combo = ttk.Combobox(frame, values=["Aspect Ratio", "Width", "Height", "Size"], textvariable=self.fixed_sel_mode_var, state="readonly", width=16)
        fixed_sel_combo.grid(row=0, column=1, columnspan=99, sticky="e", padx=self.pady, pady=self.pady)
        fixed_sel_combo.bind("<<ComboboxSelected>>", self.toggle_widgets_by_mode)
        fixed_sel_combo.bind("<MouseWheel>", self.toggle_widgets_by_mode)
        ToolTip(fixed_sel_combo, "Choose what to be fixed", 200, 6, 12)
        # Auto Mode
        self.auto_aspect_check = ttk.Checkbutton(frame, text="Auto", variable=self.auto_aspect_var, command=self.update_auto_entry_state, state="disabled")
        self.auto_aspect_check.grid(row=1, column=0, padx=self.padxl, pady=self.pady, sticky="w")
        ToolTip(self.auto_aspect_check, "Automatically select the best aspect ratio for the selection based on the predefined ratios and the aspect ratio of the displayed image.\n\n'Fixed' and 'Aspect Ratio' must be enabled!", 200, 6, 12, wraplength=240)
        # Error Pip
        self.sel_error_pip = tk.Label(frame)
        self.sel_error_pip.grid(row=1, column=1, pady=self.pady, sticky="w")
        self.selection_error_pip_tooltip = ToolTip(self.sel_error_pip, 100, 6, 12, state="disabled")
        # Selection Entry
        self.fixed_sel_entry = ttk.Entry(frame, textvariable=self.fixed_sel_entry_var, width=12)
        self.fixed_sel_entry.grid(row=1, column=2, padx=self.pady, pady=self.pady, sticky="ew")
        self.fixed_selection_entry_tooltip = ToolTip(self.fixed_sel_entry, "Enter a ratio 'W:H' or a decimal '1.0'", 200, 6, 12)
        self.fixed_sel_entry.bind("<KeyRelease>", lambda event: self.update_widget_values(resize=True))
        self.entry_helper.setup_entry_binds(self.fixed_sel_entry)
        # Insert Button
        insert_btn = ttk.Button(frame, text="<", width=1, command=self.insert_selection_dimension)
        insert_btn.grid(row=1, column=3, padx=self.pady, pady=self.pady, sticky="e")
        ToolTip(insert_btn, "Insert current selection dimensions relative to the selected mode", 200, 6, 12)
        # Auto Entry
        self.auto_entry = ttk.Entry(frame, textvariable=self.auto_entry_var, width=12, state="disabled")
        self.auto_entry.grid(row=3, column=0, columnspan=99, sticky="ew", padx=self.pady, pady=self.pady)
        self.entry_helper.setup_entry_binds(self.auto_entry)
        ToolTip(self.auto_entry, "Enter aspect ratios separated by commas. As a ratio: 'W:H', or a decimal: '1.0'", 200, 6, 12)


    def create_option_widgets(self):
        frame = ttk.LabelFrame(self.control_frame, text="Options")
        frame.pack(pady=self.pady, padx=self.padx, fill="x")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        check_frame = tk.Frame(frame)
        check_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        check_frame.columnconfigure(0, weight=1)
        # Expand From Center
        expand_from_center_check = ttk.Checkbutton(check_frame, variable=self.expand_center_var, text="Expand from Center")
        expand_from_center_check.grid(row=0, column=0, padx=self.padxl, pady=self.pady, sticky="w")
        ToolTip(expand_from_center_check, "Expand selection from center outwards", 200, 6, 12)
        # Highlight/Overlay
        overlay_check = ttk.Checkbutton(check_frame, variable=self.overlay_var, text="Highlight", command=self.toggle_overlay)
        overlay_check.grid(row=0, column=1, padx=self.padxl, pady=self.pady, sticky="e")
        ToolTip(overlay_check, "Toggle the overlay/highlight that darkens the background during selection", 200, 6, 12)
        # Guidelines
        ttk.Label(frame, text="Guidelines:").grid(row=1, column=0, padx=self.padxl, pady=self.pady, sticky="w")
        self.guideline_combo = ttk.Combobox(frame, values=["None", "Crosshair", "Center Lines", "Rule of Thirds", "Diagonal Lines"], textvariable=self.guidelines_var, state="readonly", width=16)
        self.guideline_combo.grid(row=1, column=1, padx=self.pady, pady=self.pady, sticky="ew")
        self.guideline_combo.bind("<<ComboboxSelected>>", lambda event: self.crop_selection.guideline_manager.update_guidelines(self.guidelines_var.get()))


    def create_transform_widgets(self):
        frame = ttk.LabelFrame(self.control_frame, text="Transform")
        frame.pack(pady=self.pady, padx=self.padx, fill="x")
        # Rotate
        ttk.Button(frame, text="Rotate", command=lambda: self.transform_img("rotate_270")).pack(side="left", fill="x", pady=self.pady, padx=2)
        # Flip
        ttk.Button(frame, text="Flip X", command=lambda: self.transform_img("flip_x")).pack(side="left", fill="x", pady=self.pady, padx=2)
        ttk.Button(frame, text="Flip Y", command=lambda: self.transform_img("flip_y")).pack(side="left", fill="x", pady=self.pady, padx=2)
        # Extract GIF
        self.extract_gif_button = ttk.Button(frame, text="Extract GIF", state="disable", command=self.save_all_gif_frames)
        self.extract_gif_button.pack(side="left", fill="x", pady=self.pady, padx=2)


# ----------------------------
# UI Helpers
# ----------------------------
    def update_widget_values(self, label=False, resize=False):
        def update_label(aspect_ratio):
            width = int(self.width_spin.get())
            height = int(self.height_spin.get())
            max_width = self.img_canvas.original_img_width
            max_height = self.img_canvas.original_img_height
            display_width = min(width, max_width)
            display_height = min(height, max_height)
            self.crop_info_label_var.set(f"Crop to: {display_width}x{display_height} ({aspect_ratio:.2f})")
            self.selection_aspect = round(aspect_ratio, 2)
            self.pos_x_spin.config(to=max_width - display_width)
            self.pos_y_spin.config(to=max_height - display_height)

        def set_spin_values(width, height, aspect_ratio):
            self.width_spin.set(width)
            self.height_spin.set(height)
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
                        ratio_width, ratio_height = map(float, value.split(':'))
                        aspect_ratio = ratio_width / ratio_height
                    else:
                        aspect_ratio = float(value)
                    width = int(height * aspect_ratio)
                set_spin_values(width, height, width / height if height != 0 else 0)
            except ValueError:
                self.width_spin.set(0)
                self.height_spin.set(0)
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
            self.pos_x_spin.set(x)
            self.pos_y_spin.set(y)
            if resize:
                if self.fixed_sel_toggle_var.get():
                    handle_fixed_selection(self.fixed_sel_entry_var.get(), width, height)
                else:
                    set_spin_values(width, height, aspect_ratio)
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
            entry.set(self.width_spin.get())
        elif mode == "Height":
            entry.set(self.height_spin.get())
        elif mode == "Size":
            entry.set(f"{self.width_spin.get()} x {self.height_spin.get()}")


    def focus_widget_and_adjust_selection(self, event):
        event.widget.focus_set()
        self.adjust_selection(event)


    def toggle_widgets_by_mode(self, event=None):
        width = self.width_spin
        height = self.height_spin
        message_map = {
            "Aspect Ratio": "Enter a ratio 'W:H' or a decimal '1.0'",
            "Width": "Enter a whole number",
            "Height": "Enter a whole number",
            "Size": "Enter 'W x H' OR 'W , H'"
        }
        if self.fixed_sel_toggle_var.get():
            state_map = {
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
            self.auto_aspect_check.config(state="normal")
            self.update_auto_entry_state()
        else:
            self.auto_aspect_check.config(state="disabled")
            self.auto_aspect_var.set(False)
            self.update_auto_entry_state()
        self.fixed_selection_entry_tooltip.config(text=message_map.get(self.fixed_sel_mode_var.get(), ""))


    def set_error_pip_color(self, state=None, message=None, event=None):
        if state == "error":
            self.sel_error_pip.config(bg="#fd8a8a")
            self.selection_error_pip_tooltip.config(state="normal", text=message)
        if state == "normal":
            self.sel_error_pip.config(bg="SystemButtonFace")
            self.selection_error_pip_tooltip.config(state="disabled")


    def update_auto_entry_state(self):
        if self.fixed_sel_toggle_var.get() and self.fixed_sel_mode_var.get() == "Aspect Ratio":
            if self.auto_aspect_var.get():
                self.auto_entry.config(state="normal")
                self.fixed_sel_entry.config(state="disabled")
            else:
                self.auto_entry.config(state="disabled")
                self.fixed_sel_entry.config(state="normal")
        else:
            self.auto_entry.config(state="disabled")
            self.fixed_sel_entry.config(state="normal")


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
        img_ratio = round(width / height, 2)
        closest_ratio = min(ratio_list, key=lambda x: abs(x - img_ratio))
        self.fixed_sel_entry.config(state="normal")
        self.fixed_sel_entry_var.set(str(closest_ratio))
        self.fixed_sel_entry.config(state="disabled")


    def img_index_changed(self, event=None, index=None):
        try:
            if not index:
                index = int(self.img_index_spin.get()) - 1
            if 0 <= index < len(self.img_files):
                self.current_index = index
                self.display_img(self.img_files[self.current_index])
        except ValueError:
            pass


    def set_working_directory(self, path=None):
        if path is None:
            path = filedialog.askdirectory(initialdir=self.working_dir)
            if not os.path.isdir(path):
                return
            self.working_dir = path
        else:
            self.working_dir = path
        self.dir_entry_var.set(self.parent.image_dir)
        self.img_files = self.parent.image_files
        self.img_index_label_var.set(f"of {len(self.img_files)}")
        self.current_index = self.parent.current_index
        self.display_img(self.img_files[self.current_index])


    def open_help_window(self):
        help_text = HelpText.CROP_UI_HELP
        self.help_window.open_window(geometry="500x700", help_text=help_text)


    def toggle_overlay(self):
        self.crop_selection.overlay_enabled = self.overlay_var.get()
        self.img_canvas.refresh_img()


# ----------------------------
# Main
# ----------------------------
    def refresh_tab(self):
        self.refresh_files()
        self.img_index_changed(index=self.parent.current_index)


    def refresh_files(self):
        current_path = self.dir_entry_var.get()
        if not os.path.exists(current_path):
            current_path = os.path.dirname(current_path)
        if os.path.isfile(current_path):
            current_path = os.path.dirname(current_path)

        if os.path.isdir(current_path):
            self.working_dir = current_path
            self.parent.refresh_file_lists()
            self.img_files = self.parent.image_files
            self.img_index_label_var.set(f"of {len(self.img_files)}")
            self.img_index_spin.config(from_=1, to=len(self.img_files))
            if self.current_index >= len(self.img_files):
                self.current_index = 0
            if self.img_files:
                self.display_img(self.img_files[self.current_index])
            else:
                self.img_canvas.delete("all")
                self.crop_selection.clear_selection()
                self.img_stats_label_var.set("No images found in directory")


    def display_img(self, img_path, logical_path=None):
        self.img_canvas._display_img(img_path)
        self.crop_selection.clear_selection()
        original_width, original_height = self.img_canvas.original_img.size
        displayed_width = self.img_canvas.winfo_width()
        percent_scale = int((displayed_width / original_width) * 100)
        self.update_imginfo(percent_scale)
        self.width_spin.config(to=self.img_canvas.original_img_width)
        self.height_spin.config(to=self.img_canvas.original_img_height)
        self.img_index_spin.config(from_=1, to=len(self.img_files))
        self.img_index_spin.set(self.current_index + 1)
        if logical_path is None:
            self.current_source_path = img_path
        else:
            self.current_source_path = logical_path
        self.dir_entry_var.set(self.current_source_path)
        if logical_path is None and self.current_source_path and self.current_source_path.lower().endswith('.gif'):
            self.extract_gif_frames()
            self.extract_gif_button.config(state="normal")
            self.highlight_thumbnail(index=0)
        else:
            if not (self.current_source_path and self.current_source_path.lower().endswith('.gif')):
                self.thumb_frame.grid_remove()
                self.extract_gif_button.config(state="disabled")


    def show_previous_img(self):
        if self.img_files:
            self.current_index = (self.current_index - 1) % len(self.img_files)
            self.display_img(self.img_files[self.current_index])


    def show_next_img(self):
        if self.img_files:
            self.current_index = (self.current_index + 1) % len(self.img_files)
            self.display_img(self.img_files[self.current_index])


    def crop_img(self):
        if not (self.img_canvas.img_path and self.crop_selection.coords):
            return
        width = int(self.width_spin.get())
        height = int(self.height_spin.get())
        pos_x = int(self.pos_x_spin.get())
        pos_y = int(self.pos_y_spin.get())
        max_width = self.img_canvas.original_img_width
        max_height = self.img_canvas.original_img_height
        display_width = min(width, max_width)
        display_height = min(height, max_height)
        coords = (pos_x, pos_y, pos_x + display_width, pos_y + display_height)
        cropped_img = self.img_canvas.original_img.crop(coords)
        self.after_crop_option(cropped_img)


    def after_crop_option(self, cropped_img):
        option = self.after_crop_var.get()
        source_path = self.current_source_path or self.img_canvas.img_path
        if option == "Save & Close":
            saved_path = self.save_cropped_img(cropped_img, 'normal', source_path)
            if saved_path:
                self.close_crop_ui(path=saved_path)
        elif option == "Save & Next":
            saved_path = self.save_cropped_img(cropped_img, 'normal', source_path)
            if saved_path:
                self.show_next_img()
        elif option == "Save As...":
            self.save_cropped_img(cropped_img, 'save_as')
        elif option == "Save":
            self.save_cropped_img(cropped_img, 'normal', source_path)
        elif option == "Overwrite":
            saved_path = self.save_cropped_img(cropped_img, 'overwrite', source_path)
            if saved_path:
                pass


    def save_cropped_img(self, cropped_img, save_mode, original_path=None):
        try:
            if save_mode == 'normal':
                save_path = self.generate_unique_filename(original_path)
            elif save_mode == 'save_as':
                save_path = filedialog.asksaveasfilename(defaultextension=".png")
                if not save_path:
                    return False
                root, ext = os.path.splitext(save_path)
                if ext.lower() != ".png":
                    save_path = root + ".png"
            elif save_mode == 'overwrite':
                confirm = messagebox.askyesno("Confirm Overwrite", "Are you sure you want to overwrite the original image?")
                if not confirm:
                    return False
                directory, filename = os.path.split(original_path)
                name, ext = os.path.splitext(filename)
                save_path = os.path.join(directory, f"{name}.png")
            else:
                return False
            cropped_img.save(save_path, format="PNG")
            if save_mode == 'overwrite':
                try:
                    if original_path and os.path.normcase(original_path) != os.path.normcase(save_path) and os.path.exists(original_path):
                        os.remove(original_path)
                except Exception as del_err:
                    messagebox.showwarning("Overwrite Warning", f"Could not remove original file:\n{original_path}\n\n{del_err}")
                if hasattr(self, 'parent') and hasattr(self.parent, 'refresh_file_lists'):
                    self.parent.refresh_file_lists()
                    self.img_files = self.parent.image_files
                self.img_canvas._display_img(save_path)
                self.crop_selection.clear_selection()
            return save_path
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save image: {str(e)}")
            return False


    def generate_unique_filename(self, original_path):
        directory, filename = os.path.split(original_path)
        name, _ = os.path.splitext(filename)
        counter = 1
        while True:
            new_filename = f"{name}_crop_{counter}.png"
            new_filepath = os.path.join(directory, new_filename)
            if not os.path.exists(new_filepath):
                return new_filepath
            counter += 1


# ----------------------------
# Selection
# ----------------------------
    def adjust_selection(self, event=None):
        if event is None:
            widget = self.root.focus_get()
        else:
            widget = event.widget
        try:
            original_value = int(widget.get())
        except (AttributeError, ValueError):
            return
        spin_map = {
            self.width_spin: 'width',
            self.height_spin: 'height',
            self.pos_x_spin: 'new_x',
            self.pos_y_spin: 'new_y'
        }
        scale = self.img_canvas.img_scale_ratio
        scaled_value = int(original_value * scale)
        kwargs = {spin_map[widget]: scaled_value, 'original_value': original_value}
        self.crop_selection.set_selection_dimensions(**kwargs)
        self.update_widget_values(label=True)


# ----------------------------
# Transform Image
# ----------------------------
    def transform_img(self, mode):
        path = self.img_files[self.current_index]
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
        self.img_canvas._display_img(self.img_canvas.img_path)
        self.crop_selection.clear_selection()


    def process_gif_frames(self, img, path, transform_function):
        frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
        transformed_frames = [transform_function(frame) for frame in frames]
        durations = [frame.info.get('duration', 34) for frame in frames]
        first_frame = transformed_frames[0]
        rest_frames = transformed_frames[1:]
        first_frame.save(path, append_images=rest_frames, save_all=True, duration=durations, loop=0)


# ----------------------------
# Handle GIF
# ----------------------------
    def save_all_gif_frames(self):
        confirm = messagebox.askyesno("Extract GIF Frames",
            "Are you sure you want to extract all frames from the GIF?\n\n"
            "This will create a folder with all the frames in the same directory as the GIF.\n\n"
            "Please be patient, depending on the number of frames, this may take a while."
        )
        if not confirm:
            return
        if not self.current_source_path or not self.current_source_path.lower().endswith('.gif'):
            messagebox.showerror("Error", "No GIF file selected.")
            return
        try:
            frames = self.extract_gif_frames(display=False)
            base_path, _ = os.path.splitext(self.current_source_path)
            folder_path = f"{base_path}_frames"
            os.makedirs(folder_path, exist_ok=True)
            for i, frame in enumerate(frames):
                frame = frame.convert("RGBA")
                frame_path = os.path.join(folder_path, f"frame_{i:04d}.png")
                frame.save(frame_path)
            frame_count = len(frames)
            final_confirm = messagebox.askokcancel("Extract GIF Frames",
                f"All {frame_count} frames extracted and saved to:\n{folder_path}\n\n"
                "Click 'OK' to open the folder."
            )
            if final_confirm:
                os.startfile(folder_path)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while extracting GIF frames: {e}")


    def extract_gif_frames(self, display=True, event=None):
        if not self.current_source_path or not self.current_source_path.lower().endswith('.gif'):
            return []
        try:
            with Image.open(self.current_source_path) as img:
                self.gif_frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(img)]
                if display:
                    self.display_gif_thumbnails(self.gif_frames)
                    self.thumb_time_label_var.set(f"01/{len(self.gif_frames)}")
                return self.gif_frames
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while extracting frames: {e}")
            return []


    def display_gif_thumbnails(self, frames):
        def save_and_display_frame(img, index):
            try:
                trash_folder = os.path.join(os.path.dirname(self.current_source_path), "Trash")
                os.makedirs(trash_folder, exist_ok=True)
                filename = os.path.basename(self.img_files[self.current_index])
                save_img_path = os.path.join(trash_folder, f"{filename}.png")
                img.save(save_img_path)
                self.display_img(save_img_path, logical_path=self.img_files[self.current_index])
                self.highlight_thumbnail(index)
                self.thumb_timeline.set(index)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while saving the image: {e}")
        for widget in self.thumbnail_frame.winfo_children():
            widget.destroy()
        self.thumb_frame.grid()
        self.thumb_timeline.configure(to=len(frames)-1)
        self.thumb_timeline.set(0)
        fixed_height = 64
        for i, frame in enumerate(frames):
            thumb = frame.copy()
            aspect_ratio = thumb.width / thumb.height
            new_width = int(fixed_height * aspect_ratio)
            thumb = thumb.resize((new_width, fixed_height), Image.BILINEAR)
            thumb_img = ImageTk.PhotoImage(thumb)
            thumb_btn = ttk.Button(self.thumbnail_frame, image=thumb_img, takefocus=False)
            thumb_btn.image = thumb_img
            thumb_btn.bind("<Button-1>", lambda e, img=frame, index=i: save_and_display_frame(img, index))
            thumb_btn.bind("<MouseWheel>", lambda event: self.thumb_canvas.xview_scroll(-1 * (event.delta // 120), "units"))
            thumb_btn.pack(side='left')
        if frames:
            save_and_display_frame(frames[0], 0)


    def highlight_thumbnail(self, index):
        for i, widget in enumerate(self.thumbnail_frame.winfo_children()):
            widget.config(style="TButton")
            if i == index:
                widget.config(style="Highlighted.TButton")


    def thumbnail_timeline_changed(self, event=None):
        if not self.gif_frames:
            return
        try:
            index = int(float(self.thumb_timeline.get()))
            frame = self.gif_frames[index]
            trash_folder = os.path.join(os.path.dirname(self.current_source_path), "Trash")
            os.makedirs(trash_folder, exist_ok=True)
            filename = os.path.basename(self.img_files[self.current_index])
            save_img_path = os.path.join(trash_folder, f"{filename}.png")
            frame.save(save_img_path)
            self.display_img(save_img_path, logical_path=self.img_files[self.current_index])
            self.highlight_thumbnail(index)
            self.ensure_thumbnail_visible(index)
            padded_index = str(index + 1).zfill(len(str(len(self.gif_frames))))
            self.thumb_time_label_var.set(f"{padded_index}/{len(self.gif_frames)}")
        except (ValueError, IndexError) as e:
            messagebox.showerror("Error", f"An error occurred while changing the frame: {e}")


    def ensure_thumbnail_visible(self, index):
        thumbnail_widgets = self.thumbnail_frame.winfo_children()
        if index < 0 or index >= len(thumbnail_widgets):
            return
        widget = thumbnail_widgets[index]
        widget_x = widget.winfo_x()
        widget_width = widget.winfo_width()
        canvas_x = self.thumb_canvas.canvasx(0)
        canvas_width = self.thumb_canvas.winfo_width()
        if widget_x < canvas_x:
            self.thumb_canvas.xview_moveto(widget_x / self.thumb_canvas.bbox("all")[2])
        elif widget_x + widget_width > canvas_x + canvas_width:
            self.thumb_canvas.xview_moveto((widget_x + widget_width - canvas_width) / self.thumb_canvas.bbox("all")[2])


# ----------------------------
# Image Info
# ----------------------------
    def update_imginfo(self, percent_scale=0):
        if self.img_files:
            self.img_file = self.img_files[self.current_index]
            if self.img_file not in self.img_info_cache:
                self.img_info_cache[self.img_file] = self.get_img_info(self.img_file)
            img_info = self.img_info_cache[self.img_file]
            self.img_stats_label_var.set(f"{img_info['filename']}  |  {img_info['resolution']}  |  {percent_scale}%  |  {img_info['size']}  |  {img_info['color_mode']}")


    def get_img_info(self, img_file):
        img = self.img_canvas.original_img
        width, height = img.size
        color_mode = img.mode
        size = os.path.getsize(img_file)
        size_kb = size / 1024
        size_str = f"{round(size_kb)} KB" if size_kb < 1024 else f"{round(size_kb / 1024, 2)} MB"
        filename = os.path.basename(img_file)
        filename = (filename[:61] + '(...)') if len(filename) > 64 else filename
        return {"filename": filename, "resolution": f"{width}x{height}", "size": size_str, "color_mode": color_mode}


# ----------------------------
# Close CropUI
# ----------------------------
    def close_crop_ui(self, path=None, event=None):
        self.parent.refresh_text_box()
        self.parent.refresh_file_lists()
        self.parent.debounce_update_thumbnail_panel()
        if path:
            index = (self.parent.get_image_index_by_filename(path) + 1)
            self.parent.jump_to_image(index)
        self.parent.main_notebook.select(self.parent.primary_tab)


#endregion
