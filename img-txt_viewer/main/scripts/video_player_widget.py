#region Imports


import datetime
import os
import tkinter as tk
from tkinter import PhotoImage, ttk, filedialog
from tkVideoPlayer import TkinterVideo


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region TimelineCanvas


class TimelineCanvas(tk.Canvas):
    """A custom Canvas-based timeline widget for video scrubbing"""
    def __init__(self, master, height=15, **kwargs):
        super().__init__(master, height=height, highlightthickness=0, **kwargs)
        self.duration = 0
        self.current_position = 0
        self._dragging = False
        self._hover = False

        # Callback for position changes
        self.position_callback = None
        self.press_callback = None
        self.release_callback = None

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


    def _draw(self):
        """Draw the timeline"""
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


    def _on_resize(self, event=None):
        """Redraw when canvas is resized"""
        self._draw()


    def _on_click(self, event):
        """Handle click on timeline"""
        self._dragging = True
        self._update_position_from_event(event)
        if self.press_callback:
            self.press_callback()


    def _on_drag(self, event):
        """Handle dragging on timeline"""
        if self._dragging:
            self._update_position_from_event(event)


    def _on_release(self, event):
        """Handle release on timeline"""
        self._dragging = False
        self._update_position_from_event(event)
        if self.release_callback:
            self.release_callback()
        self._draw()


    def _on_hover(self, event):
        """Handle hover effect"""
        if not self._hover:
            self._hover = True
            self._draw()


    def _on_leave(self, event):
        """Handle mouse leave"""
        if self._hover and not self._dragging:
            self._hover = False
            self._draw()


    def _update_position_from_event(self, event):
        """Update position based on mouse event"""
        width = self.winfo_width()
        if width > 0 and self.duration > 0:
            # Clamp position to canvas bounds
            x = max(0, min(event.x, width))
            new_position = (x / width) * self.duration
            self.set_position(new_position)
            if self.position_callback:
                self.position_callback(new_position)


    def set_duration(self, duration):
        """Set the total duration of the timeline"""
        self.duration = duration
        self._draw()


    def set_position(self, position):
        """Set the current position"""
        self.current_position = max(0, min(position, self.duration))
        self._draw()


    def get_position(self):
        """Get the current position"""
        return self.current_position


    def is_dragging(self):
        """Check if timeline is being dragged"""
        return self._dragging


#endregion
#region VideoPlayerWidget


class VideoPlayerWidget(ttk.Frame):
    """A Tkinter widget for video playback using tkVideoPlayer"""
    def __init__(self, master=None, app: 'Main'=None, show_controls=True, play_image=None, pause_image=None, **kwargs):
        """
        Initialize the video player widget

        Parameters:
        - master: Parent tk.Frame or tk.Tk instance
        - show_controls: Whether to show playback controls
        - kwargs: Additional arguments to pass to ttk.Frame
        """
        super().__init__(master, **kwargs)
        self.root = self._find_root()
        # Initialize video player
        self.player = TkinterVideo(keep_aspect=True, master=self)
        self.player.pack(expand=True, fill="both")
        # Create loading label (initially hidden)
        self.loading_label = ttk.Label(self, text="Loading...", font=('', 14))
        # Initialize repeat state
        self.repeat = True
        self.playing = False
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
        self._timeline_update_job = None


    def _find_root(self):
        """Find the root window from master."""
        master = self.master
        while master is not None and not isinstance(master, tk.Tk):
            master = getattr(master, "master", None)
        return master


    def _set_play_pause_btn(self, playing: bool):
        """Set play/pause button icon or text based on playing state."""
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


    def _create_controls(self):
        """Create player controls"""
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
        self._was_playing = False


    def show_loading_label(self):
        """Display the loading label centered on the video player"""
        self.loading_label.place(relx=0.5, rely=0.5, anchor='center')
        self.update_idletasks()


    def hide_loading_label(self):
        """Hide the loading label"""
        self.loading_label.place_forget()


    def load_video(self, file_path=None):
        """Load a video file"""
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


    def play(self):
        """Play the video"""
        self.hide_loading_label()
        self.player.play()
        self._set_play_pause_btn(playing=True)
        self.playing = True
        self._start_timeline_update()


    def pause(self):
        """Pause the video"""
        self.player.pause()
        self._set_play_pause_btn(playing=False)
        self.playing = False
        self._stop_timeline_update()


    def toggle_play_pause(self):
        """Toggle between play and pause"""
        if not self.player or not self.player.video_path:
            return  # No video loaded yet
        if self.player.is_paused():
            self.play()
        else:
            self.pause()


    def stop(self):
        """Stop the video"""
        self.player.stop()
        self._set_play_pause_btn(playing=False)
        self.timeline.set_position(0)
        self.playing = False
        self._stop_timeline_update()


    def seek(self, position):
        """Seek to a specific position in seconds"""
        if self.player:
            self.player.seek(float(position))
            self.timeline.set_position(position)
            if not self.playing:
                self.toggle_play_pause()
                self.after(20, self.toggle_play_pause)


    def skip(self, seconds):
        """Skip forward or backward by the specified seconds"""
        if self.player:
            current_pos = self.player.current_duration()
            new_pos = max(0, current_pos + seconds)
            self.seek(new_pos)


    def _on_timeline_press(self):
        """Handle timeline press - pause video"""
        self._was_playing = self.playing
        if self.playing:
            self.pause()


    def _on_timeline_release(self):
        """Handle timeline release - resume playback if needed"""
        position = self.timeline.get_position()
        self.player.seek(float(position), precise=True)
        if self._was_playing:
            self.play()


    def _seek_from_timeline(self, value):
        """Update time label and seek when timeline moves"""
        seconds = float(value)
        formatted_time = str(datetime.timedelta(seconds=seconds)).split(".")[0]
        milliseconds = int((seconds - int(seconds)) * 1000)
        self.current_duration_label.config(text=f"{formatted_time}.{milliseconds:03d}")

        # Seek during drag
        if self.timeline.is_dragging():
            self.player.seek(float(seconds), precise=True)


    def _update_duration(self, event=None):
        """Update duration display when video is loaded"""
        duration = self.player.video_info()["duration"]
        self.full_duration_label.config(text=str(datetime.timedelta(seconds=duration)).split(".")[0])
        self.timeline.set_duration(duration)


    def _start_timeline_update(self):
        """Start frequent timeline updates during playback"""
        if self._timeline_update_job is None:
            self._timeline_update_job = self.after(50, self._update_timeline_frequently)


    def _stop_timeline_update(self):
        """Stop frequent timeline updates"""
        if self._timeline_update_job is not None:
            self.after_cancel(self._timeline_update_job)
            self._timeline_update_job = None


    def _update_timeline_frequently(self):
        """Update timeline position more frequently during playback"""
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


    def _update_progress(self, event=None):
        """Update progress slider when video plays"""
        # This method is still called by <<SecondChanged>>, but frequent updates are handled separately.
        if not self.timeline.is_dragging():
            current = self.player.current_duration()
            self.timeline.set_position(current)
            formatted_time = str(datetime.timedelta(seconds=int(current))).split(".")[0]
            milliseconds = int((current - int(current)) * 1000)
            self.current_duration_label.config(text=f"{formatted_time}.{milliseconds:03d}")


    def _handle_video_ended(self, event=None):
        """Handle video end event"""
        self._stop_timeline_update()
        if self.repeat:
            self.seek(0)
            self.play()
        else:
            self._set_play_pause_btn(playing=False)
            self.timeline.set_position(0)


    def get_player(self):
        """Return the underlying TkinterVideo instance"""
        return self.player


    def destroy_player(self):
        """Destroy the underlying TkinterVideo instance"""
        self.player.destroy()
        self.player = None
        self.playing = False
        self.destroy()


    def get_current_frame(self):
        """
        Get the current frame of the video as a PIL Image object.

        Returns:
            PIL.Image: The current frame or None if no frame is available
        """
        if self.player and self.player.video_path:
            return self.player.current_img()
        return None


    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
        self.player.config(cursor="size")


    def stop_drag(self, event):
        self.drag_x = None
        self.drag_y = None
        self.player.config(cursor="arrow")


    def dragging_window(self, event):
        if self.drag_x is not None and self.drag_y is not None:
            dx = event.x - self.drag_x
            dy = event.y - self.drag_y
            x = self.root.winfo_x() + dx
            y = self.root.winfo_y() + dy
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            self.root.geometry(f"{width}x{height}+{x}+{y}")
