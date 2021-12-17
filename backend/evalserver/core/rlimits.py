import logging

import requests

from evalserver.settings import settings

logger = logging.getLogger("evalserver")


BASE_ENDPOINT = f"{settings.rlimit_url}/api/v1/rquotas"


def is_request_allowed(identity: str) -> bool:
    resp = requests.post(f"{BASE_ENDPOINT}/{identity}")
    if resp.status_code == 200:
        return True
    elif resp.status_code == 429:
        logger.debug(f"User {identity} is out of requests")
        return False
    else:
        logger.error("Error while contacting quotas service")
        return False
