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
                attrs_to_remove = [attr for attr in tag.attrs if attr.startswith("on") or attr in ["class", "id", "style"]]
                for attr in attrs_to_remove:
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


def generate_html_differences(html_list: list[str]) -> list[str]:
    """
    Generate a list of initial HTML followed by diffs between consecutive HTMLs.

    Used by JudgeBaseOnHTML test to analyze HTML changes between actions.

    Args:
        html_list: List of HTML strings from different browser states

    Returns:
        List with first HTML + diffs between consecutive states
    """
    import difflib

    if not html_list:
        return []

    diffs = [html_list[0]]
    prev_html = html_list[0]

    for current_html in html_list[1:]:
        prev_lines = prev_html.splitlines(keepends=True)
        current_lines = current_html.splitlines(keepends=True)
        diff_generator = difflib.unified_diff(prev_lines, current_lines, lineterm="")
        diff_str = "".join(diff_generator)
        if diff_str:
            diffs.append(diff_str)
        prev_html = current_html

    return diffs
