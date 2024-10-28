from fastapi.responses import JSONResponse
from loguru import logger

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
async def _(data: PostData | None = None):
    if not data:
        data = PostData()
    logger.info(f"执行get-pix, data: {data}")
    result_list = await PixManage.get_pix(
        data.tags, data.num, data.nsfw_tag, data.ai, data.r18
    )
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
            )
        )

    return Result.ok(data_list)
