# region Imports


# Standard Library - GUI
from tkinter import Event, Label, Toplevel, BooleanVar, Canvas

# Third-Party Libraries
from PIL import Image, ImageTk, ImageDraw, ImageChops

# Typing
from typing import Optional


# endregion
# region PopUpZoom


class PopUpZoom:
    def __init__(self, widget: 'Label'):
        # Initialize the PopUpZoom class
        self.widget: Optional[Label] = widget
        self.zoom_factor = 1.75
        self.min_zoom_factor = 1.25
        self.max_zoom_factor = 10.0
        self.max_image_size = 4096
        self.corner_radius = 8

        # Only keep original_image for zooming
        self.original_image: Optional[Image.Image] = None

        # Initialize zoom enabled variable
        self.zoom_enabled = BooleanVar(value=False)

        # Set up the zoom window
        self._create_popup_window()
        # Bind events to the widget
        self._bind_events()


    def _create_popup_window(self):
        self.popup_size = 400
        self.min_popup_size = 100
        self.max_popup_size = 600

        self.popup = Toplevel(self.widget)
        self.popup.withdraw()
        self.popup.overrideredirect(True)
        self.popup.wm_attributes("-transparentcolor", self.popup["bg"])
        self.zoom_canvas = Canvas(self.popup, width=self.popup_size, height=self.popup_size, highlightthickness=0, bg=self.popup["bg"])
        self.zoom_canvas.pack()


    def _bind_events(self):
        self.widget.bind("<Motion>", self.show_popup, add="+")
        self.widget.bind("<Leave>", self.hide_popup, add="+")
        self.widget.bind("<Button-1>", self.hide_popup, add="+")
        self.widget.bind("<MouseWheel>", self._zoom, add="+")
        self.widget.bind("<Shift-MouseWheel>", self._resize_popup, add="+")


# endregion
# region Public API


    def set_image(self, image: Image.Image):
        """Set the image to be used for zooming.

        Args:
            image: The PIL Image object to display and zoom.
        """
        if self.original_image is image:
            return
        self.original_image = image
        self._resize_original_image()


    def show_popup(self, event: Event):
        """Show the popup window and update its image based on mouse position."""
        if event is None or not self.zoom_enabled.get() or not self.original_image:
            return
        self._show_and_update(event)


    def hide_popup(self, event: Event):
        """Hide the popup window"""
        self.popup.withdraw()


# endregion
# region Zoom Logic


    # --- Entry-point/controller methods ---
    def _show_and_update(self, event: Event):
        """Update popup position and image based on mouse event."""
        x, y = event.x, event.y
        new_x, new_y = self._compute_popup_position(event)
        self.popup.geometry(f"+{new_x}+{new_y}")
        display_w, display_h, pad_x, pad_y, scale_x, scale_y = self._get_display_metrics()
        if display_w == 0 or display_h == 0 or scale_x == 0 or scale_y == 0:
            return
        img_x = self._clamp((x - pad_x) / scale_x, 0, self.original_image.width)
        img_y = self._clamp((y - pad_y) / scale_y, 0, self.original_image.height)
        self._update_popup_image(img_x, img_y)


    def _zoom(self, event: Event):
        """Adjust the zoom factor based on the mouse wheel event"""
        if event is None:
            return
        delta_direction = 1 if event.delta > 0 else -1 if event.delta < 0 else 0
        if delta_direction == 0:
            return
        step = self.min_zoom_factor * delta_direction
        self.zoom_factor = self._clamp(self.zoom_factor + step, self.min_zoom_factor, self.max_zoom_factor)
        self.show_popup(event)


    def _resize_popup(self, event: Event):
        """Adjust the popup size based on Shift+MouseWheel event"""
        if event is None:
            return
        delta_direction = 1 if event.delta > 0 else -1 if event.delta < 0 else 0
        if delta_direction == 0:
            return
        self.popup_size = self._clamp(self.popup_size + 20 * delta_direction, self.min_popup_size, self.max_popup_size)
        self.zoom_canvas.config(width=self.popup_size, height=self.popup_size)
        self.show_popup(event)


    # --- UI update helpers ---
    def _update_popup_image(self, img_x: float, img_y: float):
        """Update the popup image based on calculated coordinates."""
        left, top, right, bottom = self._calculate_coordinates(img_x, img_y)
        if left < right and top < bottom:
            self._create_zoomed_image(left, top, right, bottom)
            self.popup.deiconify()
        else:
            self.popup.withdraw()


    def _create_zoomed_image(self, left: int, top: int, right: int, bottom: int):
        """Create and display the zoomed image in the zoom window"""
        cropped_image, new_width, new_height = self._crop_and_resize_image(left, top, right, bottom)
        resize_method = Image.Resampling.NEAREST if self.zoom_factor >= 4 else Image.Resampling.LANCZOS
        zoomed_image = cropped_image.resize((new_width, new_height), resize_method).convert("RGBA")
        transparent_background = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
        self._apply_corner_radius(new_width, new_height, zoomed_image, transparent_background)
        self._delete_zoom_image()
        self._display_zoomed_image(new_width, new_height, transparent_background)


    def _display_zoomed_image(self, new_width, new_height, transparent_background):
        self.zoom_photo_image = ImageTk.PhotoImage(transparent_background)
        self.zoom_canvas.delete("all")
        x = (self.popup_size - new_width) // 2
        y = (self.popup_size - new_height) // 2
        self.zoom_canvas.create_image(x, y, anchor="nw", image=self.zoom_photo_image)


    # --- Image processing helpers ---
    def _crop_and_resize_image(self, left: int, top: int, right: int, bottom: int) -> tuple[Image.Image, int, int]:
        cropped_image = self.original_image.crop((left, top, right, bottom))
        aspect_ratio = cropped_image.width / cropped_image.height
        if aspect_ratio > 1:
            new_width = self.popup_size
            new_height = int(self.popup_size / aspect_ratio)
        else:
            new_height = self.popup_size
            new_width = int(self.popup_size * aspect_ratio)
        return cropped_image, new_width, new_height


    def _apply_corner_radius(self, new_width: int, new_height: int, zoomed_image: Image, transparent_background: Image):
        if self.corner_radius >= 1:
            mask = Image.new('L', (new_width, new_height), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, new_width, new_height), radius=self.corner_radius, fill=255)
            alpha_channel = zoomed_image.getchannel("A")
            combined_mask = ImageChops.multiply(alpha_channel, mask)
            transparent_background.paste(zoomed_image, (0, 0), combined_mask)
        else:
            transparent_background.paste(zoomed_image, (0, 0), zoomed_image)


    def _resize_original_image(self):
        """Resize the original image if it's too large"""
        max_size = self.max_image_size
        img_copy = self.original_image.copy()
        img_copy.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        self.original_image = img_copy.convert("RGBA")


    # --- Coordinate and metrics helpers ---
    def _calculate_coordinates(self, img_x: float, img_y: float) -> tuple[int, int, int, int]:
        """Calculate the coordinates for the zoomed image."""
        width, height = self.original_image.width, self.original_image.height
        span = int(round(self.popup_size / self.zoom_factor))
        span = max(1, min(span, width, height))
        half_span = span / 2
        if width <= span:
            left, right = 0, width
        else:
            min_center_x = half_span
            max_center_x = width - (span - half_span)
            center_x = self._clamp(img_x, min_center_x, max_center_x)
            left = int(round(center_x - half_span))
            right = left + span
            if right > width:
                right = width
                left = right - span
            if left < 0:
                left = 0
                right = span
        if height <= span:
            top, bottom = 0, height
        else:
            min_center_y = half_span
            max_center_y = height - (span - half_span)
            center_y = self._clamp(img_y, min_center_y, max_center_y)
            top = int(round(center_y - half_span))
            bottom = top + span
            if bottom > height:
                bottom = height
                top = bottom - span
            if top < 0:
                top = 0
                bottom = span
        return int(left), int(top), int(right), int(bottom)


    def _compute_popup_position(self, event: Event) -> tuple[int, int]:
        """Return popup coordinates constrained to the visible screen area."""
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()
        default_x = event.x_root + self.popup_size // 10
        if default_x + self.popup_size > screen_width:
            default_x = event.x_root - self.popup_size - 20
        x_limit = max(0, screen_width - self.popup_size)
        y_limit = max(0, screen_height - self.popup_size)
        new_x = self._clamp(default_x, 0, x_limit)
        default_y = event.y_root - self.popup_size // 2
        new_y = self._clamp(default_y, 0, y_limit)
        return new_x, new_y


# endregion
# region Utility


    def _delete_zoom_image(self):
        if hasattr(self, "zoom_photo_image"):
            try:
                del self.zoom_photo_image
            except Exception:
                pass


    def _clamp(self, value: float, min_value: float, max_value: float) -> float:
        """Clamp a value between the provided bounds."""
        if max_value < min_value:
            return min_value
        return max(min_value, min(value, max_value))


    def _get_display_metrics(self) -> tuple[float, float, float, float, float, float]:
        null = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        if not self.widget or not self.original_image:
            return null
        widget_w, widget_h = self.widget.winfo_width(), self.widget.winfo_height()
        if widget_w <= 0 or widget_h <= 0:
            return null
        img_w, img_h = self.original_image.size
        if img_w == 0 or img_h == 0:
            return null
        image_obj = getattr(self.widget, "image", None)
        width_fn = getattr(image_obj, "width", None) if image_obj is not None else None
        height_fn = getattr(image_obj, "height", None) if image_obj is not None else None
        if callable(width_fn) and callable(height_fn):
            display_w = float(width_fn())
            display_h = float(height_fn())
        else:
            scale = min(widget_w / img_w, widget_h / img_h, 1.0)
            display_w = img_w * scale
            display_h = img_h * scale
        pad_x = (widget_w - display_w) / 2
        pad_y = (widget_h - display_h) / 2
        scale_x = display_w / img_w if img_w else 0.0
        scale_y = display_h / img_h if img_h else 0.0
        return display_w, display_h, pad_x, pad_y, scale_x, scale_y


# endregion
