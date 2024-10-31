# Standard Library
import os
import csv

# Standard Library - GUI
from tkinter import BooleanVar, messagebox

# Third-Party Libraries
import numpy
from PIL import Image
from onnxruntime import InferenceSession


class OnnxTagger:
    """This module contains the OnnxTagger class, which is responsible for loading an ONNX vision model and tagging images."""

    def __init__(self, parent):
        # Parent class
        self.parent = parent

        # Model related attributes
        self.model = None
        self.model_path = None
        self.model_input = None
        self.model_input_height = None
        self.tag_label = None

        # Tagging thresholds
        self.general_threshold = 0.35
        self.character_threshold = 0.85

        # Tagging options
        self.exclude_tags = []
        self.exclude_tags_set = set()
        self.replace_underscore = BooleanVar(value=True)
        self.sort = True
        self.reverse = True

        # Tag indices and labels
        self.model_tags = []
        self.general_index = None
        self.character_index = None

        # Tags with underscores
        self.tags_with_underscore = ["0_0", "(o)_(o)", "o_o", ">_o", "u_u", "x_x", "|_|", "||_||", "._.", "^_^", ">_<", "@_@", ">_@", "+_+", "+_-", "=_=", "<o>_<o>", "<|>_<|>", "ಠ_ಠ", "3_3", "6_9"]


    # --------------------------------------
    # Handle Model
    # --------------------------------------
    def _load_model(self):
        self.model = InferenceSession(self.model_path, providers=['CPUExecutionProvider'])
        self.model_input = self.model.get_inputs()[0]
        self.model_input_height = self.model_input.shape[1]
        self.tag_label = self.model.get_outputs()[0].name


    # --------------------------------------
    # Handle Tags
    # --------------------------------------
    def _read_csv_tags(self):
        self.model_tags.clear()
        csv_path = os.path.join(os.path.dirname(self.model_path), "selected_tags.csv")
        with open(csv_path, newline='') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            for idx, row in enumerate(csv_reader):
                if self.general_index is None and row[2] == "0":
                    self.general_index = idx
                elif self.character_index is None and row[2] == "4":
                    self.character_index = idx
                tag = row[1]
                if tag not in self.tags_with_underscore and self.replace_underscore.get():
                    tag = tag.replace("_", " ")
                self.model_tags.append(tag)
        self.exclude_tags_set = set(tag.lower() for tag in self.exclude_tags)


    def _process_tags(self, image):
        self._read_csv_tags()
        preprocessed_image = self._preprocess_image(image)
        confidence_scores = self.model.run([self.tag_label], {self.model_input.name: preprocessed_image})[0][0]
        tag_confidence_pairs = list(zip(self.model_tags, confidence_scores))
        if self.general_index is None or self.character_index is None:
            raise ValueError("General index or character index not set correctly.")

        def filter_tags(tag_confidence_pairs, start, end, threshold, category):
            filtered_tags = []
            for tag, confidence in tag_confidence_pairs[start:end]:
                if confidence > threshold and tag.lower() not in self.exclude_tags_set:
                    filtered_tags.append((tag, round(float(confidence), 2), category))
            return filtered_tags

        general_tags = filter_tags(tag_confidence_pairs, self.general_index, self.character_index, self.general_threshold, "general")
        character_tags = filter_tags(tag_confidence_pairs, self.character_index, len(tag_confidence_pairs), self.character_threshold, "character")
        all_tags = character_tags + general_tags
        if self.sort:
            all_tags.sort(key=lambda x: x[1], reverse=self.reverse)
        return all_tags


    def _format_results(self, inferred_tags):
        formatted_tags = [[tag.replace("(", "\\(").replace(")", "\\)"), confidence, category] for tag, confidence, category in inferred_tags]
        tag_list = ", ".join(tag for tag, _, _ in formatted_tags)
        tag_dict = {tag: {confidence, category} for tag, confidence, category in formatted_tags}
        return tag_list, tag_dict


    # --------------------------------------
    # Handle Image
    # --------------------------------------
    def _preprocess_image(self, image):
        image.thumbnail((self.model_input_height, self.model_input_height), Image.BILINEAR)
        square_image = Image.new("RGB", (self.model_input_height, self.model_input_height), (255, 255, 255))
        square_image.paste(image, ((self.model_input_height - image.size[0]) // 2, (self.model_input_height - image.size[1]) // 2))
        preprocessed_image = numpy.array(square_image, dtype=numpy.float32)
        preprocessed_image = preprocessed_image[:, :, ::-1]  # RGB -> BGR
        preprocessed_image = numpy.expand_dims(preprocessed_image, 0)
        return preprocessed_image


    # --------------------------------------
    # Tag Image
    # --------------------------------------
    def tag_image(self, image_path, model_path):
        """
        Tags an image using the provided ONNX model.

        Args:
            image_path (str): The file path to the image that needs to be tagged.
            model_path (str): The file path to the `.onnx` model that will be used to tag the image.
            - Ensure that the model has a corresponding `selected_tags.csv` file in the same directory as the model_path.

        Returns:
            tuple: A tuple containing:
                - tag_list (str): A CSV formatted string of the inferred tags.
                - tag_dict (dict): A dictionary where the keys are the inferred tags and the values are the confidence scores and categories.

        Raises:
            FileNotFoundError: If the image file specified by `image_path` does not exist.

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
