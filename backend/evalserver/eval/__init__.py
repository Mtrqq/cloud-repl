__all__ = [
    "evaluate",
    "stages_count",
    "StageStartedCallback",
    "StageFinishedCallback",
    "StdoutUpdateCallback",
]

from typing import Tuple

from .dispatcher import get_evaluator
from .dispatcher import stages_count
from .evaluator import StageFinishedCallback
from .evaluator import StageStartedCallback
from .evaluator import StdoutUpdateCallback


async def evaluate(
    lang: str,
    code: str,
    on_start: StageStartedCallback,
    on_finished: StageFinishedCallback,
    on_output: StdoutUpdateCallback,
) -> Tuple[bool, int]:
    evaluator = get_evaluator(lang)
    return await evaluator(
        code,
        on_start,
        on_finished,
        on_output,
    )
