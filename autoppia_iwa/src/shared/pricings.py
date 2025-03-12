pricing_dict = {
    "gpt-3.5-turbo-0125": {
        "input": 0.50 / 1_000_000,  # $0.50 per million tokens → $0.0000005 per token
        "output": 1.50 / 1_000_000,  # $1.50 per million tokens → $0.0000015 per token
    },
    "gpt-4.5-preview": {
        "input": 75.00 / 1_000_000,  # $75.00 per million tokens → $0.000075 per token
        "output": 150.00 / 1_000_000,  # $150.00 per million tokens → $0.000150 per token
    },
    "gpt-4.5-preview-2025-02-27": {
        "input": 75.00 / 1_000_000,  # $75.00 per million tokens → $0.000075 per token
        "output": 150.00 / 1_000_000,  # $150.00 per million tokens → $0.000150 per token
    },
    "gpt-4o": {
        "input": 2.50 / 1_000_000,  # $2.50 per million tokens → $0.0000025 per token
        "output": 10.00 / 1_000_000,  # $10.00 per million tokens → $0.000010 per token
    },
    "gpt-4o-2024-08-06": {
        "input": 2.50 / 1_000_000,  # $2.50 per million tokens → $0.0000025 per token
        "output": 10.00 / 1_000_000,  # $10.00 per million tokens → $0.000010 per token
    },
    "gpt-4o-audio-preview": {
        "input": 2.50 / 1_000_000,  # $2.50 per million tokens → $0.0000025 per token
        "output": 10.00 / 1_000_000,  # $10.00 per million tokens → $0.000010 per token
    },
    "gpt-4o-audio-preview-2024-12-17": {
        "input": 2.50 / 1_000_000,  # $2.50 per million tokens → $0.0000025 per token
        "output": 10.00 / 1_000_000,  # $10.00 per million tokens → $0.000010 per token
    },
    "gpt-4o-realtime-preview": {
        "input": 5.00 / 1_000_000,  # $5.00 per million tokens → $0.0000050 per token
        "output": 20.00 / 1_000_000,  # $20.00 per million tokens → $0.000020 per token
    },
    "gpt-4o-realtime-preview-2024-12-17": {
        "input": 5.00 / 1_000_000,  # $5.00 per million tokens → $0.0000050 per token
        "output": 20.00 / 1_000_000,  # $20.00 per million tokens → $0.000020 per token
    },
    "gpt-4o-mini": {
        "input": 0.15 / 1_000_000,  # $0.15 per million tokens → $0.00000015 per token
        "output": 0.60 / 1_000_000,  # $0.60 per million tokens → $0.00000060 per token
    },
    "gpt-4o-mini-2024-07-18": {
        "input": 0.15 / 1_000_000,  # $0.15 per million tokens → $0.00000015 per token
        "output": 0.60 / 1_000_000,  # $0.60 per million tokens → $0.00000060 per token
    },
    "gpt-4o-mini-audio-preview": {
        "input": 0.15 / 1_000_000,  # $0.15 per million tokens → $0.00000015 per token
        "output": 0.60 / 1_000_000,  # $0.60 per million tokens → $0.00000060 per token
    },
    "gpt-4o-mini-audio-preview-2024-12-17": {
        "input": 0.15 / 1_000_000,  # $0.15 per million tokens → $0.00000015 per token
        "output": 0.60 / 1_000_000,  # $0.60 per million tokens → $0.00000060 per token
    },
    "gpt-4o-mini-realtime-preview": {
        "input": 0.60 / 1_000_000,  # $0.60 per million tokens → $0.00000060 per token
        "output": 2.40 / 1_000_000,  # $2.40 per million tokens → $0.00000240 per token
    },
    "gpt-4o-mini-realtime-preview-2024-12-17": {
        "input": 0.60 / 1_000_000,  # $0.60 per million tokens → $0.00000060 per token
        "output": 2.40 / 1_000_000,  # $2.40 per million tokens → $0.00000240 per token
    },
    "o1": {
        "input": 15.00 / 1_000_000,  # $15.00 per million tokens → $0.000015 per token
        "output": 60.00 / 1_000_000,  # $60.00 per million tokens → $0.000060 per token
    },
    "o1-2024-12-17": {
        "input": 15.00 / 1_000_000,  # $15.00 per million tokens → $0.000015 per token
        "output": 60.00 / 1_000_000,  # $60.00 per million tokens → $0.000060 per token
    },
    "o3-mini": {
        "input": 1.10 / 1_000_000,  # $1.10 per million tokens → $0.00000110 per token
        "output": 4.40 / 1_000_000,  # $4.40 per million tokens → $0.00000440 per token
    },
    "o3-mini-2025-01-31": {
        "input": 1.10 / 1_000_000,  # $1.10 per million tokens → $0.00000110 per token
        "output": 4.40 / 1_000_000,  # $4.40 per million tokens → $0.00000440 per token
    },
    "o1-mini": {
        "input": 1.10 / 1_000_000,  # $1.10 per million tokens → $0.00000110 per token
        "output": 4.40 / 1_000_000,  # $4.40 per million tokens → $0.00000440 per token
    },
    "o1-mini-2024-09-12": {
        "input": 1.10 / 1_000_000,  # $1.10 per million tokens → $0.00000110 per token
        "output": 4.40 / 1_000_000,  # $4.40 per million tokens → $0.00000440 per token
    },
}
