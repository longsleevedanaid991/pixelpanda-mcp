"""Paid API tools — require PIXELPANDA_API_TOKEN (Bearer auth)."""

import os
import base64
from ..utils import api_client
from ..utils.auth import require_token
from ..utils.image_io import get_content_type


def register(mcp):
    """Register paid API tools with the MCP server."""

    @mcp.tool()
    async def check_credits() -> str:
        """Check your PixelPanda credit balance and account info.

        Requires PIXELPANDA_API_TOKEN.
        """
        require_token()
        result = await api_client.get_json("/api/auth/me")
        return (
            f"Email: {result.get('email', '?')}\n"
            f"Credits: {result.get('credits', '?')}\n"
            f"Tier: {result.get('subscription_tier', 'free')}"
        )

    @mcp.tool()
    async def list_avatars() -> str:
        """List your saved AI avatars (for use in product photo generation).

        Requires PIXELPANDA_API_TOKEN.
        """
        require_token()
        result = await api_client.get_json("/api/v2/avatars")
        avatars = result if isinstance(result, list) else result.get("avatars", [])

        if not avatars:
            return "No saved avatars. Create one at https://pixelpanda.ai/dashboard?tab=avatar-builder"

        lines = [f"You have {len(avatars)} avatar(s):\n"]
        for a in avatars:
            lines.append(f"  - {a.get('name', 'Unnamed')} (uuid: {a.get('uuid', '?')}, gender: {a.get('gender', '?')})")
        return "\n".join(lines)

    @mcp.tool()
    async def list_products(category: str | None = None) -> str:
        """List your saved products in PixelPanda.

        Requires PIXELPANDA_API_TOKEN.
        """
        require_token()
        endpoint = "/api/v2/products"
        if category:
            endpoint += f"?category={category}"
        result = await api_client.get_json(endpoint)
        products = result if isinstance(result, list) else result.get("products", [])

        if not products:
            return "No saved products. Upload one with the upload_product tool."

        lines = [f"You have {len(products)} product(s):\n"]
        for p in products:
            lines.append(f"  - {p.get('name', 'Unnamed')} (uuid: {p.get('uuid', '?')}, category: {p.get('category', '?')})")
        return "\n".join(lines)

    @mcp.tool()
    async def upload_product(
        file_path: str,
        name: str | None = None,
        category: str | None = None,
    ) -> str:
        """Upload a product image to PixelPanda for use in AI photo generation.

        Requires PIXELPANDA_API_TOKEN. Categories: clothing, accessories, shoes, bags, jewelry, electronics, food, beauty, home, other.
        """
        require_token()
        file_path = os.path.expanduser(file_path)
        content_type = get_content_type(file_path)
        filename = os.path.basename(file_path)

        with open(file_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        data = {
            "image": b64,
            "filename": filename,
        }
        if name:
            data["name"] = name
        if category:
            data["category"] = category

        result = await api_client.post_json("/api/v2/products", data)
        return (
            f"Product uploaded!\n"
            f"UUID: {result.get('uuid', '?')}\n"
            f"Name: {result.get('name', filename)}\n"
            f"Category: {result.get('category', 'other')}"
        )

    @mcp.tool()
    async def generate_product_photo(
        avatar_uuid: str,
        product_uuid: str,
        num_outputs: int = 6,
        prompt: str | None = None,
    ) -> str:
        """Generate AI product photos with an avatar holding/using your product. 1 credit per image.

        Requires PIXELPANDA_API_TOKEN. Use list_avatars and list_products to get UUIDs.
        """
        require_token()
        data = {
            "avatar_uuid": avatar_uuid,
            "product_uuid": product_uuid,
            "num_outputs": num_outputs,
        }
        if prompt:
            data["prompt"] = prompt

        result = await api_client.post_json("/api/v2/generate/product-photo", data)
        job_id = result.get("job_id", "?")
        credits = result.get("credits_reserved", num_outputs)

        return (
            f"Product photo generation started!\n"
            f"Job ID: {job_id}\n"
            f"Credits reserved: {credits}\n"
            f"Images: {num_outputs}\n\n"
            f"Use check_job_status with job_id '{job_id}' to check progress."
        )

    @mcp.tool()
    async def generate_tryon(
        avatar_uuid: str,
        product_uuid: str,
        num_outputs: int = 6,
        prompt: str | None = None,
    ) -> str:
        """Generate AI try-on photos with an avatar wearing your product (clothing). 1 credit per image.

        Requires PIXELPANDA_API_TOKEN.
        """
        require_token()
        data = {
            "avatar_uuid": avatar_uuid,
            "product_uuid": product_uuid,
            "num_outputs": num_outputs,
        }
        if prompt:
            data["prompt"] = prompt

        result = await api_client.post_json("/api/v2/generate/tryon", data)
        job_id = result.get("job_id", "?")
        credits = result.get("credits_reserved", num_outputs)

        return (
            f"Try-on generation started!\n"
            f"Job ID: {job_id}\n"
            f"Credits reserved: {credits}\n\n"
            f"Use check_job_status with job_id '{job_id}' to check progress."
        )

    @mcp.tool()
    async def generate_scenes(
        product_uuid: str,
        num_scenes: int = 6,
        category: str | None = None,
    ) -> str:
        """Generate AI product scene photos (lifestyle, studio, detail shots). No avatar needed. 1 credit per scene.

        Requires PIXELPANDA_API_TOKEN.
        """
        require_token()
        data = {
            "product_uuid": product_uuid,
            "num_scenes": num_scenes,
        }
        if category:
            data["category"] = category

        result = await api_client.post_json("/api/v2/generate/scenes", data)
        job_id = result.get("job_id", "?")
        credits = result.get("credits_reserved", num_scenes)

        return (
            f"Scene generation started!\n"
            f"Job ID: {job_id}\n"
            f"Credits reserved: {credits}\n\n"
            f"Use check_job_status with job_id '{job_id}' to check progress."
        )

    @mcp.tool()
    async def check_job_status(job_id: str) -> str:
        """Check the status of an AI generation job. Returns progress and result URLs when complete.

        Requires PIXELPANDA_API_TOKEN.
        """
        require_token()
        result = await api_client.get_json(f"/api/v2/jobs/{job_id}")

        status = result.get("status", "unknown")
        lines = [f"Job {job_id}: {status}"]

        if status == "completed":
            results = result.get("results", [])
            credits_used = result.get("credits_used", "?")
            lines.append(f"Credits used: {credits_used}")
            lines.append(f"Generated {len(results)} image(s):")
            for r in results:
                scene = r.get("scene", "")
                url = r.get("url", "")
                lines.append(f"  - {scene}: {url}")
        elif status == "processing":
            progress = result.get("progress", {})
            completed = progress.get("completed", 0)
            total = progress.get("total", "?")
            lines.append(f"Progress: {completed}/{total}")
        elif status == "failed":
            error = result.get("error", "Unknown error")
            lines.append(f"Error: {error}")

        return "\n".join(lines)

    @mcp.tool()
    async def list_jobs(limit: int = 10) -> str:
        """List your recent AI generation jobs.

        Requires PIXELPANDA_API_TOKEN.
        """
        require_token()
        result = await api_client.get_json(f"/api/v2/jobs?limit={limit}")
        jobs = result if isinstance(result, list) else result.get("jobs", [])

        if not jobs:
            return "No jobs found."

        lines = [f"Recent jobs ({len(jobs)}):\n"]
        for j in jobs:
            lines.append(
                f"  {j.get('job_id', '?')} | {j.get('status', '?')} | "
                f"{j.get('created_at', '?')} | credits: {j.get('credits_used', '?')}"
            )
        return "\n".join(lines)

    @mcp.tool()
    async def upscale_image(
        image_url: str | None = None,
        file_path: str | None = None,
        scale: int = 4,
        quality: str = "balanced",
    ) -> str:
        """Upscale an image to higher resolution using AI.

        Provide either image_url (public URL) or file_path (local file).
        Scale: 2 (1 credit, fast), 4 (3 credits, recommended), 8 (5 credits, print-ready).
        Quality: fast (Real-ESRGAN), balanced (Clarity Upscaler), high (Clarity max).

        Requires PIXELPANDA_API_TOKEN.
        """
        require_token()

        data = {"scale": scale, "quality": quality}

        if file_path:
            file_path = os.path.expanduser(file_path)
            with open(file_path, "rb") as f:
                data["image_base64"] = base64.b64encode(f.read()).decode()
        elif image_url:
            data["image_url"] = image_url
        else:
            return "Error: provide either image_url or file_path"

        result = await api_client.post_json("/api/v2/upscale", data)

        details = result.get("details", {})
        width = details.get("width", "?")
        height = details.get("height", "?")

        return (
            f"Image upscaled {scale}x!\n"
            f"Result: {result.get('result_url', '?')}\n"
            f"Dimensions: {width} x {height}\n"
            f"Credits used: {result.get('credits_used', '?')}\n"
            f"Credits remaining: {result.get('credits_remaining', '?')}"
        )

    @mcp.tool()
    async def enhance_image(
        image_url: str | None = None,
        file_path: str | None = None,
    ) -> str:
        """Enhance, sharpen, and restore an image using multiple AI methods.

        Returns multiple variants (Clean Upscale, Face Enhance, AI Restore, Full Restore).
        Cost: 1 credit. Provide either image_url (public URL) or file_path (local file).

        Requires PIXELPANDA_API_TOKEN.
        """
        require_token()

        data = {}
        if file_path:
            file_path = os.path.expanduser(file_path)
            with open(file_path, "rb") as f:
                data["image_base64"] = base64.b64encode(f.read()).decode()
        elif image_url:
            data["image_url"] = image_url
        else:
            return "Error: provide either image_url or file_path"

        result = await api_client.post_json("/api/v2/enhance", data)

        details = result.get("details", {})
        variants = details.get("variants", [])

        lines = [
            f"Image enhanced! ({len(variants)} variant(s))\n",
            f"Best result: {result.get('result_url', '?')}\n",
        ]

        if variants:
            lines.append("All variants:")
            for v in variants:
                lines.append(f"  - {v.get('label', '?')}: {v.get('url', '?')}")

        lines.append(f"\nCredits used: {result.get('credits_used', '?')}")
        lines.append(f"Credits remaining: {result.get('credits_remaining', '?')}")

        return "\n".join(lines)
