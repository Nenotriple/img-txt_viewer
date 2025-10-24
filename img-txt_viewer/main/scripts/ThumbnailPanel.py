#region Imports


# Standard
import os
import queue
import threading

# tkinter
from tkinter import ttk, Frame, Menu

# Third-Party
from nenotk import ToolTip as Tip
from PIL import Image, ImageTk, ImageOps

# Typing
from typing import TYPE_CHECKING, Dict, Optional
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region ThumbnailPanel


class ThumbnailPanel(Frame):
    """Panel displaying image thumbnails in a horizontal scrollable view."""

    # Thumbnail spacing constants for precise layout
    THUMB_PAD = 4  # Padding between thumbnails
    THUMB_BORDER = 2   # Border around each thumbnail
    TOTAL_SPACING = THUMB_PAD + (THUMB_BORDER * 2)  # Total spacing per thumbnail

    def __init__(self, master: 'Frame', app: 'Main'):
        """
        Args:
            master: Parent widget.
            app: Main application instance.
        """
        super().__init__(master)
        self.app = app
        self.thumbnail_cache: Dict[tuple, ImageTk.PhotoImage] = {}
        self.image_info_cache: Dict[str, dict] = {}  # Cache for image info {}
        self._last_layout_info = None  # Cache last layout to detect changes
        self._thumbnail_queue = queue.Queue()  # Queue for completed thumbnails
        self._thumbnail_lock = threading.Lock()  # Lock for pending thumbnails
        self._pending_thumbnails = {}  # {(image_file, thumbnail_width): True}
        self._update_pending = False  # Debounce flag for panel updates
        self._main_thread_id = threading.get_ident()  # Store main thread ID
        self._thumbnail_buttons = {}  # {index: button_widget} to track buttons for replacement
        # Keep geometry updated and respond to resizes
        self.bind("<MouseWheel>", self.app.mousewheel_nav)
        self.bind("<Configure>", lambda e: self._schedule_update_panel())
        # Start processing queue
        self._process_thumbnail_queue()

#endregion
#region Main


    def update_panel(self) -> None:
        """Update thumbnail panel display. Must be called from main thread."""
        # Ensure we're on the main thread
        if threading.get_ident() != self._main_thread_id:
            self._schedule_update_panel()
            return
        # Make sure geometry is current before computing layout
        self._refresh_geometry()
        if not self._should_display_thumbnails():
            self.grid_remove()
            return
        self.grid()
        layout_info = self._calculate_layout()
        # Only clear if layout has meaningfully changed
        if self._layout_has_changed(layout_info):
            self._clear_panel()
            self._last_layout_info = layout_info
        thumbnail_buttons = self._create_thumbnail_buttons(layout_info)
        self._display_thumbnails(thumbnail_buttons, layout_info)


    def refresh_thumbnails(self):
        """Clear caches and refresh thumbnails. Must be called from main thread."""
        # Ensure we're on the main thread
        if threading.get_ident() != self._main_thread_id:
            self.after(0, self.refresh_thumbnails)
            return

        self.thumbnail_cache.clear()
        self.image_info_cache.clear()
        self._last_layout_info = None
        with self._thumbnail_lock:
            self._pending_thumbnails.clear()
        self.app.refresh_file_lists()
        self.update_panel()


#endregion
#region Mechanics


    def _should_display_thumbnails(self) -> bool:
        """Check if thumbnails should be displayed."""
        return self.app.thumbnails_visible.get() and bool(self.app.image_files)


    def _layout_has_changed(self, new_layout: dict) -> bool:
        """Check if layout has meaningfully changed."""
        if self._last_layout_info is None:
            return True
        # Compare key layout parameters including scroll position and current selection
        return (self._last_layout_info.get('thumbnail_width') != new_layout.get('thumbnail_width') or
                self._last_layout_info.get('num_thumbnails') != new_layout.get('num_thumbnails') or
                self._last_layout_info.get('total_images') != new_layout.get('total_images') or
                self._last_layout_info.get('start_index') != new_layout.get('start_index') or
                self._last_layout_info.get('current_index') != new_layout.get('current_index'))


    def _clear_panel(self) -> None:
        """Clear all thumbnails from the panel."""
        for widget in self.winfo_children():
            widget.destroy()
        self._thumbnail_buttons.clear()  # Clear button tracking


    def _clear_panel_if_needed(self) -> None:
        """Clear existing thumbnails if the number of images has changed.
        - Count only widgets that look like thumbnail buttons (have an 'image' attribute) so other widgets don't cause unnecessary clears.
        """
        thumb_widgets = [w for w in self.winfo_children() if getattr(w, "image", None) is not None]
        if len(thumb_widgets) != len(self.app.image_files):
            self._clear_panel()


    def _calculate_layout(self) -> dict:
        """Calculate layout parameters for thumbnails with precise spacing."""
        thumbnail_width = self.app.thumbnail_width.get()
        # Ensure geometry is up-to-date
        self._refresh_geometry()
        panel_width = self.winfo_width() or self.app.master_image_frame.winfo_width() or 1
        # Calculate effective width per thumbnail (thumbnail + spacing)
        effective_thumbnail_width = thumbnail_width + self.TOTAL_SPACING
        # Calculate number of thumbnails that fit, accounting for edge padding
        try:
            num_thumbnails = max(1, (panel_width - self.THUMB_PAD) // effective_thumbnail_width)
        except Exception:
            num_thumbnails = 1
        total_images = len(self.app.image_files)
        # Early return if no images
        if total_images == 0:
            return {
                'start_index': 0,
                'num_thumbnails': 0,
                'total_images': 0,
                'thumbnail_width': thumbnail_width,
                'current_index': 0
            }
        # Normalize current index for circular navigation
        self.app.current_index = self.app.current_index % total_images
        # Calculate start index for centered current image
        if total_images <= num_thumbnails:
            start_index = 0
        else:
            half_visible = num_thumbnails // 2
            start_index = (self.app.current_index - half_visible) % total_images

        return {
            'start_index': start_index,
            'num_thumbnails': min(total_images, num_thumbnails),
            'total_images': total_images,
            'thumbnail_width': thumbnail_width,
            'effective_width': effective_thumbnail_width,
            'current_index': self.app.current_index
        }


    def _is_video_file(self, file_path: str) -> bool:
        """Check if the file is a video file by extension."""
        return file_path.lower().endswith(('.mp4', '.webm', '.mkv', '.avi', '.mov'))


    def _create_thumbnail(self, image_file: str, thumbnail_width: int) -> Optional[ImageTk.PhotoImage]:
        """Create and cache a thumbnail for the given image or video file.
        - PIL work is done in a background thread, conversion to ImageTk.PhotoImage and UI update is done on the main thread.
        - Returns None immediately; UI update is handled asynchronously.
        - Thread-safe: Can be called from main thread only (checks cache and spawns background thread).
        """
        cache_key = (image_file, thumbnail_width)
        if cache_key in self.thumbnail_cache:
            return self.thumbnail_cache[cache_key]
        # If already pending, just return None (will update later)
        with self._thumbnail_lock:
            if cache_key in self._pending_thumbnails:
                return None
            self._pending_thumbnails[cache_key] = True
        # Start background thread for PIL work
        threading.Thread(target=self._generate_thumbnail_bg, args=(image_file, thumbnail_width, cache_key), daemon=True).start()
        return None


    def _generate_thumbnail_bg(self, image_file, thumbnail_width, cache_key):
        """Background thread: generate PIL thumbnail, then schedule conversion/UI update.
        - Thread-safe: Runs in background thread, does NOT touch GUI.
        """
        try:
            if self._is_video_file(image_file):
                pil_img = self._get_video_pil_thumbnail(image_file, thumbnail_width)
            else:
                pil_img = self._get_image_pil_thumbnail(image_file, thumbnail_width)
            if pil_img is not None:
                # Queue the PIL image for main thread processing
                self._thumbnail_queue.put((cache_key, pil_img))
        except Exception:
            # Clear pending flag on error
            with self._thumbnail_lock:
                self._pending_thumbnails.pop(cache_key, None)


    def _get_video_pil_thumbnail(self, image_file, thumbnail_width):
        """Generate video thumbnail in background thread.
        - Thread-safe: May need to call main thread for video thumbnail generation.
        """
        # Check if thumbnail exists in video_thumb_dict
        if hasattr(self.app, 'video_thumb_dict') and image_file in self.app.video_thumb_dict:
            img = self.app.video_thumb_dict[image_file]['thumbnail'].copy()
        else:
            # Generate video thumbnail - this may need main thread access
            # Schedule on main thread if not already there
            if threading.get_ident() != self._main_thread_id:
                # Can't safely generate video thumbnail from background thread
                return None
            self.app.update_video_thumbnails()
            if hasattr(self.app, 'video_thumb_dict') and image_file in self.app.video_thumb_dict:
                img = self.app.video_thumb_dict[image_file]['thumbnail'].copy()
            else:
                return None
        img.thumbnail((thumbnail_width, thumbnail_width), self.app.quality_filter)
        img = img.convert("RGBA") if img.mode != "RGBA" else img
        padded_img = ImageOps.pad(img, (thumbnail_width, thumbnail_width), color=(0, 0, 0, 0))
        return padded_img


    def _get_image_pil_thumbnail(self, image_file, thumbnail_width):
        with Image.open(image_file) as img:
            img.thumbnail((thumbnail_width, thumbnail_width), self.app.quality_filter)
            img = img.convert("RGBA") if img.mode != "RGBA" else img
            padded_img = ImageOps.pad(img, (thumbnail_width, thumbnail_width), color=(0, 0, 0, 0))
            return padded_img


    def _finish_thumbnail_main(self, cache_key, pil_img):
        """Main thread: convert PIL image to ImageTk.PhotoImage, cache, and schedule update.
        - Thread-safe: Must be called from main thread only.
        """
        try:
            thumbnail_photo = ImageTk.PhotoImage(pil_img)
            self.thumbnail_cache[cache_key] = thumbnail_photo
        finally:
            # Always remove from pending, even if conversion fails
            with self._thumbnail_lock:
                self._pending_thumbnails.pop(cache_key, None)
        # Schedule panel update (debounced)
        self._schedule_update_panel()


    def _process_thumbnail_queue(self):
        """Process completed thumbnails from the queue on the main thread.
        - Thread-safe: Runs on main thread, processes queue items.
        """
        try:
            # Process all available items in the queue (batch processing)
            while True:
                cache_key, pil_img = self._thumbnail_queue.get_nowait()
                self._finish_thumbnail_main(cache_key, pil_img)
        except queue.Empty:
            pass
        finally:
            # Schedule next check
            self.after(50, self._process_thumbnail_queue)


    def _schedule_update_panel(self):
        """Schedule a debounced panel update on the main thread.
        - Thread-safe: Can be called from any thread.
        """
        if not self._update_pending:
            self._update_pending = True
            self.after_idle(self._do_update_panel)


    def _do_update_panel(self):
        """Execute the actual panel update and reset debounce flag.
        - Thread-safe: Runs on main thread only.
        """
        self._update_pending = False
        self.update_panel()


    def _create_thumbnail_buttons(self, layout_info: dict) -> list:
        """Create thumbnail buttons with proper bindings and tooltips."""
        thumbnail_buttons = []
        for i in range(layout_info['num_thumbnails']):
            index = (layout_info['start_index'] + i) % layout_info['total_images']
            image_file = self.app.image_files[index]
            # Cache image info if needed
            if image_file not in self.image_info_cache:
                if self._is_video_file(image_file):
                    self.image_info_cache[image_file] = self.app.update_videoinfo(image_file)
                else:
                    self.image_info_cache[image_file] = self.app.get_image_info(image_file)
            # Create thumbnail
            thumbnail_photo = self._create_thumbnail(image_file, layout_info['thumbnail_width'])
            # If thumbnail not ready, create a placeholder button (disabled)
            if not thumbnail_photo:
                # Check if we already have a button for this index
                if index in self._thumbnail_buttons and self._thumbnail_buttons[index].winfo_exists():
                    button = self._thumbnail_buttons[index]
                else:
                    button = ttk.Button(self, text="...", state="disabled")
                    self._thumbnail_buttons[index] = button
                thumbnail_buttons.append(button)
                continue
            # Create and configure button (or update existing placeholder)
            if index in self._thumbnail_buttons and self._thumbnail_buttons[index].winfo_exists():
                # Replace placeholder with real thumbnail
                old_button = self._thumbnail_buttons[index]
                old_button.destroy()
            button = self._create_button(thumbnail_photo, index)
            self._thumbnail_buttons[index] = button
            thumbnail_buttons.append(button)
        return thumbnail_buttons


    def _create_button(self, thumbnail_photo: ImageTk.PhotoImage, index: int) -> ttk.Button:
        """Create a single thumbnail button with all necessary configuration."""
        button = ttk.Button(self, image=thumbnail_photo, cursor="hand2", command=lambda idx=index: self.app.jump_to_image(idx))
        button.image = thumbnail_photo  # Keep reference to prevent garbage collection
        # Style current selection
        if index == self.app.current_index:
            button.config(style="Highlighted.TButton")
        # Add bindings
        button.bind("<Button-3>", self._create_context_menu(button, index))
        button.bind("<MouseWheel>", self.app.mousewheel_nav)
        # Add tooltip with image info
        self._create_thumbnail_tooltip(index, button)
        return button


    def _create_thumbnail_tooltip(self, index, button):
        image_file = self.app.image_files[index]
        if image_file in self.image_info_cache:
            image_info = self.image_info_cache[image_file]
            filename = image_info.get('filename') or os.path.basename(image_file)
            resolution = image_info.get('resolution') or image_info.get('size', '')
            size = image_info.get('size', '')
            tooltip_text = f"#{index + 1} | {filename} | {resolution} | {size}"
            Tip.create(widget=button, text=tooltip_text, show_delay=100, origin='widget', tooltip_anchor='sw', padx=1, pady=-2)


    def _display_thumbnails(self, thumbnail_buttons: list, layout_info: dict) -> None:
        """Display the thumbnail buttons in the panel with precise spacing."""
        # Remove any buttons that are no longer in the current view
        current_indices = set()
        for idx, button in enumerate(thumbnail_buttons):
            i = (layout_info['start_index'] + idx) % layout_info['total_images']
            current_indices.add(i)
            button.grid(
                row=0,
                column=idx,
                padx=(self.THUMB_PAD if idx == 0 else self.THUMB_PAD // 2,
                      self.THUMB_PAD if idx == len(thumbnail_buttons) - 1 else self.THUMB_PAD // 2),
                pady=self.THUMB_PAD
            )
        # Clean up buttons that are no longer visible
        for index in list(self._thumbnail_buttons.keys()):
            if index not in current_indices:
                button = self._thumbnail_buttons[index]
                if button.winfo_exists():
                    button.destroy()
                del self._thumbnail_buttons[index]
        self._refresh_geometry()


    def _refresh_geometry(self):
        try:
            self.update_idletasks()
        except Exception:
            pass


#endregion
#region Context Menu


    def _create_context_menu(self, thumbnail_button, index):
        """
        Args:
            thumbnail_button: Button widget.
            index: Image index in file list.
        Returns:
            Event handler for context menu.
        """
        def show_context_menu(event):
            thumb_menu = Menu(thumbnail_button, tearoff=0)
            thumb_menu.add_command(label="Open Image", command=lambda: self.app.open_image(index=index))
            thumb_menu.add_command(label="Delete Pair", command=lambda: self.app.delete_pair(index=index))
            thumb_menu.add_command(label="Edit Image", command=lambda: self.app.open_image_in_editor(index=index))
            thumb_menu.add_separator()
            thumb_menu.add_checkbutton(label="Toggle Thumbnail Panel", variable=self.app.thumbnails_visible, command=self.update_panel)
            # Thumbnail Size submenu
            thumbnail_size_menu = Menu(thumb_menu, tearoff=0)
            thumb_menu.add_cascade(label="Thumbnail Size", menu=thumbnail_size_menu)
            thumbnail_sizes = {"Small": 25, "Medium": 50, "Large": 100}
            for label, size in thumbnail_sizes.items():
                thumbnail_size_menu.add_radiobutton(label=label, variable=self.app.thumbnail_width, value=size, command=self.update_panel)
            thumb_menu.add_separator()
            thumb_menu.add_command(label="Refresh Thumbnails", command=self.refresh_thumbnails)
            thumb_menu.post(event.x_root, event.y_root)
        return show_context_menu


#endregion
