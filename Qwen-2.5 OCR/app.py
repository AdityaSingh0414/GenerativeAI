#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import tensorflow as tf
from tensorflow import keras

from PIL import Image, ImageDraw, ImageFont
import ast
import base64
import os
from openai import OpenAI


# =========================================================
# STREAMLIT CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Qwen 2.5 OCR - TensorFlow/Keras",
    layout="wide"
)

st.title("Qwen 2.5 OCR")
st.caption("OCR and Text Spotting using Qwen2.5-VL API with TensorFlow/Keras image processing")


# =========================================================
# TENSORFLOW DEVICE INFORMATION
# =========================================================

@st.cache_resource
def initialize_tensorflow():

    gpus = tf.config.list_physical_devices("GPU")

    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)

            return "GPU"

        except RuntimeError:
            return "GPU"

    return "CPU"


device = initialize_tensorflow()

st.sidebar.write(f"TensorFlow Device: {device}")


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Qwen 2.5 OCR")

uploaded_file = st.sidebar.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png"]
)


# =========================================================
# IMAGE PREPROCESSING USING TENSORFLOW / KERAS
# =========================================================

def preprocess_image_tensorflow(image_path):

    # Read image
    image_data = tf.io.read_file(image_path)

    # Decode image
    image = tf.image.decode_image(
        image_data,
        channels=3,
        expand_animations=False
    )

    # Convert to float32
    image = tf.image.convert_image_dtype(
        image,
        tf.float32
    )

    # Add batch dimension
    image = tf.expand_dims(
        image,
        axis=0
    )

    return image


def get_image_dimensions_tensorflow(image_path):

    image_tensor = preprocess_image_tensorflow(image_path)

    shape = tf.shape(image_tensor)

    height = int(shape[1])
    width = int(shape[2])

    return width, height


# =========================================================
# JSON PARSER
# =========================================================

def parse_json(json_output):

    lines = json_output.splitlines()

    for i, line in enumerate(lines):

        if line.strip() == "```json":

            json_output = "\n".join(
                lines[i + 1:]
            )

            json_output = json_output.split(
                "```"
            )[0]

            break

    return json_output.strip()


# =========================================================
# BASE64 IMAGE ENCODING
# =========================================================

def encode_image(image_path):

    with open(
        image_path,
        "rb"
    ) as image_file:

        return base64.b64encode(
            image_file.read()
        ).decode("utf-8")


# =========================================================
# QWEN 2.5 VL API INFERENCE
# =========================================================

def inference_with_api(
    image_path,
    prompt,
    sys_prompt="You are a helpful OCR assistant.",
    model_id="qwen2.5-vl-72b-instruct",
    min_pixels=512 * 28 * 28,
    max_pixels=2048 * 28 * 28
):

    base64_image = encode_image(
        image_path
    )

    api_key = os.getenv(
        "DASHSCOPE_API_KEY"
    )

    if not api_key:

        raise ValueError(
            "DASHSCOPE_API_KEY environment variable is not set."
        )

    client = OpenAI(

        api_key=api_key,

        base_url=(
            "https://dashscope-intl.aliyuncs.com/"
            "compatible-mode/v1"
        )
    )

    messages = [

        {
            "role": "system",

            "content": [

                {
                    "type": "text",
                    "text": sys_prompt
                }

            ]
        },

        {
            "role": "user",

            "content": [

                {
                    "type": "image_url",

                    "min_pixels": min_pixels,

                    "max_pixels": max_pixels,

                    "image_url": {

                        "url": (
                            f"data:image/jpeg;base64,"
                            f"{base64_image}"
                        )

                    }
                },

                {
                    "type": "text",
                    "text": prompt
                }

            ]
        }

    ]

    completion = client.chat.completions.create(

        model=model_id,

        messages=messages

    )

    return completion.choices[0].message.content


# =========================================================
# DRAW TEXT BOUNDING BOXES
# =========================================================

def plot_text_bounding_boxes(
    image_path,
    bounding_boxes,
    input_width,
    input_height
):

    img = Image.open(
        image_path
    ).convert("RGB")

    width, height = img.size

    draw = ImageDraw.Draw(
        img
    )

    bounding_boxes = parse_json(
        bounding_boxes
    )

    try:

        font = ImageFont.truetype(
            "NotoSansCJK-Regular.ttc",
            size=12
        )

    except Exception:

        font = ImageFont.load_default()

    try:

        boxes = ast.literal_eval(
            bounding_boxes
        )

    except Exception as e:

        raise ValueError(
            f"Could not parse bounding boxes: {e}"
        )

    for bounding_box in boxes:

        if "bbox_2d" not in bounding_box:

            continue

        bbox = bounding_box[
            "bbox_2d"
        ]

        abs_x1 = int(
            bbox[0] / input_width * width
        )

        abs_y1 = int(
            bbox[1] / input_height * height
        )

        abs_x2 = int(
            bbox[2] / input_width * width
        )

        abs_y2 = int(
            bbox[3] / input_height * height
        )

        # Correct coordinates

        if abs_x1 > abs_x2:

            abs_x1, abs_x2 = (
                abs_x2,
                abs_x1
            )

        if abs_y1 > abs_y2:

            abs_y1, abs_y2 = (
                abs_y2,
                abs_y1
            )

        # Draw bounding box

        draw.rectangle(

            (
                (abs_x1, abs_y1),
                (abs_x2, abs_y2)
            ),

            outline="green",

            width=2

        )

        # Draw detected text

        if "text_content" in bounding_box:

            draw.text(

                (
                    abs_x1,
                    abs_y2 + 2
                ),

                str(
                    bounding_box[
                        "text_content"
                    ]
                ),

                fill="green",

                font=font

            )

    return img


# =========================================================
# SAVE UPLOADED IMAGE
# =========================================================

temp_image_path = None


if uploaded_file is not None:

    image = Image.open(
        uploaded_file
    )

    # Convert image to RGB

    if image.mode != "RGB":

        image = image.convert(
            "RGB"
        )

    # Display image

    st.sidebar.image(

        image,

        caption="Uploaded Image",

        use_container_width=True

    )

    # Save temporary image

    temp_image_path = (
        "temp_uploaded_image.jpg"
    )

    image.save(

        temp_image_path,

        format="JPEG"

    )


# =========================================================
# MODE SELECTION
# =========================================================

mode = st.radio(

    "Select Mode",

    [
        "Full Page OCR",
        "Text Spotting"
    ]

)


# =========================================================
# MAIN APPLICATION
# =========================================================

if uploaded_file is not None:

    # -----------------------------------------------------
    # FULL PAGE OCR
    # -----------------------------------------------------

    if mode == "Full Page OCR":

        st.header(
            "Full Page OCR"
        )

        if st.button(
            "Extract Text"
        ):

            with st.spinner(
                "Extracting text..."
            ):

                prompt = """
                Extract all text from this image.

                Return only the extracted text.

                Do not include explanations,
                descriptions, or markdown formatting.
                """

                try:

                    # TensorFlow preprocessing

                    image_tensor = (
                        preprocess_image_tensorflow(
                            temp_image_path
                        )
                    )

                    st.write(
                        "Tensor shape:",
                        image_tensor.shape
                    )

                    # Qwen API inference

                    response = (
                        inference_with_api(

                            temp_image_path,

                            prompt

                        )
                    )

                    st.markdown(
                        "### Extracted Text"
                    )

                    st.text(
                        response
                    )

                except Exception as e:

                    st.error(

                        f"Error during inference: {e}"

                    )


    # -----------------------------------------------------
    # TEXT SPOTTING
    # -----------------------------------------------------

    elif mode == "Text Spotting":

        st.header(
            "Text Spotting"
        )

        if st.button(
            "Spot Text"
        ):

            with st.spinner(
                "Detecting text..."
            ):

                prompt = """
                Detect all text in the image.

                Return the result as a JSON array.

                Each detected text line must contain:

                {
                    "bbox_2d":
                    [x1, y1, x2, y2],

                    "text_content":
                    "detected text"
                }

                Coordinates should correspond
                to the original image dimensions.

                Return JSON only.
                """

                try:

                    # Get dimensions using TensorFlow

                    input_width, input_height = (
                        get_image_dimensions_tensorflow(

                            temp_image_path

                        )
                    )

                    # Qwen API inference

                    response = (
                        inference_with_api(

                            temp_image_path,

                            prompt

                        )
                    )

                    # Draw bounding boxes

                    result_image = (
                        plot_text_bounding_boxes(

                            temp_image_path,

                            response,

                            input_width,

                            input_height

                        )
                    )

                    # Display results

                    col1, col2 = (
                        st.columns(2)
                    )

                    with col1:

                        st.image(

                            result_image,

                            caption=(
                                "Text Spotting Result"
                            ),

                            use_container_width=True

                        )

                    with col2:

                        st.markdown(
                            "### Detected Text"
                        )

                        st.code(

                            parse_json(
                                response
                            ),

                            language="json"

                        )

                except Exception as e:

                    st.error(

                        f"Error during inference: {e}"

                    )


# =========================================================
# NO IMAGE UPLOADED
# =========================================================

else:

    st.info(

        "Please upload an image to begin."

    )