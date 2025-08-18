import av
import os
from typing import List, Dict, Optional, Tuple, Any

from PIL import Image


def _open_video_container(file_path: str) -> Optional[av.container.InputContainer]:
    """
    Helper function to open a video file and check if it exists.

    Args:
        file_path: Path to the video file

    Returns:
        Container object or None if file doesn't exist or on error
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    try:
        return av.open(file_path)
    except Exception as e:
        print(f"Error opening {file_path}: {str(e)}")
        return None


def _get_video_stream(container: av.container.InputContainer) -> Optional[av.video.stream.VideoStream]:
    """
    Helper function to get the video stream from a container.

    Args:
        container: AV container object

    Returns:
        Video stream or None if no video stream exists
    """
    if not container.streams.video:
        print(f"No video stream found in container")
        return None
    return container.streams.video[0]


def _extract_frame(
    container: av.container.InputContainer,
    stream: av.video.stream.VideoStream,
    timestamp_seconds: float,
    thumbnail_size: Optional[Tuple[int, int]] = None
) -> Optional[Image.Image]:
    """
    Helper function to extract a frame from a video at the specified timestamp.

    Args:
        container: AV container object
        stream: Video stream object
        timestamp_seconds: Time position in seconds to extract the frame from
        thumbnail_size: Optional tuple (width, height) to resize the frame

    Returns:
        PIL Image object of the extracted frame or None if extraction fails
    """
    try:
        # Seek to the target frame
        container.seek(int(timestamp_seconds * 1000000), stream=stream)

        # Get the frame
        for frame in container.decode(stream):
            # Convert the frame to a PIL Image
            img = frame.to_image()

            # Resize if needed
            if thumbnail_size:
                img = img.resize(thumbnail_size, Image.LANCZOS)

            return img

        print("Could not extract frame from video")
        return None
    except Exception as e:
        print(f"Error extracting frame: {str(e)}")
        return None


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
            container = _open_video_container(file_path)
            if not container:
                continue
            stream = _get_video_stream(container)
            if not stream:
                container.close()
                continue
            # Extract resolution and framerate
            resolution = (stream.width, stream.height)
            framerate = float(stream.average_rate) if stream.average_rate else None
            # Extract frame
            img = _extract_frame(container, stream, timestamp_seconds, thumbnail_size)
            if img:
                video_thumb_dict[file_path] = {
                    'thumbnail': img,
                    'resolution': resolution,
                    'framerate': framerate
                }
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
        container = _open_video_container(file_path)
        if not container:
            return None
        stream = _get_video_stream(container)
        if not stream:
            container.close()
            return None
        img = _extract_frame(container, stream, timestamp_seconds, thumbnail_size)
        container.close()
        return img
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None
