import os
from PIL import Image

def to_webp(input_path, output_path=None):
    img = Image.open(input_path).convert("RGB")
    img.save(output_path, "WEBP", quality=80)
    if os.path.exists(input_path):
        os.remove(input_path)