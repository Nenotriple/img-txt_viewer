"""This module contains the OnnxTagger class, which is responsible for loading an ONNX vision model and tagging images."""


################################################################################################################################################
#region Imports


# Standard Library
import os
import csv

# Standard Library - GUI
from tkinter import BooleanVar, messagebox

# Third-Party Libraries
import numpy
from PIL import Image
from onnxruntime import InferenceSession


#endregion
################################################################################################################################################
#region CLS OnnxTagger


class OnnxTagger:
    """This module contains the OnnxTagger class, which is responsible for loading an ONNX vision model and tagging images."""
    def __init__(self, parent):
        # Parent class
        self.parent = parent

        # Model related variables
        self.model = None
        self.model_path = None
        self.model_input = None
        self.model_input_height = None
        self.tag_label = None
        self.last_model_path = None
        self.last_exclude_tags = None
        self.last_keep_underscore = None

        # Tagging thresholds
        self.general_threshold = 0.35
        self.character_threshold = 0.85

        # Tagging options
        self.replace_tag_dict = {} # {"original_tag": "replaced_tag"}
        self.keep_tags = []
        self.exclude_tags = []
        self.exclude_tags_set = set()
        self.keep_underscore = BooleanVar(value=False)
        self.keep_escape_character = BooleanVar(value=True)
        self.sort = True
        self.reverse = True

        # Tag indices and labels
        self.model_tags = []
        self.general_index = None
        self.character_index = None

        # Tags with underscores
        self.tags_with_underscore = ["0_0", "(o)_(o)", "o_o", ">_o", "u_u", "x_x", "|_|", "||_||", "._.", "^_^", ">_<", "@_@", ">_@", "+_+", "+_-", "=_=", "<o>_<o>", "<|>_<|>", "ಠ_ಠ", "3_3", "6_9"]


#endregion
################################################################################################################################################
#region Handle Model


    def _load_model(self):
        if self.model_path != self.last_model_path:
            self.model = InferenceSession(self.model_path, providers=['CPUExecutionProvider'])
            self.model_input = self.model.get_inputs()[0]
            self.model_input_height = self.model_input.shape[1]
            self.tag_label = self.model.get_outputs()[0].name
            self.last_model_path = self.model_path


#endregion
################################################################################################################################################
#region Handle Tags


    def _read_csv_tags(self):
        if (self.model_path != self.last_model_path or self.exclude_tags != self.last_exclude_tags):
            self.model_tags.clear()
            csv_path = os.path.join(os.path.dirname(self.model_path), "selected_tags.csv")
            with open(csv_path, newline='', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)
                for idx, row in enumerate(csv_reader):
                    if self.general_index is None and row[2] == "0":
                        self.general_index = idx
                    elif self.character_index is None and row[2] == "4":
                        self.character_index = idx
                    tag = row[1]
                    self.model_tags.append(tag)
            self.exclude_tags_set = set(tag.lower() for tag in self.exclude_tags)
            self.last_exclude_tags = self.exclude_tags.copy()
            self.last_keep_underscore = self.keep_underscore.get()


    def _process_tags(self, image):
        self._read_csv_tags()
        tag_confidence_pairs = self._interrogate_image(image)
        general_tags = self._filter_tags(tag_confidence_pairs, self.general_index, self.character_index, self.general_threshold, "general")
        character_tags = self._filter_tags(tag_confidence_pairs, self.character_index, len(tag_confidence_pairs), self.character_threshold, "character")
        all_tags = character_tags + general_tags
        self._insert_keep_tags(all_tags, self.general_index, self.character_index, "keep")
        if self.sort:
            all_tags.sort(key=lambda x: x[1], reverse=self.reverse)
        return all_tags


    def _filter_tags(self, tag_confidence_pairs, start, end, threshold, category):
        filtered_tags = []
        for tag, confidence in tag_confidence_pairs[start:end]:
            if confidence > threshold and tag.lower() not in self.exclude_tags_set:
                if tag in self.replace_tag_dict:
                    tag = self.replace_tag_dict[tag]
                filtered_tags.append((tag, round(float(confidence), 2), category))
        return filtered_tags


    def _insert_keep_tags(self, tag_confidence_pairs, start, end, category):
        for tag in self.keep_tags:
            if tag not in [t[0] for t in tag_confidence_pairs[start:end]]:
                tag_confidence_pairs.append((tag, 1.0, category))


    def _format_results(self, inferred_tags):
        escape_character = self.keep_escape_character.get()
        formatted_tags = [[tag.replace("(", "\\(").replace(")", "\\)") if escape_character else tag, confidence, category] for tag, confidence, category in inferred_tags]
        if not self.keep_underscore.get():
            formatted_tags = [[tag.replace("_", " "), confidence, category] for tag, confidence, category in formatted_tags]
        tag_list = [tag for tag, _, _ in formatted_tags]
        tag_dict = {tag: {confidence, category} for tag, confidence, category in formatted_tags}
        return tag_list, tag_dict


#endregion
################################################################################################################################################
#region Handle Image


    def _preprocess_image(self, image):
        if image.mode != 'RGB':
            image = image.convert('RGB')
        avg_color = self._get_avg_color(image)
        ratio = float(self.model_input_height) / max(image.size)
        new_size = tuple([int(x * ratio) for x in image.size])
        image = image.resize(new_size, Image.LANCZOS)
        square = Image.new("RGB", (self.model_input_height, self.model_input_height), avg_color)
        square.paste(image, ((self.model_input_height - new_size[0]) // 2, (self.model_input_height - new_size[1]) // 2))
        np_image = numpy.array(square).astype(numpy.float32)
        np_image = np_image[:, :, ::-1]  # RGB -> BGR
        preprocessed_image = numpy.expand_dims(np_image, 0)
        return preprocessed_image


    def _get_avg_color(self, image):
        border_pixels = []
        for x in range(image.width):
            border_pixels.append(image.getpixel((x, 0)))
            border_pixels.append(image.getpixel((x, image.height - 1)))
        for y in range(image.height):
            border_pixels.append(image.getpixel((0, y)))
            border_pixels.append(image.getpixel((image.width - 1, y)))
        avg_color = tuple(map(lambda x: int(sum(x) / len(x)), zip(*border_pixels)))
        return avg_color


    def _interrogate_image(self, image):
        preprocessed_image = self._preprocess_image(image)
        confidence_scores = self.model.run([self.tag_label], {self.model_input.name: preprocessed_image})[0][0]
        tag_confidence_pairs = list(zip(self.model_tags, confidence_scores))
        return tag_confidence_pairs


#endregion
################################################################################################################################################
#region Tag Image


    def tag_image(self, image_path, model_path):
        """
        Tags an image using the specified ONNX Vision model.

        Parameters:
            image_path (str): Path to the image file to be tagged.
            model_path (str): Path to the ONNX model file.
            - Ensure that the model has a corresponding `selected_tags.csv` file in the same directory as the model_path.

        Returns:
            tuple: A tuple containing:
                - tag_list (list): A list of tags generated from the image.
                - tag_dict (dict): A dictionary mapping tags to their confidence scores and categories.
        """
        self.model_path = model_path
        try:
            self._load_model()
            with Image.open(image_path) as image:
                inferred_tags = self._process_tags(image)
        except FileNotFoundError as e:
            messagebox.showerror("File Not Found", f"The file specified by {image_path} does not exist.\n\n{e}")
            return
        tag_list, tag_dict = self._format_results(inferred_tags)
        return tag_list, tag_dict


#endregion
