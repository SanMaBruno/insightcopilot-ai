from src.shared.config.settings import Settings


def test_settings_defaults() -> None:
    s = Settings(app_env="test", log_level="DEBUG")
    assert s.app_env == "test"
    assert s.log_level == "DEBUG"
