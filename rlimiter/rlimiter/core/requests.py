from rlimiter.core.kv import rediskv
from rlimiter.settings import settings


_NAMESPACE: str = "requests"


class RequestsLimitReached(RuntimeError):
    pass


def _make_key(key: str) -> str:
    return f"{_NAMESPACE}:{key}"


def _create_if_not_exists(identity: str) -> None:
    if not counter_exists(identity):
        rediskv.set(
            _make_key(identity),
            settings.limit,
            ex=settings.period.as_seconds(),
        )


def counter_exists(identity: str) -> int:
    return rediskv.exists(_make_key(identity))


def get_left_requests(identity: str) -> int:
    _create_if_not_exists(identity)
    return int(rediskv.get(_make_key(identity)))


def consume_request(identity: str) -> int:
    if get_left_requests(identity) <= 0:
        raise RequestsLimitReached("Too many requests")
    return rediskv.decr(_make_key(identity))
