import random
import io
from pathlib import Path
import requests
from PIL import Image
from PIL import ExifTags

# Spectra 6 palette
PALETTE = [
    0,   0,   0, # Black
    255, 255, 255, # White
    200, 50,  60, # Red
    45,  110, 60, # Green
    55,  75,  150, # Blue
    200, 200, 50, # Yellow
]


@pyscript_executor
def _do_work(immich_url, api_key, album_id, output_path):
    url = immich_url.rstrip("/")
    headers = {"x-api-key": api_key}

    album = requests.get(f"{url}/api/albums/{album_id}", headers=headers, timeout=30).json()
    images = [a for a in album["assets"] if a["type"] == "IMAGE"]
    chosen = random.choice(images)


    data = requests.get(f"{url}/api/assets/{chosen['id']}/original", headers=headers, timeout=60).content
    img = Image.open(io.BytesIO(data)).convert("RGB")

    # Check orientation from EXIF and rotate if needed
    try:
        orient_key = next(k for k, v in ExifTags.TAGS.items() if v == "Orientation")
        orient = img.getexif().get(orient_key)
        if orient == 3:   img = img.rotate(180, expand=True)
        elif orient == 6: img = img.rotate(270, expand=True)
        elif orient == 8: img = img.rotate(90, expand=True)
    except Exception:
        pass

    w, h = img.size
    scale = max(800 / w, 480 / h)
    img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    left = (img.width - 800) // 2
    top = (img.height - 480) // 2
    img = img.crop((left, top, left + 800, top + 480))

    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette(PALETTE + [0] * (768 - len(PALETTE)))
    img = img.quantize(palette=pal_img, dither=Image.Dither.FLOYDSTEINBERG).convert("RGB")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out), format="PNG")
    return chosen["id"]


# Requests need to be made with:
# immich_url=http://
# api_key=
# album_id=

@service
def fetch_immich_photo(
    immich_url="http://192.168.2.157:2283",
    api_key="",
    album_id="",
    output_path="/config/www/photo_frame/current.png",
):
    asset_id = _do_work(immich_url, api_key, album_id, output_path)
    log.info(f"[photo_frame] Saved to {output_path} (asset {asset_id})")