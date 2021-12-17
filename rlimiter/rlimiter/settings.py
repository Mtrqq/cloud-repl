from pydantic import BaseSettings, BaseConfig

from rlimiter.core.period import Period


class AppSettings(BaseSettings):
    redis_host: str
    redis_port: int
    limit: int
    period: Period = Period.MINUTE
    host: str = "0.0.0.0"
    port: int = 80

    class Config(BaseConfig):
        env_prefix = "RLIMITER_"


settings = AppSettings()
