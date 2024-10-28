from fastapi.responses import JSONResponse

from ...auth import auth_superuser, authentication
from ...router import router
from ..base_models import Result
from .data_source import InfoManage
from .models import ImageCount, KeywordItem, QueryCount, QuerySeek


@router.post(
    "/pix_gallery_count",
    dependencies=[authentication()],
    response_model=Result[ImageCount],
    response_class=JSONResponse,
    description="PIX图片数量",
)
async def _(data: QueryCount | None = None):
    if not data:
        data = QueryCount()
    result = await InfoManage.get_pix_gallery(data.tags)
    return Result.ok(result)


@router.post(
    "/pix_seek_info",
    dependencies=[auth_superuser()],
    response_model=Result[list[KeywordItem]],
    response_class=JSONResponse,
    description="PIX搜索关键词信息",
)
async def _(data: QuerySeek | None = None):
    if not data:
        data = QuerySeek()
    result = await InfoManage.get_seek_info(data.seek_type)
    return Result.ok(result)
