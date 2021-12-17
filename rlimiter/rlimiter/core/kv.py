import redis as _redis

from rlimiter.settings import settings

rediskv = _redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
