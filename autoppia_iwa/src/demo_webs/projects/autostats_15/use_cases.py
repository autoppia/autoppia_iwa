"""Autostats web_15 use cases for task generation and validation."""

from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    ExecuteBuyEvent,
    ExecuteSellEvent,
    ViewAccountEvent,
    ViewBlockEvent,
    ViewSubnetEvent,
    ViewValidatorEvent,
)
from .generation_functions import (
    generate_execute_buy_constraints,
    generate_execute_sell_constraints,
    generate_view_account_constraints,
    generate_view_block_constraints,
    generate_view_subnet_constraints,
    generate_view_validator_constraints,
)

STRICT_COPY_INSTRUCTION = "CRITICAL: Copy values EXACTLY as provided in the constraints. Do NOT correct typos, do NOT remove numbers, do NOT truncate or summarize strings."

VIEW_SUBNET_USE_CASE = UseCase(
    name="VIEW_SUBNET",
    description="The user viewed a subnet detail page (subnet name, emission, price, market cap, volume).",
    event=ViewSubnetEvent,
    event_source_code=ViewSubnetEvent.get_source_code_of_class(),
    constraints_generator=generate_view_subnet_constraints,
    additional_prompt_info=f"Use field names: subnet_name, emission, price, marketCap, volume24h. Format: 'View a subnet where <field> <operator> <value>'. {STRICT_COPY_INSTRUCTION}",
    examples=[
        {
            "prompt": "View a subnet where subnet_name equals 'Text Prompting' and marketCap greater_than 2000000000",
            "prompt_for_task_generation": "View a subnet where subnet_name equals 'Text Prompting' and marketCap greater_than 2000000000",
        },
        {
            "prompt": "View a subnet named 'Data Scraping' with market cap above 1 billion",
            "prompt_for_task_generation": "View a subnet where subnet_name equals 'Data Scraping' and marketCap greater_than 1000000000",
        },
    ],
)

VIEW_VALIDATOR_USE_CASE = UseCase(
    name="VIEW_VALIDATOR",
    description="The user viewed a validator detail page (hotkey, rank, dominance, stake, commission).",
    event=ViewValidatorEvent,
    event_source_code=ViewValidatorEvent.get_source_code_of_class(),
    constraints_generator=generate_view_validator_constraints,
    additional_prompt_info=f"Use field names: hotkey, rank, dominance, nominatorCount, totalWeight, rootStake, alphaStake, commission. Format: 'View a validator where <field> <operator> <value>'. {STRICT_COPY_INSTRUCTION}",
    examples=[
        {
            "prompt": "View a validator where dominance greater_than 2.3",
            "prompt_for_task_generation": "View a validator where dominance greater_than 2.3",
        },
        {
            "prompt": "View a validator with rank equals 1 and totalWeight greater_than 500000",
            "prompt_for_task_generation": "View a validator where rank equals 1 and totalWeight greater_than 500000",
        },
    ],
)

VIEW_BLOCK_USE_CASE = UseCase(
    name="VIEW_BLOCK",
    description="The user viewed a block detail page (block number, hash, validator, epoch, extrinsics, events).",
    event=ViewBlockEvent,
    event_source_code=ViewBlockEvent.get_source_code_of_class(),
    constraints_generator=generate_view_block_constraints,
    additional_prompt_info="Use field names: number, hash, validator, epoch, extrinsicsCount, eventsCount. Format: 'View block where <field> <operator> <value>'.",
    examples=[
        {
            "prompt": "View block where number equals 999991",
            "prompt_for_task_generation": "View block where number equals 999991",
        },
        {
            "prompt": "View block where extrinsicsCount greater_than 5",
            "prompt_for_task_generation": "View block where extrinsicsCount greater_than 5",
        },
    ],
)

VIEW_ACCOUNT_USE_CASE = UseCase(
    name="VIEW_ACCOUNT",
    description="The user viewed an account detail page (address, balance, staked amount, account type).",
    event=ViewAccountEvent,
    event_source_code=ViewAccountEvent.get_source_code_of_class(),
    constraints_generator=generate_view_account_constraints,
    additional_prompt_info=f"Use field names: rank, address, balance, stakedAmount, stakingRatio, accountType. Format: 'View account where <field> <operator> <value>'. {STRICT_COPY_INSTRUCTION}",
    examples=[
        {
            "prompt": "View account where accountType equals 'validator' and balance greater_than 100000",
            "prompt_for_task_generation": "View account where accountType equals 'validator' and balance greater_than 100000",
        },
        {
            "prompt": "View account where rank equals 1",
            "prompt_for_task_generation": "View account where rank equals 1",
        },
    ],
)

EXECUTE_BUY_USE_CASE = UseCase(
    name="EXECUTE_BUY",
    description="The user confirmed a market or limit buy order (amount TAU, amount Alpha, price impact).",
    event=ExecuteBuyEvent,
    event_source_code=ExecuteBuyEvent.get_source_code_of_class(),
    constraints_generator=generate_execute_buy_constraints,
    additional_prompt_info=(
        "Use field names: subnet_name, orderType, amountTAU, amountAlpha (numbers without quotes). "
        "Format: 'Buy X TAU in the <subnet_name> subnet' or 'Execute buy where subnet_name equals <name> and amountTAU equals <number>'. "
        f"Subnet names and numeric values must be copied exactly. {STRICT_COPY_INSTRUCTION}"
    ),
    examples=[
        {
            "prompt": "Buy 100 TAU in the Text Prompting subnet",
            "prompt_for_task_generation": "Execute buy where subnet_name equals 'Text Prompting' and amountTAU equals 100",
        },
        {
            "prompt": "Buy 50 alpha at market in Data Scraping",
            "prompt_for_task_generation": "Execute buy where subnet_name equals 'Data Scraping' and amountAlpha equals 50",
        },
        {
            "prompt": "Buy 10 TAU in the Image Generation subnet",
            "prompt_for_task_generation": "Execute buy where subnet_name equals 'Image Generation' and amountTAU equals 10",
        },
    ],
)

EXECUTE_SELL_USE_CASE = UseCase(
    name="EXECUTE_SELL",
    description="The user confirmed a market or limit sell order (amount TAU, amount Alpha, max delegated Alpha).",
    event=ExecuteSellEvent,
    event_source_code=ExecuteSellEvent.get_source_code_of_class(),
    constraints_generator=generate_execute_sell_constraints,
    additional_prompt_info=(
        "Use field names: subnet_name, orderType, amountAlpha, maxDelegatedAlpha (numbers without quotes). "
        "Format: 'Sell X alpha in the <subnet_name> subnet' or 'Execute sell where subnet_name equals <name> and amountAlpha equals <number>'. "
        f"Subnet names and numeric values must be copied exactly. {STRICT_COPY_INSTRUCTION}"
    ),
    examples=[
        {
            "prompt": "Sell 20 alpha in the Text Prompting subnet",
            "prompt_for_task_generation": "Execute sell where subnet_name equals 'Text Prompting' and amountAlpha equals 20",
        },
        {
            "prompt": "Sell 50 alpha in the Gaming subnet",
            "prompt_for_task_generation": "Execute sell where subnet_name equals 'Gaming' and amountAlpha equals 50",
        },
        {
            "prompt": "Sell 30 alpha in Data Scraping",
            "prompt_for_task_generation": "Execute sell where subnet_name equals 'Data Scraping' and amountAlpha equals 30",
        },
    ],
)

ALL_USE_CASES = [
    VIEW_SUBNET_USE_CASE,
    VIEW_VALIDATOR_USE_CASE,
    VIEW_BLOCK_USE_CASE,
    VIEW_ACCOUNT_USE_CASE,
    EXECUTE_BUY_USE_CASE,
    EXECUTE_SELL_USE_CASE,
]
