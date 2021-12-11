from typing import TYPE_CHECKING, Callable, Tuple, Union
import websockets
import json

import crepl.messages as msg

if TYPE_CHECKING:
    from websockets.legacy.client import WebSocketClientProtocol


async def _receive_stages_count(ws: "WebSocketClientProtocol") -> int:
    return (await msg.recv_as(ws, msg.ExecutionStartedResponse)).stages


async def _receive_stage_name(ws: "WebSocketClientProtocol") -> str:
    return (await msg.recv_as(ws, msg.StageStartedNotification)).stage


async def _wait_for_stage_finish(
    ws: "WebSocketClientProtocol", on_output: Callable[[str], None]
) -> msg.StageFinishedNotification:
    while True:
        message = json.loads(await ws.recv())
        if message["type"] == "ExecutionOutputNotification":
            on_output(msg.ExecutionOutputNotification.parse_obj(message).output)
        elif message["type"] == "StageFinishedNotification":
            return msg.StageFinishedNotification.parse_obj(message)
        else:
            raise RuntimeError("Got unexpected message", message)


def _get_success_label(success: bool) -> str:
    return "SUCCEEDED" if success else "FAILED"


def _format_stage_name(name: str, num: int, max: int) -> str:
    return f"{name.upper()} [{num}/{max}]"


async def execute_code(code: str, endpoint: str) -> None:
    print(endpoint)
    async with websockets.connect(endpoint) as ws:
        await msg.send(ws, msg.StartExecutionRequest(code=code))
        stages_count = await _receive_stages_count(ws)
        print(f"Starting execution with {stages_count} stages")
        for stage_num in range(1, stages_count + 1):
            stage_name = await _receive_stage_name(ws)
            fmt_name = _format_stage_name(stage_name, stage_num, stages_count)
            print(fmt_name, "- STARTED")
            fin_notification = await _wait_for_stage_finish(
                ws, on_output=lambda o: print(o, end="")
            )
            print(
                fmt_name,
                f"- FINISHED ({_get_success_label(fin_notification.succeeded)})",
            )

            if not fin_notification.succeeded:
                print("Finishing execution due to failure")

        finished = await msg.recv_as(ws, msg.ExecutionFinishedNotification)
        print(
            f"Execution result - {_get_success_label(finished.succeeded)}, last exit code - {finished.exit_code}"
        )
