import uvicorn

from rlimiter.settings import settings
from rlimiter.app import create_app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
    )
