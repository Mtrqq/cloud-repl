import asyncio
import logging
import traceback
from functools import partial
from typing import TYPE_CHECKING
from typing import Any

import pydantic
import websockets

from evalserver import messages as msg
from evalserver.core import evaluate
from evalserver.core import get_stages_count
from evalserver.core.rlimits import is_request_allowed
from evalserver.settings import settings

if TYPE_CHECKING:
    from websockets.legacy.server import WebSocketServerProtocol


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


async def acquire_execution_request(
    ws: "WebSocketServerProtocol",
) -> msg.StartExecutionRequest:
    logger.info("Waiting for evaluation request")
    while True:
        try:
            request = await msg.recv_as(ws, msg.StartExecutionRequest)
            logger.debug("Got execution request %s from %s", request, ws.id)
            return request
        except pydantic.ValidationError:
            await msg.send(
                ws,
                msg.ExecutionFailedResponse(
                    detail="Validation failed", traceback=traceback.format_exc()
                ),
            )
            logger.exception("Validation failed for client - %s", ws.id)
            continue


async def evaluate_request(
    ws: "WebSocketServerProtocol",
    request: msg.StartExecutionRequest,
) -> None:
    try:
        startn = msg.ExecutionStartedResponse(stages=get_stages_count(settings.lang))
        execution_task = evaluate(
            lang=settings.lang,
            code=request.code,
            on_start=partial(on_stage_start, ws=ws),
            on_finished=partial(on_stage_finish, ws=ws),
            on_output=partial(on_output_ready, ws=ws),
        )
        await msg.send(ws, message=startn)
        logger.info(f"Evaluation for {ws.id} started")
        success, excode = await asyncio.wait_for(
            execution_task, timeout=settings.timeout
        )
        logger.info(f"Evaluation for {ws.id} finished")
        await msg.send(
            ws, msg.ExecutionFinishedNotification(succeeded=success, exit_code=excode)
        )
    except asyncio.TimeoutError:
        await msg.send(
            ws,
            msg.ExecutionFailedResponse(detail="Request timed out", traceback=""),
        )
        logger.error(f"Request for {ws.id} timed out")


async def evaluation_handler(ws: "WebSocketServerProtocol", _: Any) -> None:
    logger.info("Connected client with id - %s", ws.id)
    while True:
        try:
            request = await acquire_execution_request(ws)
            if not is_request_allowed(ws.host):
                await msg.send(
                    ws,
                    msg.ExecutionFailedResponse(
                        detail="Too many requests", traceback=""
                    ),
                )
                logger.debug("Canceling request due to too many requests")
                continue
            await evaluate_request(ws, request)
        except Exception:
            await msg.send(
                ws,
                msg.ExecutionFailedResponse(
                    detail="Execution failed", traceback=traceback.format_exc()
                ),
            )
            logger.exception("Execution failed for client - %s", ws.id)


async def serve_forever() -> None:
    async with websockets.serve(  # type: ignore
        evaluation_handler,
        settings.host,
        settings.port,
        compression=None,
    ):
        await asyncio.Future()


def main() -> None:
    main_coro = serve_forever()
    try:
        asyncio.run(main_coro)
    except KeyboardInterrupt:
        logger.info("Exit requested by user")


if __name__ == "__main__":
    main()
