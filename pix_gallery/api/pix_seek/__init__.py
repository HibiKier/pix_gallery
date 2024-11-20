import asyncio

from fastapi.responses import JSONResponse
from loguru import logger

from ...auth import auth_superuser
from ...router import router
from ..base_models import Result
from .data_source import PixSeekManage
from .models import PostData


@router.post(
    "/pix_seek",
    dependencies=[auth_superuser()],
    response_model=Result,
    response_class=JSONResponse,
    description="PIX搜索",
)
async def _(data: PostData | None = None):
    try:
        seek_type = data.seek_type if data else "a"
        num = data.num if data else None
        result = await PixSeekManage.start_seek(seek_type or "a", num)  # type: ignore
        logger.info(f"PIX 添加结果: {result}")
        return Result.ok(info=result)
    except ValueError:
        return Result.warning_(info="没有需要收录的数据...")
    except Exception as e:
        return Result.fail(info=f"异常错误 {type(e)}: {e}")


async def __start_seek():
    while True:
        await PixSeekManage.start_seek("u", 100, False)
        await asyncio.sleep(60 * 60 * 24)


is_run = False


@router.post(
    "/pix_seek_run",
    dependencies=[auth_superuser()],
    response_model=Result,
    response_class=JSONResponse,
    description="PIX搜索",
)
async def _():
    global is_run
    if is_run:
        return Result.ok(info="pix搜索已启动")
    is_run = True
    asyncio.create_task(__start_seek())
    return Result.ok(info="启动pix搜索")
