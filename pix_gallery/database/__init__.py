from tortoise import Tortoise

from ..utils import config


async def init_db():
    await Tortoise.init(
        db_url=config.data.db_url,
        modules={
            "models": [
                "pix_gallery.database.models.pix_gallery",
                "pix_gallery.database.models.pix_keyword",
            ]
        },
        timezone="Asia/Shanghai",
    )
    await Tortoise.generate_schemas()
