"""Static data and field-operator maps for autostats_15 constraint generation."""

from ..operators import (
    CONTAINS,
    EQUALS,
    GREATER_EQUAL,
    GREATER_THAN,
    LESS_EQUAL,
    LESS_THAN,
    NOT_EQUALS,
)

# Subnet names from web_15 shared/constants (Root = id 0, then these)
SUBNET_NAMES = [
    "Root",
    "Text Prompting",
    "Image Generation",
    "Data Scraping",
    "Compute",
    "Storage",
    "Prediction Markets",
    "Audio Generation",
    "Video Generation",
    "Translation",
    "Code Generation",
    "Social Media",
    "Gaming",
    "DeFi",
    "NFT Marketplace",
    "Identity",
    "Governance",
]

STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS]
NUMERIC_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL]

FIELD_OPERATORS_MAP_VIEW_SUBNET = {
    "subnet_name": STRING_OPERATORS,
    "emission": NUMERIC_OPERATORS,
    "price": NUMERIC_OPERATORS,
    "marketCap": NUMERIC_OPERATORS,
    "volume24h": NUMERIC_OPERATORS,
}

FIELD_OPERATORS_MAP_VIEW_VALIDATOR = {
    "hotkey": STRING_OPERATORS,
    "rank": NUMERIC_OPERATORS,
    "dominance": NUMERIC_OPERATORS,
    "nominatorCount": NUMERIC_OPERATORS,
    "totalWeight": NUMERIC_OPERATORS,
    "rootStake": NUMERIC_OPERATORS,
    "alphaStake": NUMERIC_OPERATORS,
    "commission": NUMERIC_OPERATORS,
}

FIELD_OPERATORS_MAP_VIEW_BLOCK = {
    "number": NUMERIC_OPERATORS,
    "hash": STRING_OPERATORS,
    "validator": STRING_OPERATORS,
    "epoch": NUMERIC_OPERATORS,
    "extrinsicsCount": NUMERIC_OPERATORS,
    "eventsCount": NUMERIC_OPERATORS,
}

FIELD_OPERATORS_MAP_VIEW_ACCOUNT = {
    "rank": NUMERIC_OPERATORS,
    "address": STRING_OPERATORS,
    "balance": NUMERIC_OPERATORS,
    "stakedAmount": NUMERIC_OPERATORS,
    "stakingRatio": NUMERIC_OPERATORS,
    "accountType": STRING_OPERATORS,
}

ACCOUNT_TYPES = ["validator", "nominator", "miner", "regular"]

FIELD_OPERATORS_MAP_EXECUTE_BUY = {
    "subnet_name": STRING_OPERATORS,
    "orderType": [EQUALS],
    "amountTAU": NUMERIC_OPERATORS,
    "amountAlpha": NUMERIC_OPERATORS,
    "priceImpact": NUMERIC_OPERATORS,
    "maxAvailableTAU": NUMERIC_OPERATORS,
}

FIELD_OPERATORS_MAP_EXECUTE_SELL = {
    "subnet_name": STRING_OPERATORS,
    "orderType": [EQUALS],
    "amountTAU": NUMERIC_OPERATORS,
    "amountAlpha": NUMERIC_OPERATORS,
    "priceImpact": NUMERIC_OPERATORS,
    "maxDelegatedAlpha": NUMERIC_OPERATORS,
}

# Fields to pick from when generating constraints (subset of FIELD_OPERATORS_MAP keys per use case)
SELECTED_FIELDS_VIEW_SUBNET = ["subnet_name", "emission", "price", "marketCap", "volume24h"]
SELECTED_FIELDS_VIEW_VALIDATOR = ["rank", "dominance", "totalWeight", "rootStake", "alphaStake", "commission"]
SELECTED_FIELDS_VIEW_BLOCK = ["number", "epoch", "extrinsicsCount", "eventsCount"]
SELECTED_FIELDS_VIEW_ACCOUNT = ["rank", "address", "balance", "stakedAmount", "accountType"]
SELECTED_FIELDS_EXECUTE_BUY = ["subnet_name", "amountTAU", "amountAlpha"]
SELECTED_FIELDS_EXECUTE_SELL = ["subnet_name", "amountAlpha", "maxDelegatedAlpha"]

# Fields whose constraint value must be integer (match FIELD_OPERATORS_MAP keys)
INTEGER_FIELDS_VIEW_VALIDATOR = {"rank", "nominatorCount"}
INTEGER_FIELDS_VIEW_BLOCK = {"number", "epoch", "extrinsicsCount", "eventsCount"}
INTEGER_FIELDS_VIEW_ACCOUNT = {"rank"}
INTEGER_FIELDS_EXECUTE_BUY = {"amountTAU", "amountAlpha", "maxAvailableTAU"}
INTEGER_FIELDS_EXECUTE_SELL = {"amountTAU", "amountAlpha", "maxDelegatedAlpha"}
