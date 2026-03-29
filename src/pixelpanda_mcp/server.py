"""PixelPanda MCP Server — AI image processing tools."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "pixelpanda",
    instructions=(
        "PixelPanda provides image processing tools in three tiers:\n\n"
        "1. LOCAL TOOLS (free, no network): resize, crop, rotate, flip, grayscale, "
        "invert, round corners, border, compress, merge, convert, transparency, "
        "profile picture, blur, adjust, watermark, pixelate, image info.\n\n"
        "2. AI TOOLS (free, rate-limited): remove background, upscale (2x/4x), "
        "remove text, analyze image. These call the PixelPanda API — 3 free uses/day.\n\n"
        "3. PRO TOOLS (paid, needs PIXELPANDA_API_TOKEN): generate product photos, "
        "try-on, scenes, manage avatars/products, check jobs. "
        "1 credit per image. Get started at https://pixelpanda.ai/pricing"
    ),
)

# Register all tool modules
from .tools.local_image import register as register_local
from .tools.api_free import register as register_free
from .tools.api_paid import register as register_paid

register_local(mcp)
register_free(mcp)
register_paid(mcp)


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
