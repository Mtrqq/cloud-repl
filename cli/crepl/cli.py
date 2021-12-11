import argparse
import os
from typing import Any
from typing import Dict
from typing import Optional

import pydantic

from crepl.settings import settings

EXT_MAPPING = {".py": "python", ".rs": "rust", ".js": "nodejs"}


class Arguments(pydantic.BaseModel):
    file: pydantic.FilePath
    language: str
    base_url: str

    @pydantic.validator("language", pre=True)
    def validate_language(
        cls: "Arguments", value: Optional[str], values: Dict[str, Any]  # noqa: N805
    ) -> str:
        if value is not None:
            return value

        ext = os.path.splitext(values["file"])[-1]
        if ext in EXT_MAPPING:
            return EXT_MAPPING[ext]

        raise ValueError(
            f"File extension is not registered ({ext}), specify language explicitly or change file name"
        )

    @property
    def code(self: "Arguments") -> str:
        with open(self.file) as fobj:
            return fobj.read()


def _existing_file(path: str) -> str:
    if not os.path.exists(path):
        raise ValueError("File does not exists")

    return path


def cmdline_arguments() -> Arguments:
    parser = argparse.ArgumentParser("crepl")

    parser.add_argument("file", type=_existing_file)
    parser.add_argument(
        "--lang", "-l", choices=settings.AVAILABLE_LANGUAGES, default=None
    )
    parser.add_argument(
        "--base-url", default=settings.DEFAULT_BASE_URL, dest="base_url"
    )

    args = parser.parse_args()

    return Arguments(
        file=args.file,
        language=args.lang,
        base_url=args.base_url,
    )
