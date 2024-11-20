import re

from loguru import logger
from tortoise.expressions import Q

from ...database.models.call_log import CallLog
from ...database.models.pix_gallery import PixGallery
from ...database.models.tag_log import TagLog


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
        is_r18: bool | None,
    ) -> list[PixGallery]:
        """获取图片

        参数:
            tags: tags，包含uid和pid
            num: 数量

        返回:
            list[PixGallery]: 图片数据列表
        """
        query = PixGallery.filter(block_level__isnull=True)
        if len(tags) == 1 and re.search(r"^\d+-\d+$", tags[0]):
            pid_split = tags[0].split("-")
            result = await query.filter(pid=pid_split[0], img_p=pid_split[1]).first()
            return [result] if result else []
        else:
            if nsfw_tag:
                query = query.filter(nsfw_tag__in=nsfw_tag)
            if is_ai is not None:
                query = query.filter(is_ai=is_ai)
            if is_r18 is not None:
                query = (
                    query.filter(nsfw_tag=2)
                    if is_r18
                    else query.filter(nsfw_tag__not=2)
                )
            for tag in tags:
                query = query.filter(
                    Q(tags__icontains=tag)
                    | Q(author__icontains=tag)
                    | Q(pid__icontains=tag)
                    | Q(uid__icontains=tag)
                    | Q(title__icontains=tag)
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
