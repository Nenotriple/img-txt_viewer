"""
########################################
#                                      #
#             Crop Image UI            #
#                                      #
#   Version : v1.00                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
Crop an image to a square.

More info here: https://github.com/Nenotriple/img-txt_viewer

"""

#endregion
################################################################################################################################################
#region -  Imports


import os
import sys
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk


#endregion
################################################################################################################################################
#region -  Class Setup


class Crop:
    def __init__(self, root, filepath):
        self.root = root
        self.top = Toplevel(self.root)
        self.image_path = filepath
        self.rect = None
        self.state = None
        self.start_x = None
        self.start_y = None
        self.rect_center = None
        self.prompt_small_crop_var = True
        self.rect_size = 0
        self.free_crop_var = BooleanVar(value=False)
        self.set_icon()
        self.create_image()
        self.create_canvas()
        self.create_context_menu()
        self.setup_window()


        self.top.bind('<space>', self.crop_image)


#endregion
################################################################################################################################################
#region -  Interface Setup


    def set_icon(self):
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(__file__)
        icon_path = os.path.join(application_path, "icon.ico")
        try:
            self.top.iconbitmap(icon_path)
        except TclError: pass


    def create_image(self):
        self.original_image = Image.open(self.image_path)
        self.image = self.original_image.copy()
        self.max_size = (1024, 1024)
        self.scale_factor = max(1, max([round(original_dim / max_dim) for original_dim, max_dim in zip(self.original_image.size, self.max_size)]))
        self.image.thumbnail((self.original_image.size[0] // self.scale_factor, self.original_image.size[1] // self.scale_factor), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.image)


    def create_canvas(self):
        self.canvas = tk.Canvas(self.top, width=self.tk_image.width(), height=self.tk_image.height())
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<Double-1>", self.on_double_click)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)


    def create_context_menu(self, event=None):
        def show_menu(event):
            self.context_menu.tk_popup(event.x_root, event.y_root)
        self.canvas.bind("<Button-3>", show_menu)
        self.context_menu = tk.Menu(self.top, tearoff=0)
        self.context_menu.add_command(label="Crop", accelerator="(Spacebar)", command=self.crop_image)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Clear", command=self.destroy_rectangle)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Open Directory...", command=lambda: self.open_directory(os.path.dirname(self.image_path)))
        self.context_menu.add_checkbutton(label="Freeform Crop", variable=self.free_crop_var)


    def setup_window(self):
        self.top.resizable(False, False)
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() - self.tk_image.width()) / 2
        y = (self.top.winfo_screenheight() - self.tk_image.height()) / 2
        self.top.geometry("+%d+%d" % (x, y))
        self.top.title(f"Crop Image  |  {os.path.basename(self.image_path)}  |  (0 x 0)")


    def update_title(self):
        if self.rect:
            rect_coords = self.canvas.coords(self.rect)
            x_scale = self.original_image.width / self.tk_image.width()
            y_scale = self.original_image.height / self.tk_image.height()
            width = abs(rect_coords[2] - rect_coords[0]) * x_scale
            height = abs(rect_coords[3] - rect_coords[1]) * y_scale
            if self.free_crop_var:
                self.rect_size = (width, height)
                self.top.title(f"Crop Image  |  {os.path.basename(self.image_path)}  |  ({int(width)} x {int(height)})")
            else:
                self.rect_size = min(width, height)
                self.top.title(f"Crop Image  |  {os.path.basename(self.image_path)}  |  ({int(self.rect_size)} x {int(self.rect_size)})")


#endregion
################################################################################################################################################
#region -  Handle rectangle creation and positioning


####### Input setup ##################################################


    def on_button_press(self, event):
        if self.rect and self.is_within_rectangle(event.x, event.y):
            self.start_dragging(event)
        else:
            self.start_drawing(event)


    def on_move_press(self, event):
        if self.state == "is_dragging":
            self.drag(event)
        elif self.state == "is_drawing":
            self.draw(event)
        self.update_title()


    def on_double_click(self, event):
        self.create_rectangle_based_on_image_size()


    def is_within_rectangle(self, x, y):
        rect_coords = self.canvas.coords(self.rect)
        return rect_coords[0] < x < rect_coords[2] and rect_coords[1] < y < rect_coords[3]


    def on_mouse_wheel(self, event):
        if self.rect and self.is_within_rectangle(event.x, event.y):
            rect_coords = self.canvas.coords(self.rect)
            if self.scale_factor == 1:
                new_size = max(512, rect_coords[2] - rect_coords[0] + event.delta//15)
            else:
                new_size = max(256, rect_coords[2] - rect_coords[0] + event.delta//15)
            center_x = (rect_coords[2] + rect_coords[0]) // 2
            center_y = (rect_coords[3] + rect_coords[1]) // 2
            new_coords = [center_x - new_size // 2, center_y - new_size // 2, center_x + new_size // 2, center_y + new_size // 2]
            self.resize_rectangle(new_coords, new_size, center_x, center_y)


####### Drawing ##################################################


    def start_drawing(self, event):
        self.destroy_rectangle()
        self.state = "is_drawing"
        self.start_x = event.x
        self.start_y = event.y


    def draw(self, event):
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=4)
            self.canvas.itemconfig(self.rect, fill='black', stipple='gray12')
        else:
            cur_width = event.x - self.start_x
            cur_height = event.y - self.start_y
            if self.free_crop_var.get() == True:
                curX = min(max(0, self.start_x + cur_width), self.tk_image.width())
                curY = min(max(0, self.start_y + cur_height), self.tk_image.height())
            else:
                cur_size = min(abs(cur_width), abs(cur_height))
                cur_size = self.snap_to_points(cur_size)
                curX = min(max(0, self.start_x + (cur_size if cur_width >= 0 else -cur_size)), self.tk_image.width())
                curY = min(max(0, self.start_y + (cur_size if cur_height >= 0 else -cur_size)), self.tk_image.height())
            if curX <= 0 or curY <= 0 or curX >= self.tk_image.width() or curY >= self.tk_image.height():
                return
            self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)


    def snap_to_points(self, cur_size):
        snap_points = [1024, 768, 512, 256]
        snap_distance = 16
        for snap_point in snap_points:
            if snap_point - snap_distance < cur_size < snap_point + snap_distance:
                return snap_point
            elif cur_size > snap_point + snap_distance:
                break
        return cur_size


####### Dragging ##################################################


    def start_dragging(self, event):
        self.state = "is_dragging"
        rect_coords = self.canvas.coords(self.rect)
        self.rect_center = ((rect_coords[2] + rect_coords[0]) / 2, (rect_coords[3] + rect_coords[1]) / 2)
        self.start_x = event.x - self.rect_center[0]
        self.start_y = event.y - self.rect_center[1]


    def drag(self, event):
        dx = event.x - self.start_x - self.rect_center[0]
        dy = event.y - self.start_y - self.rect_center[1]
        rect_coords = self.canvas.coords(self.rect)
        new_coords = [rect_coords[0] + dx, rect_coords[1] + dy, rect_coords[2] + dx, rect_coords[3] + dy]
        new_coords[0] = max(min(new_coords[0], self.tk_image.width() - (rect_coords[2] - rect_coords[0])), 0)
        new_coords[1] = max(min(new_coords[1], self.tk_image.height() - (rect_coords[3] - rect_coords[1])), 0)
        new_coords[2] = min(max(new_coords[2], rect_coords[2] - rect_coords[0]), self.tk_image.width())
        new_coords[3] = min(max(new_coords[3], rect_coords[3] - rect_coords[1]), self.tk_image.height())
        dx = new_coords[0] - rect_coords[0]
        dy = new_coords[1] - rect_coords[1]
        self.canvas.move(self.rect, dx, dy)
        self.rect_center = (self.rect_center[0] + dx, self.rect_center[1] + dy)


####### Resizing ##################################################


    def resize_rectangle(self, new_coords, new_size, center_x, center_y):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if (new_coords[0] >= 0 and new_coords[2] <= canvas_width and new_coords[1] >= 0 and new_coords[3] <= canvas_height):
            self.canvas.coords(self.rect, *new_coords)
        else:
            new_coords = [max(0, min(canvas_width - new_size, center_x - new_size // 2)),
                          max(0, min(canvas_height - new_size, center_y - new_size // 2)),
                          min(canvas_width, max(new_size, center_x + new_size // 2)),
                          min(canvas_height, max(new_size, center_y + new_size // 2))]
            if new_coords[0] == 0 and new_coords[2] == canvas_width or new_coords[1] == 0 and new_coords[3] == canvas_height:
                return
            self.canvas.coords(self.rect, *new_coords)
        self.update_title()


####### Create ##################################################


    def create_rectangle_based_on_image_size(self):
        self.destroy_rectangle()
        original_width, original_height = self.original_image.size
        if original_width <= 511 or original_height <= 511:
            return
        size = 256 if self.scale_factor == 2 else 512
        if original_width >= 1024 and original_height >= 1024:
            size = 512 if self.scale_factor == 2 else 1024
        self.create_rectangle(size)


    def create_rectangle(self, size):
        rect_size = size
        canvas_width = self.tk_image.width()
        canvas_height = self.tk_image.height()
        rect_x1 = max(0, (canvas_width - rect_size) // 2)
        rect_y1 = max(0, (canvas_height - rect_size) // 2)
        rect_x2 = min(canvas_width, rect_x1 + rect_size)
        rect_y2 = min(canvas_height, rect_y1 + rect_size)
        self.rect = self.canvas.create_rectangle(rect_x1, rect_y1, rect_x2, rect_y2, outline='red', width=4)
        self.canvas.itemconfig(self.rect, fill='black', stipple='gray12')
        self.update_title()


####### Flash Color ##################################################


    def flash_rectangle(self):
        def reset_color():
            if self.rect:
                self.canvas.itemconfig(self.rect, outline='red', width=4)
        self.canvas.itemconfig(self.rect, outline='teal', width=8)
        self.canvas.after(100, reset_color)


####### Destroy ##################################################


    def destroy_rectangle(self):
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None
            self.top.title(f"Crop Image  |  {os.path.basename(self.image_path)}  |  (0 x 0)")


#endregion
################################################################################################################################################
#region -  Misc


    def open_directory(self, directory):
        try:
            if os.path.isdir(directory):
                os.startfile(directory)
        except Exception: pass


#endregion
################################################################################################################################################
#region -  Crop and Save



    def crop_image(self, event=None):
        if self.rect:
            rect_coords = self.canvas.coords(self.rect)
            x_scale = self.original_image.width / self.tk_image.width()
            y_scale = self.original_image.height / self.tk_image.height()
            rect_coords = [int(coord * x_scale) if i % 2 == 0 else int(coord * y_scale) for i, coord in enumerate(rect_coords)]
            width = abs(rect_coords[2] - rect_coords[0])
            height = abs(rect_coords[3] - rect_coords[1])
            size = min(width, height)
            if self.check_crop_size(size, width, height) is False:
                return
            if self.free_crop_var.get():
                cropped_image = self.original_image.crop((rect_coords[0], rect_coords[1], rect_coords[2], rect_coords[3]))
            else:
                cropped_image = self.original_image.crop((rect_coords[0], rect_coords[1], rect_coords[0] + size, rect_coords[1] + size))
            self.save_image(cropped_image)
            self.flash_rectangle()


    def check_crop_size(self, size, width, height):
        if size <= 511 and self.prompt_small_crop_var:
            result = messagebox.askyesno("Confirm small crop size", f"You are about to create a small crop: ({width}x{height}).\nDo you want to continue?")
            if result is True:
                self.prompt_small_crop_var = False
                return True
            else:
                return False


    def save_image(self, cropped_image):
        directory, filename = os.path.split(self.image_path)
        filename, ext = os.path.splitext(filename)
        matching_files = [f for f in os.listdir(directory) if f.startswith(filename + "_crop") and f.endswith(ext)]
        count = len(matching_files) + 1
        new_filename = f"{filename}_crop{count:02d}{ext}"
        cropped_image.save(os.path.join(directory, new_filename), "JPEG", quality=100)
        self.top.title("Crop Image  |  Image Saved!")


#endregion