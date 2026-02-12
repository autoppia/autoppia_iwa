from .data_utils import fetch_books_data


def login_replace_func(text: str, **kwargs) -> str:
    if not isinstance(text, str):
        return text

    replacements = {"<username>": "user<web_agent_id>", "<password>": "password123"}

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


def register_replace_func(text: str, **kwargs) -> str:
    if not isinstance(text, str):
        return text

    replacements = {"<username>": "newuser<web_agent_id>", "<email>": "newuser<web_agent_id>@gmail.com", "<password>": "password123"}

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


async def replace_book_placeholders(
    text: str,
    seed_value: int | None = None,
    dataset: list[dict] | dict | None = None,
    **kwargs,
) -> str:
    if not isinstance(text, str):
        return text

    if isinstance(dataset, dict):
        dataset = dataset.get("books", [])

    books_data = dataset if dataset is not None else await fetch_books_data(seed_value=seed_value)
    if not books_data:
        return text

    import random
    import re

    special_placeholders = {
        "<decade>": None,
    }
    all_placeholders = re.findall(r"<(\w+)>", text)

    if "decade" in all_placeholders:
        decades = set()
        for book in books_data:
            if "year" in book:
                decade = (book["year"] // 10) * 10
                decades.add(decade)

        if decades:
            selected_decade = random.choice(list(decades))
            special_placeholders["<decade>"] = str(selected_decade // 10)

            decade_books = [m for m in books_data if m.get("year", 0) >= selected_decade and m.get("year", 0) < selected_decade + 10]
            if decade_books:
                books_data = decade_books

    book = random.choice(books_data)

    for placeholder, value in special_placeholders.items():
        if value and placeholder in text:
            text = text.replace(placeholder, value)

    for key, value in book.items():
        placeholder = f"<{key}>"
        if placeholder in text:
            text = text.replace(placeholder, random.choice(value)) if isinstance(value, list) and value else text.replace(placeholder, str(value))

    if "<genre>" in text and book.get("genres"):
        text = text.replace("<genre>", random.choice(book["genres"]))

    if "<book>" in text:
        text = text.replace("<book>", book["name"])

    if "<page_count>" in text:
        text = text.replace("<page_count>", str(book.get("page_count", 120)))

    if "<authors>" in text:
        text = text.replace("<authors>", book["author"])

    if "<author>" in text:
        director_field = book.get("author", "")
        if isinstance(director_field, str):
            authors = [name.strip() for name in director_field.split(",") if name.strip()]
            author_count = text.count("<author>")

            for i in range(author_count):
                replacement = authors[i % len(authors)] if authors else ""
                text = text.replace("<author>", replacement, 1)

    text = login_replace_func(text=text)
    return text
