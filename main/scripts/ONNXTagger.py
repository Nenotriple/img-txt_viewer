import os
import csv

from PIL import Image
import numpy as np
from onnxruntime import InferenceSession
from tkinter import filedialog, messagebox


class OnnxTagger:
    def __init__(self, parent):
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
        self.replace_underscore = True
        self.sort = True
        self.reverse = True

        # Tag indices and labels
        self.model_tags = []
        self.general_index = None
        self.character_index = None


# --------------------------------------
# Handle Model
# --------------------------------------
    def _load_model(self):
        if not self.model_path or not os.path.exists(self.model_path):
            self.model_path = filedialog.askopenfilename(initialdir="./onnx_models", title="Choose ONNX model for tagging", filetypes=[("ONNX Model", "*.onnx")])
            if not self.model_path or not os.path.exists(self.model_path):
                messagebox.showerror(
                    "Model Not Found",
                    f'ONNX model ({self.model_path}) not found. Please visit https://huggingface.co/SmilingWolf and pick a model. I recommend wd-v1-4-moat-tagger-v2.'
                    ' Download "model.onnx" and "selected_tags.csv" for your chosen model.'
                    ' Rename both files to have matching names, e.g., "WDMoat_v2.onnx" and "WDMoat_v2.csv".'
                    ' Place these files in the "onnx_models" folder.'
                    )
                return False
        self.model = InferenceSession(self.model_path, providers=['CPUExecutionProvider'])
        self.model_input = self.model.get_inputs()[0]
        self.model_input_height = self.model_input.shape[1]
        self.tag_label = self.model.get_outputs()[0].name
        self._read_csv_tags()
        return True


# --------------------------------------
# Handle Tags
# --------------------------------------

    def _read_csv_tags(self):
        csv_path = os.path.splitext(self.model_path)[0] + ".csv"
        with open(csv_path) as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            for row in csv_reader:
                if self.general_index is None and row[2] == "0":
                    self.general_index = csv_reader.line_num - 2
                elif self.character_index is None and row[2] == "4":
                    self.character_index = csv_reader.line_num - 2
                if self.replace_underscore:
                    self.model_tags.append(row[1].replace("_", " "))
                else:
                    self.model_tags.append(row[1])


    def _process_tags(self, image):
        preprocessed_image = self._preprocess_image(image)
        confidence_scores = self.model.run([self.tag_label], {self.model_input.name: preprocessed_image})[0]
        tag_confidence_pairs = list(zip(self.model_tags, confidence_scores[0]))
        general_tags = [tag_tuple for tag_tuple in tag_confidence_pairs[self.general_index:self.character_index] if tag_tuple[1] > self.general_threshold]
        character_tags = [tag_tuple for tag_tuple in tag_confidence_pairs[self.character_index:] if tag_tuple[1] > self.character_threshold]
        all_tags = character_tags + general_tags
        if self.sort:
            all_tags = sorted([(tag, round(float(confidence), 2)) for (tag, confidence) in all_tags if tag.lower() not in self.exclude_tags], key=lambda x: x[1], reverse=self.reverse)
        else:
            all_tags = [tag_tuple for tag_tuple in all_tags if tag_tuple[0].lower() not in self.exclude_tags]
        return all_tags


    def _format_results(self, inferred_tags):
        formatted_tags = [[item[0].replace("(", "\\(").replace(")", "\\)"), item[1]]for item in inferred_tags]
        csv_result = ", ".join(item[0] for item in formatted_tags)
        confidence_result = "\n".join(f"{item[0]}: {item[1]}" for item in inferred_tags)
        return csv_result, confidence_result


# --------------------------------------
# Handle Image
# --------------------------------------


    def _preprocess_image(self, image):
        image.thumbnail((self.model_input_height, self.model_input_height), Image.BILINEAR)
        square_image = Image.new("RGB", (self.model_input_height, self.model_input_height), (255, 255, 255))
        square_image.paste(image, ((self.model_input_height - image.size[0]) // 2, (self.model_input_height - image.size[1]) // 2))
        preprocessed_image = np.array(square_image).astype(np.float32)
        preprocessed_image = preprocessed_image[:, :, ::-1]  # RGB -> BGR
        preprocessed_image = np.expand_dims(preprocessed_image, 0)
        return preprocessed_image


# --------------------------------------
# Tag Image
# --------------------------------------
    def tag_image(self, image_path):
        if not self.model:
            model_loaded = self._load_model()
            if not model_loaded:
                return
        try:
            with Image.open(image_path) as image:
                inferred_tags = self._process_tags(image)
        except FileNotFoundError as e:
            print("Error:", e)
            return
        csv_result, confidence_result = self._format_results(inferred_tags)
        return csv_result, confidence_result


# Example usage:
# tagger = OnnxTagger()
# tagger.tag_image("path_to_image.jpg")