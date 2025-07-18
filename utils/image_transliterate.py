import torch
from ultralytics import YOLO
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq, TextStreamer

torch.set_num_threads(torch.get_num_threads())
torch.set_num_interop_threads(torch.get_num_threads())

model_detect = YOLO('storage/models/pegon-ai-detect.pt')
padding = 4

model_path = 'storage/models/pegon-ai-vision'
processor = AutoProcessor.from_pretrained(model_path)
model_vision = AutoModelForVision2Seq.from_pretrained(
    model_path,
    torch_dtype=torch.float32,
    device_map="cpu"
)

def image_transliterate(image_path):  
    img = Image.open(image_path).convert("RGB")
    orig_width, orig_height = img.size

    results = model_detect(image_path, imgsz=640, augment=False)[0]
    boxes = results.boxes.xyxy.cpu().numpy()

    input_w, input_h = results.orig_shape[1], results.orig_shape[0]
    scale_x = orig_width / input_w
    scale_y = orig_height / input_h

    adjusted_boxes = []
    for box in boxes:
        x1, y1, x2, y2 = box

        x1 = int(x1 * scale_x) - padding
        y1 = int(y1 * scale_y) - padding
        x2 = int(x2 * scale_x) + padding
        y2 = int(y2 * scale_y) + padding

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(orig_width, x2)
        y2 = min(orig_height, y2)

        adjusted_boxes.append((x1, y1, x2, y2))

    adjusted_boxes.sort(key=lambda b: b[1])

    for x1, y1, x2, y2 in adjusted_boxes:
        cropped = img.crop((x1, y1, x2, y2))

        instruction = "Extract the text written in Pegon script (Arabic script used for Javanese or Indonesian) from the image and convert it into Latin script. Follow phonetic transcription rules based on Javanese or Indonesian pronunciation. Maintain accurate word separation and preserve the original meaning. Output only the Latin-script transcription."

        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": instruction}]
            },
            {
                "role": "user",
                "content": [{"type": "image"}]
            }
        ]

        tokenizer = processor.tokenizer
        prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
        inputs = processor(text=prompt, images=cropped, return_tensors="pt").to("cpu")

        output_ids = model_vision.generate(
            **inputs,
            do_sample=False,
            num_beams=1,
        )

        output_text = processor.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        clean_output = output_text.split("Assistant:")[-1].strip()
        print(clean_output)