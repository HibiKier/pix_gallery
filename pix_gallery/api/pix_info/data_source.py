import asyncio

from tortoise.expressions import Q

from ...config import KwType
from ...database.models.pix_gallery import PixGallery
from ...database.models.pix_keyword import PixKeyword
from .models import ImageCount, KeywordItem


class InfoManage:
    @classmethod
    async def get_seek_info(cls, seek_type: KwType | None) -> list[KeywordItem]:
        """获取收录数据

        参数:
            seek_type: 类型

        返回:
            BuildImage: 图片
        """
        query = PixKeyword
        if seek_type:
            query = query.filter(kw_type=seek_type)
        result = await query.annotate().values(
            "id", "content", "kw_type", "handle_type", "seek_count"
        )
        return [
            KeywordItem(
                id=r["id"],
                content=r["content"],
                kw_type=r["kw_type"],
                handle_type=r["handle_type"],
                seek_count=r["seek_count"],
            )
            for r in result
        ]

    @classmethod
    async def get_pix_gallery(cls, tags: list[str] | None) -> ImageCount:
        """查看pix图库

        参数:
            tags: tags列表

        返回:
            BuildImage: 图片
        """
        query = PixGallery.filter(block_level__isnull=True)
        if tags:
            for tag in tags:
                query = query.filter(
                    Q(tags__icontains=tag)
                    | Q(author__icontains=tag)
                    | Q(pid__icontains=tag)
                    | Q(uid__icontains=tag)
                    | Q(title__icontains=tag)
                )
        result = await asyncio.gather(
            *[
                query.annotate().count(),
                query.filter(nsfw_tag__not=2).annotate().count(),
                query.filter(nsfw_tag=2).annotate().count(),
                query.filter(is_ai=True).annotate().count(),
            ]
        )
        return ImageCount(
            count=result[0], normal=result[1], r18=result[2], ai=result[3]
        )
