from loguru import logger
from tortoise import Tortoise

from ..utils.utils import config


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
                "pix_gallery.database.models.pid_search_log",
                "pix_gallery.database.models.set_request",
                "pix_gallery.database.models.star_users",
                "pix_gallery.database.models.star_log",
                "pix_gallery.database.models.tag_stat",
            ]
        },
        timezone="Asia/Shanghai",
    )
    await Tortoise.generate_schemas()
    logger.info("数据库初始化完成")
