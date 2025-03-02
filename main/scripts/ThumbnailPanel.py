#region - Imports


# Standard Library
from typing import Dict
import os

# Standard Library - GUI
from tkinter import ttk, Frame, Menu

# Third-Party Libraries
from PIL import Image, ImageTk, ImageOps

# Custom Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip

# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
################################################################################################################################################
#region CLS: ThumbnailPanel


class ThumbnailPanel(Frame):
    """
    A panel that displays thumbnails of images in a horizontal scrollable view.

    This class extends tkinter's Frame to create a thumbnail navigation panel
    that shows previews of images, handles thumbnail caching, and provides
    context menu interactions.
    """

    def __init__(self, master: 'Frame', parent: 'Main'):
        """
        Initialize the ThumbnailPanel.

        Args:
            master: The master widget
            parent: The main application instance implementing ThumbnailPanelParent interface
        """
        super().__init__(master)
        self.parent = parent
        self.thumbnail_cache: Dict[tuple, ImageTk.PhotoImage] = {}
        self.image_info_cache: Dict[str, dict] = {}
        self.bind("<MouseWheel>", self.parent.mouse_scroll)


#endregion
################################################################################################################################################
#region Main


    def update_panel(self) -> None:
        """
        Update the thumbnail panel display.

        Hides the panel if needed, clears existing thumbnails, calculates layout, and displays new thumbnails.

        Call this function whenever the panel should be updated.
        """
        if not self._should_display_thumbnails():
            self.grid_remove()
            return
        self.grid()
        self._clear_panel_if_needed()
        layout_info = self._calculate_layout()
        thumbnail_buttons = self._create_thumbnail_buttons(layout_info)
        self._display_thumbnails(thumbnail_buttons)


    def refresh_thumbnails(self):
        """
        Clear thumbnail and image info caches and refresh the thumbnail panel.

        Forces a complete regeneration of all thumbnails.

        Call this function whenever the image list has changed.
        """
        self.thumbnail_cache.clear()
        self.image_info_cache.clear()
        self.parent.refresh_file_lists()
        self.update_panel()


#endregion
################################################################################################################################################
#region Mechanics


    def _should_display_thumbnails(self) -> bool:
        """Check if thumbnails should be displayed."""
        return self.parent.thumbnails_visible.get() and bool(self.parent.image_files)


    def _clear_panel_if_needed(self) -> None:
        """Clear existing thumbnails if the number of images has changed."""
        if len(self.winfo_children()) != len(self.parent.image_files):
            for widget in self.winfo_children():
                widget.destroy()


    def _calculate_layout(self) -> dict:
        """Calculate layout parameters for thumbnails."""
        thumbnail_width = self.parent.thumbnail_width.get()
        panel_width = self.winfo_width() or self.parent.master_image_frame.winfo_width()
        num_thumbnails = max(1, panel_width // (thumbnail_width + 10))
        total_images = len(self.parent.image_files)
        half_visible = num_thumbnails // 2
        # Normalize current index for circular navigation
        self.parent.current_index = self.parent.current_index % total_images
        # Calculate start index
        start_index = (0 if total_images <= num_thumbnails else (self.parent.current_index - half_visible) % total_images)
        return {
            'start_index': start_index,
            'num_thumbnails': min(total_images, num_thumbnails),
            'total_images': total_images,
            'thumbnail_width': thumbnail_width
        }


    def _is_video_file(self, file_path: str) -> bool:
        """Check if the file is a video file by extension."""
        return file_path.lower().endswith('.mp4')


    def _create_thumbnail(self, image_file: str, thumbnail_width: int) -> ImageTk.PhotoImage:
        """Create and cache a thumbnail for the given image or video file."""
        cache_key = (image_file, thumbnail_width)
        if cache_key in self.thumbnail_cache:
            return self.thumbnail_cache[cache_key]
        try:
            # Check if it's a video file
            if self._is_video_file(image_file):
                # Get the thumbnail from video_thumb_dict if available
                if hasattr(self.parent, 'video_thumb_dict') and image_file in self.parent.video_thumb_dict:
                    img = self.parent.video_thumb_dict[image_file]
                    img.thumbnail((thumbnail_width, thumbnail_width), self.parent.quality_filter)
                    img = img.convert("RGBA") if img.mode != "RGBA" else img
                    padded_img = ImageOps.pad(img, (thumbnail_width, thumbnail_width), color=(0, 0, 0, 0))
                    thumbnail_photo = ImageTk.PhotoImage(padded_img)
                    self.thumbnail_cache[cache_key] = thumbnail_photo
                    return thumbnail_photo
                else:
                    self.parent.update_video_thumbnails()
                    return self._create_thumbnail(image_file, thumbnail_width)
            # Regular image handling (or fallback for videos)
            with Image.open(image_file) as img:
                img.thumbnail((thumbnail_width, thumbnail_width), self.parent.quality_filter)
                img = img.convert("RGBA") if img.mode != "RGBA" else img
                padded_img = ImageOps.pad(img, (thumbnail_width, thumbnail_width), color=(0, 0, 0, 0))
                thumbnail_photo = ImageTk.PhotoImage(padded_img)
                self.thumbnail_cache[cache_key] = thumbnail_photo
                return thumbnail_photo
        except Exception as e:
            #print(f"Error creating thumbnail for {image_file}: {e}")
            return None


    def _create_thumbnail_buttons(self, layout_info: dict) -> list:
        """Create thumbnail buttons with proper bindings and tooltips."""
        thumbnail_buttons = []
        for i in range(layout_info['num_thumbnails']):
            index = (layout_info['start_index'] + i) % layout_info['total_images']
            image_file = self.parent.image_files[index]
            # Cache image info if needed
            if image_file not in self.image_info_cache:
                # Use update_videoinfo for MP4 files, otherwise use get_image_info
                if self._is_video_file(image_file):
                    self.image_info_cache[image_file] = self.parent.update_videoinfo(image_file)
                else:
                    self.image_info_cache[image_file] = self.parent.get_image_info(image_file)
            # Create thumbnail
            thumbnail_photo = self._create_thumbnail(image_file, layout_info['thumbnail_width'])
            if not thumbnail_photo:
                continue
            # Create and configure button
            button = self._create_single_thumbnail_button(thumbnail_photo, index)
            thumbnail_buttons.append(button)
        return thumbnail_buttons


    def _create_single_thumbnail_button(self, thumbnail_photo: ImageTk.PhotoImage, index: int) -> ttk.Button:
        """Create a single thumbnail button with all necessary configuration."""
        button = ttk.Button(self, image=thumbnail_photo, cursor="hand2", command=lambda idx=index: self.parent.jump_to_image(idx))
        button.image = thumbnail_photo
        # Style current selection
        if index == self.parent.current_index:
            button.config(style="Highlighted.TButton")
        # Add bindings
        button.bind("<Button-3>", self._create_context_menu(button, index))
        button.bind("<MouseWheel>", self.parent.mouse_scroll)
        # Add tooltip
        image_file = self.parent.image_files[index]
        image_info = self.image_info_cache[image_file]
        tooltip_text = f"#{index + 1} | {image_info['filename']} | {image_info['resolution']} | {image_info['size']} | {image_info['color_mode']}"
        ToolTip.create(button, tooltip_text, delay=100, pady=-25, origin='widget')
        return button


    def _display_thumbnails(self, thumbnail_buttons: list) -> None:
        """Display the thumbnail buttons in the panel."""
        for idx, button in enumerate(thumbnail_buttons):
            button.grid(row=0, column=idx)
        self.update_idletasks()


#endregion
################################################################################################################################################
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
            thumb_menu.add_command(label="Open Image", command=lambda: self.parent.open_image(index=index))
            thumb_menu.add_command(label="Delete Pair", command=lambda: self.parent.delete_pair(index=index))
            thumb_menu.add_command(label="Edit Image", command=lambda: self.parent.open_image_in_editor(index=index))
            thumb_menu.add_separator()
            thumb_menu.add_checkbutton(label="Toggle Thumbnail Panel", variable=self.parent.thumbnails_visible, command=self.update_panel)
            # Thumbnail Size submenu
            thumbnail_size_menu = Menu(thumb_menu, tearoff=0)
            thumb_menu.add_cascade(label="Thumbnail Size", menu=thumbnail_size_menu)
            thumbnail_sizes = {"Small": 25, "Medium": 50, "Large": 100}
            for label, size in thumbnail_sizes.items():
                thumbnail_size_menu.add_radiobutton(label=label, variable=self.parent.thumbnail_width, value=size, command=self.update_panel)
            thumb_menu.add_separator()
            thumb_menu.add_command(label="Refresh Thumbnails", command=self.refresh_thumbnails)
            thumb_menu.post(event.x_root, event.y_root)
        return show_context_menu
