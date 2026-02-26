"""Web utilities for HTML cleaning and processing."""

import contextlib

from bs4 import BeautifulSoup, Comment

# ============================================================================
# HTML CLEANING HELPERS
# ============================================================================


def _parse_html_soup(html_content: str) -> BeautifulSoup | None:
    """Parse HTML content into BeautifulSoup object."""
    try:
        return BeautifulSoup(html_content, "html.parser")
    except Exception:
        return None


def _remove_script_and_style_tags(soup: BeautifulSoup) -> None:
    """Remove scripts, styles, metas, links, and noscript tags."""
    try:
        for tag in soup(["script", "style", "noscript", "meta", "link"]):
            with contextlib.suppress(Exception):
                tag.decompose()
    except Exception:
        pass


def _remove_html_comments(soup: BeautifulSoup) -> None:
    """Remove HTML comments from the soup."""
    try:
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            with contextlib.suppress(Exception):
                comment.extract()
    except Exception:
        pass


def _is_hidden_by_style(tag) -> bool:
    """Check if tag is hidden by style attribute."""
    if not tag.has_attr("style") or not tag["style"]:
        return False
    try:
        style_lc = tag["style"].lower()
        return "display: none" in style_lc or "visibility: hidden" in style_lc
    except Exception:
        return False


def _remove_hidden_tag(tag) -> None:
    """Remove a hidden tag."""
    with contextlib.suppress(Exception):
        tag.decompose()


def _remove_inline_attributes(tag) -> None:
    """Remove inline event handlers and style/id/class attributes."""
    try:
        attrs_to_remove = []
        for attr in tag.attrs:
            if attr.startswith("on") or attr in ["class", "id", "style"]:
                attrs_to_remove.append(attr)
        for attr in attrs_to_remove:
            with contextlib.suppress(Exception):
                del tag[attr]
    except Exception:
        pass


def _process_tag_for_cleaning(tag) -> None:
    """Process a single tag to remove hidden elements and inline attributes."""
    try:
        if _is_hidden_by_style(tag):
            _remove_hidden_tag(tag)
            return
        if tag.has_attr("hidden"):
            _remove_hidden_tag(tag)
            return
        _remove_inline_attributes(tag)
    except Exception:
        pass


def _remove_hidden_elements_and_events(soup: BeautifulSoup) -> None:
    """Remove hidden elements and inline event handlers."""
    try:
        for tag in soup.find_all(True):
            _process_tag_for_cleaning(tag)
    except Exception:
        pass


def _is_empty_tag(tag) -> bool:
    """Check if a tag is empty (no text and no children)."""
    try:
        return not tag.text.strip() and not tag.find_all()
    except Exception:
        return False


def _remove_empty_tags(soup: BeautifulSoup) -> None:
    """Remove empty tags from the soup."""
    try:
        for tag in soup.find_all():
            if _is_empty_tag(tag):
                with contextlib.suppress(Exception):
                    tag.decompose()
    except Exception:
        pass


def _get_cleaned_html(soup: BeautifulSoup) -> str:
    """Get the cleaned HTML string from the soup."""
    try:
        clean_soup = soup.body if soup.body else soup
        return clean_soup.prettify()
    except Exception:
        return ""


# ============================================================================
# HTML CLEANING FUNCTION
# ============================================================================


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
    soup = _parse_html_soup(html_content)
    if not soup:
        return ""

    _remove_script_and_style_tags(soup)
    _remove_html_comments(soup)
    _remove_hidden_elements_and_events(soup)
    _remove_empty_tags(soup)

    return _get_cleaned_html(soup)


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
