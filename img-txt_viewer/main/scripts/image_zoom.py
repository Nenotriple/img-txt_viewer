# (Windows-only)


#region Imports


import os
import math
import concurrent.futures

import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageTk, ImageSequence
from PIL.Image import Image as PILImage
from PIL.ImageTk import PhotoImage as PILPhotoImage

from collections import OrderedDict
from typing import Optional, Tuple, Any, Union, List


#endregion
#region ImageManager


class ImageManager:
    """Load, resize and provide images for display."""
    def __init__(self) -> None:
        # Original PIL image and last-created PhotoImage (kept to avoid GC).
        self._orig_image: Optional[PILImage] = None
        self._tk_image: Optional[PILPhotoImage] = None
        self._scale: float = 1.0
        self._max_scale: float = 10.0
        self._cache_size: int = 1024
        # Resize cache keyed by (width, height, resample)
        self._resize_cache: "OrderedDict[Tuple[int,int,int], PILImage]" = OrderedDict()
        self._clear_cache()

    # --- Public / lifecycle ---
    def load_image(self, path: str) -> None:
        """Load image and convert to RGBA for consistent resizing."""
        with Image.open(path) as img:
            self._orig_image = img.convert("RGBA")
        self._clear_cache()

    def set_image(self, pil_image: PILImage) -> None:
        """Set the manager's original image from a PIL.Image (no file I/O)."""
        if pil_image is None:
            return
        try:
            self._orig_image = pil_image.convert("RGBA")
        except Exception:
            try:
                self._orig_image = pil_image.copy()
            except Exception:
                self._orig_image = pil_image
        self._clear_cache()

    def unload_image(self) -> None:
        """Clear image and caches."""
        self._orig_image = None
        self._clear_cache()
        return

    def has_image(self) -> bool:
        """Return True when an image is loaded."""
        return self._orig_image is not None

    # --- Size / scaling helpers ---
    def compute_fit_scale_and_size(self, can_w: int, can_h: int) -> Tuple[float, int, int]:
        """Compute scale and integer target size to fit the canvas."""
        og_img_w, og_img_h = self._orig_image.size
        scale = min(can_w / og_img_w, can_h / og_img_h)
        new_w = max(1, int(og_img_w * scale))
        new_h = max(1, int(og_img_h * scale))
        return scale, new_w, new_h

    def resize_for_scale(self, scale: float) -> PILImage:
        """Return (and cache) a resized PIL image for the given scale.

        Uses NEAREST at high zoom levels for speed/clarity, otherwise LANCZOS.
        """
        og_img_w, og_img_h = self._orig_image.size
        new_w = max(1, int(og_img_w * scale))
        new_h = max(1, int(og_img_h * scale))
        resample_mode = Image.Resampling.NEAREST if self._use_nearest_for_scale(scale) else Image.Resampling.LANCZOS
        key = self._cache_key(new_w, new_h, int(resample_mode))
        cached = self._get_cached_resize(key)
        if cached is not None:
            return cached
        resized = self._orig_image.resize((new_w, new_h), resample_mode)
        self._store_cached_resize(key, resized)
        return resized

    def crop_to_viewport(self, crop_box: Tuple[float, float, float, float], target_size: Tuple[float, float], resample: int = Image.Resampling.NEAREST) -> Optional[PILImage]:
        """Crop to integer bounds and resize to target viewport size."""
        left, top, right, bottom = crop_box
        img_w, img_h = self._orig_image.size
        left = max(0, min(img_w, int(math.floor(left))))
        top = max(0, min(img_h, int(math.floor(top))))
        right = max(left + 1, min(img_w, int(math.ceil(right))))
        bottom = max(top + 1, min(img_h, int(math.ceil(bottom))))
        if right <= left or bottom <= top:
            return None
        cropped = self._orig_image.crop((left, top, right, bottom))
        width, height = target_size
        width = max(1, int(round(width)))
        height = max(1, int(round(height)))
        if cropped.size != (width, height):
            cropped = cropped.resize((width, height), resample)
        return cropped

    def create_tk_image(self, pil_image: PILImage) -> PILPhotoImage:
        """Create and retain a Tk PhotoImage (must run on Tk main thread)."""
        self._tk_image = ImageTk.PhotoImage(pil_image)
        return self._tk_image

    # --- Properties ---
    @property
    def scale(self) -> float:
        return self._scale

    @scale.setter
    def scale(self, value: Any) -> None:
        """Accept only positive numeric scales."""
        try:
            v = float(value)
        except (TypeError, ValueError):
            return
        if v <= 0:
            return
        self._scale = v

    # --- Cache / internal utilities ---
    def _clear_cache(self) -> None:
        """Clear resize cache and drop PhotoImage reference."""
        self._resize_cache.clear()
        self._tk_image = None

    def _cache_key(self, width: int, height: int, resample: Optional[int] = None) -> Tuple[int, int, int]:
        if resample is None:
            resample = 0
        return width, height, int(resample)

    def _get_cached_resize(self, key: Tuple[int, int, int]) -> Optional[PILImage]:
        """Return cached image and mark it recently used (LRU)."""
        cached = self._resize_cache.get(key)
        if cached is not None:
            self._resize_cache.move_to_end(key)
        return cached

    def _store_cached_resize(self, key: Tuple[int, int, int], image: PILImage) -> None:
        """Store resized image and evict oldest entries when over cap."""
        self._resize_cache[key] = image
        self._resize_cache.move_to_end(key)
        while len(self._resize_cache) > self._cache_size:
            self._resize_cache.popitem(last=False)

    def _use_nearest_for_scale(self, scale: float = None) -> bool:
        """Decide when to use NEAREST (for high zoom levels)."""
        if scale is None:
            scale = self._scale
        try:
            s = float(scale)
        except (TypeError, ValueError):
            return False
        threshold = 0.4 * float(self._max_scale)
        return s >= threshold

#endregion
#region CanvasController


class CanvasController:
    """Helpers to place and update an image on a canvas."""
    def __init__(self) -> None:
        self.canvas: Optional[tk.Canvas] = None
        self._image_id: Optional[int] = None

    # --- Attachment / basic queries ---
    def attach_canvas(self, canvas: tk.Canvas) -> None:
        self.canvas = canvas

    def get_size(self) -> Tuple[int, int]:
        """Return canvas size (width, height), clamped to >=1."""
        if self.canvas is None:
            return 1, 1
        return max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height())

    def center_coords(self, can_w: int, can_h: int, pan_offset_x: float, pan_offset_y: float) -> Tuple[int, int]:
        return can_w // 2 + int(pan_offset_x), can_h // 2 + int(pan_offset_y)

    def set_cursor(self, cursor: str) -> None:
        """Safely set canvas cursor (ignore unsupported values)."""
        if self.canvas is None:
            return
        try:
            self.canvas.configure(cursor=cursor)
        except tk.TclError:
            pass

    # --- Pan/clamp and scale helpers ---
    def clamp_pan(self, pan_x: float, pan_y: float, img_w: float, img_h: float) -> Tuple[float, float]:
        """Clamp pan so the image remains at least partially visible."""
        can_w, can_h = self.get_size()
        max_pan_x = max(0.0, (img_w - float(can_w)) / 2.0)
        max_pan_y = max(0.0, (img_h - float(can_h)) / 2.0)
        pan_x = min(max_pan_x, max(-max_pan_x, float(pan_x)))
        pan_y = min(max_pan_y, max(-max_pan_y, float(pan_y)))
        return pan_x, pan_y

    def compute_min_scale_for_image(self, image_mgr: "ImageManager") -> float:
        if not image_mgr.has_image():
            return 1.0
        can_w, can_h = self.get_size()
        min_scale, _, _ = image_mgr.compute_fit_scale_and_size(can_w, can_h)
        return float(min_scale)

    def fit_image_to_canvas(self, image_mgr: "ImageManager") -> float:
        if not image_mgr.has_image():
            return 1.0
        can_w, can_h = self.get_size()
        fit_scale, _, _ = image_mgr.compute_fit_scale_and_size(can_w, can_h)
        image_mgr.scale = fit_scale
        return float(fit_scale)

    # --- Canvas image operations ---
    def update_canvas_image(self, tk_image: Any, x: float, y: float, anchor: str = "center") -> int:
        """Create or update the canvas image item and track its id."""
        if self.canvas is None:
            raise RuntimeError("CanvasController has no attached canvas")
        if self._image_id is None:
            self._image_id = self.canvas.create_image(x, y, image=tk_image, anchor=anchor)
            return self._image_id
        self.canvas.coords(self._image_id, x, y)
        self.canvas.itemconfig(self._image_id, image=tk_image, anchor=anchor)
        return self._image_id

    def clear_image(self) -> None:
        """Remove current canvas image item if present."""
        if self.canvas is None:
            return
        if self._image_id is not None:
            try:
                self.canvas.delete(self._image_id)
            except tk.TclError:
                pass
            self._image_id = None

    # --- Rendering helpers ---
    def render_viewport_preview(self, image_mgr: "ImageManager", pan_offset_x: float, pan_offset_y: float) -> bool:
        """Render a fast NEAREST crop for interactive feedback."""
        if not image_mgr.has_image():
            return False
        can_w, can_h = self.get_size()
        scale = float(image_mgr.scale)
        og_w, og_h = image_mgr._orig_image.size
        cx, cy = self.center_coords(can_w, can_h, pan_offset_x, pan_offset_y)
        scaled_w = og_w * scale
        scaled_h = og_h * scale
        left = cx - scaled_w / 2.0
        top = cy - scaled_h / 2.0
        right = left + scaled_w
        bottom = top + scaled_h
        vis_left = max(0.0, left)
        vis_top = max(0.0, top)
        vis_right = min(float(can_w), right)
        vis_bottom = min(float(can_h), bottom)
        if vis_right <= vis_left or vis_bottom <= vis_top:
            return False
        img_left = max(0.0, (vis_left - left) / scale)
        img_top = max(0.0, (vis_top - top) / scale)
        img_right = min(float(og_w), (vis_right - left) / scale)
        img_bottom = min(float(og_h), (vis_bottom - top) / scale)
        pil_preview = image_mgr.crop_to_viewport((img_left, img_top, img_right, img_bottom), (vis_right - vis_left, vis_bottom - vis_top), resample=Image.Resampling.NEAREST)
        if pil_preview is None:
            return False
        tk_img = image_mgr.create_tk_image(pil_preview)
        # Place preview at the visible area's top-left.
        self.update_canvas_image(tk_img, vis_left, vis_top, anchor="nw")
        return True

    def render_full_image(self, image_mgr: "ImageManager", pan_offset_x: float, pan_offset_y: float) -> None:
        """Render the full-resolution scaled image synchronously."""
        if not image_mgr.has_image():
            return
        resized = image_mgr.resize_for_scale(image_mgr.scale)
        tk_img = image_mgr.create_tk_image(resized)
        can_w, can_h = self.get_size()
        cx, cy = self.center_coords(can_w, can_h, pan_offset_x, pan_offset_y)
        self.update_canvas_image(tk_img, cx, cy, anchor="center")


#endregion
#region EventController


class EventController:
    """Event handlers for ImageZoomWidget."""
    def __init__(self, widget: "ImageZoomWidget") -> None:
        self.widget = widget

    def _on_canvas_configure(self, event: tk.Event) -> None:
        """On canvas resize: show fast preview and schedule full render."""
        if not self.widget.image_mgr.has_image():
            return
        can_w, can_h = self.widget.canvas_ctrl.get_size()
        if self.widget.image_fits_canvas:
            self.widget._switch_to_fit_and_preview(can_w, can_h, delay=100)
            return
        # Clamp pan so the image remains visible after resize.
        scale = float(self.widget.image_mgr.scale)
        og_w, og_h = self.widget.image_mgr._orig_image.size
        img_w = og_w * scale
        img_h = og_h * scale
        self.widget.pan_offset_x, self.widget.pan_offset_y = self.widget.canvas_ctrl.clamp_pan(self.widget.pan_offset_x, self.widget.pan_offset_y, img_w, img_h)
        # If image now fits the canvas, switch to fit mode and preview.
        if img_w <= float(can_w) + 1e-6 and img_h <= float(can_h) + 1e-6:
            self.widget._switch_to_fit_and_preview(can_w, can_h, delay=100)
        else:
            # Render a fast viewport preview and schedule a full render.
            self.widget._using_preview = self.widget.canvas_ctrl.render_viewport_preview(self.widget.image_mgr, self.widget.pan_offset_x, self.widget.pan_offset_y)
            self.widget._schedule_full_render()

    def _on_mouse_wheel(self, event: tk.Event) -> None:
        """Zoom about the mouse cursor; keep the cursor point fixed on the image."""
        if not self.widget.image_mgr.has_image():
            return
        delta_notches = event.delta / 120.0
        if delta_notches == 0:
            return
        zoom_per_notch = 1.1
        factor = zoom_per_notch ** delta_notches
        new_scale = self.widget.image_mgr.scale * factor
        min_scale = self.widget.canvas_ctrl.compute_min_scale_for_image(self.widget.image_mgr)
        new_scale = max(min_scale, min(self.widget.image_mgr._max_scale, new_scale))
        if abs(new_scale - self.widget.image_mgr.scale) < 1e-9:
            return
        # Compute new pan so the cursor point remains fixed.
        mx = float(event.x)
        my = float(event.y)
        can_w, can_h = self.widget.canvas_ctrl.get_size()
        cx_old = float(can_w) / 2.0 + float(self.widget.pan_offset_x)
        cy_old = float(can_h) / 2.0 + float(self.widget.pan_offset_y)
        dx = mx - cx_old
        dy = my - cy_old
        s_old = float(self.widget.image_mgr.scale)
        s_new = float(new_scale)
        cx_new = mx - dx * (s_new / s_old)
        cy_new = my - dy * (s_new / s_old)
        if abs(s_new - min_scale) < 1e-9:
            # Snap to fit-to-canvas.
            self.widget.pan_offset_x = 0
            self.widget.pan_offset_y = 0
            self.widget.image_fits_canvas = True
        else:
            self.widget.pan_offset_x = cx_new - (float(can_w) / 2.0)
            self.widget.pan_offset_y = cy_new - (float(can_h) / 2.0)
            og_w, og_h = self.widget.image_mgr._orig_image.size
            img_w = og_w * s_new
            img_h = og_h * s_new
            self.widget.pan_offset_x, self.widget.pan_offset_y = self.widget.canvas_ctrl.clamp_pan(self.widget.pan_offset_x, self.widget.pan_offset_y, img_w, img_h)
            self.widget.image_fits_canvas = False
        self.widget.image_mgr.scale = s_new
        # Fast preview and schedule full render.
        self.widget._using_preview = self.widget.canvas_ctrl.render_viewport_preview(self.widget.image_mgr, self.widget.pan_offset_x, self.widget.pan_offset_y)
        self.widget._schedule_full_render()

    def _on_button_press(self, event: tk.Event) -> None:
        """Begin drag; record start and set pan cursor."""
        self.widget._drag_start = (event.x, event.y, self.widget.pan_offset_x, self.widget.pan_offset_y)
        self.widget.canvas_ctrl.set_cursor("fleur")

    def _on_mouse_drag(self, event: tk.Event) -> None:
        """Pan while dragging; render preview if active, else move current image."""
        if self.widget._drag_start is None or not self.widget.image_mgr.has_image():
            return
        start_x, start_y, start_off_x, start_off_y = self.widget._drag_start
        dx = event.x - start_x
        dy = event.y - start_y
        self.widget.pan_offset_x = start_off_x + dx
        self.widget.pan_offset_y = start_off_y + dy
        # Clamp pan so image cannot be dragged fully out of view.
        can_w, can_h = self.widget.canvas_ctrl.get_size()
        og_w, og_h = self.widget.image_mgr._orig_image.size
        scale = float(self.widget.image_mgr.scale)
        img_w = og_w * scale
        img_h = og_h * scale
        self.widget.pan_offset_x, self.widget.pan_offset_y = self.widget.canvas_ctrl.clamp_pan(self.widget.pan_offset_x, self.widget.pan_offset_y, img_w, img_h)
        if self.widget._using_preview:
            # Render preview while dragging and schedule full render.
            self.widget._using_preview = self.widget.canvas_ctrl.render_viewport_preview(self.widget.image_mgr, self.widget.pan_offset_x, self.widget.pan_offset_y)
            self.widget._schedule_full_render()
        else:
            # Move existing full-resolution image for snappy dragging.
            cx, cy = self.widget.canvas_ctrl.center_coords(can_w, can_h, self.widget.pan_offset_x, self.widget.pan_offset_y)
            if self.widget.image_mgr._tk_image is not None:
                self.widget.canvas_ctrl.update_canvas_image(self.widget.image_mgr._tk_image, cx, cy, anchor="center")

    def _on_button_release(self, event: tk.Event) -> None:
        """End drag, restore cursor, and ensure a full render if necessary."""
        self.widget._drag_start = None
        self.widget.canvas_ctrl.set_cursor("")
        if not self.widget.image_mgr.has_image():
            return
        # If preview was used or a background job is pending, ensure a full render runs.
        if self.widget._using_preview or getattr(self.widget, "_pending_future", None) is not None or self.widget.image_mgr._tk_image is None:
            self.widget._schedule_full_render(delay=150)
        else:
            # Ensure the existing Tk image is positioned correctly.
            can_w, can_h = self.widget.canvas_ctrl.get_size()
            cx, cy = self.widget.canvas_ctrl.center_coords(can_w, can_h, self.widget.pan_offset_x, self.widget.pan_offset_y)
            if self.widget.image_mgr._tk_image is not None:
                try:
                    self.widget.canvas_ctrl.update_canvas_image(self.widget.image_mgr._tk_image, cx, cy, anchor="center")
                except tk.TclError:
                    pass


#endregion
#region ImageZoomWidget


class ImageZoomWidget(tk.Frame):
    """Embeddable image zoom/pan widget for tkinter."""
# --- Initialization ---
    def __init__(self, master: Optional[Any] = None, **kwargs: Any) -> None:
        """Initialize state, background executor and UI."""
        super().__init__(master, **kwargs)
        self.image_mgr = ImageManager()
        self.canvas_ctrl = CanvasController()
        # View state
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self._drag_start = None
        # Background-rendering state
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._render_sequence: int = 0  # bump to invalidate older background results
        self._pending_future: Optional[concurrent.futures.Future] = None
        self._full_render_job = None
        self._using_preview = False
        # If True, image is scaled to fit canvas and pan offsets are zero.
        self.image_fits_canvas = False
        # GIF animation state
        self._is_gif: bool = False
        self._gif_frames: List[PILImage] = []
        self._frame_durations: List[int] = []
        self._frame_iterator: Optional[Any] = None
        self._current_frame_index: int = 0
        self._animation_job_id: Optional[str] = None
        self._gif_frame_cache: dict = {}
        # Event binding IDs
        self._event_bindings: dict = {}
        self.events = EventController(self)
        self._create_ui()

# --- UI construction / initialization ---
    def _create_ui(self) -> None:
        """Create canvas and bind input events."""
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill="both", expand=True)
        self.canvas_ctrl.attach_canvas(self.canvas)
        # Bind events by default
        self.bind_events()

    def bind_events(self) -> None:
        """Bind pan and zoom events to the canvas."""
        if self.canvas is None:
            return
        # Only bind if not already bound
        if self._event_bindings:
            return
        self._event_bindings['configure'] = self.canvas.bind("<Configure>", self.events._on_canvas_configure, add="+")
        self._event_bindings['mousewheel'] = self.canvas.bind("<MouseWheel>", self.events._on_mouse_wheel, add="+")
        self._event_bindings['button_press'] = self.canvas.bind("<ButtonPress-1>", self.events._on_button_press, add="+")
        self._event_bindings['motion'] = self.canvas.bind("<B1-Motion>", self.events._on_mouse_drag, add="+")
        self._event_bindings['button_release'] = self.canvas.bind("<ButtonRelease-1>", self.events._on_button_release, add="+")

    def unbind_events(self) -> None:
        """Unbind pan and zoom events from the canvas."""
        if self.canvas is None:
            return
        for event_type, bind_id in self._event_bindings.items():
            try:
                if event_type == 'mousewheel':
                    self.canvas.unbind("<MouseWheel>", bind_id)
                elif event_type == 'button_press':
                    self.canvas.unbind("<ButtonPress-1>", bind_id)
                elif event_type == 'motion':
                    self.canvas.unbind("<B1-Motion>", bind_id)
                elif event_type == 'button_release':
                    self.canvas.unbind("<ButtonRelease-1>", bind_id)
            except tk.TclError:
                pass
        self._event_bindings.clear()

# --- Public API / High-level actions ---
    def load_image(self, path: str) -> None:
        """Load image, reset view, and request a full render."""
        if not path:
            return
        # Check if GIF
        file_extension = os.path.splitext(path)[1].lower()
        if file_extension == '.gif':
            self._load_gif(path)
        else:
            self._stop_gif_animation()
            self.image_mgr.load_image(path)
            self.pan_offset_x = 0
            self.pan_offset_y = 0
            if self.image_mgr.has_image():
                self._fit_image_to_canvas()
            else:
                self.image_fits_canvas = False
            self._cancel_full_render_job()
            self._request_full_render(self._render_sequence)
            self._using_preview = False

    def set_image(self, pil_image: PILImage) -> None:
        """Set widget image from a PIL.Image instance (like load_image but from-memory)."""
        if pil_image is None:
            return
        # Stop any GIF animation
        self._stop_gif_animation()
        # Put the image into the manager and reset view / schedule a full render
        self.image_mgr.set_image(pil_image)
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        if self.image_mgr.has_image():
            self._fit_image_to_canvas()
        else:
            self.image_fits_canvas = False
        self._cancel_full_render_job()
        self._request_full_render(self._render_sequence)
        self._using_preview = False

    def force_fit_to_canvas(self) -> None:
        """Force fit-to-canvas and trigger immediate full render."""
        if not self._do_image_check():
            return
        self._fit_image_to_canvas()
        self._render_full_image()

    def unload_image(self) -> None:
        """Unload image and reset widget state."""
        self._stop_gif_animation()
        self._cancel_full_render_job()
        self.image_mgr.unload_image()
        self.canvas_ctrl.clear_image()
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self._drag_start = None
        self._using_preview = False
        self.image_fits_canvas = False
        if getattr(self, "canvas", None) is not None:
            try:
                self.canvas.delete("all")
            except tk.TclError:
                pass

    def get_image(self, original: bool = True) -> Optional[PILImage]:
        """Return either original image copy or a scaled PIL.Image."""
        if not self._do_image_check():
            return None
        if original:
            try:
                return self.image_mgr._orig_image.copy()
            except Exception:
                return self.image_mgr._orig_image
        try:
            scale = float(self.image_mgr.scale)
        except Exception:
            scale = 1.0
        return self.image_mgr.resize_for_scale(scale)

# --- GIF Animation Support ---
    def _load_gif(self, path: str) -> None:
        """Load and prepare GIF animation."""
        try:
            self._stop_gif_animation()
            with Image.open(path) as img:
                # Extract all frames
                self._gif_frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(img)]
                self._frame_durations = [frame.info.get('duration', 100) for frame in ImageSequence.Iterator(img)]

            if not self._gif_frames:
                return
            # Set first frame to image manager for initial display
            self.image_mgr.set_image(self._gif_frames[0])
            self.pan_offset_x = 0
            self.pan_offset_y = 0
            if self.image_mgr.has_image():
                self._fit_image_to_canvas()
            else:
                self.image_fits_canvas = False
            self._is_gif = True
            self._frame_iterator = iter(self._gif_frames)
            self._current_frame_index = 0
            self._gif_frame_cache.clear()
            self.unbind_events()
            # Start animation
            self._play_gif_animation()
        except Exception as e:
            print(f"Error loading GIF: {e}")
            self._is_gif = False

    def _play_gif_animation(self) -> None:
        """Play the next frame of GIF animation."""
        if not self._is_gif or not self._gif_frames:
            return
        # Cancel any pending animation job
        if self._animation_job_id is not None:
            try:
                self.after_cancel(self._animation_job_id)
            except tk.TclError:
                pass
            self._animation_job_id = None
        try:
            # Get next frame
            current_frame = next(self._frame_iterator)
            # Get canvas dimensions
            can_w, can_h = self.canvas_ctrl.get_size()
            if can_w <= 1 or can_h <= 1:
                # Canvas not ready, retry later
                self._animation_job_id = self.after(50, self._play_gif_animation)
                return
            # Calculate scale to fit canvas
            frame_w, frame_h = current_frame.size
            scale_factor = min(can_w / frame_w, can_h / frame_h)
            new_w = max(1, int(frame_w * scale_factor))
            new_h = max(1, int(frame_h * scale_factor))
            # Check cache
            cache_key = (id(current_frame), self._current_frame_index, new_w, new_h)
            if cache_key in self._gif_frame_cache:
                scaled_frame = self._gif_frame_cache[cache_key]
            else:
                # Resize and cache
                scaled_frame = current_frame.resize((new_w, new_h), Image.Resampling.LANCZOS)
                self._gif_frame_cache[cache_key] = scaled_frame
            # Create PhotoImage and display
            tk_img = ImageTk.PhotoImage(scaled_frame)
            self.image_mgr._tk_image = tk_img  # Keep reference to prevent GC
            # Center on canvas
            cx, cy = can_w // 2, can_h // 2
            self.canvas_ctrl.update_canvas_image(tk_img, cx, cy, anchor="center")
            # Schedule next frame
            delay = self._frame_durations[self._current_frame_index] if self._frame_durations[self._current_frame_index] else 100
            self._animation_job_id = self.after(delay, self._play_gif_animation)
            # Advance frame index
            self._current_frame_index = (self._current_frame_index + 1) % len(self._gif_frames)
        except StopIteration:
            # Loop back to start
            self._frame_iterator = iter(self._gif_frames)
            self._current_frame_index = 0
            self._play_gif_animation()
        except Exception as e:
            print(f"Error playing GIF frame: {e}")

    def _stop_gif_animation(self) -> None:
        """Stop GIF animation and clean up."""
        if self._animation_job_id is not None:
            try:
                self.after_cancel(self._animation_job_id)
            except tk.TclError:
                pass
            self._animation_job_id = None
        self._is_gif = False
        self._gif_frames.clear()
        self._frame_durations.clear()
        self._frame_iterator = None
        self._current_frame_index = 0
        self._gif_frame_cache.clear()
        self.bind_events()

# --- Canvas / sizing helpers ---
    def _compute_min_scale_for_canvas(self) -> float:
        return self.canvas_ctrl.compute_min_scale_for_image(self.image_mgr)

    def _fit_image_to_canvas(self) -> None:
        """Set scale to fit canvas and reset pan offsets."""
        if not self._do_image_check():
            self.image_fits_canvas = False
            return
        fit_scale = self.canvas_ctrl.fit_image_to_canvas(self.image_mgr)
        self.image_mgr.scale = fit_scale
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.image_fits_canvas = True
        self._ensure_min_zoom_steps(base_scale=fit_scale)

    def _show_fit_preview(self, can_w: int, can_h: int) -> bool:
        """Create a fast NEAREST preview sized to the canvas and place it centered."""
        if not self.image_mgr.has_image():
            return False
        # Compute fit size (already set by caller in some code paths, but recompute here for safety).
        fit_scale, new_w, new_h = self.image_mgr.compute_fit_scale_and_size(can_w, can_h)
        # Ensure sizes are integers >= 1
        new_w = max(1, int(new_w))
        new_h = max(1, int(new_h))
        # Resize using NEAREST for a fast preview and update the canvas at center.
        pil_preview = self.image_mgr._orig_image.resize((new_w, new_h), Image.Resampling.NEAREST)
        tk_img = self.image_mgr.create_tk_image(pil_preview)
        cx, cy = self.canvas_ctrl.center_coords(can_w, can_h, 0, 0)
        self.canvas_ctrl.update_canvas_image(tk_img, cx, cy, anchor="center")
        return True

    def _switch_to_fit_and_preview(self, can_w: int, can_h: int, delay: int = 100) -> None:
        """Switch to fit mode, display preview, and schedule full render."""
        if not self.image_mgr.has_image():
            return
        # Compute and apply fit scale + reset pan
        fit_scale, _, _ = self.image_mgr.compute_fit_scale_and_size(can_w, can_h)
        self.image_mgr.scale = fit_scale
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.image_fits_canvas = True
        self._ensure_min_zoom_steps(base_scale=fit_scale)
        # Try to show a fast NEAREST preview; ignore errors and still schedule a full render.
        try:
            self._show_fit_preview(can_w, can_h)
        except Exception:
            pass
        self._schedule_full_render(delay=delay)

    def _ensure_min_zoom_steps(self, steps: int = 10, zoom_per_notch: float = 1.1, base_scale: Optional[float] = None) -> None:
        """Make sure image_mgr._max_scale allows at least `steps` zoom increments."""
        try:
            if base_scale is None:
                base_scale = self.canvas_ctrl.compute_min_scale_for_image(self.image_mgr)
            min_required = float(base_scale) * (zoom_per_notch ** float(steps))
            if getattr(self.image_mgr, "_max_scale", 0) < min_required:
                self.image_mgr._max_scale = min_required
        except Exception:
            pass

# --- Rendering pipeline (preview, full, scheduling) ---
    def _render_viewport_preview(self) -> None:
        if not self._do_image_check():
            return
        self._using_preview = self.canvas_ctrl.render_viewport_preview(self.image_mgr, self.pan_offset_x, self.pan_offset_y)

    def _render_full_image(self) -> None:
        """Start background full-resolution render immediately."""
        if not self._do_image_check():
            return
        self._cancel_full_render_job()
        self._request_full_render(self._render_sequence)

    def _request_full_render(self, seq: int) -> None:
        """Submit a background resize task and arrange main-thread completion."""
        if not self._do_image_check():
            return
        scale = float(self.image_mgr.scale)
        future = self._executor.submit(self.image_mgr.resize_for_scale, scale)
        self._pending_future = future

        def _done_callback(fut, s=seq):
            try:
                self.after(0, lambda: self._on_background_render_done(fut, s))
            except tk.TclError:
                pass

        future.add_done_callback(_done_callback)

    def _on_background_render_done(self, future: concurrent.futures.Future, seq: int) -> None:
        """Handle background resize completion on the main thread."""
        if seq != self._render_sequence:
            return
        if not self._do_image_check():
            self._pending_future = None
            return
        try:
            pil_img = future.result()
        except Exception:
            self._pending_future = None
            return
        if pil_img is None:
            self._pending_future = None
            return
        try:
            tk_img = self.image_mgr.create_tk_image(pil_img)
        except Exception:
            self._pending_future = None
            return
        can_w, can_h = self.canvas_ctrl.get_size()
        cx, cy = self.canvas_ctrl.center_coords(can_w, can_h, self.pan_offset_x, self.pan_offset_y)
        try:
            self.canvas_ctrl.update_canvas_image(tk_img, cx, cy, anchor="center")
        except tk.TclError:
            pass
        self._using_preview = False
        self._pending_future = None

    def _redraw_image(self) -> None:
        self._render_full_image()

    def _cancel_full_render_job(self) -> None:
        """Cancel scheduled callbacks and invalidate pending background results."""
        self._render_sequence += 1
        if self._full_render_job is not None:
            try:
                self.after_cancel(self._full_render_job)
            except tk.TclError:
                pass
            self._full_render_job = None
        if self._pending_future is not None:
            try:
                self._pending_future.cancel()
            except Exception:
                pass
            self._pending_future = None

    def _schedule_full_render(self, delay: int = 200) -> None:
        """Schedule a delayed full render (runs background work)."""
        if not self._do_image_check():
            return
        self._cancel_full_render_job()
        seq = self._render_sequence
        try:
            self._full_render_job = self.after(delay, lambda: self._request_full_render(seq))
        except tk.TclError:
            self._full_render_job = None

    def _do_image_check(self) -> bool:
        """Return True if image is loaded and high-quality resize is appropriate."""
        if not self.image_mgr.has_image():
            return False
        if self.image_mgr._use_nearest_for_scale(self.image_mgr.scale):
            return False
        return True

    def destroy(self) -> None:
        """Clean up background executor and pending work on destroy."""
        self._stop_gif_animation()
        self.unbind_events()
        pending = self._pending_future
        try:
            self._cancel_full_render_job()
        except Exception:
            pass
        if pending is not None:
            try:
                pending.result(timeout=1.0)
            except concurrent.futures.TimeoutError:
                pass
            except Exception:
                pass
        try:
            self._executor.shutdown(wait=False)
        except Exception:
            pass
        super().destroy()


#endregion
#region Main


if __name__ == "__main__":
    # Standalone demo.
    root = tk.Tk()
    root.geometry("800x600")

    # Demo Menu
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    commands_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Commands", menu=commands_menu)
    commands_menu.add_command(label="Load Image...", command=lambda: widget.load_image(filedialog.askopenfilename( title="Select Image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff"), ("All files", "*.*")], initialdir=os.path.expanduser("~"))))
    commands_menu.add_command(label="Unload Image", command=lambda: widget.unload_image())
    commands_menu.add_command(label="Fit to Canvas", command=lambda: widget.force_fit_to_canvas())

    # Widget
    widget = ImageZoomWidget(root)
    widget.pack(fill="both", expand=True)

    root.mainloop()


#endregion