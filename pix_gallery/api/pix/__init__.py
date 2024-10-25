from fastapi.responses import JSONResponse

from ..base_models import Result
from ..router import router
from .data_source import PixManage
from .models import Pix


@router.get(
    "/get_pix",
    response_model=Result[list[Pix]],
    response_class=JSONResponse,
    description="随机pix",
)
async def _(
    tags: list[str] | None = None,
    num: int = 1,
    size: str = "large",
    nsfw_tag: int | None = None,
    is_ai: bool | None = None,
):
    if tags is None:
        tags = []
    result_list = await PixManage.get_pix(tags, num, nsfw_tag, is_ai)
    data_list = []
    for result in result_list:
        if size in result.image_urls:
            url = result.image_urls[size]
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
