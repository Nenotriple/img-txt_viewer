import os
import numpy as np
import csv
import argparse

from PIL import Image
from onnxruntime import InferenceSession

ROOT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def tag(image, model_name, threshold="0.35", character_threshold="0.85", exclude_tags="", replace_underscore=True, sort=True, reverse=True):
    model_path = os.path.join(ROOT_DIRECTORY, "ONNX_models", model_name + ".ONNX")
    threshold = float(threshold)
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
    with open(os.path.join(ROOT_DIRECTORY, "ONNX_models", model_name + ".csv")) as f:
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

    general = [item for item in result[general_index:character_index] if item[1] > threshold]
    character = [item for item in result[character_index:] if item[1] > character_threshold]

    all = character + general
    remove = [s.strip() for s in exclude_tags.lower().split(",")]
    if sort:
        all = sorted([(tag, round(float(conf), 2)) for (tag, conf) in all if tag not in remove], key=lambda x: x[1], reverse=reverse)
    else:
        all = [tag for tag in all if tag[0] not in remove]

    return all

def main(**kwargs):
    image = kwargs.pop("image")
    try:
        image = Image.open(image)
    except FileNotFoundError as e:
        print("Error: " + e)
        return
    model= kwargs.pop("model")

    all = tag(image, model, **kwargs)
    all = [[item[0].replace("(", "\\(").replace(")", "\\)") , item[1]] for item in all]
    res = (", ").join((item[0].replace("(", "\\(").replace(")", "\\)") for item in all))
    conf = "\n".join(
        [f"{(item[0])}: {item[1]}" for item in all]
        )
    print(res)
    #print(json.dumps(all,indent=2))
    #print(json.dumps(all,indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process image with ONNX model")

    # Required
    parser.add_argument(
        "--image", 
        type=str, 
        required=False,
        help="Path to the image"
    )

    # Optional
    parser.add_argument(
        "--model", 
        type=str, 
        required=False, 
        default="WDMoat_v2",
        help="Name of the model in ONNX_models for inference"
    )

    parser.add_argument(
        "--threshold", 
        type=str, 
        required=False, 
        default="0.35",
        help="Tag confidence threshold"
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
        kwargs["image"] = r"x:\Kohya\Datasets\1_Tacticool2-InProgress\__termichan_original_drawn_by_polilla__79f92e56d0ff60d338db21d3c68ec890.jpg"
        #raise ValueError("First argument must be an image file")

    main(**kwargs)