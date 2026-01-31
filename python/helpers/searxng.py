import os
import aiohttp
from python.helpers import runtime, errors, settings
from python.helpers.print_style import PrintStyle

DEFAULT_URL = "http://localhost:55510/search"


def _get_searxng_url() -> str:
    env_url = os.getenv("SEARXNG_URL")
    if env_url:
        return env_url

    if runtime.is_development():
        try:
            cfg = settings.get_settings()
            host = cfg.get("rfc_url") or "localhost"
            if "://" not in host:
                host = "http://" + host
            return host + ":55510/search"
        except Exception:
            return DEFAULT_URL

    return DEFAULT_URL

async def search(query:str):
    if runtime.is_development():
        try:
            return await runtime.call_development_function(_search, query=query)
        except Exception as e:
            # Fall back to local execution when RFC is not available in dev
            PrintStyle.warning(
                "RFC search unavailable, falling back to local SearXNG call: "
                + errors.error_text(e)
            )
            return await _search(query=query)
    return await _search(query=query)

async def _search(query:str):
    async with aiohttp.ClientSession() as session:
        url = _get_searxng_url()
        async with session.post(url, data={"q": query, "format": "json"}) as response:
            return await response.json()
