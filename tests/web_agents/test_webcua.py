"""Import and export checks for web_agents.cua.webcua (protocol definitions)."""


def test_webcua_module_import_and_aliases() -> None:
    from autoppia_iwa.src.web_agents.cua import webcua as m

    assert m.WebAgentSession is m.AsyncWebAgentSession
    assert m.WebAgentSyncSession is m.SyncWebAgentSession
    assert m.AsyncWebCUASession is m.AsyncWebAgentSession
    assert m.SyncWebCUASession is m.SyncWebAgentSession
    expected = {
        "AsyncWebAgentSession",
        "AsyncWebCUASession",
        "BrowserSnapshot",
        "ScoreDetails",
        "StepResult",
        "SyncWebAgentSession",
        "SyncWebCUASession",
        "WebAgentSession",
        "WebAgentSyncSession",
    }
    assert set(m.__all__) == expected
