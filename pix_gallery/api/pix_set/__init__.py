from fastapi import Request
from fastapi.responses import JSONResponse

from ...auth import auth_superuser, authentication
from ...router import router
from ..base_models import Result
from .data_source import PixSetManage
from .models import SetPixHandle, SetPixPost


@router.post(
    "/set_pix",
    dependencies=[authentication()],
    response_model=Result[str],
    response_class=JSONResponse,
    description="修改pix数据请求",
)
async def _(data: SetPixPost, request: Request):
    if data.block_level is None and data.nsfw_tag is None:
        return Result.fail("block与nsfw_tag不能同时为空...")
    if data.block_level is not None and data.nsfw_tag is not None:
        return Result.fail("block与nsfw_tag不能同时有值...")
    if data.nsfw_tag and data.nsfw_tag not in [0, 1, 2]:
        return Result.fail("nsfw_tag值不合法，必须在[0, 1, 2]中...")
    if data.block_level and data.block_level not in [1, 2]:
        return Result.fail("block_level值不合法，必须在[1, 2]中...")
    if authorization_str := request.headers.get("Authorization") or "":
        authorization_str = authorization_str.split()[-1]
    await PixSetManage.create_set_pix(data, authorization_str)
    return Result.ok(info="成功提交此次修改请求...")


@router.post(
    "/set_pix_handle",
    dependencies=[auth_superuser()],
    response_model=Result[str],
    response_class=JSONResponse,
    description="处理pix数据请求",
)
async def _(data: SetPixHandle):
    result = await PixSetManage.set_pix(data.id, data.handle_type)
    return Result.ok(info=result)
