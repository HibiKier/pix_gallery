import asyncio

from fastapi.responses import JSONResponse

from pix_gallery.database.models.pix_gallery import PixGallery
from pix_gallery.database.models.star_log import StarLog
from pix_gallery.database.models.star_users import StarUsers

from ...auth import authentication
from ...router import router
from ..base_models import Result
from .models import Pix, RankData, StarData


@router.post(
    "/star",
    dependencies=[authentication(True)],
    response_model=Result[str],
    response_class=JSONResponse,
    description="收藏图片",
)
async def _(data: StarData):
    if "-" not in data.pid:
        return Result.fail(info="图片数据不合法...")
    pid_split = data.pid.split("-")
    pid = pid_split[0]
    img_p = int(pid_split[1])
    if not (pix := await PixGallery.get_or_none(pid=pid, img_p=img_p)):
        return Result.fail(info="图片数据不存在...")
    user, _ = await StarUsers.get_or_create(user_id=data.user_id)
    if data.pid in user.pids:
        return Result.fail(info="该图片已收藏...")
    user.pids += f"{data.pid},"
    pix.star += 1
    asyncio.gather(
        *[
            user.save(update_fields=["pids"]),
            pix.save(update_fields=["star"]),
            StarLog.create(pid=data.pid, is_star=True),
        ]
    )
    return Result.ok(info="成功收藏该图片!")


@router.post(
    "/unstar",
    dependencies=[authentication(True)],
    response_model=Result[str],
    response_class=JSONResponse,
    description="处理pix数据请求",
)
async def _(data: StarData):
    if "-" not in data.pid:
        return Result.fail(info="图片数据不合法...")
    pid_split = data.pid.split("-")
    pid = pid_split[0]
    img_p = int(pid_split[1])
    if not (pix := await PixGallery.get_or_none(pid=pid, img_p=img_p)):
        return Result.fail(info="图片数据不存在...")
    user, _ = await StarUsers.get_or_create(user_id=data.user_id)
    if data.pid not in user.pids:
        return Result.fail(info="为收藏该图片哦...")
    user.pids = user.pids.replace(f"{data.pid},", "")
    pix.star -= 1
    asyncio.gather(
        *[
            user.save(update_fields=["pids"]),
            pix.save(update_fields=["star"]),
            StarLog.create(pid=data.pid, is_star=False),
        ]
    )
    return Result.ok(info="成功取消收藏该图片!")


@router.get(
    "/get_user_star_list",
    dependencies=[authentication(True)],
    response_model=Result[str],
    response_class=JSONResponse,
    description="处理pix数据请求",
)
async def _(user_id: str):
    user = await StarUsers.get_or_none(user_id=user_id)
    if not user:
        return Result.ok(info="该用户没有收藏任何图片哦...")
    return Result.ok(user.pids.split(","))


@router.post(
    "/star_rank",
    dependencies=[authentication(True)],
    response_model=Result[list[Pix]],
    response_class=JSONResponse,
    description="处理pix数据请求",
)
async def _(data: RankData):
    if data.num > 50:
        return Result.fail(info="最多查询50条数据哦...")
    result_list = (
        await PixGallery.filter(block_level__isnull=True, nsfw_tag__in=data.nsfw)
        .annotate()
        .order_by("-star")
        .limit(data.num)
    )
    data_list = []
    for result in result_list:
        k = list(result.image_urls)[0]
        url = result.image_urls[k]
        data_list.append(
            Pix(
                pid=result.pid,
                uid=result.uid,
                author=result.author,
                title=result.title,
                sanity_level=result.sanity_level,
                x_restrict=result.x_restrict,
                total_view=result.total_view,
                total_bookmarks=result.total_bookmarks,
                nsfw_tag=result.nsfw_tag,
                is_ai=result.is_ai,
                url=url,
                is_multiple=result.is_multiple,
                img_p=result.img_p,
                tags=result.tags,
                star=result.star,
            )
        )
    return Result.ok(data_list)
