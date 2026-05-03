import os
from pathlib import Path


def _load_dotenv_values() -> dict[str, str]:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")

    return values


_DOTENV_VALUES = _load_dotenv_values()


def _get_setting(name: str, default: str) -> str:
    return os.getenv(name, _DOTENV_VALUES.get(name, default))


class Settings:
    app_name = "Nail Salon Voice Assistant"
    database_url = _get_setting("DATABASE_URL", "sqlite:///./salon_assistant.db")
    ollama_base_url = _get_setting("OLLAMA_BASE_URL", "http://localhost:11434/api")
    ollama_model = _get_setting("OLLAMA_MODEL", "qwen3")
    salon_name = _get_setting("SALON_NAME", "the nail salon")
    twilio_forward_number = _get_setting("TWILIO_FORWARD_NUMBER", "")


settings = Settings()
