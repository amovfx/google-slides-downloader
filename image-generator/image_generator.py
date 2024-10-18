import io
import operator
import os
import pathlib
import time


import requests
import yaml
from dotenv import load_dotenv

from PIL import Image


# Load environment variables
load_dotenv()

API_KEY = os.getenv("LEONARDO_API_KEY")
BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"

headers = {
    "accept": "application/json",
    "authorization": f"Bearer {API_KEY}",
    "content-type": "application/json",
}


def make_image(prompt, output_path):
    generation_id = create_generation_id(prompt)
    if generation_id:
        time.sleep(25)
        generation_url = get_image_urls(generation_id)
        if generation_url:
            return download_image_url(generation_url, output_path)


def create_generation_id(prompt):
    # Step 1: Generate images
    generation_url = f"{BASE_URL}/generations"

    payload = {
        "modelId": "e71a1c2f-4f80-4800-934f-2c68979d8cc8",
        "prompt": prompt,
        "num_images": 1,
        "width": 1024,
        "height": 1024,
        "ultra": False,
        "enhancePrompt": True,
    }

    response = requests.post(generation_url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Error generating image: {response.text}")
        return None

    generation_id = response.json()["sdGenerationJob"]["generationId"]
    print(generation_id)

    return generation_id


def get_image_urls(generation_id):
    status_url = f"{BASE_URL}/generations/{generation_id}"
    status_response = requests.get(status_url, headers=headers)
    if status_response.status_code == 200:
        return status_response.json()["generations_by_pk"]["generated_images"][0]["url"]


def download_image_url(generation_url: str, output_path: str | pathlib.Path):

    response = requests.get(generation_url, stream=True)
    if response.status_code == 200:
        # Stream content to memory
        image_data = io.BytesIO(response.content)

        # Open the image using PIL
        with Image.open(image_data) as img:
            # Convert to RGB (in case it's RGBA) and save as JPG
            img.convert("RGB").save(output_path, "JPEG")

        print(f"Image downloaded and converted successfully: {output_path}")
    else:
        print(f"Failed to download image from {generation_url}")
