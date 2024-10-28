from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from pix_gallery.database.models.call_log import CallLog
from pix_gallery.database.models.tag_log import TagLog

from ...auth import authentication
from ...router import router
from ..base_models import Result
from .data_source import PixManage
from .models import Pix, PostData


@router.post(
    "/get_pix",
    dependencies=[authentication()],
    response_model=Result[list[Pix]],
    response_class=JSONResponse,
    description="随机pix",
)
async def _(request: Request, data: PostData | None = None):
    if not data:
        data = PostData()
    logger.info(f"执行get-pix, data: {data}")
    result_list = await PixManage.get_pix(
        data.tags, data.num, data.nsfw_tag, data.ai, data.r18
    )
    authorization_str = request.headers.get("Authorization") or ""
    if authorization_str:
        authorization_str = authorization_str.split()[-1]
    ip = request.client.host if request.client else ""
    data_list = []
    for result in result_list:
        if data.size in result.image_urls:
            url = result.image_urls[data.size]
        else:
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
            )
        )
    await CallLog.create(token=authorization_str, ip=ip, tags=",".join(data.tags))
    if tag_db_list := [TagLog(name=tag, token=authorization_str) for tag in data.tags]:
        await TagLog.bulk_create(tag_db_list, 10)
    return Result.ok(data_list)
