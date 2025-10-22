#region Imports


import os
import shutil
import subprocess

from tkinter import messagebox

from PIL import Image, ImageSequence

import main.scripts.custom_simpledialog as custom_simpledialog

from typing import TYPE_CHECKING, Optional, Tuple
if TYPE_CHECKING:
	from app import ImgTxtViewer as Main


#endregion
#region Main Controller


def extract(app: "Main", input_path: Optional[str] = None) -> Optional[str]:
	"""Extract frames from a GIF or MP4 into PNG files.
	Returns the output directory path on success, otherwise None.
	"""
	input_path = _resolve_input_path(app, input_path)
	if input_path is None:
		return None
	out_dir = get_out_dir(input_path)
	if not messagebox.askyesno("Confirm Extraction", f"Extract frames from:\n\n{input_path}\n\nInto the folder:\n\n{out_dir}\n\nThis may take some time depending on the frame size and number of frames."):
		return None
	out_dir = _prepare_output_directory(input_path)
	if out_dir is None:
		return None
	ext = os.path.splitext(input_path)[1].lower()
	try:
		if ext == '.gif':
			success, frame_count = _extract_gif_frames_with_progress(input_path, out_dir)
			if success:
				_show_done_and_open_folder(frame_count, out_dir)
				return out_dir
		elif ext == '.mp4':
			success, frame_count = _extract_mp4_frames_with_progress(app, input_path, out_dir)
			if success:
				_show_done_and_open_folder(frame_count, out_dir)
				return out_dir
	except subprocess.CalledProcessError as e:
		messagebox.showerror("FFmpeg Error", f"FFmpeg failed to extract frames:\n\n{e}")
	except Exception as e:
		messagebox.showerror("Error", f"An error occurred while extracting frames:\n\n{e}")
	return None


#endregion
#region Validation & Output Helpers


def _resolve_input_path(app: "Main", input_path: Optional[str]) -> Optional[str]:
	"""Return a validated input path for GIF or MP4, or None on failure."""
	if input_path is None:
		if not app.check_if_directory():
			return None
		if not app.image_files:
			messagebox.showwarning("No File Selected", "No image or video file is selected.")
			return None
		input_path = app.image_files[app.current_index]
	if not os.path.isfile(input_path):
		messagebox.showerror("File Not Found", f"The file does not exist:\n\n{input_path}")
		return None
	ext = os.path.splitext(input_path)[1].lower()
	if ext not in ('.gif', '.mp4'):
		messagebox.showwarning("Unsupported Filetype", "Only GIF and MP4 files can be extracted.")
		return None
	return input_path


def _prepare_output_directory(input_path: str) -> Optional[str]:
	"""Create or clear the output folder named after the input file (without extension)."""
	out_dir = get_out_dir(input_path)
	if os.path.exists(out_dir) and os.listdir(out_dir):
		if not messagebox.askyesno("Output Folder Exists", f"The folder:\n\n{out_dir}\n\nalready exists and contains files.\n\nDelete its contents and continue?"):
			return None
		try:
			shutil.rmtree(out_dir)
		except Exception as e:
			messagebox.showerror("Error", f"Failed to clear existing output folder:\n\n{e}")
			return None
	os.makedirs(out_dir, exist_ok=True)
	return out_dir


def get_out_dir(input_path: str) -> str:
	"""Return the output directory path for the given input file."""
	parent_dir = os.path.dirname(input_path)
	base_name = os.path.splitext(os.path.basename(input_path))[0]
	out_dir = os.path.join(parent_dir, base_name)
	return out_dir


def _show_done_and_open_folder(frame_count: int, out_dir: str):
	"""Show 'Done' dialog and optionally open folder in explorer."""
	if messagebox.askyesno("Done", f"Extracted {frame_count} frame(s) to:\n\n{out_dir}\n\nOpen this folder in File Explorer?"):
		_open_folder_in_explorer(out_dir)


def _open_folder_in_explorer(path: str):
	"""Open the given folder in Windows File Explorer."""
	try:
		os.startfile(path)
	except Exception as e:
		messagebox.showerror("Error", f"Could not open folder:\n\n{e}")


#endregion
#region Format Extraction


def _extract_gif_frames_with_progress(input_path: str, out_dir: str) -> Tuple[bool, int]:
	"""Extract frames from a GIF with progress dialog."""
	def gif_task(progress_callback):
		with Image.open(input_path) as img:
			palette = img.getpalette()
			previous = Image.new('RGBA', img.size)
			frame_count = 0
			total_frames = getattr(img, "n_frames", None)
			for i, frame in enumerate(ImageSequence.Iterator(img)):
				if frame.mode == 'P' and palette is not None:
					frame.putpalette(palette)
				frame_rgba = frame.convert('RGBA')
				x_offset, y_offset = 0, 0
				tile = getattr(frame, 'tile', None)
				if tile:
					try:
						bbox = tile[0][1]
						if isinstance(bbox, (tuple, list)) and len(bbox) >= 2:
							x_offset, y_offset = bbox[0], bbox[1]
					except Exception:
						x_offset, y_offset = 0, 0
				composed = previous.copy()
				composed.paste(frame_rgba, (x_offset, y_offset), frame_rgba)
				out_path = os.path.join(out_dir, f"frame_{i:05d}.png")
				composed.save(out_path)
				disposal = frame.info.get('disposal', 1)
				if disposal == 2:
					previous = Image.new('RGBA', img.size)
				else:
					previous = composed
				frame_count += 1
				progress_callback(i + 1, f"Extracting frame {i+1}", f"{frame_count} extracted")
			return frame_count
	total_frames = None
	with Image.open(input_path) as img:
		total_frames = getattr(img, "n_frames", None)
	if total_frames is None:
		# fallback: count frames
		with Image.open(input_path) as img:
			total_frames = sum(1 for _ in ImageSequence.Iterator(img))
	frame_count = custom_simpledialog.showprogress("Extracting GIF Frames", "Extracting frames from GIF...", gif_task, args=(), max_value=total_frames)
	return (frame_count is not None), frame_count or 0


def _extract_mp4_frames_with_progress(app: "Main", input_path: str, out_dir: str) -> Tuple[bool, int]:
	"""Extract frames from an MP4 using ffmpeg with progress dialog."""
	if not app.is_ffmpeg_installed:
		messagebox.showwarning("FFmpeg Not Found", "FFmpeg is required to extract frames from videos.\n\nPlease install FFmpeg and ensure it is in your PATH.")
		return False, 0

	def mp4_task(progress_callback):
		cmd = [
			"ffmpeg",
			"-hide_banner",
			"-loglevel", "error",
			"-i", input_path,
			os.path.join(out_dir, "frame_%05d.png")
		]
		# Use helper to estimate frame count
		total_frames = _estimate_frames_with_ffprobe(input_path)
		proc = subprocess.Popen(cmd)
		import time
		frame_count = 0
		while proc.poll() is None:
			# Use helper to count extracted image files
			frame_count = _count_image_files(out_dir)
			progress_callback(frame_count, f"Extracting frame {frame_count}", f"{frame_count} extracted")
			time.sleep(0.2)
		# Final count
		frame_count = _count_image_files(out_dir)
		progress_callback(frame_count, f"Extracting frame {frame_count}", f"{frame_count} extracted")
		return frame_count

	try:
		total_frames = _estimate_frames_with_ffprobe(input_path)
	except Exception:
		total_frames = None
	frame_count = custom_simpledialog.showprogress("Extracting MP4 Frames", "Extracting frames from MP4...", mp4_task, args=(), max_value=total_frames if total_frames else 1000)
	return (frame_count is not None), frame_count or 0


def _count_image_files(out_dir: str, exts: Tuple[str, ...] = ('.png', '.jpg', '.jpeg')) -> int:
	"""Return the number of image files in out_dir matching the given extensions."""
	try:
		return sum(1 for f in os.listdir(out_dir) if f.lower().endswith(exts))
	except Exception:
		return 0


def _estimate_frames_with_ffprobe(input_path: str) -> Optional[int]:
	"""Use ffprobe to estimate the total frame count for a video. Returns None on failure."""
	try:
		import json
		probe_cmd = [
			"ffprobe",
			"-v", "error",
			"-select_streams", "v:0",
			"-count_frames",
			"-show_entries", "stream=nb_read_frames",
			"-of", "json",
			input_path
		]
		proc = subprocess.run(probe_cmd, capture_output=True, text=True)
		info = json.loads(proc.stdout or "{}")
		streams = info.get("streams")
		if not streams:
			return None
		val = streams[0].get("nb_read_frames")
		if val is None:
			return None
		try:
			return int(val)
		except (ValueError, TypeError):
			return None
	except Exception:
		return None


#endregion
