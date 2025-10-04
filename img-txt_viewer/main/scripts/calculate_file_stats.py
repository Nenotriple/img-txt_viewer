#region Imports


# Standard Library
import os
import re
import statistics
from collections import Counter

# Standard Library - GUI
from tkinter import Tk, messagebox

# Third-Party Libraries
from PIL import Image

# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region CalculateFileStats


class CalculateFileStats:
    def __init__(self, app: 'Main', root: 'Tk'):
        self.app = app
        self.root = root
        self.caption_counter = Counter()
        self.sorted_captions = []
        # Internal copies for stats calculation
        self._text_files = []
        self._image_files = []
        self._video_thumb_dict = {}


    def calculate_file_stats(self, manual_refresh=None, text_only=False, image_only=False):
        """Calculate and display file statistics.

        Args:
            manual_refresh: If True, display a message box after refreshing
            text_only: If True, only refresh text statistics
            image_only: If True, only refresh image statistics
        """
        if text_only and image_only:
            raise ValueError("Cannot set both text_only and image_only to True")
        self.initialize_counters()
        # Use internal copies, do not modify app
        self._text_files = [f for f in self.app.text_files if os.path.exists(f)]
        self._image_files = list(self.app.image_files)
        self._video_thumb_dict = dict(getattr(self.app, "video_thumb_dict", {}))
        num_txt_files = len(self._text_files)
        num_img_files = sum(1 for f in self._image_files if not f.lower().endswith('.mp4'))
        num_video_files = sum(1 for f in self._image_files if f.lower().endswith('.mp4'))
        num_total_files = num_img_files + num_txt_files + num_video_files
        formatted_total_files = f"{num_total_files} (Text: {num_txt_files}, Images: {num_img_files}, Videos: {num_video_files})"
        # Process files based on flags
        if not image_only:
            self.process_text_files()
        if (self.app.process_image_stats_var.get() and not text_only) or image_only:
            self.process_image_files()
        # Format statistics into a text string
        stats_text = self.compile_file_statistics(formatted_total_files)
        self.update_filestats_textbox(stats_text, manual_refresh)
        if self.sorted_captions:
            self.app.text_controller.my_tags.refresh_all_tags_listbox(tags=self.sorted_captions)


    def initialize_counters(self):
        """Initialize counters and accumulators."""
        # Counters
        self.caption_counter.clear()
        self.word_counter = Counter()
        self.char_counter = Counter()
        self.image_resolutions_counter = Counter()
        self.aspect_ratios_counter = Counter()
        self.video_formats_counter = Counter()
        # Accumulators
        self.total_chars = 0
        self.total_words = 0
        self.total_captions = 0
        self.total_sentences = 0
        self.total_paragraphs = 0
        self.total_text_filesize = 0
        self.total_image_filesize = 0
        self.total_video_filesize = 0
        self.total_ppi = 0
        self.total_image_width = 0
        self.total_image_height = 0
        self.square_images = 0
        self.portrait_images = 0
        self.landscape_images = 0
        self.video_count = 0
        self.total_video_width = 0
        self.total_video_height = 0
        self.total_video_duration = 0
        self.square_videos = 0
        self.portrait_videos = 0
        self.landscape_videos = 0
        # Sets
        self.unique_words = set()
        self.image_formats = set()
        self.video_formats = set()
        self.longest_words = set()
        # Lists
        self.word_lengths = []
        self.sentence_lengths = []
        self.caption_lengths = []
        self.file_word_counts = []
        self.file_char_counts = []
        self.file_caption_counts = []


    def process_text_files(self):
        """Process text files to calculate statistics."""
        for text_file in self._text_files:
            try:
                file_content, words, sentences, paragraphs, captions = self.compute_text_file(text_file)
                self.total_chars += len(file_content)
                self.total_words += len(words)
                self.word_counter.update(words)
                self.unique_words.update(words)
                self.char_counter.update(file_content)
                self.word_lengths.extend(len(word) for word in words)
                self.total_sentences += len(sentences)
                self.sentence_lengths.extend(len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences)
                self.total_paragraphs += len(paragraphs)
                self.update_caption_counter(captions)
                captions_count = len(captions)
                self.total_captions += captions_count
                self.file_word_counts.append((os.path.basename(text_file), len(words)))
                self.file_char_counts.append((os.path.basename(text_file), len(file_content)))
                self.file_caption_counts.append((os.path.basename(text_file), captions_count))
                for word in words:
                    self.longest_words.add(word)
                    if len(self.longest_words) > 5:
                        self.longest_words = set(sorted(self.longest_words, key=len, reverse=True)[:5])
                self.total_text_filesize += os.path.getsize(text_file)
                self.caption_lengths.extend(len(caption.split()) for caption in captions)
            except FileNotFoundError:
                pass
            except Exception as e:
                messagebox.showerror("Error: process_text_files()", f"An error occurred while processing {os.path.basename(text_file)}:\n\n{e}")


    def process_image_files(self):
        """Process image files to calculate statistics."""
        for media_file in self._image_files:
            try:
                if media_file.lower().endswith('.mp4'):
                    # Handle video file
                    self.process_video_file(media_file)
                else:
                    # Handle image file
                    width, height, dpi, aspect_ratio, image_format = self.compute_image_file(media_file)
                    self.total_image_filesize += os.path.getsize(media_file)
                    self.image_formats.add(image_format)
                    self.total_ppi += dpi[0]
                    self.image_resolutions_counter[(width, height)] += 1
                    self.aspect_ratios_counter[round(aspect_ratio, 2)] += 1
                    self.total_image_width += width
                    self.total_image_height += height
                    if aspect_ratio == 1:
                        self.square_images += 1
                    elif aspect_ratio > 1:
                        self.landscape_images += 1
                    else:
                        self.portrait_images += 1
            except FileNotFoundError:
                pass
            except Exception as e:
                messagebox.showerror("Error: process_image_files()", f"An error occurred while processing {os.path.basename(media_file)}:\n\n{e}")


    def process_video_file(self, video_file):
        """Process a video file to calculate statistics."""
        try:
            file_size = os.path.getsize(video_file)
            self.total_video_filesize += file_size
            # Get video information from local copy
            if video_file in self._video_thumb_dict:
                video_info = self._video_thumb_dict[video_file]
                width, height = video_info['resolution']
                framerate = video_info.get('framerate', 0)
                # Update counters
                self.video_count += 1
                self.video_formats.add('.mp4')
                self.video_formats_counter['.mp4'] += 1
                self.image_resolutions_counter[(width, height)] += 1
                # Calculate aspect ratio
                aspect_ratio = width / height if height > 0 else 0
                self.aspect_ratios_counter[round(aspect_ratio, 2)] += 1
                # Update totals
                self.total_video_width += width
                self.total_video_height += height
                # Classify video shape
                if aspect_ratio == 1:
                    self.square_videos += 1
                elif aspect_ratio > 1:
                    self.landscape_videos += 1
                else:
                    self.portrait_videos += 1
            else:
                # If video is not in thumb dict, just count it
                self.video_count += 1
                self.video_formats.add('.mp4')
                self.video_formats_counter['.mp4'] += 1

        except Exception as e:
            messagebox.showerror("Error: process_video_file()", f"An error occurred while processing {os.path.basename(video_file)}:\n\n{e}")


#endregion
#region Statistics Functions


    def compile_file_statistics(self, formatted_total_files):
        """Compile all calculated statistics into a text string."""
        # Calculate average statistics
        avg_chars = self.total_chars / len(self._text_files) if self._text_files else 0
        avg_words = self.total_words / len(self._text_files) if self._text_files else 0
        avg_captions = self.total_captions / len(self._text_files) if self._text_files else 0
        avg_ppi = self.total_ppi / len(self._image_files) if self._image_files else 0
        avg_word_length = sum(self.word_lengths) / len(self.word_lengths) if self.word_lengths else 0
        median_word_length = statistics.median(self.word_lengths) if self.word_lengths else 0
        avg_sentence_length = sum(self.sentence_lengths) / len(self.sentence_lengths) if self.sentence_lengths else 0
        # Calculate additional statistics
        type_token_ratio = len(self.unique_words) / self.total_words if self.total_words else 0
        std_dev_word_length = statistics.stdev(self.word_lengths) if len(self.word_lengths) > 1 else 0
        std_dev_sentence_length = statistics.stdev(self.sentence_lengths) if len(self.sentence_lengths) > 1 else 0
        # Calculate image averages (excluding videos)
        image_count = len(self._image_files) - self.video_count if self._image_files else 0
        avg_image_width = self.total_image_width / image_count if image_count else 0
        avg_image_height = self.total_image_height / image_count if image_count else 0
        # Calculate video averages
        avg_video_width = self.total_video_width / self.video_count if self.video_count else 0
        avg_video_height = self.total_video_height / self.video_count if self.video_count else 0
        avg_caption_length = sum(self.caption_lengths) / len(self.caption_lengths) if self.caption_lengths else 0
        # Sort and format the most common words, characters, resolutions, aspect ratios, and captions
        most_common_words = self.word_counter.most_common(50)
        most_common_words = sorted(most_common_words, key=lambda x: (-x[1], x[0].lower()))
        formatted_common_words = "\n".join([f"{count:03}x, {word}" for word, count in most_common_words])
        most_common_chars = self.char_counter.most_common()
        formatted_common_chars = "\n".join([f"{count:03}x, {char}" for char, count in most_common_chars])
        self.sorted_captions = self.get_sorted_captions()
        formatted_captions = self.get_formatted_captions(self.sorted_captions)
        sorted_resolutions = sorted(self.image_resolutions_counter.items(), key=lambda x: (-x[1], -(x[0][0] * x[0][1])))
        formatted_resolutions = "\n".join([f"{count:03}x, {res[0]}x{res[1]}" for res, count in sorted_resolutions])
        sorted_aspect_ratios = sorted(self.aspect_ratios_counter.items(), key=lambda x: (-x[1], x[0]))
        formatted_aspect_ratios = "\n".join([f"{count:03}x, {aspect_ratio}" for aspect_ratio, count in sorted_aspect_ratios])
        formatted_longest_words = "\n".join([f"- {word}" for word in sorted(self.longest_words, key=lambda x: (-len(x), x.lower()))])
        top_5_files_words = sorted(self.file_word_counts, key=lambda x: (-x[1], x[0].lower()))[:5]
        formatted_top_5_files_words = "\n".join([f"{count}x, {file}" for file, count in top_5_files_words])
        top_5_files_chars = sorted(self.file_char_counts, key=lambda x: (-x[1], x[0].lower()))[:5]
        formatted_top_5_files_chars = "\n".join([f"{count}x, {file}" for file, count in top_5_files_chars])
        top_5_files_captions = sorted(self.file_caption_counts, key=lambda x: (-x[1], x[0].lower()))[:5]
        formatted_top_5_files_captions = "\n".join([f"{count}x, {file}" for file, count in top_5_files_captions])
        word_page_count = self.total_words / 500 if self.total_words > 0 else 0
        formatted_filepath = os.path.normpath(self.app.image_dir.get())
        formatted_total_filesize = self.format_filesize(self.total_image_filesize + self.total_text_filesize + self.total_video_filesize)
        # Format statistics into a dictionary
        stats = {
            'filepath': formatted_filepath,
            'formatted_total_files': formatted_total_files,
            'total_text_filesize': self.format_filesize(self.total_text_filesize),
            'total_image_filesize': self.format_filesize(self.total_image_filesize),
            'total_video_filesize': self.format_filesize(self.total_video_filesize),
            'total_filesize': formatted_total_filesize,
            'total_chars': self.total_chars,
            'total_words': self.total_words,
            'word_page_count': word_page_count,
            'total_captions': self.total_captions,
            'total_sentences': self.total_sentences,
            'total_paragraphs': self.total_paragraphs,
            'unique_words': self.unique_words,
            'avg_chars': avg_chars,
            'avg_words': avg_words,
            'avg_captions': avg_captions,
            'avg_word_length': avg_word_length,
            'median_word_length': median_word_length,
            'avg_sentence_length': avg_sentence_length,
            'image_formats': self.image_formats,
            'square_images': self.square_images,
            'portrait_images': self.portrait_images,
            'landscape_images': self.landscape_images,
            'video_formats': self.video_formats,
            'video_count': self.video_count,
            'square_videos': self.square_videos,
            'portrait_videos': self.portrait_videos,
            'landscape_videos': self.landscape_videos,
            'avg_ppi': avg_ppi,
            'avg_image_width': avg_image_width,
            'avg_image_height': avg_image_height,
            'avg_video_width': avg_video_width,
            'avg_video_height': avg_video_height,
            'formatted_resolutions': formatted_resolutions,
            'formatted_aspect_ratios': formatted_aspect_ratios,
            'formatted_top_5_files_words': formatted_top_5_files_words,
            'formatted_top_5_files_chars': formatted_top_5_files_chars,
            'formatted_top_5_files_captions': formatted_top_5_files_captions,
            'formatted_longest_words': formatted_longest_words,
            'formatted_common_words': formatted_common_words,
            'formatted_common_chars': formatted_common_chars,
            'formatted_captions': formatted_captions,
            'type_token_ratio': type_token_ratio,
            'std_dev_word_length': std_dev_word_length,
            'std_dev_sentence_length': std_dev_sentence_length,
            'avg_caption_length': avg_caption_length,
        }
        stats_text = self.format_stats_text(stats)
        return stats_text


    def format_stats_text(self, stats):
        """Format statistics into a text string."""
        stats_text = (
            # Summary
            f"{stats['filepath']}\n\n"
            f"--- File Summary ---\n"
            f"Total Files: {stats['formatted_total_files']}\n"
            f"Total Text Filesize: {stats['total_text_filesize']}\n"
            f"Total Image Filesize: {stats['total_image_filesize']}\n"
            f"Total Video Filesize: {stats['total_video_filesize']}\n"
            f"Total Filesize: {stats['total_filesize']}\n"
            # Text Statistics
            f"\n--- Text Statistics ---\n"
            f"Total Characters: {stats['total_chars']}\n"
            f"Total Words: {stats['total_words']} ({stats['word_page_count']:.2f} pages)\n"
            f"Total Captions: {stats['total_captions']}\n"
            f"Total Sentences: {stats['total_sentences']}\n"
            f"Total Paragraphs: {stats['total_paragraphs']}\n"
            f"Unique Words: {len(stats['unique_words'])}\n"
            # Average Text Statistics
            f"\n--- Average Text Statistics ---\n"
            f"Average Characters per File: {stats['avg_chars']:.2f}\n"
            f"Average Words per File: {stats['avg_words']:.2f}\n"
            f"Average Captions per File: {stats['avg_captions']:.2f}\n"
            f"Average Caption Length: {stats['avg_caption_length']:.2f} words\n"
            f"Average Word Length: {stats['avg_word_length']:.2f}\n"
            f"Median Word Length: {stats['median_word_length']:.2f}\n"
            f"Average Sentence Length: {stats['avg_sentence_length']:.2f}\n"
            # Additional Text Statistics
            f"\n--- Additional Text Statistics ---\n"
            f"Type-Token Ratio: {stats['type_token_ratio']:.4f}\n"
            f"Word Length Standard Deviation: {stats['std_dev_word_length']:.2f}\n"
            f"Sentence Length Standard Deviation: {stats['std_dev_sentence_length']:.2f}\n"
            # Image Statistics
            f"\n--- Image Information ---\n"
            f"Image File Formats: {', '.join(stats['image_formats'])}\n"
            f"Square Images: {stats['square_images']}\n"
            f"Portrait Images: {stats['portrait_images']}\n"
            f"Landscape Images: {stats['landscape_images']}\n"
            f"Average PPI for All Images: {stats['avg_ppi']:.2f}\n"
            f"Average Image Width: {stats['avg_image_width']:.2f}px\n"
            f"Average Image Height: {stats['avg_image_height']:.2f}px\n"
            # Video Statistics
            f"\n--- Video Information ---\n"
            f"Total Videos: {stats['video_count']}\n"
            f"Video File Formats: {', '.join(stats['video_formats'])}\n"
            f"Square Videos: {stats['square_videos']}\n"
            f"Portrait Videos: {stats['portrait_videos']}\n"
            f"Landscape Videos: {stats['landscape_videos']}\n"
            f"Average Video Width: {stats['avg_video_width']:.2f}px\n"
            f"Average Video Height: {stats['avg_video_height']:.2f}px\n"
            # Other Statistics
            f"\n--- Media Resolutions ---\n"
            f"{stats['formatted_resolutions']}\n"
            f"\n--- Media Aspect Ratios ---\n"
            f"{stats['formatted_aspect_ratios']}\n"
            f"\n--- Top 5 Files by Word Count ---\n"
            f"{stats['formatted_top_5_files_words']}\n"
            f"\n--- Top 5 Files by Character Count ---\n"
            f"{stats['formatted_top_5_files_chars']}\n"
            f"\n--- Top 5 Files by Caption Count ---\n"
            f"{stats['formatted_top_5_files_captions']}\n"
            f"\n--- Top 5 Longest Words ---\n"
            f"{stats['formatted_longest_words']}\n"
            f"\n--- Top 50 Most Common Words ---\n"
            f"{stats['formatted_common_words']}\n"
            f"\n--- Character Occurrence ---\n"
            f"{stats['formatted_common_chars']}\n"
            f"\n--- Unique Captions ---\n"
            f"{stats['formatted_captions']}\n"
        )
        return stats_text


#endregion
#region Helper Functions


    def compute_text_file(self, text_file):
        """Read and process a single text file."""
        with open(text_file, 'r', encoding="utf-8") as file:
            file_content = file.read()
        words = re.findall(r'\b\w+\b', file_content.lower())
        sentences = re.split(r'[.!?]', file_content)
        paragraphs = file_content.split('\n\n')
        captions = [cap.strip() for cap in file_content.split(',')]
        return file_content, words, sentences, paragraphs, captions


    def compute_image_file(self, image_file):
        """Read and process a single image file."""
        with Image.open(image_file) as image:
            width, height = image.size
            dpi = self.get_image_dpi(image)
            aspect_ratio = width / height
        image_format = image.format
        return width, height, dpi, aspect_ratio, image_format


    def get_image_dpi(self, image):
        """Get the DPI of an image, calculating if necessary."""
        dpi = image.info.get('dpi', (0, 0))
        # Ensure dpi is a tuple of numbers (not strings)
        if isinstance(dpi, tuple):
            dpi = tuple(float(x) if isinstance(x, str) and x.replace('.', '', 1).isdigit() else x for x in dpi)
        else:
            # If dpi is a single value, make it a tuple
            try:
                dpi = (float(dpi), float(dpi))
            except Exception:
                dpi = (0, 0)
        if not all(isinstance(x, (int, float)) and x > 0 for x in dpi):
            width, height = image.size
            diagonal_inches = 10
            diagonal_pixels = (width**2 + height**2) ** 0.5
            dpi = (diagonal_pixels / diagonal_inches, diagonal_pixels / diagonal_inches)
        return dpi


    def get_sorted_captions(self):
        """Sort the captions by count and alphabetically."""
        sorted_captions = self.caption_counter.most_common()
        return sorted(sorted_captions, key=lambda x: (-x[1], x[0].lower()))


    def get_formatted_captions(self, sorted_captions):
        """Format the captions into a string for display."""
        return "\n".join([f"{count:03}x, {caption}" for caption, count in sorted_captions])


    def update_caption_counter(self, captions):
        """Update the caption counter with the captions from a text file."""
        for caption in captions:
            caption_words = caption.split()
            if self.app.truncate_stat_captions_var.get() and (len(caption_words) > 8 or len(caption) > 50):
                caption = ' '.join(caption_words[:8]) + "..." if len(caption_words) > 8 else caption[:50] + "..."
            self.caption_counter[caption] += 1


    def filter_and_update_textfiles(self, initial_call=False):
        """Filter out non-existent text files and update the text file list."""
        # This function is now only used for initial filtering, but does not update app.text_files
        # Use self._text_files instead
        num_txt_files = len(self._text_files)
        num_img_files = sum(1 for f in self._image_files if not f.lower().endswith('.mp4'))
        num_video_files = sum(1 for f in self._image_files if f.lower().endswith('.mp4'))
        num_total_files = num_img_files + num_txt_files + num_video_files
        formatted_total_files = f"{num_total_files} (Text: {num_txt_files}, Images: {num_img_files}, Videos: {num_video_files})"
        if not initial_call:
            self.app.refresh_file_lists()
        return num_total_files, num_txt_files, num_img_files, num_video_files, formatted_total_files


    def format_filesize(self, size):
        """Format a file size in bytes into a human-readable string."""
        if size >= 1_000_000:
            return f"{size} bytes ({size / 1_000_000:.2f} MB)"
        elif size >= 1_000:
            return f"{size} bytes ({size / 1_000:.2f} KB)"
        else:
            return f"{size} bytes"


#endregion
#region GUI Functions


    def update_filestats_textbox(self, stats_text, manual_refresh=None):
        """Update the GUI textbox with the calculated statistics."""
        self.app.text_controller.filestats_textbox.config(state="normal")
        self.app.text_controller.filestats_textbox.delete("1.0", "end")
        self.app.text_controller.filestats_textbox.insert("1.0", stats_text)
        self.app.text_controller.filestats_textbox.config(state="disabled")
        if manual_refresh:
            messagebox.showinfo("Stats Calculated", "Stats have been updated!")


#endregion