from pydantic import BaseConfig
from pydantic import BaseSettings
from pydantic import Field


class AppSettings(BaseSettings):
    lang: str
    timeout: int = 60

    host: str = "0.0.0.0"  # noqa: S104
    port: int = 80

    log_level: str = "INFO"

    rlimit_url: str = Field(env="RLIMITER_BASE_URL")

    class Config(BaseConfig):
        env_prefix = "EVAL_SERVER_"


settings = AppSettings()
