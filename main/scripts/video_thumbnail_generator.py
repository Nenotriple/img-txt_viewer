import av
import os
from typing import List, Dict, Optional, Tuple, Any

from PIL import Image


def generate_video_thumbnails(
    file_paths: List[str],
    timestamp_seconds: float = 2.0,
    thumbnail_size: Optional[Tuple[int, int]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Generate thumbnails for MP4 files in the given list of file paths.

    Args:
        file_paths: List of file paths to process
        timestamp_seconds: Time position in seconds to extract the thumbnail from
        thumbnail_size: Optional tuple (width, height) to resize thumbnails

    Returns:
        Dictionary with file paths as keys and dictionaries as values containing:
            - 'thumbnail': PIL Image object
            - 'resolution': Tuple (width, height) of original video
            - 'framerate': Float value of video framerate
    """
    video_thumb_dict = {}
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
            # Extract resolution and framerate
            resolution = (stream.width, stream.height)
            framerate = float(stream.average_rate) if stream.average_rate else None
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
                # Store thumbnail along with resolution and framerate
                video_thumb_dict[file_path] = {
                    'thumbnail': img,
                    'resolution': resolution,
                    'framerate': framerate
                }
                frame_extracted = True
                break  # Only need one frame
            if not frame_extracted:
                print(f"Could not extract frame from: {file_path}")
            container.close()
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    return video_thumb_dict


def get_video_frame(
    file_path: str,
    timestamp_seconds: float = 2.0,
    thumbnail_size: Optional[Tuple[int, int]] = None
) -> Optional[Image.Image]:
    """
    Extract a single frame from a video file at the specified timestamp.

    Args:
        file_path: Path to the video file
        timestamp_seconds: Time position in seconds to extract the frame from
        thumbnail_size: Optional tuple (width, height) to resize the frame

    Returns:
        PIL Image object of the extracted frame or None if extraction fails
    """
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        # Open the video file
        container = av.open(file_path)
        # Get video stream
        if not container.streams.video:
            print(f"No video stream found in: {file_path}")
            container.close()
            return None
        stream = container.streams.video[0]
        # Seek to the target frame
        container.seek(int(timestamp_seconds * 1000000), stream=stream)
        # Get the frame
        for frame in container.decode(stream):
            # Convert the frame to a PIL Image
            img = frame.to_image()
            # Resize if needed
            if thumbnail_size:
                img = img.resize(thumbnail_size, Image.LANCZOS)
            # Clean up and return the frame
            container.close()
            return img
        print(f"Could not extract frame from: {file_path}")
        container.close()
        return None
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None
