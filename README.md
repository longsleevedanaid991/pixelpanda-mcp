<!-- mcp-name: io.github.RyanKramer/pixelpanda-mcp -->
# PixelPanda MCP Server

AI image processing tools for Claude Desktop, Cursor, VS Code, and other MCP-compatible clients.

**33 tools** across three tiers — from free local image editing to AI-powered product photography.

## Install

```bash
# Using uv (recommended)
uvx pixelpanda-mcp

# Or pip
pip install pixelpanda-mcp
```

## Setup

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pixelpanda": {
      "command": "uvx",
      "args": ["pixelpanda-mcp"],
      "env": {
        "PIXELPANDA_API_TOKEN": "pk_live_your_token_here"
      }
    }
  }
}
```

### Cursor

Add to your MCP settings (Settings > MCP Servers):

```json
{
  "pixelpanda": {
    "command": "uvx",
    "args": ["pixelpanda-mcp"],
    "env": {
      "PIXELPANDA_API_TOKEN": "pk_live_your_token_here"
    }
  }
}
```

> The API token is **optional** — all local and free AI tools work without it. You only need a token for paid generation tools.

## Tools

### Local Tools (free, no account needed, runs offline)

| Tool | Description |
|------|-------------|
| `resize_image` | Resize with optional aspect ratio preservation |
| `crop_image` | Crop to specific pixel coordinates |
| `rotate_image` | Rotate by any degree |
| `flip_image` | Flip horizontal or vertical |
| `grayscale_image` | Convert to grayscale |
| `invert_image` | Invert colors (negative) |
| `round_corners` | Round corners with custom radius |
| `add_border` | Add solid color border |
| `compress_image` | Compress to JPEG/WebP with quality control |
| `merge_images` | Merge multiple images (horizontal/vertical/grid) |
| `convert_format` | Convert between PNG, JPEG, WebP, BMP, TIFF |
| `make_transparent` | Adjust image opacity |
| `create_profile_picture` | Circle/square/rounded profile picture |
| `blur_image` | Gaussian blur |
| `adjust_image` | Brightness, contrast, sharpness, saturation |
| `add_watermark` | Text watermark (center/corner/tiled) |
| `pixelate_image` | Pixelation effect |
| `get_image_info` | Dimensions, format, file size, DPI, color mode |

### AI Tools (free, 3 uses/day)

| Tool | Description |
|------|-------------|
| `remove_background` | AI background removal (transparent PNG) |
| `upscale_image` | AI upscaling 2x or 4x (Real-ESRGAN) |
| `remove_text` | AI text/watermark removal (OCR + inpainting) |
| `analyze_image` | AI image analysis (objects, colors, composition, quality) |

### Pro Tools (paid, 1 credit/image)

| Tool | Credits | Description |
|------|---------|-------------|
| `check_credits` | 0 | Check your credit balance |
| `list_avatars` | 0 | List your AI avatars |
| `list_products` | 0 | List your uploaded products |
| `upload_product` | 0 | Upload a product image |
| `generate_product_photo` | 1/image | AI product photos with avatar |
| `generate_tryon` | 1/image | AI try-on (avatar wearing product) |
| `generate_scenes` | 1/scene | AI product scenes (studio, lifestyle) |
| `check_job_status` | 0 | Check generation progress |
| `list_jobs` | 0 | List recent generation jobs |

## Pricing

- **Free**: All local tools + 3 AI tool uses/day
- **$5 one-time**: 200 credits for pro tools (no subscription)
- **$24/mo**: 1,125 credits/month + unlimited AI tools

Get your API token at [pixelpanda.ai/pricing](https://pixelpanda.ai/pricing)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PIXELPANDA_API_TOKEN` | For pro tools | Your API token (`pk_live_...`) |
| `PIXELPANDA_API_URL` | No | API base URL (default: `https://pixelpanda.ai`) |

## Examples

```
"Resize photo.jpg to 800px wide"
"Remove the background from product.png"
"Upscale this image 4x"
"Merge these 3 screenshots horizontally"
"Generate 6 product photos using avatar abc123 and product def456"
```

## License

MIT
