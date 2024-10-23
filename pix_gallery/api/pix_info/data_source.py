from zhenxun.utils._build_image import BuildImage
from zhenxun.utils._image_template import ImageTemplate

from ..config import KwType
from ..models.pix_gallery import PixGallery
from ..models.pix_keyword import PixKeyword


class InfoManage:
    @classmethod
    async def get_seek_info(cls, seek_type: str | None) -> BuildImage:
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
        data_list = [
            [
                r["id"],
                r["content"],
                r["kw_type"],
                r["handle_type"],
                r["seek_count"],
            ]
            for r in result
        ]
        return await ImageTemplate.table_page(
            "PIX收录关键词",
            None,
            ["ID", "内容", "类型", "处理方式", "搜索次数"],
            data_list,
        )

    @classmethod
    async def get_pix_gallery(cls, tags: list[str]) -> BuildImage:
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
        return await ImageTemplate.table_page(
            "PIX图库",
            None,
            ["类型", "数量"],
            [
                ["总数", all_count],
                ["普通", count],
                ["R18", r18_count],
                ["AI", ai_count],
            ],
        )
