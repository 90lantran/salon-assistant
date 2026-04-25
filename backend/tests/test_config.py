import importlib

from app.core import config


def test_load_dotenv_values_reads_backend_env_file(monkeypatch) -> None:
    monkeypatch.setattr(config.Path, "exists", lambda self: True)
    monkeypatch.setattr(
        config.Path,
        "read_text",
        lambda self: "\n# comment\nOLLAMA_MODEL=llama3.2\nDATABASE_URL=sqlite:///./test.db\n",
    )

    values = config._load_dotenv_values()

    assert values["OLLAMA_MODEL"] == "llama3.2"
    assert values["DATABASE_URL"] == "sqlite:///./test.db"


def test_get_setting_prefers_environment_over_dotenv(monkeypatch) -> None:
    monkeypatch.setenv("OLLAMA_MODEL", "env-model")
    monkeypatch.setattr(config, "_DOTENV_VALUES", {"OLLAMA_MODEL": "dotenv-model"})

    assert config._get_setting("OLLAMA_MODEL", "fallback-model") == "env-model"


def test_settings_use_dotenv_values_when_environment_is_missing(monkeypatch) -> None:
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(config.Path, "exists", lambda self: True)
    monkeypatch.setattr(
        config.Path,
        "read_text",
        lambda self: (
            "OLLAMA_MODEL=dotenv-model\n"
            "OLLAMA_BASE_URL=http://localhost:9999/api\n"
            "DATABASE_URL=sqlite:///./dotenv.db\n"
        ),
    )

    reloaded_config = importlib.reload(config)

    assert reloaded_config.settings.ollama_model == "dotenv-model"
    assert reloaded_config.settings.ollama_base_url == "http://localhost:9999/api"
    assert reloaded_config.settings.database_url == "sqlite:///./dotenv.db"
