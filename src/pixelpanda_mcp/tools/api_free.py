"""Free server-powered tools — no auth required, rate-limited (3/day per tool)."""

from ..utils import api_client
from ..utils.image_io import auto_output_path


def register(mcp):
    """Register free server-powered tools with the MCP server."""

    @mcp.tool()
    async def remove_background(
        file_path: str,
        output_path: str | None = None,
    ) -> str:
        """Remove the background from an image using AI. Returns a transparent PNG.

        Free tool — 3 uses/day without an account. Unlimited with a PixelPanda API token.
        """
        result = await api_client.post_image(
            "/api/free-tools/background-remover/generate",
            file_path,
        )

        image_url = result.get("image_url", "")
        remaining = result.get("remaining", "?")

        if not image_url:
            return "Background removal failed — no image returned."

        out = output_path or auto_output_path(file_path, "nobg", ".png")

        if image_url.startswith("data:"):
            # Base64 fallback
            import base64
            b64_data = image_url.split(",", 1)[1]
            with open(out, "wb") as f:
                f.write(base64.b64decode(b64_data))
        else:
            await api_client.download_file(image_url, out)

        return f"Background removed. Saved to {out}\nFree uses remaining today: {remaining}"

    @mcp.tool()
    async def upscale_image(
        file_path: str,
        scale: int = 2,
        output_path: str | None = None,
    ) -> str:
        """Upscale an image 2x or 4x using AI (Real-ESRGAN). Enhances resolution and sharpness.

        Free tool — 3 uses/day without an account. Unlimited with a PixelPanda API token.
        """
        if scale not in (2, 4):
            return "Scale must be 2 or 4."

        result = await api_client.post_image(
            "/api/free-tools/image-upscaler/generate",
            file_path,
            extra_fields={"scale": str(scale)},
        )

        image_url = result.get("image_url", "")
        remaining = result.get("remaining", "?")
        original_size = result.get("original_size", "?")
        new_size = result.get("new_size", "?")

        if not image_url:
            return "Upscaling failed — no image returned."

        out = output_path or auto_output_path(file_path, f"upscaled_{scale}x", ".png")

        if image_url.startswith("data:"):
            import base64
            b64_data = image_url.split(",", 1)[1]
            with open(out, "wb") as f:
                f.write(base64.b64decode(b64_data))
        else:
            await api_client.download_file(image_url, out)

        return f"Upscaled {scale}x: {original_size} -> {new_size}. Saved to {out}\nFree uses remaining today: {remaining}"

    @mcp.tool()
    async def remove_text(
        file_path: str,
        output_path: str | None = None,
    ) -> str:
        """Remove text and watermarks from an image using AI (OCR + inpainting).

        Free tool — 3 uses/day without an account. Unlimited with a PixelPanda API token.
        """
        result = await api_client.post_image(
            "/api/free-tools/text-remover/generate",
            file_path,
        )

        image_url = result.get("image_url", "")
        remaining = result.get("remaining", "?")

        if not image_url:
            return "Text removal failed — no image returned."

        out = output_path or auto_output_path(file_path, "text_removed", ".png")

        if image_url.startswith("data:"):
            import base64
            b64_data = image_url.split(",", 1)[1]
            with open(out, "wb") as f:
                f.write(base64.b64decode(b64_data))
        else:
            await api_client.download_file(image_url, out)

        return f"Text removed. Saved to {out}\nFree uses remaining today: {remaining}"

    @mcp.tool()
    async def analyze_image(file_path: str) -> str:
        """Analyze an image with AI — detect objects, colors, text, composition, quality, and mood.

        Free tool — 3 uses/day without an account. Unlimited with a PixelPanda API token.
        """
        result = await api_client.post_image(
            "/api/free-tools/image-analyzer/analyze",
            file_path,
        )

        analysis = result.get("analysis", {})
        metadata = result.get("image_metadata", {})
        remaining = result.get("remaining", "?")

        lines = [
            f"Image: {metadata.get('width', '?')}x{metadata.get('height', '?')} {metadata.get('format', '?')} ({metadata.get('file_size_kb', '?')} KB)",
            f"Description: {analysis.get('description', 'N/A')}",
        ]

        if analysis.get("objects"):
            lines.append(f"Objects: {', '.join(analysis['objects'][:10])}")
        if analysis.get("colors"):
            color_strs = [f"{c.get('name', '?')} ({c.get('hex', '?')}, {c.get('percentage', '?')}%)" for c in analysis["colors"][:5]]
            lines.append(f"Colors: {', '.join(color_strs)}")
        if analysis.get("text_detected"):
            lines.append(f"Text found: {', '.join(analysis['text_detected'][:5])}")
        if analysis.get("categories"):
            lines.append(f"Categories: {', '.join(analysis['categories'])}")
        if analysis.get("mood"):
            lines.append(f"Mood: {analysis['mood']}")

        comp = analysis.get("composition", {})
        if comp:
            lines.append(f"Composition: {comp.get('type', '?')}, {comp.get('lighting', '?')} lighting")

        quality = analysis.get("quality_assessment", {})
        if quality:
            lines.append(f"Quality: {quality.get('overall', '?')} (sharpness: {quality.get('sharpness', '?')}, exposure: {quality.get('exposure', '?')})")

        if analysis.get("suggested_uses"):
            lines.append(f"Suggested uses: {', '.join(analysis['suggested_uses'][:5])}")
        if analysis.get("accessibility_alt_text"):
            lines.append(f"Alt text: {analysis['accessibility_alt_text']}")

        lines.append(f"\nFree uses remaining today: {remaining}")

        return "\n".join(lines)
