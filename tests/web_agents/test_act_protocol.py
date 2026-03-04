from autoppia_iwa.src.web_agents.act_protocol import ActExecutionMode, ActResponse


def test_act_response_accepts_canonical_actions() -> None:
    parsed = ActResponse.from_raw(
        {
            "protocol_version": "1.0",
            "execution_mode": "batch",
            "actions": [{"type": "DoneAction", "reason": "completed"}],
        }
    )

    assert parsed.protocol_version == "1.0"
    assert parsed.execution_mode == ActExecutionMode.BATCH
    assert parsed.actions == [{"type": "DoneAction", "reason": "completed"}]


def test_act_response_normalizes_tool_calls() -> None:
    parsed = ActResponse.from_raw(
        {
            "tool_calls": [
                {
                    "type": "function",
                    "function": {
                        "name": "request_user_input",
                        "arguments": '{"prompt": "Need OTP", "options": ["sms", "email"]}',
                    },
                }
            ]
        }
    )

    assert parsed.actions == [
        {
            "type": "request_user_input",
            "prompt": "Need OTP",
            "options": ["sms", "email"],
        }
    ]


def test_act_response_normalizes_report_result_tool_call() -> None:
    parsed = ActResponse.from_raw(
        {
            "tool_calls": [
                {
                    "type": "function",
                    "function": {
                        "name": "report_result",
                        "arguments": '{"content":"Portfolio is $120","success":true}',
                    },
                }
            ]
        }
    )

    assert parsed.actions == [{"type": "report_result", "content": "Portfolio is $120", "success": True}]


def test_act_response_supports_legacy_single_action_and_navigate_url() -> None:
    parsed_action = ActResponse.from_raw({"action": {"type": "DoneAction", "reason": "ok"}})
    parsed_nav = ActResponse.from_raw({"navigate_url": "/checkout"})

    assert parsed_action.actions == [{"type": "DoneAction", "reason": "ok"}]
    assert parsed_nav.actions == [{"type": "NavigateAction", "url": "/checkout"}]
