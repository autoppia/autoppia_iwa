"""Web utilities for HTML cleaning and processing."""

import contextlib

from bs4 import BeautifulSoup, Comment


def clean_html(html_content: str) -> str:
    """
    Removes scripts, styles, hidden tags, inline event handlers, etc.,
    returning a 'clean' version of the DOM.

    Used by test generation to create cleaner HTML for validation.
    This version is exception resistant.

    Args:
        html_content: Raw HTML string

    Returns:
        Cleaned HTML string with unnecessary elements removed
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")
    except Exception:
        return ""

    # Remove scripts, styles, metas, links, noscript
    try:
        for tag in soup(["script", "style", "noscript", "meta", "link"]):
            with contextlib.suppress(Exception):
                tag.decompose()
    except Exception:
        pass

    # Remove HTML comments
    try:
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            with contextlib.suppress(Exception):
                comment.extract()
    except Exception:
        pass

    # Remove hidden elements and inline events
    try:
        for tag in soup.find_all(True):
            try:
                if tag.has_attr("style") and tag["style"]:
                    try:
                        style_lc = tag["style"].lower()
                    except Exception:
                        style_lc = ""
                    if "display: none" in style_lc or "visibility: hidden" in style_lc:
                        with contextlib.suppress(Exception):
                            tag.decompose()
                        continue
                if tag.has_attr("hidden"):
                    with contextlib.suppress(Exception):
                        tag.decompose()
                    continue
                # Remove inline event handlers and style/id/class attributes
                for attr in list(tag.attrs):
                    if attr.startswith("on") or attr in ["class", "id", "style"]:
                        with contextlib.suppress(Exception):
                            del tag[attr]
            except Exception:
                pass
    except Exception:
        pass

    # Remove empty tags
    try:
        for tag in soup.find_all():
            try:
                if not tag.text.strip() and not tag.find_all():
                    tag.decompose()
            except Exception:
                pass
    except Exception:
        pass

    # Return the cleaned HTML
    try:
        clean_soup = soup.body if soup.body else soup
        return clean_soup.prettify()
    except Exception:
        return ""
