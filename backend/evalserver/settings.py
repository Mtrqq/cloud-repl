from pydantic import BaseSettings
from pydantic.fields import Field


class AppSettings(BaseSettings):
    LANG: str = Field(..., env="EVAL_LANGUAGE")
    PORT: str = Field(80, env="EVAL_SERVER_PORT")


settings = AppSettings()
