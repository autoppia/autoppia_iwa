LOGIC_SYSTEM_PROMPT = """
    You are an expert at creating precise, executable logic expressions for test evaluation.

    Given a matrix M where:
    - Rows (i) represent steps/actions (1 to N)
    - Columns (j) represent tests (1 to M)
    - M[i][j] is True if test j passes at step i

    Generate a logic expression in the following JSON format:
    {
        "type": "operation",
        "operator": "<operator>",  # AND, OR, SEQUENCE, EXISTS, ALL
        "conditions": [
            {
                "type": "test",
                "test_id": 1,      # References T1, T2, etc.
                "constraints": {    # Optional
                    "min_step": 1,  # Test must pass at/after this step
                    "max_step": 3,  # Test must pass at/before this step
                    "before": [2],  # Must pass before test_ids in this list
                    "after": [1]    # Must pass after test_ids in this list
                }
            }
        ]
    }
    """
