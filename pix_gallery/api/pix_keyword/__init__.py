from fastapi import Request
from fastapi.responses import JSONResponse
from httpx import HTTPStatusError
from loguru import logger

from ...auth import auth_superuser, authentication
from ...config import KwType
from ...router import router
from ..base_models import Result
from .data_source import KeywordManage
from .models import PixAddData, PixHandleData


@router.post(
    "/pix_add",
    dependencies=[authentication()],
    response_model=Result,
    response_class=JSONResponse,
    description="PIX搜索",
)
async def _(data: PixAddData, request: Request):
    ip = request.client.host if request.client else ""
    if auth := request.headers.get("Authorization") or None:
        auth = auth.split()[-1]
    try:
        if data.add_type == KwType.BLACK:
            result = await KeywordManage.add_black_pid(ip, data.content[0], auth)
        elif data.add_type == KwType.UID:
            result = await KeywordManage.add_uid(ip, data.content, auth)
        elif data.add_type == KwType.PID:
            result = await KeywordManage.add_pid(ip, data.content, auth)
        else:
            result = await KeywordManage.add_keyword(ip, data.content, auth)
        logger.info(f"PIX ip: {ip} 添加结果: {result}")
        return Result.ok(info=result)
    except HTTPStatusError as e:
        logger.error(f"PIX ip: {ip} 添加失败")
        return Result.fail(f"访问错误 code: {e.response.status_code}")


@router.post(
    "/pix_handle",
    dependencies=[auth_superuser()],
    response_model=Result,
    response_class=JSONResponse,
    description="PIX搜索",
)
async def _(data: PixHandleData, request: Request):
    ip = request.client.host if request.client else ""
    result = await KeywordManage.handle_keyword(ip, data.id, None, data.handle_type)
    logger.info(f"PIX ip: {ip} 处理结果: {result}")
    return Result.ok(info=result)
