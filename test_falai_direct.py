import asyncio
import base64
from app.falai_client import edit_image_with_falai
import os
from PIL import Image, ImageDraw

# Create a proper test image with minimum size (256x256)
test_image_path = "test_images/direct_test_image.png"
os.makedirs(os.path.dirname(test_image_path), exist_ok=True)

# Create a 256x256 red square image
image = Image.new('RGB', (256, 256), color='red')
image.save(test_image_path, 'PNG')

# Test the Fal.ai client directly
async def test_falai():
    try:
        print("Testing Fal.ai client directly...")
        result = await edit_image_with_falai(test_image_path, "Turn the red square into a blue circle")
        print(f"Success! Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

# Run the test
asyncio.run(test_falai())