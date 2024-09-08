from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    REF_LINK: str = "https://t.me/cexio_tap_bot?start=1716977635264001"

    AUTO_TAP: bool = False
    RANDOM_TAPS_COUNT: list = [25, 75]
    SLEEP_BETWEEN_TAPS: list = [25, 35]
    AUTO_CONVERT: bool = True
    MINIMUM_TO_CONVERT: float = 0.1
    AUTO_BUY_UPGRADE: bool = True
    WAIT_FOR_MOST_PROFITABLE_CARD: bool = True # Recommended to keep it True for high-level accounts
    AUTO_TASK: bool = True
    AUTO_CLAIM_SQUAD_BONUS: bool = False

    USE_PROXY_FROM_FILE: bool = False


settings = Settings()


