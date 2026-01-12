import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash-image')
# emini-3-pro-image-preview
def generate_image(prompt: str, image_path: Optional[str] = None, output_filename: str = "generated_image.png") -> Optional[str]:
    """
    Generates image from text prompt or edits input image.
    
    Args:
        prompt (str): Text description for generation or edit.
        image_path (str, optional): Path to input image for img2img.
        output_filename (str): Name for saved output image.
    
    Returns:
        str: Path to saved image or None if failed.
    """
    content = [prompt]
    
    if image_path:
        try:
            img_to_edit = Image.open(image_path)
            content.append(img_to_edit)
        except FileNotFoundError:
            print(f"Error: {image_path} not found.")
            return None
    
    response = model.generate_content(content)
    
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_data = BytesIO(part.inline_data.data)
                img = Image.open(image_data)
                img.save(output_filename)
                print(f"Image saved as {output_filename}")
                return output_filename
    print("No image data found in response.")
    return None

# # Text-to-image
# generate_image("A futuristic nano banana pro, glowing neon lights, 4K", output_filename="text_output.png")

# # Image-to-image (add image_path)



# brand_label = f"""create brand label replace swanky with collection name {collection_name}
# and dress description as {header_description}
# and generate same image with modified detail 
# """

# care_label = """generate care label for garment with fabric description: {fabric_description}
# and garment descrition:{garment_description}"""





# measurement_diagram = """A professional fashion technical flat (tech pack measurement diagram) of given image garment, shown in front view and back view side-by-side on a clean white background.

# Draw everything using thin black vector CAD-style lines with no shading, no textures, and no colors.

# On the front view, include red technical measurement guides:

# horizontal, vertical, and diagonal double-arrow dimension lines

# dots at measurement points

# empty letter placeholders (A, B, C, D, E, F…) placed near each measurement line

# Do NOT add text labels or values — only the letters should appear so that labels can be added later.

# Layout must look like a factory-ready fashion tech pack page used for clothing manufacturing.

# measurement details:
# {measurement_details}"""
# first_page_logo = """replace swanky by collection name {collection_name}"""

# generate_image(f"replace swanky by collection name Grandiose", "assets/first_page_logo.png",
#                output_filename="img2img_output.png")


