from fastapi import FastAPI


def create_app() -> FastAPI:
    from .api import router

    app = FastAPI(
        title="Requests Limiter",
        description="Service which allows to track and limit API usage using requests quotas",
    )
    app.include_router(router)

    return app
