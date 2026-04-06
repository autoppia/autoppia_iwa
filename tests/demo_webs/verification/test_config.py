from autoppia_iwa.src.demo_webs.web_verification.config import WebVerificationConfig


def test_web_verification_config_uses_env_default_base_url(monkeypatch):
    monkeypatch.setenv("IWAP_BASE_URL", "https://iwap.example.test")

    config = WebVerificationConfig(iwap_base_url=None, seed_values=None)

    assert config.iwap_base_url == "https://iwap.example.test"
    assert config.seed_values == [1, 50, 100, 200, 300]
    assert config.evaluate_trajectories is False
    assert config.evaluate_trajectories_only is False


def test_evaluate_trajectories_only_implies_evaluate_trajectories():
    cfg = WebVerificationConfig(evaluate_trajectories_only=True, seed_values=[1, 2])
    assert cfg.evaluate_trajectories is True
    assert cfg.evaluate_trajectories_only is True
