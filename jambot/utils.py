from io import BytesIO

import requests
from PIL import Image

THUMB_SIZE = (100, 100)


def get_thumb(link):
    try:
        r = requests.get(link, stream=True)
        img = Image.open(BytesIO(r.content))
        img.thumbnail(THUMB_SIZE)
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        return img_bytes.getvalue()
    except Exception:
        return None
