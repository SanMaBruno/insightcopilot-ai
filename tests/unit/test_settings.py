from src.shared.config.settings import Settings


def test_settings_defaults() -> None:
    s = Settings(app_env="test", log_level="DEBUG")
    assert s.app_env == "test"
    assert s.log_level == "DEBUG"
    assert s.llm_mode == "mock"
    assert s.embedding_mode == "mock"
    assert s.gemini_api_key == ""
    assert s.gemini_model == "gemini-2.0-flash"
    assert s.ollama_base_url == "http://localhost:11434"
    assert s.ollama_model == "llama3.2"
