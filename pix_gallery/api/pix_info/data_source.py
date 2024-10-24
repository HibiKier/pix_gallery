from ...config import KwType
from ...database.models.pix_gallery import PixGallery
from ...database.models.pix_keyword import PixKeyword
from .models import ImageCount, KeywordItem


class InfoManage:
    @classmethod
    async def get_seek_info(cls, seek_type: str | None) -> list[KeywordItem]:
        """获取收录数据

        参数:
            seek_type: 类型

        返回:
            BuildImage: 图片
        """
        query = PixKeyword
        if seek_type == "u":
            query = query.filter(kw_type=KwType.UID)
        if seek_type == "p":
            query = query.filter(kw_type=KwType.PID)
        if seek_type == "k":
            query = query.filter(kw_type=KwType.KEYWORD)
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
    async def get_pix_gallery(cls, tags: list[str]) -> ImageCount:
        """查看pix图库

        参数:
            tags: tags列表

        返回:
            BuildImage: 图片
        """
        query = PixGallery
        for tag in tags:
            query = query.filter(tags__contains=tag)
        all_count = await query.annotate().count()
        count = await query.filter(nsfw_tag__not=2).annotate().count()
        r18_count = await query.filter(nsfw_tag=2).annotate().count()
        ai_count = await query.filter(is_ai=True).annotate().count()
        return ImageCount(count=all_count, normal=count, r18=r18_count, ai=ai_count)
