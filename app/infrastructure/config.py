from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    session_file: Path = Field(
        default=Path(__file__).parent.parent.parent / "session.yaml"
    )

    xai_api_key: SecretStr
    xai_model: str = "grok-4.3"

    login: str
    password: str
    secret: str | None = None
