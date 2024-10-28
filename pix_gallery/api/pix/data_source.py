from loguru import logger
from tortoise.expressions import Q

from ...database.models.call_log import CallLog
from ...database.models.pix_gallery import PixGallery
from ...database.models.tag_log import TagLog

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
        cls,
        tags: list[str],
        num: int,
        nsfw_tag: list[int] | None,
        is_ai: bool | None,
        is_r18: bool,
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
            query = query.filter(nsfw_tag__in=nsfw_tag)
        if is_ai is not None:
            query = query.filter(is_ai=is_ai)
        if is_r18 is not None:
            query = (
                query.filter(nsfw_tag=2) if is_r18 else query.filter(nsfw_tag__not=2)
            )
        for tag in tags:
            query = query.filter(
                Q(tags__contains=tag)
                | Q(author__contains=tag)
                | Q(pid__contains=tag)
                | Q(uid__contains=tag)
            )
        sql = random(query.annotate(), num)
        logger.debug(f"执行pix查询sql: {sql}")
        return await PixGallery.raw(sql)  # type: ignore

    @classmethod
    async def token_to_db(cls, ip: str, token: str, tags: list[str]):
        """存储查询日志

        参数:
            ip: ip
            token: token
            tags: tags
        """
        if not tags:
            return
        await CallLog.create(
            ip=ip,
            token=token,
            tags=tags,
        )
        if create_list := [TagLog(tag=t, token=token) for t in tags if t.strip()]:
            await TagLog.bulk_create(create_list, 10)
