from pydantic import BaseConfig
from pydantic import BaseSettings


class AppSettings(BaseSettings):
    lang: str
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 80
    timeout: int = 60

    class Config(BaseConfig):
        env_prefix = "EVAL_SERVER_"


settings = AppSettings()
