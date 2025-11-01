from __future__ import annotations

import re
from typing import Dict

import httpx
from bs4 import BeautifulSoup
from langchain.tools import tool


def _clean_text(text: str) -> str:
    """Collapse whitespace and trim boilerplate."""
    # Remove common boilerplate
    text = re.sub(r"\bApply for this job\b", "", text, flags=re.IGNORECASE)
    # Normalize whitespace/newlines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)  # at most 2 blank lines
    return text.strip()


def _extract_greenhouse_text(html: str) -> str:
    """Extract the main job description text; prefer #content if present."""
    soup = BeautifulSoup(html, "lxml")

    # Drop scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Preferred main container on Greenhouse
    node = soup.select_one("#content")

    # Fallbacks if #content is missing
    if not node:
        for sel in ("section#content", "section.content", "div.content", "main", "article", "body"):
            node = soup.select_one(sel)
            if node:
                break

    text = (node or soup).get_text(separator="\n", strip=True)
    return _clean_text(text)


def _fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; JobFetcher/1.0; +https://example.com)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-GB,en;q=0.9",
    }
    with httpx.Client(follow_redirects=True, timeout=httpx.Timeout(10.0)) as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.text


@tool("fetch_job", return_direct=False)
def fetch_greenhouse_job_text(url: str) -> str:
    """
    Fetch a Greenhouse job page and return the job description as plain text.

    Args:
        url: Full Greenhouse job URL (e.g., https://boards.greenhouse.io/<company>/jobs/<id>)

    Returns:
        str: Cleaned job description text.

    Raises:
        ValueError: If the URL is not a Greenhouse job link.
        httpx.HTTPError: On network/HTTP errors.
    """
    if "boards.greenhouse.io" not in url:
        raise ValueError("Only Greenhouse job URLs are supported by this tool.")
    html = _fetch_html(url)
    return _extract_greenhouse_text(html)


# Optional: allow calling this file directly for a quick manual test
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m tools.fetch_job https://boards.greenhouse.io/<company>/jobs/<id>")
        sys.exit(1)
    print(fetch_greenhouse_job_text.run(sys.argv[1]))
