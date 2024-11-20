from fastapi import FastAPI

from pix_gallery.api import router
from pix_gallery.database import init_db
from pix_gallery.logger import logger  # noqa: F401
from pix_gallery.utils.utils import config

if __name__ == "__main__":
    import uvicorn

    from pix_gallery.auth import init_superuser_token

    if not config.token:
        config.data.token = init_superuser_token()
        config.save()

    app = FastAPI()

    app.include_router(router)

    @app.on_event("startup")
    async def startup_event():
        # 执行数据库连接操作
        await init_db()

    # asyncio.run(init_db())

    uvicorn.run(app, host="0.0.0.0", port=8000)
