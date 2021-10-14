import dataclasses
import os
import shutil
import uuid
from string import Template
from typing import Callable
from typing import Optional


def default_succeeded(exit_code: int) -> bool:
    return exit_code == 0


@dataclasses.dataclass
class Stage:
    name: str
    command: str
    fname: Optional[str] = None
    succeeded: Callable[[int], bool] = default_succeeded

    def render_command(self: "Stage", code: str, fcode: str, folder: str) -> str:
        if self.fname:
            dst_folder = os.path.join(folder, uuid.uuid4().hex)
            os.makedirs(dst_folder)
            dst = os.path.join(dst_folder, self.fname)
            shutil.copy(fcode, dst)
            fcode = dst

        return Template(self.command).substitute(
            fcode=fcode, code=code, dir=folder.rstrip(os.sep)
        )
