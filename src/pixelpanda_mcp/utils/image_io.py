"""Image I/O utilities for reading, writing, and path management."""

import os
from PIL import Image
from io import BytesIO


def read_image(file_path: str) -> tuple[Image.Image, bytes]:
    """Read an image from a file path, return PIL Image and raw bytes."""
    file_path = os.path.expanduser(file_path)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Image not found: {file_path}")
    with open(file_path, "rb") as f:
        raw = f.read()
    img = Image.open(BytesIO(raw))
    return img, raw


def save_image(image: Image.Image, output_path: str, quality: int = 95, fmt: str | None = None) -> str:
    """Save a PIL Image to a path. Auto-detects format from extension."""
    output_path = os.path.expanduser(output_path)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    ext = os.path.splitext(output_path)[1].lower()
    save_fmt = fmt or {
        ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG",
        ".webp": "WEBP", ".bmp": "BMP", ".tiff": "TIFF", ".tif": "TIFF",
    }.get(ext, "PNG")

    save_kwargs = {}
    if save_fmt in ("JPEG", "WEBP"):
        save_kwargs["quality"] = quality
    if save_fmt == "PNG":
        save_kwargs["optimize"] = True

    # JPEG doesn't support alpha
    if save_fmt == "JPEG" and image.mode in ("RGBA", "LA", "PA"):
        bg = Image.new("RGB", image.size, (255, 255, 255))
        bg.paste(image, mask=image.split()[-1])
        image = bg
    elif save_fmt == "JPEG" and image.mode != "RGB":
        image = image.convert("RGB")

    image.save(output_path, format=save_fmt, **save_kwargs)
    return output_path


def auto_output_path(input_path: str, suffix: str, ext: str | None = None) -> str:
    """Generate an output path like 'photo_resized.png' from 'photo.png'."""
    base, original_ext = os.path.splitext(input_path)
    out_ext = ext or original_ext or ".png"
    return f"{base}_{suffix}{out_ext}"


def get_content_type(file_path: str) -> str:
    """Get MIME type from file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".webp": "image/webp", ".gif": "image/gif", ".bmp": "image/bmp",
        ".tiff": "image/tiff", ".tif": "image/tiff",
    }.get(ext, "image/png")
