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



# --------------------------------------
# Testing
# --------------------------------------

    def tag_images_sequential_test(self, image_path_list):
        from tqdm import tqdm
        out_dict = {}
        if not self.model:
            model_loaded = self._load_model()
            if not model_loaded:
                return
        for image_path in tqdm(image_path_list, desc="Tagging images", unit="image"):
            try:
                with Image.open(image_path) as image:
                    inferred_tags = self._process_tags(image)
            except FileNotFoundError as e:
                print("Error:", e)
                continue
            csv_result, confidence_result = self._format_results(inferred_tags)
            out_dict[image_path] =  (csv_result, confidence_result)
        return out_dict
    

    def tag_images_concurrent_test(self, image_path_list, batch_size=8):
        from tqdm import tqdm
        import concurrent.futures

        if not self.model:
            model_loaded = self._load_model()
            if not model_loaded:
                return
        
        input_shape = self.model.get_inputs()[0].shape
        model_batch_dimension = input_shape[0]

        if batch_size != model_batch_dimension and not isinstance(model_batch_dimension, str) and model_batch_dimension > 0:
            # model_batch_dimension of 0 or any string means it has dynamic axes
            print(f"Batch size {batch_size} doesn't match onnx model batch dimension {model_batch_dimension}, using model batch dimension {model_batch_dimension} instead")
            batch_size = model_batch_dimension


        def preprocess_image(image_path):
            try:
                with Image.open(image_path) as image:
                    return image_path, self._preprocess_image(image)
            except FileNotFoundError as e:
                print(f"Error: {e}")
                return image_path, None

        # Threaded preprocessing
        with concurrent.futures.ThreadPoolExecutor() as executor:
            preprocessed_images = list(executor.map(preprocess_image, image_path_list))
        
        # Remove any images that failed to preprocess
        preprocessed_prev_len = len(preprocessed_images)
        preprocessed_images = [(path, img) for path, img in preprocessed_images if img is not None]
        preprocessed_post_len = len(preprocessed_images)
        print(f"# images failed preprocessing: {preprocessed_prev_len - preprocessed_post_len}")

        out_dict = {}
        for i in tqdm(range(0, len(preprocessed_images), batch_size), desc="Tagging images in batches", unit="batch"):
            batch = preprocessed_images[i:i+batch_size]
            batch_paths, batch_images = zip(*batch)
            batch_images = np.vstack(batch_images)  # Stack images for batch inference

            confidence_scores = self.model.run([self.tag_label], {self.model_input.name: batch_images})[0]

            for j, image_path in enumerate(batch_paths):
                tag_confidence_pairs = list(zip(self.model_tags, confidence_scores[j]))
                general_tags = [tag_tuple for tag_tuple in tag_confidence_pairs[self.general_index:self.character_index] if tag_tuple[1] > self.general_threshold]
                character_tags = [tag_tuple for tag_tuple in tag_confidence_pairs[self.character_index:] if tag_tuple[1] > self.character_threshold]
                all_tags = character_tags + general_tags

                if self.sort:
                    all_tags = sorted([(tag, round(float(confidence), 2)) for (tag, confidence) in all_tags if tag.lower() not in self.exclude_tags],key=lambda x: x[1],reverse=self.reverse)
                else:
                    all_tags = [tag_tuple for tag_tuple in all_tags if tag_tuple[0].lower() not in self.exclude_tags]

                csv_result, confidence_result = self._format_results(all_tags)
                out_dict[image_path] = (csv_result, confidence_result)

        return out_dict
     

    def test_model_batch_dim(self):
        if not self.model:
            model_loaded = self._load_model()
            if not model_loaded:
                return
            
        input_shape = self.model.get_inputs()[0].shape
        batch_dimension = input_shape[0]

        # Check if the batch dimension is dynamic
        if isinstance(batch_dimension, str) or batch_dimension == 0:
            print(f"The model supports dynamic batching with symbolic dimension: '{batch_dimension}'\nTesting inference on mock batches of 1, 4, and 8...")
            # Further test dynamic batching by feeding multiple batch sizes
            try:
                # Example batch sizes to test
                for test_batch_size in [1, 4, 8]:
                    test_input = np.random.rand(test_batch_size, *input_shape[1:]).astype(np.float32)
                    self.model.run(None, {self.model.get_inputs()[0].name: test_input})
                print("Model successfully processed variable batch sizes, confirming dynamic batching support.")
            except Exception as e:
                print("Error encountered while testing variable batch sizes:", e)
        else:
            if batch_dimension == 1:
                print("The model has a fixed batch size of 1 (single-image processing only).")
            else:
                print(f"The model has a fixed batch size of {batch_dimension}.")


# Example usage:
# tagger = OnnxTagger()
# tagger.tag_image("path_to_image.jpg")