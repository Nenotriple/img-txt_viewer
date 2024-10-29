import os
import numpy as np
import csv
import json
import argparse

from tkinter import filedialog
from PIL import Image

from onnxruntime import InferenceSession
# GPU inference requires onnxruntime-gpu as well as proper PyTorch, CUDA and cuDNN versions: https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html
# model = InferenceSession(model_path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider']) 

def tag(image, model_path, general_threshold="0.35", character_threshold="0.85", exclude_tags="", replace_underscore=True, sort=True, reverse=True):
    general_threshold = float(general_threshold)
    character_threshold = float(character_threshold)
    
    model = InferenceSession(model_path, providers=['CPUExecutionProvider'])
    input = model.get_inputs()[0]
    height = input.shape[1]

    # Reduce to max size and pad with white
    ratio = float(height) / max(image.size)
    new_size = tuple([int(x * ratio) for x in image.size])
    image = image.resize(new_size, Image.LANCZOS)
    square = Image.new("RGB", (height, height), (255, 255, 255))
    square.paste(image, ((height - new_size[0]) // 2, (height - new_size[1]) // 2))

    image = np.array(square).astype(np.float32)
    image = image[:, :, ::-1]  # RGB -> BGR
    image = np.expand_dims(image, 0)

    # Read all tags from csv and locate start of each category
    tags = []
    general_index = None
    character_index = None
    with open(os.path.join(os.path.splitext(model_path)[0] + ".csv")) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if general_index is None and row[2] == "0":
                general_index = reader.line_num - 2
            elif character_index is None and row[2] == "4":
                character_index = reader.line_num - 2
            if replace_underscore:
                tags.append(row[1].replace("_", " "))
            else:
                tags.append(row[1])

    label_name = model.get_outputs()[0].name
    probs = model.run([label_name], {input.name: image})[0]

    result = list(zip(tags, probs[0]))

    general = [tag_tuple for tag_tuple in result[general_index:character_index] if tag_tuple[1] > general_threshold]
    character = [tag_tuple for tag_tuple in result[character_index:] if tag_tuple[1] > character_threshold]
    all = character + general

    remove = [s.strip() for s in exclude_tags.lower().split(",")]
    if sort:
        all = sorted([(tag, round(float(conf), 2)) for (tag, conf) in all if tag.lower() not in remove], key=lambda x: x[1], reverse=reverse)
    else:
        all = [tag_tuple for tag_tuple in all if tag_tuple[0] not in remove]

    return all


def main(**kwargs):
    arg_string_repr = json.dumps(kwargs, indent=2)
    image = kwargs.pop("image")
    try:
        image = Image.open(image)
    except FileNotFoundError as e:
        print("Error: " + e)
        return
    
    model_path = kwargs.pop("model_path")
    if not os.path.exists(model_path):
        model_path = filedialog.askopenfilename(initialdir="../../ONNX_models", title="Choose ONNX model for tagging", filetypes=[("ONNX Model", "*.onnx")])
        if not os.path.exists(model_path):
            print(f'''ONNX model ({model_path}) not found.
Please visit https://huggingface.co/SmilingWolf and pick a model. I recommend wd-v1-4-moat-tagger-v2.
Download "model.onnx" and "selected_tags.csv" for your chosen model.
Rename both files to whatever you\'d like, ensuring both names match e.g., "WDMoat_v2.onnx" and "WDMoat_v2.csv"
Place these files in the "onnx_models" folder and that's it!''')
            return
        
    inferred_tags = tag(image, model_path, **kwargs)

    all_formatted = [
        [item[0].replace("(", "\\(").replace(")", "\\)") , item[1]] for item in inferred_tags
        ]

    csv_result = (", ").join(
        (item[0] for item in all_formatted)
        )

    confidence_result = "\n".join(
        [f"{(item[0])}: {item[1]}" for item in inferred_tags]
        )
    print(f"{csv_result}\n\n{confidence_result}\n\nArguments: {arg_string_repr}")
    #print(json.dumps(all,indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process image with ONNX model")

    # Required
    parser.add_argument(
        "--image", 
        type=str, 
        required=True,
        help="Path to the image"
    )

    parser.add_argument(
        "--model_path", 
        type=str, 
        required=False, 
        help="Path of the ONNX model for inference"
    )

    # Optional
    parser.add_argument(
        "--general_threshold", 
        type=str, 
        required=False, 
        default="0.35",
        help="General tag confidence threshold"
    )

    parser.add_argument(
        "--character_threshold", 
        type=str, 
        required=False, 
        default="0.85",
        help="Character tag confidence threshold"
    )

    parser.add_argument(
        "--exclude_tags", 
        type=str, 
        required=False, 
        default="",
        help="Comma separated list of tags to exclude"
    )

    # parser.add_argument(
    #     "--verbose", 
    #     action="store_true",  # This is a flag, no value is required
    #     help="Enable verbose mode for more detailed output"
    # )

    kwargs = vars(parser.parse_args())
    if not kwargs["image"]:
        raise ValueError("First argument must be an image file")

    
    main(**kwargs)