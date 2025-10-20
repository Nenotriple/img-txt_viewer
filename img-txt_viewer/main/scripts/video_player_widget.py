#region Imports


import datetime
import os
import tkinter as tk
from tkinter import PhotoImage, ttk, filedialog
from tkVideoPlayer import TkinterVideo


# Type Hinting
from typing import TYPE_CHECKING, Optional, Callable, Any, Union
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region TimelineCanvas


class TimelineCanvas(tk.Canvas):
    """Canvas timeline for scrubbing and showing playback progress."""
    def __init__(self,
                master: tk.Widget,
                height: int = 15,
                **kwargs: Any
                ) -> None:
        super().__init__(master,
                        height=height,
                        highlightthickness=0,
                        **kwargs)
        self.duration: float = 0.0
        self.current_position: float = 0.0
        self._dragging: bool = False
        self._hover: bool = False

        # Callback for position changes
        self.position_callback: Optional[Callable[[float], None]] = None
        self.press_callback: Optional[Callable[[], None]] = None
        self.release_callback: Optional[Callable[[], None]] = None

        # Bind mouse events
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Motion>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", self._on_resize)

        # Colors
        self.bg_color = "#FFFFFF"
        self.progress_color = "#1e90ff"
        self.playhead_color = "#44546d"
        self.hover_color = "#272c33"

        self._draw()


    def _draw(self) -> None:
        """Render background, progress bar and playhead."""
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1:  # Not yet rendered
            return
        # Draw background
        self.create_rectangle(0, 0, width, height, fill=self.bg_color, outline="")
        # Draw progress bar
        if self.duration > 0:
            progress_width = (self.current_position / self.duration) * width
            self.create_rectangle(0, 0, progress_width, height, fill=self.progress_color, outline="")
        # Draw playhead
        if self.duration > 0:
            playhead_x = (self.current_position / self.duration) * width
            playhead_color = self.hover_color if self._hover or self._dragging else self.playhead_color
            self.create_line(playhead_x, 0, playhead_x, height, fill=playhead_color, width=3)


    def _on_resize(self, event: Optional[tk.Event] = None) -> None:
        """Redraw when the widget size changes."""
        self._draw()


    def _on_click(self, event: tk.Event) -> None:
        """Begin dragging and call press callback if set."""
        self._dragging = True
        self._update_position_from_event(event)
        if self.press_callback:
            self.press_callback()


    def _on_drag(self, event: tk.Event) -> None:
        """Update position while dragging."""
        if self._dragging:
            self._update_position_from_event(event)


    def _on_release(self, event: tk.Event) -> None:
        """End dragging and call release callback if set."""
        self._dragging = False
        self._update_position_from_event(event)
        if self.release_callback:
            self.release_callback()
        self._draw()


    def _on_hover(self, event: tk.Event) -> None:
        """Enable hover state for visual feedback."""
        if not self._hover:
            self._hover = True
            self._draw()


    def _on_leave(self, event: tk.Event) -> None:
        """Disable hover state when pointer leaves (unless dragging)."""
        if self._hover and not self._dragging:
            self._hover = False
            self._draw()


    def _update_position_from_event(self, event: tk.Event) -> None:
        """Convert mouse X coordinate to timeline position (seconds) and notify."""
        width = self.winfo_width()
        if width > 0 and self.duration > 0:
            # Clamp position to canvas bounds
            x = max(0, min(event.x, width))
            new_position = (x / width) * self.duration
            self.set_position(new_position)
            if self.position_callback:
                self.position_callback(new_position)


    def set_duration(self, duration: float) -> None:
        """Set timeline total duration (seconds)."""
        self.duration = duration
        self._draw()


    def set_position(self, position: float) -> None:
        """Set current timeline position (seconds), clamped to [0, duration]."""
        self.current_position = max(0.0, min(position, self.duration))
        self._draw()


    def get_position(self) -> float:
        """Return current timeline position in seconds."""
        return self.current_position


    def is_dragging(self) -> bool:
        """Return True if the timeline is being dragged."""
        return self._dragging


#endregion
#region VideoPlayerWidget


class VideoPlayerWidget(ttk.Frame):
    """Video player widget using tkVideoPlayer; optional controls shown."""
    def __init__(self,
                master: Optional[tk.Widget] = None,
                app: Optional['Main'] = None,
                show_controls: bool = True,
                play_image: Optional[Union[PhotoImage, str]] = None,
                pause_image: Optional[Union[PhotoImage, str]] = None,
                **kwargs: Any
                ) -> None:
        """
        Initialize widget, player, controls and event bindings.

        Parameters:
        - master: Parent tk.Frame or tk.Tk instance
        - show_controls: Whether to show playback controls
        - kwargs: Additional arguments to pass to ttk.Frame
        """
        super().__init__(master, **kwargs)
        self.root = self._find_root()
        # Initialize video player
        self.player: Optional[TkinterVideo] = TkinterVideo(keep_aspect=True, master=self)
        self.player.pack(expand=True, fill="both")
        # Create loading label (initially hidden)
        self.loading_label = ttk.Label(self, text="Loading...", font=('', 14))
        # Initialize repeat state
        self.repeat: bool = True
        self.playing: bool = False
        # Bind video events
        self.player.bind("<<Duration>>", self._update_duration)
        self.player.bind("<<SecondChanged>>", self._update_progress)
        self.player.bind("<<Ended>>", self._handle_video_ended)
        # Convert file paths to PhotoImage if needed
        if isinstance(play_image, str) and os.path.isfile(play_image):
            play_image = PhotoImage(file=play_image)
        if isinstance(pause_image, str) and os.path.isfile(pause_image):
            pause_image = PhotoImage(file=pause_image)
        self.play_image = play_image
        self.pause_image = pause_image
        # Create player controls if enabled
        if show_controls:
            self._create_controls()
        # Bind events to app if provided
        if app:
            self.player.bind("<Double-1>", lambda event: app.open_image(index=app.current_index, event=event))
            self.player.bind('<Button-2>', app.open_image_directory)
            self.player.bind("<Button-3>", app.show_image_context_menu)
            self.player.bind("<Shift-MouseWheel>", app.mousewheel_nav)
        self.player.bind("<Shift-Button-1>", self.start_drag, add="+")
        self.player.bind("<Shift-B1-Motion>", self.dragging_window, add="+")
        self.player.bind("<Shift-ButtonRelease-1>", self.stop_drag, add="+")
        self._timeline_update_job: Optional[str] = None


    def _find_root(self) -> Optional[tk.Tk]:
        """Find the root tk.Tk window from this widget's parent chain."""
        master = self.master
        while master is not None and not isinstance(master, tk.Tk):
            master = getattr(master, "master", None)
        return master


    def _set_play_pause_btn(self, playing: bool) -> None:
        """Update play/pause button image or text based on state."""
        if not hasattr(self, 'play_pause_btn'):
            return
        if playing:
            if self.pause_image:
                self.play_pause_btn.config(image=self.pause_image)
                self.play_pause_btn.image = self.pause_image
            else:
                self.play_pause_btn.config(text="◼")
        else:
            if self.play_image:
                self.play_pause_btn.config(image=self.play_image)
                self.play_pause_btn.image = self.play_image
            else:
                self.play_pause_btn.config(text="▶")


    def _create_controls(self) -> None:
        """Create control row: play/pause, time labels and timeline canvas."""
        # Single control row
        frame = ttk.Frame(self)
        frame.pack(side="bottom", fill="x", padx=5)
        # Play/Pause button
        if self.play_image:
            self.play_pause_btn = ttk.Button(frame, image=self.play_image, command=self.toggle_play_pause, width=2, takefocus=False)
            self.play_pause_btn.image = self.play_image
        else:
            self.play_pause_btn = ttk.Button(frame, text="▶", command=self.toggle_play_pause, width=2, takefocus=False)
        self.play_pause_btn.pack(side="left")
        # Current duration label
        self.current_duration_label = ttk.Label(frame, text="0:00:00")
        self.current_duration_label.pack(side="left")
        # Custom Canvas timeline
        self.timeline = TimelineCanvas(frame)
        self.timeline.position_callback = self._seek_from_timeline
        self.timeline.press_callback = self._on_timeline_press
        self.timeline.release_callback = self._on_timeline_release
        self.timeline.pack(side="left", fill="x", expand=True, padx=5)
        # Total video duration label
        self.full_duration_label = ttk.Label(frame, text="0:00:00")
        self.full_duration_label.pack(side="left")
        # Track state
        self._was_playing: bool = False


    def show_loading_label(self) -> None:
        """Place a centered loading label over the player."""
        self.loading_label.place(relx=0.5, rely=0.5, anchor='center')
        self.update_idletasks()


    def hide_loading_label(self) -> None:
        """Hide the loading label."""
        self.loading_label.place_forget()


    def load_video(self, file_path: Optional[str] = None) -> bool:
        """Load a video file (or prompt). Start playback shortly after load."""
        if file_path is None:
            file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4"), ("All files", "*.*")])
        if file_path:
            self.player.load(file_path)
            self._set_play_pause_btn(playing=False)
            self.timeline.set_duration(0)
            self.timeline.set_position(0)
            self.show_loading_label()
            self.after(425, self.play)
            return True
        return False


    def play(self) -> None:
        """Start playback and begin frequent timeline updates."""
        self.hide_loading_label()
        self.player.play()
        self._set_play_pause_btn(playing=True)
        self.playing = True
        self._start_timeline_update()


    def pause(self) -> None:
        """Pause playback and stop frequent timeline updates."""
        self.player.pause()
        self._set_play_pause_btn(playing=False)
        self.playing = False
        self._stop_timeline_update()


    def toggle_play_pause(self) -> None:
        """Toggle playback if a video is loaded."""
        if not self.player or not getattr(self.player, "video_path", None):
            return  # No video loaded yet
        if self.player.is_paused():
            self.play()
        else:
            self.pause()


    def stop(self) -> None:
        """Stop playback and reset timeline position."""
        self.player.stop()
        self._set_play_pause_btn(playing=False)
        self.timeline.set_position(0)
        self.playing = False
        self._stop_timeline_update()


    def seek(self, position: float) -> None:
        """Seek to position (seconds). Use precise seek when available."""
        if self.player:
            try:
                # Prefer precise seek if supported by underlying player
                self.player.seek(float(position), precise=True)
            except TypeError:
                # Fallback if 'precise' kwarg isn't accepted
                self.player.seek(float(position))
            self.timeline.set_position(position)


    def skip(self, seconds: float) -> None:
        """Skip forward/back by seconds from current position."""
        if self.player:
            current_pos = self.player.current_duration()
            new_pos = max(0.0, current_pos + seconds)
            self.seek(new_pos)


    def _on_timeline_press(self) -> None:
        """Pause while user starts dragging the timeline (remember state)."""
        self._was_playing = self.playing
        if self.playing:
            self.pause()


    def _on_timeline_release(self) -> None:
        """Seek to released position and resume if previously playing."""
        position = self.timeline.get_position()
        self.player.seek(float(position), precise=True)
        if self._was_playing:
            self.play()


    def _seek_from_timeline(self, value: float) -> None:
        """Update time label and, while dragging, seek to the transient position."""
        seconds = float(value)
        formatted_time = str(datetime.timedelta(seconds=seconds)).split(".")[0]
        milliseconds = int((seconds - int(seconds)) * 1000)
        self.current_duration_label.config(text=f"{formatted_time}.{milliseconds:03d}")

        # Seek during drag
        if self.timeline.is_dragging():
            self.player.seek(float(seconds), precise=True)


    def _update_duration(self, event: Optional[tk.Event] = None) -> None:
        """Update displayed total duration and timeline length when available."""
        duration = self.player.video_info()["duration"]
        self.full_duration_label.config(text=str(datetime.timedelta(seconds=duration)).split(".")[0])
        self.timeline.set_duration(duration)


    def _start_timeline_update(self) -> None:
        """Begin the recurring UI updates for the timeline during playback."""
        if self._timeline_update_job is None:
            self._timeline_update_job = self.after(50, self._update_timeline_frequently)


    def _stop_timeline_update(self) -> None:
        """Cancel recurring timeline UI updates."""
        if self._timeline_update_job is not None:
            self.after_cancel(self._timeline_update_job)
            self._timeline_update_job = None


    def _update_timeline_frequently(self) -> None:
        """Frequent updater: sync timeline and time label while playing."""
        if self.playing and not self.timeline.is_dragging():
            current = self.player.current_duration()
            self.timeline.set_position(current)
            formatted_time = str(datetime.timedelta(seconds=int(current))).split(".")[0]
            milliseconds = int((current - int(current)) * 1000)
            self.current_duration_label.config(text=f"{formatted_time}.{milliseconds:03d}")
        # Schedule next update if still playing
        if self.playing:
            self._timeline_update_job = self.after(50, self._update_timeline_frequently)
        else:
            self._timeline_update_job = None


    def _update_progress(self, event: Optional[tk.Event] = None) -> None:
        """Less frequent progress callback kept for compatibility."""
        # This method is still called by <<SecondChanged>>, but frequent updates are handled separately.
        if not self.timeline.is_dragging():
            current = self.player.current_duration()
            self.timeline.set_position(current)
            formatted_time = str(datetime.timedelta(seconds=int(current))).split(".")[0]
            milliseconds = int((current - int(current)) * 1000)
            self.current_duration_label.config(text=f"{formatted_time}.{milliseconds:03d}")


    def _handle_video_ended(self, event: Optional[tk.Event] = None) -> None:
        """Reset/seek to start and optionally replay when video ends."""
        # Stop any frequent timeline updates to avoid overlapping jobs
        self._stop_timeline_update()
        # Reset timeline visually to start
        self.timeline.set_position(0)
        # Seek player to start; prefer precise seek if available
        if self.player:
            try:
                self.player.seek(0, precise=True)
            except TypeError:
                self.player.seek(0)
        if self.repeat:
            # Small delay ensures the player internal state is settled before starting playback
            self.after(50, self.play)
        else:
            # Show stopped UI state
            self._set_play_pause_btn(playing=False)
            self.timeline.set_position(0)


    def get_player(self) -> Optional[TkinterVideo]:
        """Return the internal TkinterVideo instance."""
        return self.player


    def destroy_player(self) -> None:
        """Destroy the player instance and widget."""
        self.player.destroy()
        self.player = None
        self.playing = False
        self.destroy()


    def get_current_frame(self) -> Optional[Any]:
        """Return current frame as PIL.Image if available, else None."""
        if self.player and getattr(self.player, "video_path", None):
            return self.player.current_img()
        return None


    def start_drag(self, event: tk.Event) -> None:
        """Begin window-dragging when shift+click is used on the player."""
        self.drag_x = event.x
        self.drag_y = event.y
        self.player.config(cursor="size")


    def stop_drag(self, event: tk.Event) -> None:
        """End window-dragging and restore cursor."""
        self.drag_x = None
        self.drag_y = None
        self.player.config(cursor="arrow")


    def dragging_window(self, event: tk.Event) -> None:
        """Move the root window while dragging (shift + mouse drag)."""
        if self.drag_x is not None and self.drag_y is not None:
            dx = event.x - self.drag_x
            dy = event.y - self.drag_y
            x = self.root.winfo_x() + dx
            y = self.root.winfo_y() + dy
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            self.root.geometry(f"{width}x{height}+{x}+{y}")
