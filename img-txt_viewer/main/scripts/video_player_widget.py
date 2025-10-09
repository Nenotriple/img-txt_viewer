#region Imports


import datetime
from tkinter import ttk, filedialog
from tkVideoPlayer import TkinterVideo


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region VideoPlayerWidget


class VideoPlayerWidget(ttk.Frame):
    """A Tkinter widget for video playback using tkVideoPlayer"""
    def __init__(self, master=None, app: 'Main'=None, show_controls=True, **kwargs):
        """
        Initialize the video player widget

        Parameters:
        - master: Parent tk.Frame or tk.Tk instance
        - show_controls: Whether to show playback controls
        - kwargs: Additional arguments to pass to ttk.Frame
        """
        super().__init__(master, **kwargs)
        # Initialize video player
        self.vid_player = TkinterVideo(keep_aspect=True, master=self)
        self.vid_player.pack(expand=True, fill="both")
        # Create loading label (initially hidden)
        self.loading_label = ttk.Label(self, text="Loading...", font=('', 14))
        # Initialize repeat state
        self.repeat = True
        self.playing = False
        # Bind video events
        self.vid_player.bind("<<Duration>>", self._update_duration)
        self.vid_player.bind("<<SecondChanged>>", self._update_progress)
        self.vid_player.bind("<<Ended>>", self._handle_video_ended)
        # Create player controls if enabled
        if show_controls:
            self._create_controls()
        # Bind events to app if provided
        if app:
            self.vid_player.bind("<Double-1>", lambda event: app.open_image(index=app.current_index, event=event))
            self.vid_player.bind('<Button-2>', app.open_image_directory)
            self.vid_player.bind("<Button-3>", app.show_image_context_menu)


    def _create_controls(self):
        """Create player controls"""
        # Single control row
        controls = ttk.Frame(self)
        controls.pack(side="bottom", fill="x", padx=5)
        # Play/Pause button
        self.play_pause_btn = ttk.Button(controls, text="▶", command=self.toggle_play_pause, width=3)
        self.play_pause_btn.pack(side="left")
        # Start time label
        self.start_time = ttk.Label(controls, text="0:00:00")
        self.start_time.pack(side="left")
        # Progress slider
        self.progress_slider = ttk.Scale(controls, from_=0, to=0, orient="horizontal", command=self._seek_from_slider)
        self.progress_slider.bind("<ButtonRelease-1>", self._seek_on_release)
        self.progress_slider.pack(side="left", fill="x", expand=True)
        # End time label
        self.end_time = ttk.Label(controls, text="0:00:00")
        self.end_time.pack(side="left")


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
            self.vid_player.load(file_path)
            self.play_pause_btn.config(text="▶")
            self.progress_slider.config(to=0, from_=0)
            self.progress_slider.set(0)
            self.show_loading_label()
            self.after(425, self.play)
            return True
        return False


    def play(self):
        """Play the video"""
        self.hide_loading_label()
        self.vid_player.play()
        self.play_pause_btn.config(text="◼")
        self.playing = True


    def pause(self):
        """Pause the video"""
        self.vid_player.pause()
        self.play_pause_btn.config(text="▶")
        self.playing = False


    def toggle_play_pause(self):
        """Toggle between play and pause"""
        if not self.vid_player.path:
            return  # No video loaded yet
        if self.vid_player.is_paused():
            self.play()
        else:
            self.pause()


    def stop(self):
        """Stop the video"""
        self.vid_player.stop()
        self.play_pause_btn.config(text="▶")
        self.progress_slider.set(0)
        self.playing = False


    def seek(self, position):
        """Seek to a specific position in seconds"""
        self.vid_player.seek(int(position))
        self.progress_slider.set(position)
        if not self.playing:
            self.toggle_play_pause()
            self.after(20, self.toggle_play_pause)


    def skip(self, seconds):
        """Skip forward or backward by the specified seconds"""
        current_pos = self.vid_player.current_duration()
        new_pos = max(0, current_pos + seconds)
        self.seek(new_pos)


    def _seek_from_slider(self, value):
        """Update time label when slider moves"""
        seconds = float(value)
        self.start_time.config(text=str(datetime.timedelta(seconds=seconds)).split(".")[0])


    def _seek_on_release(self, event=None):
        """Seek when slider is released"""
        self.seek(self.progress_slider.get())


    def _update_duration(self, event=None):
        """Update duration display when video is loaded"""
        duration = self.vid_player.video_info()["duration"]
        self.end_time.config(text=str(datetime.timedelta(seconds=duration)).split(".")[0])
        self.progress_slider.config(to=duration)


    def _update_progress(self, event=None):
        """Update progress slider when video plays"""
        current = self.vid_player.current_duration()
        self.progress_slider.set(current)
        self.start_time.config(text=str(datetime.timedelta(seconds=current)).split(".")[0])


    def _handle_video_ended(self, event=None):
        """Handle video end event"""
        if self.repeat:
            self.seek(0)
            self.play()
        else:
            self.play_pause_btn.config(text="▶")
            self.progress_slider.set(0)


    def get_player(self):
        """Return the underlying TkinterVideo instance"""
        return self.vid_player


    def destroy_player(self):
        """Destroy the underlying TkinterVideo instance"""
        self.vid_player.destroy()
        self.vid_player = None
        self.playing = False
        self.destroy()


    def get_current_frame(self):
        """
        Get the current frame of the video as a PIL Image object.

        Returns:
            PIL.Image: The current frame or None if no frame is available
        """
        if self.vid_player and self.vid_player.path:
            return self.vid_player.current_img()
        return None
