"""Local PIL-based image tools — free, no auth, no network required."""

from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from ..utils.image_io import read_image, save_image, auto_output_path


def register(mcp):
    """Register all local image tools with the MCP server."""

    @mcp.tool()
    async def resize_image(
        file_path: str,
        width: int | None = None,
        height: int | None = None,
        maintain_aspect_ratio: bool = True,
        output_path: str | None = None,
    ) -> str:
        """Resize an image. Specify width, height, or both. Maintains aspect ratio by default.

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        orig_w, orig_h = img.size

        if width and height and not maintain_aspect_ratio:
            new_size = (width, height)
        elif width and height:
            ratio = min(width / orig_w, height / orig_h)
            new_size = (int(orig_w * ratio), int(orig_h * ratio))
        elif width:
            ratio = width / orig_w
            new_size = (width, int(orig_h * ratio))
        elif height:
            ratio = height / orig_h
            new_size = (int(orig_w * ratio), height)
        else:
            return f"Specify at least width or height. Current size: {orig_w}x{orig_h}"

        result = img.resize(new_size, Image.LANCZOS)
        out = output_path or auto_output_path(file_path, f"{new_size[0]}x{new_size[1]}")
        save_image(result, out)
        return f"Resized {orig_w}x{orig_h} -> {new_size[0]}x{new_size[1]}. Saved to {out}"

    @mcp.tool()
    async def crop_image(
        file_path: str,
        left: int,
        top: int,
        right: int,
        bottom: int,
        output_path: str | None = None,
    ) -> str:
        """Crop an image to the specified rectangle (left, top, right, bottom in pixels).

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        result = img.crop((left, top, right, bottom))
        out = output_path or auto_output_path(file_path, "cropped")
        save_image(result, out)
        return f"Cropped to ({left},{top})-({right},{bottom}) = {result.size[0]}x{result.size[1]}. Saved to {out}"

    @mcp.tool()
    async def rotate_image(
        file_path: str,
        degrees: float,
        expand: bool = True,
        output_path: str | None = None,
    ) -> str:
        """Rotate an image by the specified degrees (counter-clockwise). Expands canvas by default.

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        result = img.rotate(degrees, expand=expand, resample=Image.BICUBIC)
        out = output_path or auto_output_path(file_path, f"rotated_{int(degrees)}")
        save_image(result, out)
        return f"Rotated {degrees} degrees. Saved to {out}"

    @mcp.tool()
    async def flip_image(
        file_path: str,
        direction: str = "horizontal",
        output_path: str | None = None,
    ) -> str:
        """Flip an image horizontally or vertically.

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        if direction == "vertical":
            result = img.transpose(Image.FLIP_TOP_BOTTOM)
        else:
            result = img.transpose(Image.FLIP_LEFT_RIGHT)
        out = output_path or auto_output_path(file_path, f"flipped_{direction}")
        save_image(result, out)
        return f"Flipped {direction}. Saved to {out}"

    @mcp.tool()
    async def grayscale_image(
        file_path: str,
        output_path: str | None = None,
    ) -> str:
        """Convert an image to grayscale.

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        result = ImageOps.grayscale(img)
        out = output_path or auto_output_path(file_path, "grayscale")
        save_image(result, out)
        return f"Converted to grayscale. Saved to {out}"

    @mcp.tool()
    async def invert_image(
        file_path: str,
        output_path: str | None = None,
    ) -> str:
        """Invert the colors of an image (negative).

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        if img.mode == "RGBA":
            r, g, b, a = img.split()
            rgb = Image.merge("RGB", (r, g, b))
            inverted = ImageOps.invert(rgb)
            result = Image.merge("RGBA", (*inverted.split(), a))
        else:
            result = ImageOps.invert(img.convert("RGB"))
        out = output_path or auto_output_path(file_path, "inverted")
        save_image(result, out)
        return f"Colors inverted. Saved to {out}"

    @mcp.tool()
    async def round_corners(
        file_path: str,
        radius: int = 20,
        output_path: str | None = None,
    ) -> str:
        """Round the corners of an image with a specified radius.

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        img = img.convert("RGBA")
        w, h = img.size
        mask = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), (w, h)], radius=radius, fill=255)
        result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        result.paste(img, mask=mask)
        out = output_path or auto_output_path(file_path, f"rounded_r{radius}", ".png")
        save_image(result, out)
        return f"Rounded corners (radius={radius}). Saved to {out}"

    @mcp.tool()
    async def add_border(
        file_path: str,
        width: int = 10,
        color: str = "#000000",
        output_path: str | None = None,
    ) -> str:
        """Add a solid color border around an image.

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        result = ImageOps.expand(img, border=width, fill=color)
        out = output_path or auto_output_path(file_path, f"border_{width}px")
        save_image(result, out)
        return f"Added {width}px {color} border. Saved to {out}"

    @mcp.tool()
    async def compress_image(
        file_path: str,
        quality: int = 80,
        output_format: str = "jpeg",
        output_path: str | None = None,
    ) -> str:
        """Compress an image by reducing quality. Output format: jpeg, webp, or png.

        Free tool — runs locally, no account needed.
        """
        import os
        img, _ = read_image(file_path)
        fmt_ext = {"jpeg": ".jpg", "webp": ".webp", "png": ".png"}.get(output_format.lower(), ".jpg")
        out = output_path or auto_output_path(file_path, f"compressed_q{quality}", fmt_ext)
        save_image(img, out, quality=quality)
        original_size = os.path.getsize(file_path)
        new_size = os.path.getsize(out)
        pct = (1 - new_size / original_size) * 100 if original_size > 0 else 0
        return f"Compressed ({pct:.0f}% smaller): {original_size:,}B -> {new_size:,}B. Saved to {out}"

    @mcp.tool()
    async def merge_images(
        file_paths: list[str],
        direction: str = "horizontal",
        gap: int = 0,
        output_path: str | None = None,
    ) -> str:
        """Merge multiple images into one. Direction: horizontal, vertical, or grid.

        Free tool — runs locally, no account needed.
        """
        if len(file_paths) < 2:
            return "Provide at least 2 file paths to merge."

        images = [read_image(p)[0] for p in file_paths]

        if direction == "horizontal":
            max_h = max(im.size[1] for im in images)
            total_w = sum(im.size[0] for im in images) + gap * (len(images) - 1)
            canvas = Image.new("RGBA", (total_w, max_h), (0, 0, 0, 0))
            x = 0
            for im in images:
                canvas.paste(im.convert("RGBA"), (x, (max_h - im.size[1]) // 2))
                x += im.size[0] + gap
        elif direction == "vertical":
            max_w = max(im.size[0] for im in images)
            total_h = sum(im.size[1] for im in images) + gap * (len(images) - 1)
            canvas = Image.new("RGBA", (max_w, total_h), (0, 0, 0, 0))
            y = 0
            for im in images:
                canvas.paste(im.convert("RGBA"), ((max_w - im.size[0]) // 2, y))
                y += im.size[1] + gap
        else:  # grid
            import math
            cols = math.ceil(math.sqrt(len(images)))
            rows = math.ceil(len(images) / cols)
            cell_w = max(im.size[0] for im in images)
            cell_h = max(im.size[1] for im in images)
            canvas = Image.new("RGBA", (cols * (cell_w + gap) - gap, rows * (cell_h + gap) - gap), (0, 0, 0, 0))
            for i, im in enumerate(images):
                r, c = divmod(i, cols)
                x = c * (cell_w + gap) + (cell_w - im.size[0]) // 2
                y = r * (cell_h + gap) + (cell_h - im.size[1]) // 2
                canvas.paste(im.convert("RGBA"), (x, y))

        out = output_path or auto_output_path(file_paths[0], f"merged_{direction}", ".png")
        save_image(canvas, out)
        return f"Merged {len(images)} images ({direction}). Saved to {out}"

    @mcp.tool()
    async def convert_format(
        file_path: str,
        target_format: str = "png",
        output_path: str | None = None,
    ) -> str:
        """Convert an image to a different format: png, jpeg, webp, bmp, tiff.

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        ext_map = {"png": ".png", "jpeg": ".jpg", "jpg": ".jpg", "webp": ".webp", "bmp": ".bmp", "tiff": ".tiff"}
        ext = ext_map.get(target_format.lower(), f".{target_format.lower()}")
        out = output_path or auto_output_path(file_path, "converted", ext)
        save_image(img, out)
        return f"Converted to {target_format.upper()}. Saved to {out}"

    @mcp.tool()
    async def make_transparent(
        file_path: str,
        opacity: float = 0.5,
        output_path: str | None = None,
    ) -> str:
        """Adjust the opacity/transparency of an image. 0.0 = fully transparent, 1.0 = fully opaque.

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        img = img.convert("RGBA")
        r, g, b, a = img.split()
        a = a.point(lambda x: int(x * opacity))
        result = Image.merge("RGBA", (r, g, b, a))
        out = output_path or auto_output_path(file_path, f"opacity_{int(opacity*100)}", ".png")
        save_image(result, out)
        return f"Set opacity to {opacity:.0%}. Saved to {out}"

    @mcp.tool()
    async def create_profile_picture(
        file_path: str,
        size: int = 400,
        shape: str = "circle",
        output_path: str | None = None,
    ) -> str:
        """Create a profile picture from an image. Shape: circle, square, or rounded.

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side)).resize((size, size), Image.LANCZOS)

        if shape == "circle":
            img = img.convert("RGBA")
            mask = Image.new("L", (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse([(0, 0), (size, size)], fill=255)
            result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            result.paste(img, mask=mask)
        elif shape == "rounded":
            img = img.convert("RGBA")
            mask = Image.new("L", (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([(0, 0), (size, size)], radius=size // 8, fill=255)
            result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            result.paste(img, mask=mask)
        else:
            result = img

        ext = ".png" if shape in ("circle", "rounded") else None
        out = output_path or auto_output_path(file_path, f"profile_{shape}_{size}", ext)
        save_image(result, out)
        return f"Profile picture ({shape}, {size}x{size}). Saved to {out}"

    @mcp.tool()
    async def blur_image(
        file_path: str,
        radius: float = 5.0,
        output_path: str | None = None,
    ) -> str:
        """Apply Gaussian blur to an image.

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        result = img.filter(ImageFilter.GaussianBlur(radius=radius))
        out = output_path or auto_output_path(file_path, f"blur_{int(radius)}")
        save_image(result, out)
        return f"Applied blur (radius={radius}). Saved to {out}"

    @mcp.tool()
    async def adjust_image(
        file_path: str,
        brightness: float = 1.0,
        contrast: float = 1.0,
        sharpness: float = 1.0,
        saturation: float = 1.0,
        output_path: str | None = None,
    ) -> str:
        """Adjust brightness, contrast, sharpness, and saturation. 1.0 = no change, >1 = increase, <1 = decrease.

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        if brightness != 1.0:
            img = ImageEnhance.Brightness(img).enhance(brightness)
        if contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(contrast)
        if sharpness != 1.0:
            img = ImageEnhance.Sharpness(img).enhance(sharpness)
        if saturation != 1.0:
            img = ImageEnhance.Color(img).enhance(saturation)

        adjustments = []
        if brightness != 1.0: adjustments.append(f"brightness={brightness}")
        if contrast != 1.0: adjustments.append(f"contrast={contrast}")
        if sharpness != 1.0: adjustments.append(f"sharpness={sharpness}")
        if saturation != 1.0: adjustments.append(f"saturation={saturation}")

        out = output_path or auto_output_path(file_path, "adjusted")
        save_image(img, out)
        return f"Adjusted {', '.join(adjustments) or 'no changes'}. Saved to {out}"

    @mcp.tool()
    async def add_watermark(
        file_path: str,
        text: str,
        opacity: float = 0.3,
        position: str = "center",
        font_size: int = 40,
        output_path: str | None = None,
    ) -> str:
        """Add a text watermark to an image. Position: center, bottom-right, or tiled.

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        img = img.convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
            except (OSError, IOError):
                font = ImageFont.load_default()

        alpha = int(255 * opacity)
        fill = (255, 255, 255, alpha)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

        if position == "tiled":
            for y in range(0, img.size[1], th + 60):
                for x in range(0, img.size[0], tw + 60):
                    draw.text((x, y), text, fill=fill, font=font)
        elif position == "bottom-right":
            x = img.size[0] - tw - 20
            y = img.size[1] - th - 20
            draw.text((x, y), text, fill=fill, font=font)
        else:  # center
            x = (img.size[0] - tw) // 2
            y = (img.size[1] - th) // 2
            draw.text((x, y), text, fill=fill, font=font)

        result = Image.alpha_composite(img, overlay)
        out = output_path or auto_output_path(file_path, "watermarked", ".png")
        save_image(result, out)
        return f"Watermark added ({position}). Saved to {out}"

    @mcp.tool()
    async def pixelate_image(
        file_path: str,
        pixel_size: int = 10,
        output_path: str | None = None,
    ) -> str:
        """Pixelate an image with a given pixel block size.

        Free tool — runs locally, no account needed.
        """
        img, _ = read_image(file_path)
        w, h = img.size
        small = img.resize((max(1, w // pixel_size), max(1, h // pixel_size)), Image.NEAREST)
        result = small.resize((w, h), Image.NEAREST)
        out = output_path or auto_output_path(file_path, f"pixelated_{pixel_size}")
        save_image(result, out)
        return f"Pixelated (block size={pixel_size}). Saved to {out}"

    @mcp.tool()
    async def get_image_info(file_path: str) -> str:
        """Get detailed information about an image: dimensions, format, file size, color mode, DPI.

        Free tool — runs locally, no account needed.
        """
        import os
        img, _ = read_image(file_path)
        file_size = os.path.getsize(file_path)
        w, h = img.size
        dpi = img.info.get("dpi", "unknown")
        megapixels = (w * h) / 1_000_000

        return (
            f"File: {os.path.basename(file_path)}\n"
            f"Dimensions: {w} x {h} ({megapixels:.1f} MP)\n"
            f"Format: {img.format or 'unknown'}\n"
            f"Color mode: {img.mode}\n"
            f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)\n"
            f"DPI: {dpi}\n"
            f"Aspect ratio: {w/h:.2f}:1"
        )
