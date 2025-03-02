import datetime
import tkinter as tk
from tkinter import ttk, filedialog
from tkVideoPlayer import TkinterVideo


class VideoPlayerWidget(ttk.Frame):
    """A Tkinter widget for video playback using tkVideoPlayer"""
    def __init__(self, master=None, show_controls=True, **kwargs):
        """
        Initialize the video player widget

        Parameters:
        - master: Parent widget
        - show_controls: Whether to show playback controls
        - kwargs: Additional arguments to pass to ttk.Frame
        """
        super().__init__(master, **kwargs)
        # Initialize video player
        self.vid_player = TkinterVideo(keep_aspect=True, master=self)
        self.vid_player.pack(expand=True, fill="both")
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


    def _create_controls(self):
        """Create player controls"""
        # Single control row
        controls = ttk.Frame(self)
        controls.pack(fill="x", side="bottom")
        # Play/Pause button
        self.play_pause_btn = ttk.Button(controls, text="▶", command=self.stop, width=3)
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


    def load_video(self, file_path=None):
        """Load a video file"""
        if file_path is None:
            file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4"), ("All files", "*.*")])
        if file_path:
            self.vid_player.load(file_path)
            self.play_pause_btn.config(text="▶")
            self.progress_slider.config(to=0, from_=0)
            self.progress_slider.set(0)
            self.after(200, self.play)
            return True
        return False


    def play(self):
        """Play the video"""
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
