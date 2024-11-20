from loguru import logger

from pix_gallery.config import KwHandleType, KwType
from pix_gallery.database.models.pix_gallery import PixGallery
from pix_gallery.database.models.set_request import SetRequest

from ...utils.utils import config
from .models import SetPixPost


class PixSetManage:
    @classmethod
    async def create_set_pix(cls, data: SetPixPost, token: str | None):
        logger.info(f"SetRequest 创建pix_set: {data}")
        model = await SetRequest.create(
            pix_id=data.id,
            kw_type=data.type,
            block_level=data.block_level,
            nsfw_tag=data.nsfw_tag,
            token=token,
        )
        if token == config.token:
            await cls.set_pix(model.id, KwHandleType.PASS)

    @classmethod
    async def set_pix(cls, id: int, handle_type: KwHandleType):
        req = await SetRequest.get_or_none(id=id)
        if not req:
            return f"SetRequest 当前id: {id} 不存在..."
        req.handle_type = handle_type
        if handle_type == KwHandleType.PASS:
            if req.kw_type == KwType.UID:
                if req.block_level is not None:
                    await PixGallery.filter(uid=req.pix_id).update(
                        block_level=req.block_level
                    )
            elif req.block_level is not None:
                if "-" in req.pix_id:
                    split = req.pix_id.split("-")
                    if split[1] == "all":
                        await PixGallery.filter(pid=split[0]).update(
                            block_level=req.block_level
                        )
                    else:
                        await PixGallery.filter(pid=split[0], img_p=split[1]).update(
                            block_level=req.block_level
                        )
                else:
                    await PixGallery.filter(pid=req.pix_id).update(
                        block_level=req.block_level
                    )
            elif req.nsfw_tag is not None:
                if "-" in req.pix_id:
                    split = req.pix_id.split("-")
                    await PixGallery.filter(pid=split[0], img_p=split[1]).update(
                        nsfw_tag=req.nsfw_tag
                    )
                else:
                    await PixGallery.filter(pid=req.pix_id).update(
                        nsfw_tag=req.nsfw_tag
                    )
            await req.save(update_fields=["handle_type"])
        return f"SetRequest 设置id: {id}:{handle_type} 成功"
