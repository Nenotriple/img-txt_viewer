#region Imports


# Standard
import os
import logging

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
    """
    A panel that displays thumbnails of images in a horizontal scrollable view.

    This class extends tkinter's Frame to create a thumbnail navigation panel
    that shows previews of images, handles thumbnail caching, and provides
    context menu interactions.
    """

    # Thumbnail spacing constants for precise layout
    THUMB_PAD = 4  # Padding between thumbnails
    THUMB_BORDER = 2   # Border around each thumbnail
    TOTAL_SPACING = THUMB_PAD + (THUMB_BORDER * 2)  # Total spacing per thumbnail

    def __init__(self, master: 'Frame', app: 'Main'):
        """
        Initialize the ThumbnailPanel.

        Args:
            master: The master widget
            app: The main application instance implementing ThumbnailPanelParent interface
        """
        super().__init__(master)
        self.app = app
        self.thumbnail_cache: Dict[tuple, ImageTk.PhotoImage] = {}
        self.image_info_cache: Dict[str, dict] = {}
        self._last_layout_info = None  # Cache last layout to detect changes
        # Keep geometry updated and respond to resizes
        self.bind("<MouseWheel>", self.app.mousewheel_nav)
        self.bind("<Configure>", lambda e: self.update_panel())


#endregion
#region Main


    def update_panel(self) -> None:
        """
        Update the thumbnail panel display.

        Hides the panel if needed, clears existing thumbnails, calculates layout, and displays new thumbnails.

        Call this function whenever the panel should be updated.
        """
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
        """
        Clear thumbnail and image info caches and refresh the thumbnail panel.

        Forces a complete regeneration of all thumbnails.

        Call this function whenever the image list has changed.
        """
        self.thumbnail_cache.clear()
        self.image_info_cache.clear()
        self._last_layout_info = None
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


    def _clear_panel_if_needed(self) -> None:
        """Clear existing thumbnails if the number of images has changed.

        Count only widgets that look like thumbnail buttons (have an 'image' attribute) so other widgets don't cause unnecessary clears.
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
        """Create and cache a thumbnail for the given image or video file."""
        cache_key = (image_file, thumbnail_width)
        if cache_key in self.thumbnail_cache:
            return self.thumbnail_cache[cache_key]
        try:
            # Check if it's a video file
            if self._is_video_file(image_file):
                return self._create_video_thumbnail(image_file, thumbnail_width, cache_key)
            # Regular image handling
            return self._create_image_thumbnail(image_file, thumbnail_width, cache_key)
        except Exception as e:
            # Silent error handling - return None to skip problematic files
            return None


    def _create_video_thumbnail(self, image_file: str, thumbnail_width: int, cache_key: tuple) -> ImageTk.PhotoImage:
        """Create thumbnail for video file."""
        # Check if thumbnail exists in video_thumb_dict
        if hasattr(self.app, 'video_thumb_dict') and image_file in self.app.video_thumb_dict:
            img = self.app.video_thumb_dict[image_file]['thumbnail'].copy()
        else:
            # Generate video thumbnail
            self.app.update_video_thumbnails()
            if hasattr(self.app, 'video_thumb_dict') and image_file in self.app.video_thumb_dict:
                img = self.app.video_thumb_dict[image_file]['thumbnail'].copy()
            else:
                return None
        # Process and cache the thumbnail
        img.thumbnail((thumbnail_width, thumbnail_width), self.app.quality_filter)
        img = img.convert("RGBA") if img.mode != "RGBA" else img
        padded_img = ImageOps.pad(img, (thumbnail_width, thumbnail_width), color=(0, 0, 0, 0))
        thumbnail_photo = ImageTk.PhotoImage(padded_img)
        self.thumbnail_cache[cache_key] = thumbnail_photo
        return thumbnail_photo


    def _create_image_thumbnail(self, image_file: str, thumbnail_width: int, cache_key: tuple) -> ImageTk.PhotoImage:
        """Create thumbnail for image file."""
        with Image.open(image_file) as img:
            img.thumbnail((thumbnail_width, thumbnail_width), self.app.quality_filter)
            img = img.convert("RGBA") if img.mode != "RGBA" else img
            padded_img = ImageOps.pad(img, (thumbnail_width, thumbnail_width), color=(0, 0, 0, 0))
            thumbnail_photo = ImageTk.PhotoImage(padded_img)
            self.thumbnail_cache[cache_key] = thumbnail_photo
            return thumbnail_photo


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
            if not thumbnail_photo:
                continue
            # Create and configure button
            button = self._create_button(thumbnail_photo, index)
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
        for idx, button in enumerate(thumbnail_buttons):
            button.grid(
                row=0,
                column=idx,
                padx=(self.THUMB_PAD if idx == 0 else self.THUMB_PAD // 2,
                      self.THUMB_PAD if idx == len(thumbnail_buttons) - 1 else self.THUMB_PAD // 2),
                pady=self.THUMB_PAD
            )
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
        Create a context menu for thumbnail buttons.

        Args:
            thumbnail_button: The button widget to attach the menu to
            index: The index of the image in the file list

        Returns:
            function: Event handler for showing the context menu
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
