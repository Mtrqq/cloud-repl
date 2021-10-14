import asyncio
import traceback
from functools import partial
from typing import TYPE_CHECKING
from typing import Any
import logging

import pydantic
import websockets

from evalserver import messages as msg
from evalserver.eval import evaluate
from evalserver.eval import stages_count
from evalserver.settings import settings

if TYPE_CHECKING:
    from websockets.legacy.server import WebSocketServerProtocol


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evalserver")


async def on_stage_start(
    stage: str,
    ws: "WebSocketServerProtocol",
) -> None:
    await msg.send(ws, msg.StageStartedNotification(stage=stage))


async def on_stage_finish(
    stage: str,
    succeeded: bool,
    exit_code: int,
    ws: "WebSocketServerProtocol",
) -> None:
    await msg.send(
        ws,
        msg.StageFinishedNotification(
            stage=stage, succeeded=succeeded, exit_code=exit_code
        ),
    )


async def on_output_ready(
    stage: str,
    output: str,
    ws: "WebSocketServerProtocol",
) -> None:
    if len(output) != 0:
        await msg.send(
            ws,
            msg.ExecutionOutputNotification(
                stage=stage,
                output=output,
            ),
        )


async def handler(ws: "WebSocketServerProtocol", _: Any) -> None:
    logger.info("Connected client with id - %s", ws.id)
    while True:
        try:
            logger.info("Waiting for evaluation request")
            code: str = (await msg.recv_as(ws, msg.StartExecutionRequest)).code
            logger.debug("Got code %s from %s", code, ws.id)
            await msg.send(
                ws, msg.ExecutionStartedResponse(stages=stages_count(settings.LANG))
            )
            execution_task = asyncio.Task(
                evaluate(
                    lang=settings.LANG,
                    code=code,
                    on_start=partial(on_stage_start, ws=ws),
                    on_finished=partial(on_stage_finish, ws=ws),
                    on_output=partial(on_output_ready, ws=ws),
                )
            )
            logger.info("Evaluation started")
            succeeded, exit_code = await execution_task
            logger.info(
                "Evaluation finished with status - %s",
                "success" if succeeded else "failure",
            )
            await msg.send(
                ws,
                msg.ExecutionFinishedNotification(
                    succeeded=succeeded, exit_code=exit_code
                ),
            )
        except pydantic.ValidationError:
            await msg.send(
                ws,
                msg.ExecutionFailedResponse(
                    detail="Validation failed", traceback=traceback.format_exc()
                ),
            )
            logger.exception("Validation failed for client - %s", ws.id)
        except Exception:
            await msg.send(
                ws,
                msg.ExecutionFailedResponse(
                    detail="Execution failed", traceback=traceback.format_exc()
                ),
            )
            logger.exception("Execution failed for client - %s", ws.id)


async def main() -> None:
    async with websockets.serve(  # type: ignore
        handler,
        "0.0.0.0",  # noqa: S104
        settings.PORT,
        compression=None,
    ):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
