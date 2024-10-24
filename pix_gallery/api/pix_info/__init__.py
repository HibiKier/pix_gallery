from fastapi.responses import JSONResponse

from ...auth import authentication
from ..base_models import Result
from ..router import router
from .data_source import InfoManage
from .models import ImageCount, KeywordItem


@router.get(
    "/pix_gallery_count",
    dependencies=[authentication()],
    response_model=Result[ImageCount],
    response_class=JSONResponse,
    description="PIX图片数量",
)
async def _(tags: list[str] | None = None):
    if tags is None:
        tags = []
    result = await InfoManage.get_pix_gallery(tags)
    return Result.ok(result)


@router.get(
    "/pix_seek_info",
    dependencies=[authentication()],
    response_model=Result[list[KeywordItem]],
    response_class=JSONResponse,
    description="PIX搜索关键词信息",
)
async def _(seek_type: str = "a"):
    result = await InfoManage.get_seek_info(seek_type)
    return Result.ok(result)
