import av
import os
from typing import List, Dict, Optional, Tuple

from PIL import Image


def generate_video_thumbnails(
    file_paths: List[str],
    timestamp_seconds: float = 2.0,
    thumbnail_size: Optional[Tuple[int, int]] = None
) -> Dict[str, Image.Image]:
    """
    Generate thumbnails for MP4 files in the given list of file paths.

    Args:
        file_paths: List of file paths to process
        timestamp_seconds: Time position in seconds to extract the thumbnail from
        thumbnail_size: Optional tuple (width, height) to resize thumbnails

    Returns:
        Dictionary with file paths as keys and thumbnail images as values
    """
    thumbnails = {}
    for file_path in file_paths:
        # Skip if not an MP4 file
        if not file_path.lower().endswith('.mp4'):
            continue
        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue
            # Open the video file
            container = av.open(file_path)
            # Get video stream
            if not container.streams.video:
                print(f"No video stream found in: {file_path}")
                continue
            stream = container.streams.video[0]
            # Seek to the target frame
            container.seek(int(timestamp_seconds * 1000000), stream=stream)
            # Get the frame
            frame_extracted = False
            for frame in container.decode(stream):
                # Convert the frame to a PIL Image
                img = frame.to_image()
                # Resize if needed
                if thumbnail_size:
                    img = img.resize(thumbnail_size, Image.LANCZOS)
                thumbnails[file_path] = img
                frame_extracted = True
                break  # Only need one frame
            if not frame_extracted:
                print(f"Could not extract frame from: {file_path}")
            container.close()
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    return thumbnails
