from typing import Tuple

import pydantic

_DEFAULT_LANGUAGES = ("python", "rust", "nodejs")


class AppSettings(pydantic.BaseSettings):
    AVAILABLE_LANGUAGES: Tuple[str, ...] = pydantic.Field(
        env="CREPL_LANGUAGES", default=_DEFAULT_LANGUAGES
    )
    DEFAULT_BASE_URL: str = pydantic.Field(
        env="CREPL_URL", default="ws://localhost/api"
    )


settings = AppSettings()
