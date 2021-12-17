from fastapi import APIRouter
from fastapi import Response
from fastapi import status
import pydantic

from rlimiter.core.requests import consume_request, RequestsLimitReached

router = APIRouter()


class SuccessRequestSubmit(pydantic.BaseModel):
    left_requests: int


@router.post(
    "/rquotas/{identity}",
    responses={
        200: {
            "description": "Request successfully submitted",
            "model": SuccessRequestSubmit,
        },
        429: {"description": "Request cannot be created due to too many requests"},
    },
)
def create_request(identity: str):
    try:
        left = consume_request(identity)
        return SuccessRequestSubmit(left_requests=left)
    except RequestsLimitReached:
        return Response(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
