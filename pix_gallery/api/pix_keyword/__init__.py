from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from ...auth import authentication
from ...config import KwHandleType
from ..base_models import Result
from ..router import router
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
    if data.add_type == "b":
        result = await KeywordManage.add_black_pid(ip, data.content)
    elif data.add_type == "u":
        result = await KeywordManage.add_uid(ip, data.content)
    elif data.add_type == "p":
        result = await KeywordManage.add_pid(ip, data.content)
    else:
        result = await KeywordManage.add_keyword(ip, data.content)
    logger.info(f"PIX ip: {ip} 添加结果: {result}")
    return Result.ok(info=result)


@router.post(
    "/pix_handle",
    dependencies=[authentication()],
    response_model=Result,
    response_class=JSONResponse,
    description="PIX搜索",
)
async def _(data: PixHandleData, request: Request):
    ip = request.client.host if request.client else ""
    if data.handle_type == "b":
        result = await KeywordManage.handle_keyword(
            ip, data.id, None, KwHandleType.BLACK
        )
    elif data.handle_type == "a":
        result = await KeywordManage.handle_keyword(
            ip, data.id, None, KwHandleType.PASS
        )
    elif data.handle_type == "f":
        result = await KeywordManage.handle_keyword(
            ip, data.id, None, KwHandleType.FAIL
        )
    else:
        result = await KeywordManage.handle_keyword(
            ip, data.id, None, KwHandleType.IGNORE
        )
    logger.info(f"PIX ip: {ip} 处理结果: {result}")
    return Result.ok(info=result)
