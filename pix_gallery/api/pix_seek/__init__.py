import time

from fastapi.responses import JSONResponse
from loguru import logger

from ...auth import authentication
from ..base_models import Result
from ..router import router
from .data_source import PixSeekManage
from .models import PostData


@router.post(
    "/pix_seek",
    dependencies=[authentication()],
    response_model=Result,
    response_class=JSONResponse,
    description="PIX搜索",
)
async def _(data: PostData):
    try:
        start = time.time()
        result = await PixSeekManage.start_seek(data.seek_type or "a", data.num)  # type: ignore
        end = time.time()
        logger.info(f"PIX 添加结果: {result}")
        return Result.ok(
            info=f"累计耗时: {int(end-start)} 秒\n共保存 {result[0]} 条数据!"
            f"\n已存在数据: {result[1]} 条!"
        )
    except ValueError:
        return Result.warning_(info="没有需要收录的数据...")
    except Exception as e:
        return Result.fail(info=f"异常错误 {type(e)}: {e}")
