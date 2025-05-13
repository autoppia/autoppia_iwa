from autoppia_iwa.src.demo_webs.projects.omnizone_3.data import PRODUCTS_DATA


def replace_products_placeholders(
    text: str,
) -> str:
    products_data: list = PRODUCTS_DATA
    if not isinstance(text, str) or not products_data:
        return text

    import random
    # import re

    # special_placeholders = {
    #     "<decade>": None,
    # }
    # all_placeholders = re.findall(r"<(\w+)>", text)
    #
    # if "decade" in all_placeholders:
    #     decades = set()
    #     for product in products_data:
    #         if "year" in product:
    #             decade = (product["year"] // 10) * 10
    #             decades.add(decade)
    #
    #     if decades:
    #         selected_decade = random.choice(list(decades))
    #         special_placeholders["<decade>"] = str(selected_decade // 10)
    #
    #         decade_products = [m for m in products_data if m.get("year", 0) >= selected_decade and m.get("year", 0) < selected_decade + 10]
    #         if decade_products:
    #             products_data = decade_products

    product = random.choice(products_data)

    # for placeholder, value in special_placeholders.items():
    #     if value and placeholder in text:
    #         text = text.replace(placeholder, value)

    for key, value in product.items():
        placeholder = f"<{key}>"
        if placeholder in text:
            text = text.replace(placeholder, random.choice(value)) if isinstance(value, list) and value else text.replace(placeholder, str(value))

    # if "<genre>" in text and product.get("genres"):
    #     text = text.replace("<genre>", random.choice(product["genres"]))

    if "<product_name>" in text:
        text = text.replace("<product>", product["title"])

    # if "<page_count>" in text:
    #     text = text.replace("<page_count>", str(product.get("page_count", 120)))

    # if "<authors>" in text:
    #     text = text.replace("<authors>", product["author"])

    # if "<author>" in text:
    #     director_field = product.get("author", "")
    #     if isinstance(director_field, str):
    #         authors = [name.strip() for name in director_field.split(",") if name.strip()]
    #         author_count = text.count("<author>")
    #
    #         for i in range(author_count):
    #             replacement = authors[i % len(authors)] if authors else ""
    #             text = text.replace("<author>", replacement, 1)

    return text
