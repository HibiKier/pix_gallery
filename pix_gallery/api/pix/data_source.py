from tortoise.expressions import Q

from ...database.models.pix_gallery import PixGallery

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6;"
    " rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Referer": "https://www.pixiv.net/",
}


def random(query, limit: int = 1) -> str:
    query = f"{query.sql()} ORDER BY RANDOM() LIMIT {limit};"
    return query


class PixManage:
    @classmethod
    async def get_pix(
        cls, tags: list[str], num: int, nsfw_tag: int | None, is_ai: bool | None
    ) -> list[PixGallery]:
        """获取图片

        参数:
            tags: tags，包含uid和pid
            num: 数量

        返回:
            list[PixGallery]: 图片数据列表
        """
        query = PixGallery
        if nsfw_tag:
            query = query.filter(nsfw_tag=nsfw_tag)
        if is_ai:
            query = query.filter(is_ai=is_ai)
        for tag in tags:
            query = query.filter(
                Q(tags__contains=tag) | Q(author__contains=tag) | Q(pid__contains=tag)
            )
        return await PixGallery.raw(random(query.annotate(), num))  # type: ignore
