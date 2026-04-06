from ..operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS

FIELD_OPERATORS_MAP_PRODUCTS = {
    "title": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "brand": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "category": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "rating": [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL],
    "price": [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL],
}

# Visible fields for data-extraction use cases (product detail, search, filter, share, add-to-cart, add-to-wishlist)
VISIBLE_FIELDS_PRODUCT_DETAIL = ["name", "brand", "rating", "price", "category"]
VISIBLE_FIELDS_SEARCH_PRODUCT = ["name", "brand", "rating", "price", "category"]
VISIBLE_FIELDS_CATEGORY_FILTER = ["category", "name"]
