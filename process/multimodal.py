# This is the Multi Modal Part
# For now this will only support Image Recognition, but later on who knows???
from io import BytesIO
import io
import json
from PIL import Image
import torch

import discord
from aiohttp import ClientSession
import config
import util
from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp import TCPConnector

from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp import TCPConnector


async def read_image(message):
    recognized_text = ""
    recognized_image = ""
    image_description = ""
    if config.florence:
        try:
            # Process each attachment (actually just one for now)
            for attachment in message.attachments:
                # Check if it is an image based on content type
                image_bytes = await attachment.read()
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                    print(attachment.filename.lower())
                    if attachment.filename.lower().endswith('.webp'):
                        image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
                    image_description = await process_image(image_bytes)
                    #recognized_text = await process_text(image_bytes)
                    #recognized_image = await process_image(image_bytes)
                    return image_description
                else:
                    # Check if it is a link to an images
                    if attachment.url:
                        if attachment.filename.lower().endswith('.webp'):
                            image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
                        if any(attachment.url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                            # You would typically fetch the image from the URL here
                            # For example, using aiohttp to fetch the image
                            async with ClientSession() as session:
                                async with session.get(attachment.url) as response:
                                    if response.status == 200:
                                        if attachment.filename.lower().endswith('.webp'):
                                            image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
                                        #recognized_text = await process_text(image_bytes)
                                        image_description = await process_image(image_bytes)
                                        return image_description
        except Exception as e:
            print(f"An error occurred: {e}")
            return image_description


async def process_image(image_bytes):
    try:
        model = config.florence
        processor = config.florence_processor
        device = torch.device("cpu")
        
        # Move the model to the specified device
        model = model.to(device)

        def run_example(task_prompt, image, text_input=None):
            if text_input is None:
                prompt = task_prompt
            else:
                prompt = task_prompt + " " + text_input
            inputs = processor(text=prompt, images=image, return_tensors="pt")
            # Move inputs to the same device as the model
            inputs = {k: v.to(device) for k, v in inputs.items()}
            generated_ids = model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=1024,
                early_stopping=False,
                do_sample=False,
                num_beams=3,
            )
            generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
            parsed_answer = processor.post_process_generation(
                generated_text, 
                task=task_prompt, 
                image_size=(image.width, image.height)
            )
            return parsed_answer

        # Open the image and convert to RGB if necessary
        image = Image.open(BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # First, get a detailed caption
        task_prompt = '<MORE_DETAILED_CAPTION>'
        image_result = run_example(task_prompt, image)
        task_prompt = '<OCR>'
        text_result = run_example(task_prompt,image)
        # Combine the results
        final_results = f"Image Description: {image_result['<MORE_DETAILED_CAPTION>']}|Text Inside Image:{text_result['<OCR>']}"
        print(final_results)
        return final_results
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return ""