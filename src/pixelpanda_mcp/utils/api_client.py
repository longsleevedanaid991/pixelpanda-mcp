"""HTTP client for PixelPanda API calls (free + paid)."""

import os
import httpx
from .auth import get_token
from .image_io import get_content_type

API_URL = os.environ.get("PIXELPANDA_API_URL", "https://pixelpanda.ai")
TIMEOUT = 120.0  # AI processing can take a while


def _headers(auth: bool = False) -> dict:
    headers = {"Accept": "application/json"}
    if auth:
        token = get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
    return headers


async def post_image(endpoint: str, file_path: str, extra_fields: dict | None = None, auth: bool = False) -> dict:
    """Upload an image file to a PixelPanda API endpoint."""
    file_path = os.path.expanduser(file_path)
    content_type = get_content_type(file_path)
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    files = {"image": (filename, file_bytes, content_type)}
    data = extra_fields or {}

    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        resp = await client.post(
            f"{API_URL}{endpoint}",
            files=files,
            data=data,
            headers=_headers(auth),
        )

    if resp.status_code == 429:
        raise RuntimeError(
            "Free tier limit reached (3/day per tool). "
            "Get unlimited access at https://pixelpanda.ai/pricing"
        )
    if resp.status_code == 401:
        raise RuntimeError(
            "Invalid or missing API token. Check your PIXELPANDA_API_TOKEN."
        )
    if resp.status_code == 402:
        body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        raise RuntimeError(body.get("detail", "Insufficient credits. Top up at https://pixelpanda.ai/pricing"))

    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise RuntimeError(f"API error ({resp.status_code}): {detail}")

    return resp.json()


async def post_json(endpoint: str, data: dict, auth: bool = True) -> dict:
    """POST JSON to a PixelPanda API endpoint."""
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        resp = await client.post(
            f"{API_URL}{endpoint}",
            json=data,
            headers={**_headers(auth), "Content-Type": "application/json"},
        )

    if resp.status_code == 401:
        raise RuntimeError("Invalid or missing API token.")
    if resp.status_code == 402:
        body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        raise RuntimeError(body.get("detail", "Insufficient credits."))
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise RuntimeError(f"API error ({resp.status_code}): {detail}")

    return resp.json()


async def get_json(endpoint: str, auth: bool = True) -> dict:
    """GET JSON from a PixelPanda API endpoint."""
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        resp = await client.get(
            f"{API_URL}{endpoint}",
            headers=_headers(auth),
        )

    if resp.status_code == 401:
        raise RuntimeError("Invalid or missing API token.")
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise RuntimeError(f"API error ({resp.status_code}): {detail}")

    return resp.json()


async def download_file(url: str, output_path: str) -> str:
    """Download a file from a URL and save it to disk."""
    output_path = os.path.expanduser(output_path)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(resp.content)

    return output_path
