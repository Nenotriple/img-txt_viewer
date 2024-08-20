"""
########################################
#                                      #
#               PopUpZoom              #
#                                      #
#   Version : v1.01                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
Create a small popup window beside the mouse that displays a zoomed view of the image underneath.

"""

from tkinter import Toplevel, BooleanVar, Canvas
from PIL import Image, ImageTk

class PopUpZoom:
    def __init__(self, widget):
        # Initialize the PopUpZoom class
        self.widget = widget
        self.zoom_factor = 1.75
        self.min_zoom_factor = 0.5
        self.max_zoom_factor = 10.0
        self.max_image_size = 4096

        # Initialize image attributes
        self.image = None
        self.image_path = None
        self.original_image = None
        self.resized_image = None
        self.resized_width = 0
        self.resized_height = 0

        # Variables to store saved states
        self.saved_widget = None
        self.saved_image = None
        self.saved_image_path = None
        self.saved_original_image = None
        self.saved_resized_image = None
        self.saved_resized_width = 0
        self.saved_resized_height = 0

        # Initialize zoom enabled variable
        self.zoom_enabled = BooleanVar(value=False)

        # Set up the zoom window
        self.create_popup_window()

        # Bind events to the widget
        self.bind_events()

    def create_popup_window(self):
        self.popup_size = 400
        self.min_popup_size = 100
        self.max_popup_size = 600

        self.zoom_window = Toplevel(self.widget)
        self.zoom_window.withdraw()
        self.zoom_window.overrideredirect(True)
        self.zoom_window.wm_attributes("-transparentcolor", self.zoom_window["bg"])
        self.zoom_canvas = Canvas(self.zoom_window, width=self.popup_size, height=self.popup_size, highlightthickness=0, bg=self.zoom_window["bg"])
        self.zoom_canvas.pack()

    def bind_events(self):
        self.widget.bind("<Motion>", self.update_zoom, add="+")
        self.widget.bind("<Leave>", self.hide_zoom, add="+")
        self.widget.bind("<Button-1>", self.hide_zoom, add="+")
        self.widget.bind("<MouseWheel>", self.zoom, add="+")

    def set_image(self, image, path):
        '''Set the image and its path'''
        if self.image == image and self.image_path == path:
            return
        self.image = image
        self.image_path = path
        with open(self.image_path, 'rb') as img_file:
            self.original_image = Image.open(img_file)
            self.original_image.load()
        self.resize_original_image()

    def resize_original_image(self):
        '''Resize the original image if it's too large'''
        max_size = self.max_image_size
        if self.original_image.width > max_size or self.original_image.height > max_size:
            aspect_ratio = self.original_image.width / self.original_image.height
            if self.original_image.width > self.original_image.height:
                new_width = max_size
                new_height = int(max_size / aspect_ratio)
            else:
                new_height = max_size
                new_width = int(max_size * aspect_ratio)
            self.original_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)

    def set_resized_image(self, resized_image, resized_width, resized_height):
        '''Set the resized image and its dimensions'''
        self.resized_image = resized_image
        self.resized_width = resized_width
        self.resized_height = resized_height

    def create_zoomed_image(self, left, top, right, bottom):
        '''Create and display the zoomed image in the zoom window'''
        cropped_image = self.original_image.crop((left, top, right, bottom))
        aspect_ratio = cropped_image.width / cropped_image.height
        if aspect_ratio > 1:
            new_width = self.popup_size
            new_height = int(self.popup_size / aspect_ratio)
        else:
            new_height = self.popup_size
            new_width = int(self.popup_size * aspect_ratio)
        resize_method = Image.NEAREST if self.zoom_factor >= 4 else Image.LANCZOS
        zoomed_image = cropped_image.resize((new_width, new_height), resize_method)
        self.zoom_photo_image = ImageTk.PhotoImage(zoomed_image)
        self.zoom_canvas.delete("all")
        x = (self.popup_size - new_width) // 2
        y = (self.popup_size - new_height) // 2
        self.zoom_canvas.create_image(x, y, anchor="nw", image=self.zoom_photo_image)

    def calculate_coordinates(self, img_x, img_y):
        '''Calculate the coordinates for the zoomed image'''
        half_size = self.popup_size // (2 * self.zoom_factor)
        left = max(0, int(img_x - half_size))
        right = min(self.original_image.width, int(img_x + half_size))
        top = max(0, int(img_y - half_size))
        bottom = min(self.original_image.height, int(img_y + half_size))
        if right - left < self.popup_size // self.zoom_factor:
            left = max(0, right - self.popup_size // self.zoom_factor)
            right = min(self.original_image.width, left + self.popup_size // self.zoom_factor)
        if bottom - top < self.popup_size // self.zoom_factor:
            top = max(0, bottom - self.popup_size // self.zoom_factor)
            bottom = min(self.original_image.height, top + self.popup_size // self.zoom_factor)
        return left, top, right, bottom

    def update_zoom(self, event):
        '''Update the zoom window with the zoomed image'''
        if event is None:
            return
        if not self.zoom_enabled.get() or not (self.image and self.resized_image):
            return
        x, y = event.x, event.y
        screen_width, screen_height = self.widget.winfo_screenwidth(), self.widget.winfo_screenheight()
        new_x = event.x_root + self.popup_size // 10
        new_y = event.y_root - self.popup_size // 2
        if new_x + self.popup_size > screen_width:
            new_x = event.x_root - self.popup_size - 20
        elif new_x < 0:
            new_x = 0
        if new_y + self.popup_size > screen_height:
            new_y = screen_height - self.popup_size
        elif new_y < 0:
            new_y = 0
        self.zoom_window.geometry(f"+{new_x}+{new_y}")
        pad_x = (self.widget.winfo_width() - self.resized_width) / 2
        pad_y = (self.widget.winfo_height() - self.resized_height) / 2
        img_x = (x - pad_x) * self.original_image.width / self.resized_width
        img_y = (y - pad_y) * self.original_image.height / self.resized_height
        left, top, right, bottom = self.calculate_coordinates(img_x, img_y)
        if left < right and top < bottom:
            self.create_zoomed_image(left, top, right, bottom)
            self.zoom_window.deiconify()
        else:
            self.zoom_window.withdraw()

    def zoom(self, event):
        '''Adjust the zoom factor or popup size based on the mouse wheel event'''
        if event.state & 0x0001:  # Shift key is held
            self.popup_size += 20 if event.delta > 0 else -20
            self.popup_size = max(self.min_popup_size, min(self.popup_size, self.max_popup_size))
            self.zoom_canvas.config(width=self.popup_size, height=self.popup_size)
        else:
            min_zoom = self.min_zoom_factor
            max_zoom = self.max_zoom_factor
            self.zoom_factor += min_zoom if event.delta > 0 else -min_zoom
            self.zoom_factor = max(min_zoom, min(self.zoom_factor, max_zoom))
        self.update_zoom(event)

    def hide_zoom(self, event):
        '''Hide the zoom window'''
        self.zoom_window.withdraw()

    def unload(self):
        '''Save and clear references to images and widgets'''
        # Save the current state
        self.saved_widget = self.widget
        self.saved_image = self.image
        self.saved_image_path = self.image_path
        self.saved_original_image = self.original_image
        self.saved_resized_image = self.resized_image
        self.saved_resized_width = self.resized_width
        self.saved_resized_height = self.resized_height

        # Clear references
        self.widget = None
        self.image = None
        self.image_path = None
        self.original_image = None
        self.resized_image = None
        self.resized_width = 0
        self.resized_height = 0

    def reload(self):
        '''Reload the previously saved variables'''
        self.widget = self.saved_widget
        self.image = self.saved_image
        self.image_path = self.saved_image_path
        self.original_image = self.saved_original_image
        self.resized_image = self.saved_resized_image
        self.resized_width = self.saved_resized_width
        self.resized_height = self.saved_resized_height

'''

v1.01 changes:

  - New:
    - The popup is now centered beside the mouse and behaves better around the screen edges.

  - Fixed:
    -

  - Other changes:
    -

'''