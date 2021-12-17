import logging

from evalserver.app import main
from evalserver.settings import settings

logging.basicConfig(level=settings.log_level)

main()
