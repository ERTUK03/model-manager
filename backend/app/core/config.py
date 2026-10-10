from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Cała konfiguracja pochodzi ze zmiennych środowiskowych (lub lokalnego pliku .env).
    W kodzie nie ma żadnych adresów, haseł ani kluczy."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    # Lista adresów oddzielonych przecinkami. Puste = CORS wyłączony (ruch idzie przez proxy nginx)
    cors_origins: str = ""
    # SecretStr: wartość nie pojawia się w logach ani w repr().
    # Brak wartości domyślnej: aplikacja nie uruchomi się bez ustawionego DATABASE_URL
    database_url: SecretStr

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
