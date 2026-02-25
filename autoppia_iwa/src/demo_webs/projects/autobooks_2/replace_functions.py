import random
import re
from typing import Any

from .data_utils import fetch_data

# Constants for placeholder literals
AUTHOR_PLACEHOLDER = "<author>"


# =============================================================================
#                            HELPER FUNCTIONS
# =============================================================================

# --------------------------------------------------------------------- #
#  DECADE HANDLING
# --------------------------------------------------------------------- #


def _extract_decades(books_data: list[dict]) -> set[int]:
    """Extract unique decades from books data."""
    decades = set()
    for book in books_data:
        if "year" in book:
            decade = (book["year"] // 10) * 10
            decades.add(decade)
    return decades


def _filter_books_by_decade(books_data: list[dict], selected_decade: int) -> list[dict]:
    """Filter books that belong to the selected decade."""
    return [m for m in books_data if m.get("year", 0) >= selected_decade and m.get("year", 0) < selected_decade + 10]


def _process_decade_placeholder(text: str, books_data: list[dict]) -> tuple[str, list[dict], dict[str, str]]:
    """
    Process decade placeholder and filter books if needed.

    Returns:
        Tuple of (text, filtered_books_data, special_placeholders)
    """
    special_placeholders: dict[str, str] = {}
    all_placeholders = re.findall(r"<(\w+)>", text)

    if "decade" not in all_placeholders:
        return text, books_data, special_placeholders

    decades = _extract_decades(books_data)
    if not decades:
        return text, books_data, special_placeholders

    # Security Hotspot: random.choice is used for non-security purposes (test data generation)
    selected_decade = random.choice(list(decades))
    special_placeholders["<decade>"] = str(selected_decade // 10)

    decade_books = _filter_books_by_decade(books_data, selected_decade)
    if decade_books:
        books_data = decade_books

    return text, books_data, special_placeholders


# --------------------------------------------------------------------- #
#  PLACEHOLDER REPLACEMENT
# --------------------------------------------------------------------- #


def _replace_special_placeholders(text: str, special_placeholders: dict[str, str]) -> str:
    """Replace special placeholders (like decade) in text."""
    for placeholder, value in special_placeholders.items():
        if value and placeholder in text:
            text = text.replace(placeholder, value)
    return text


def _replace_book_field_placeholders(text: str, book: dict[str, Any]) -> str:
    """Replace generic book field placeholders in text."""
    for key, value in book.items():
        placeholder = f"<{key}>"
        if placeholder in text:
            # Security Hotspot: random.choice is used for non-security purposes (test data generation)
            text = text.replace(placeholder, random.choice(value) if isinstance(value, list) and value else str(value))
    return text


def _replace_genre_placeholder(text: str, book: dict[str, Any]) -> str:
    """Replace genre placeholder in text."""
    if "<genre>" in text and book.get("genres"):
        # Security Hotspot: random.choice is used for non-security purposes (test data generation)
        text = text.replace("<genre>", random.choice(book["genres"]))
    return text


def _replace_book_placeholder(text: str, book: dict[str, Any]) -> str:
    """Replace book name placeholder in text."""
    if "<book>" in text:
        text = text.replace("<book>", book["name"])
    return text


def _replace_page_count_placeholder(text: str, book: dict[str, Any]) -> str:
    """Replace page_count placeholder in text."""
    if "<page_count>" in text:
        text = text.replace("<page_count>", str(book.get("page_count", 120)))
    return text


def _replace_authors_placeholder(text: str, book: dict[str, Any]) -> str:
    """Replace authors placeholder in text."""
    if "<authors>" in text:
        text = text.replace("<authors>", book["author"])
    return text


def _replace_author_placeholder(text: str, book: dict[str, Any]) -> str:
    """Replace author placeholder(s) in text, handling multiple occurrences."""
    if AUTHOR_PLACEHOLDER not in text:
        return text

    director_field = book.get("author", "")
    if not isinstance(director_field, str):
        return text

    authors = [name.strip() for name in director_field.split(",") if name.strip()]
    author_count = text.count(AUTHOR_PLACEHOLDER)

    for i in range(author_count):
        replacement = authors[i % len(authors)] if authors else ""
        text = text.replace(AUTHOR_PLACEHOLDER, replacement, 1)

    return text


# =============================================================================
#                            MAIN FUNCTION
# =============================================================================


async def replace_book_placeholders(
    text: str,
    seed_value: int | None = None,
    dataset: list[dict] | None = None,
) -> str:
    """
    Replace book-related placeholders in text with actual values from books data.

    Args:
        text: Text containing placeholders like <book>, <author>, <genre>, etc.
        seed_value: Optional seed for fetching books data
        dataset: Optional pre-fetched books dataset

    Returns:
        Text with placeholders replaced by actual values
    """
    if not isinstance(text, str):
        return text

    books_data = dataset if dataset is not None else await fetch_data(seed_value=seed_value)
    if not books_data:
        return text

    # Process decade placeholder and filter books if needed
    text, books_data, special_placeholders = _process_decade_placeholder(text, books_data)

    # Security Hotspot: random.choice is used for non-security purposes (test data generation)
    book = random.choice(books_data)

    # Replace special placeholders (like decade)
    text = _replace_special_placeholders(text, special_placeholders)

    # Replace generic book field placeholders
    text = _replace_book_field_placeholders(text, book)

    # Replace specific placeholders
    text = _replace_genre_placeholder(text, book)
    text = _replace_book_placeholder(text, book)
    text = _replace_page_count_placeholder(text, book)
    text = _replace_authors_placeholder(text, book)
    text = _replace_author_placeholder(text, book)

    # Do NOT call login_replace_func here - credentials should remain as placeholders
    # They will be replaced during evaluation via TaskSolution.replace_credentials()
    return text
