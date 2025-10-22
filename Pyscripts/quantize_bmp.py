from PIL import Image
from pathlib import Path

@service
def quantize_bmp(src: str, dst_dir: str, dither: bool = True, rgb24: bool = True):
    # Dither to fixed 6-color Spectra palette, then save.
    src_path = Path(src)
    out_dir = Path(dst_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Spectra 6 palette
    palette = [
        0, 0, 0,          # black
        255, 255, 255,    # white
        255, 255, 0,      # yellow
        255, 0, 0,        # red
        0, 0, 255,        # blue
        0, 255, 0,        # green
    ]

    pal_img = Image.new("P", (1, 1))
    pad = 768 - len(palette)
    if pad < 0:
        raise ValueError("Palette has more than 256 colors (>768 entries).")
    pal_img.putpalette(palette + [0] * pad)

    # Open, ensure RGB, then quantize with FS dithering to the fixed palette
    im = Image.open(src_path).convert("RGB")
    q = im.quantize(
        palette=pal_img,
        dither=Image.FLOYDSTEINBERG if dither else Image.NONE,
    )

    # Output path
    dst_path = out_dir / (src_path.stem + ".bmp")

    if rgb24:
        # Convert the dithered paletted image back to RGB, saved as 24-bit BMP
        rgb = q.convert("RGB")
        rgb.save(dst_path, format="BMP", bits=24)
        bit = 24
    else:
        # Keep as paletted 8-bit BMP
        q.save(dst_path, format="BMP")
        bit = 8
    print(f"Saved {dst_path} ({bit}-bit BMP).")