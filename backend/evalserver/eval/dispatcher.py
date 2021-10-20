from typing import Dict
from typing import List

from .evaluator import Evaluator
from .evaluator import make_evaluator
from .stage import Stage

DISPATCHER: Dict[str, List[Stage]] = {
    "python": [Stage("running", "python -u ${fcode}", "code.py")],
    "rust": [
        Stage("compiling", "rustc ${fcode} -C opt-level=3 -o ${dir}/exec", "code.rst"),
        Stage("running", "${dir}/exec"),
    ],
    "nodejs": [Stage("running", "node ${fcode}", "code.js")],
}


def get_evaluator(lang: str) -> Evaluator:
    try:
        return make_evaluator(DISPATCHER[lang.lower()])
    except KeyError:
        raise RuntimeError(f"Language {lang} is not registered for evaluation")


def stages_count(lang: str) -> int:
    try:
        return len(DISPATCHER[lang.lower()])
    except KeyError:
        raise RuntimeError(f"Language {lang} is not registered for evaluation")
