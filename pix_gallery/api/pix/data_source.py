from pathlib import Path

from tortoise.expressions import Q

from zhenxun.utils.common_utils import SqlUtils
from zhenxun.utils.http_utils import AsyncHttpx
from zhenxun.configs.path_config import TEMP_PATH

from ..models.pix_gallery import PixGallery

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6;"
    " rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Referer": "https://www.pixiv.net/",
}


class PixManage:
    @classmethod
    async def get_pix(cls, tags: list[str], num: int) -> list[PixGallery]:
        """获取图片

        参数:
            tags: tags，包含uid和pid
            num: 数量

        返回:
            list[PixGallery]: 图片数据列表
        """
        query = PixGallery
        for tag in tags:
            query = query.filter(
                Q(tags__contains=tag) | Q(author__contains=tag) | Q(pid__contains=tag)
            )
        return await PixGallery.raw(SqlUtils.random(query.annotate(), num))  # type: ignore

    @classmethod
    async def get_image(cls, pix: PixGallery) -> Path | None:
        """获取图片

        参数:
            pix: PixGallery

        返回:
            Path | None: 图片路径
        """
        k = next(iter(pix.image_urls))
        img_url = pix.image_urls[k]
        file = TEMP_PATH / f"pix_{pix.pid}_{pix.img_p}_{pix.id}.png"
        return (
            file
            if await AsyncHttpx.download_file(img_url, file, headers=headers)
            else None
        )
