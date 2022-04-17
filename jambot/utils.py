from io import BytesIO
import requests


def get_thumb(link):
    try:
        r = requests.get(link)
        thumb = BytesIO(r.raw.read())
        return thumb
    except Exception as e:
        print("?!" + str(e))
        return None
