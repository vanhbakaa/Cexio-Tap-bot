from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    AUTO_TAP: dict = {
        "ENABLE": True,
        "RANDOM_TAPS_COUNT": [25, 75],
    }
    AUTO_CONVERT: bool = True
    MINIMUM_TO_CONVERT: float = 0.1
    AUTO_BUY_UPGRADE: bool = True
    AUTO_TASK: bool = False

    USE_PROXY_FROM_FILE: bool = False


settings = Settings()


