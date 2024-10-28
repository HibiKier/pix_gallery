from loguru import logger
from tortoise import Tortoise

from ..utils import config


async def init_db():
    await Tortoise.init(
        db_url=config.data.db_url,
        modules={
            "models": [
                "pix_gallery.database.models.pix_gallery",
                "pix_gallery.database.models.pix_keyword",
                "pix_gallery.database.models.call_log",
                "pix_gallery.database.models.tag_log",
                "pix_gallery.database.models.token_console",
                "pix_gallery.database.models.token_console",
            ]
        },
        timezone="Asia/Shanghai",
    )
    await Tortoise.generate_schemas()
    logger.info("数据库初始化完成")
