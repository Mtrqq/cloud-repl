import asyncio
import os
import shlex
import tempfile
import uuid
from asyncio.streams import StreamReader
from typing import Any
from typing import Callable
from typing import Coroutine
import logging
from typing import List
from typing import Tuple
from typing import cast

from evalserver.aio import wait_or_default

from .stage import Stage

StageStartedCallback = Callable[[str], Coroutine[None, None, Any]]
StageFinishedCallback = Callable[[str, bool, int], Coroutine[None, None, Any]]
StdoutUpdateCallback = Callable[[str, str], Coroutine[None, None, Any]]
Evaluator = Callable[
    [str, StageStartedCallback, StageFinishedCallback, StdoutUpdateCallback],
    Coroutine[None, None, Tuple[bool, int]],
]


logger = logging.getLogger("evalserver")


def prepare_code_file(code: str, folder: str) -> str:
    file: str = os.path.join(folder, uuid.uuid4().hex)
    with open(file, "w") as f:
        f.write(code)
    return file


def split_command(command: str) -> Tuple[str, List[str]]:
    tokens = shlex.split(command)
    return tokens[0], tokens[1:]


async def execute_stage(
    code: str,
    stage: Stage,
    folder: str,
    on_output: StdoutUpdateCallback,
) -> int:
    fcode = prepare_code_file(code, folder)
    program, args = split_command(
        stage.render_command(
            code=code,
            fcode=fcode,
            folder=folder,
        )
    )

    try:
        process = await asyncio.create_subprocess_exec(
            program,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        stdout: StreamReader = cast(StreamReader, process.stdout)
        async for stdout_line in stdout:
            logger.info("Got stdout line: %s", stdout_line)
            await on_output(stage.name, stdout_line.decode("utf-8"))

        return cast(int, await process.wait())
    except asyncio.CancelledError:
        process.kill()
        raise


def make_evaluator(stages: List[Stage]) -> Evaluator:
    async def evaluate(
        code: str,
        on_start: StageStartedCallback,
        on_finished: StageFinishedCallback,
        on_output: StdoutUpdateCallback,
    ) -> Tuple[bool, int]:
        exit_code, succeeded = None, None
        with tempfile.TemporaryDirectory() as tmp:
            for stage in stages:
                await on_start(stage.name)
                exit_code = await execute_stage(code, stage, tmp, on_output)
                succeeded = stage.succeeded(exit_code)
                await on_finished(stage.name, succeeded, exit_code)
                if not succeeded:
                    break

        if exit_code is None or succeeded is None:
            raise RuntimeError("Invalid evaluator configuration")

        return succeeded, exit_code

    return evaluate
