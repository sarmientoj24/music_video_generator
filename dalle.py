import base64
import io
import os

import openai
from PIL import Image

PROMPT_TEMPLATE = "an {} oil painting of a scene about {}, cinematic lighting, cinematic composition, rule of thirds, vivid, HDR, UHD, 4K, highly detailed, professional, trending on artstation, no text, royalty free"

STYLE_MAPPING = {
    "impressionist": "impressionist",
    "abstract": "abstract",
    "photorealistic": "photorealistic",
    "expressionist": "expressionist",
    "surrealist": "surrealist",
    "cubist": "cubist",
    "popart": "popart",
    "anime": "makoto shinkai art style",
    "scifi": "scifi scene",
}


class DALLEGenerator:
    def __init__(self):
        if not os.getenv("API_KEY"):
            raise Exception("Setup API_KEY as environment variables!")

        openai.api_key = os.getenv("API_KEY")

    def generate_image(self, prompt, style="impressionist"):
        """
        Generate image from prompt.

        Args:
            prompt (str): Prompt to generate image from.
            style (str): Style of image to generate.
        Returns:
            image: PIL image.
        """

        prompt = PROMPT_TEMPLATE.format(
            STYLE_MAPPING.get(style, "impressionist"), prompt
        )

        try:
            response = openai.Image.create(
                prompt=prompt, n=1, size="512x512", response_format="b64_json"
            )

            b64 = response["data"][0]["b64_json"]
            image_bytes = base64.b64decode(b64)
            image = Image.open(io.BytesIO(image_bytes))
        except Exception:
            # Create black placeholder image
            image = Image.new("RGB", (512, 512))

        if not image:
            image = Image.new("RGB", (512, 512))
        return image
