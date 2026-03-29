"""API token management for PixelPanda paid tools."""

import os

_SIGNUP_URL = "https://pixelpanda.ai/pricing"


def get_token() -> str | None:
    """Read PIXELPANDA_API_TOKEN from environment. Returns None if not set."""
    return os.environ.get("PIXELPANDA_API_TOKEN")


def require_token() -> str:
    """Get the API token or raise a clear error directing the user to sign up."""
    token = get_token()
    if not token:
        raise RuntimeError(
            "This tool requires a PixelPanda API token.\n\n"
            "1. Sign up or log in at https://pixelpanda.ai\n"
            "2. Go to your dashboard and copy your API token\n"
            f"3. Set the PIXELPANDA_API_TOKEN environment variable\n\n"
            f"Plans start at $5 for 200 credits: {_SIGNUP_URL}"
        )
    return token
